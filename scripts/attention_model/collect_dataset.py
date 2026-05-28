"""
collect_dataset.py — Sprint 115: сбор датасета из исторических рейсов Oracle.

Экспортирует закрытые рейсы в JSON-датасет для обучения Attention Model VRP.
Минимум 1000 рейсов для корректного обучения.

Запуск:
    python scripts/attention_model/collect_dataset.py --output data/vrp_dataset.json
"""

import argparse
import json
import os
import sys

# Добавляем корень проекта в path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))


def collect(output: str, min_pallets: int = 3, max_stops: int = 30) -> None:
    from api.wms_api_server.app.oracle_gateway import OracleGateway
    gw = OracleGateway()

    print("Fetching historical trips from Oracle...")
    rows = gw.fetch_all(
        """
        SELECT TT.ID               AS TASK_ID,
               TT.SHIPMENT_DATE,
               TT.TRANSPORT,
               TT.TRANSTYPE,
               COUNT(DISTINCT SP.ST_NUMBER) AS STOP_COUNT,
               COUNT(SP.PALLET_UID)         AS PALLET_COUNT
          FROM RABAEV.RRL_TRANSPORT_TASK TT
          JOIN RABAEV.RRL_SBORKA_PALLETS SP ON SP.TRANSTASK_ID = TT.ID AND NVL(SP.DELETED,0)=0
         WHERE NVL(TT.DELETED,0)=0
           AND TT.CONDITION IN ('Отгружен', 'Закрыт')
         GROUP BY TT.ID, TT.SHIPMENT_DATE, TT.TRANSPORT, TT.TRANSTYPE
        HAVING COUNT(SP.PALLET_UID) >= :min_pallets
           AND COUNT(DISTINCT SP.ST_NUMBER) <= :max_stops
         ORDER BY TT.SHIPMENT_DATE DESC
        """,
        {"min_pallets": min_pallets, "max_stops": max_stops},
    )
    print(f"Found {len(rows)} trips.")

    dataset = []
    for r in rows:
        task_id = int(r.get("task_id") or 0)
        # Get stop details with coordinates
        stops = gw.fetch_all(
            """
            SELECT SP.ST_NUMBER, SP.ADDR, SP.ORD,
                   A.LATITUDE, A.LONGITUDE,
                   SP.ZONE_TIME_PLAN_IN AS TW_FROM,
                   SP.ZONE_TIME_PLAN_OUT AS TW_TO,
                   COUNT(SP.PALLET_UID) AS PALLETS
              FROM RABAEV.RRL_SBORKA_PALLETS SP
              LEFT JOIN RABAEV.RRL_ADDR A ON A.ADDR = SP.ADDR
             WHERE SP.TRANSTASK_ID = :tid AND NVL(SP.DELETED,0)=0
             GROUP BY SP.ST_NUMBER, SP.ADDR, SP.ORD, A.LATITUDE, A.LONGITUDE,
                      SP.ZONE_TIME_PLAN_IN, SP.ZONE_TIME_PLAN_OUT
             ORDER BY SP.ORD NULLS LAST
            """,
            {"tid": task_id},
        )
        geo_stops = [s for s in stops if s.get("latitude") and s.get("longitude")]
        if len(geo_stops) < 2:
            continue  # Skip trips without coordinates

        dataset.append({
            "task_id": task_id,
            "shipment_date": str(r.get("shipment_date") or "")[:10],
            "transport_type": str(r.get("transtype") or ""),
            "pallet_count": int(r.get("pallet_count") or 0),
            "stops": [
                {
                    "st_number": str(s.get("st_number") or ""),
                    "lat": float(s.get("latitude")),
                    "lon": float(s.get("longitude")),
                    "pallets": int(s.get("pallets") or 0),
                    "ord": int(s.get("ord") or 0),
                    "tw_from": str(s.get("tw_from") or ""),
                    "tw_to": str(s.get("tw_to") or ""),
                }
                for s in geo_stops
            ],
        })

    print(f"Dataset: {len(dataset)} trips with coordinates.")
    os.makedirs(os.path.dirname(output), exist_ok=True)
    with open(output, "w", encoding="utf-8") as f:
        json.dump(dataset, f, ensure_ascii=False, indent=2)
    print(f"Saved to {output}")
    if len(dataset) < 1000:
        print(f"WARNING: Only {len(dataset)} trips — recommended minimum is 1000 for AM training.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Collect VRP dataset from Oracle")
    parser.add_argument("--output", default="data/vrp_dataset.json")
    parser.add_argument("--min-pallets", type=int, default=3)
    parser.add_argument("--max-stops", type=int, default=30)
    args = parser.parse_args()
    collect(args.output, args.min_pallets, args.max_stops)
