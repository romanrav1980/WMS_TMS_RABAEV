"""
driver_mobile.py — FastAPI роутер мобильного интерфейса водителя.

Sprint 103: GET /api/driver/trips — рейсы водителя на дату
Sprint 104: POST /api/driver/ops/{op_id}/start|done — отметка факта
Sprint 103-104 не требуют admin-авторизации; водитель идентифицируется по driver_id.
"""

from datetime import date

from fastapi import APIRouter, HTTPException, Query

from ..oracle_gateway import OracleGateway

router = APIRouter(prefix="/api/driver", tags=["driver-mobile"])


def _gw() -> OracleGateway:
    return OracleGateway()


# ---------------------------------------------------------------------------
# Sprint 103 — Мои рейсы
# ---------------------------------------------------------------------------

@router.get("/trips")
def get_driver_trips(
    driver_id: int = Query(..., description="ID водителя (из QR-кода или прямой ссылки)"),
    trip_date: date = Query(default=None),
) -> list[dict]:
    """Рейсы водителя на указанную дату (Sprint 103)."""
    if trip_date is None:
        from datetime import date as _date
        trip_date = _date.today()

    gw = _gw()
    rows = gw.fetch_all(
        """
        SELECT TT.ID              AS TASK_ID,
               TT.SHIPMENT_DATE,
               TT.TRANSPORT       AS NUM_PLAT,
               TT.TRANSTYPE       AS TRANSPORT_TYPE,
               TT.CONDITION,
               TT.PRIMECHANIE     AS NOTE,
               TT.PRICE,
               COUNT(DISTINCT SP.ST_NUMBER)  AS ST_COUNT,
               NVL(TT.TEMP_WEIGHT, 0)        AS WEIGHT_KG
          FROM RABAEV.RRL_TRANSPORT_TASK TT
          LEFT JOIN RABAEV.RRL_SBORKA_PALLETS SP ON SP.TRANSTASK_ID = TT.ID
         WHERE TT.VODITEL_ID = :driver_id
           AND TRUNC(TT.SHIPMENT_DATE) = TRUNC(:trip_date)
           AND NVL(TT.DELETED, 0) = 0
         GROUP BY TT.ID, TT.SHIPMENT_DATE, TT.TRANSPORT, TT.TRANSTYPE,
                  TT.CONDITION, TT.PRIMECHANIE, TT.PRICE, TT.TEMP_WEIGHT
         ORDER BY TT.SHIPMENT_DATE
        """,
        {"driver_id": driver_id, "trip_date": trip_date},
    )
    return [
        {
            "task_id": int(r.get("task_id") or 0),
            "shipment_date": str(r.get("shipment_date") or ""),
            "num_plat": str(r.get("num_plat") or ""),
            "transport_type": str(r.get("transport_type") or ""),
            "condition": str(r.get("condition") or ""),
            "note": str(r.get("note") or ""),
            "price": float(r.get("price") or 0),
            "st_count": int(r.get("st_count") or 0),
            "weight_kg": float(r.get("weight_kg") or 0),
        }
        for r in rows
    ]


@router.get("/trips/{task_id}/sts")
def get_trip_sts(task_id: int, driver_id: int = Query(...)) -> list[dict]:
    """СТ в рейсе водителя (Sprint 103)."""
    gw = _gw()
    # Проверяем принадлежность рейса водителю
    owner = gw.fetch_all(
        "SELECT COUNT(*) AS CNT FROM RABAEV.RRL_TRANSPORT_TASK WHERE ID=:tid AND VODITEL_ID=:did",
        {"tid": task_id, "did": driver_id},
    )
    if int((owner[0] if owner else {}).get("cnt") or 0) == 0:
        raise HTTPException(status_code=403, detail="Trip not assigned to this driver")

    rows = gw.fetch_all(
        """
        SELECT SP.ST_NUMBER,
               SP.ADDR,
               SP.ORD,
               SP.ZONE_TIME_PLAN_IN  AS TIME_FROM,
               SP.ZONE_TIME_PLAN_OUT AS TIME_TO,
               SP.LOAD_TYPE,
               COUNT(SP.PALLET_UID)  AS PALLET_COUNT
          FROM RABAEV.RRL_SBORKA_PALLETS SP
         WHERE SP.TRANSTASK_ID = :task_id
         GROUP BY SP.ST_NUMBER, SP.ADDR, SP.ORD, SP.ZONE_TIME_PLAN_IN,
                  SP.ZONE_TIME_PLAN_OUT, SP.LOAD_TYPE
         ORDER BY SP.ORD NULLS LAST
        """,
        {"task_id": task_id},
    )
    return [
        {
            "st_number": str(r.get("st_number") or ""),
            "addr": str(r.get("addr") or ""),
            "ord": int(r.get("ord") or 0),
            "time_from": str(r.get("time_from") or ""),
            "time_to": str(r.get("time_to") or ""),
            "load_type": str(r.get("load_type") or ""),
            "pallet_count": int(r.get("pallet_count") or 0),
        }
        for r in rows
    ]


@router.get("/trips/{task_id}/ops")
def get_trip_operations(task_id: int, driver_id: int = Query(...)) -> list[dict]:
    """Операции рейса с plan/fact временами (Sprint 103)."""
    gw = _gw()
    owner = gw.fetch_all(
        "SELECT COUNT(*) AS CNT FROM RABAEV.RRL_TRANSPORT_TASK WHERE ID=:tid AND VODITEL_ID=:did",
        {"tid": task_id, "did": driver_id},
    )
    if int((owner[0] if owner else {}).get("cnt") or 0) == 0:
        raise HTTPException(status_code=403, detail="Trip not assigned to this driver")

    rows = gw.fetch_all(
        """
        SELECT ID, OPERATION_CODE, ORD, PLAN_START, PLAN_END, FACT_START, FACT_END, NOTE
          FROM RABAEV.RRL_TT_OPERATIONS
         WHERE TT_ID = :task_id
         ORDER BY ORD
        """,
        {"task_id": task_id},
    )
    return [
        {
            "op_id": int(r.get("id") or 0),
            "operation_code": str(r.get("operation_code") or ""),
            "ord": int(r.get("ord") or 0),
            "plan_start": str(r.get("plan_start") or ""),
            "plan_end": str(r.get("plan_end") or ""),
            "fact_start": str(r.get("fact_start") or ""),
            "fact_end": str(r.get("fact_end") or ""),
            "note": str(r.get("note") or ""),
            "status": (
                "done" if r.get("fact_end") else
                "in_progress" if r.get("fact_start") else
                "pending"
            ),
        }
        for r in rows
    ]


# ---------------------------------------------------------------------------
# Sprint 104 — Отметка факта операций
# ---------------------------------------------------------------------------

@router.post("/ops/{op_id}/start", status_code=200)
def mark_op_start(op_id: int, driver_id: int = Query(...)) -> dict:
    """Зафиксировать начало операции (fact_start = now) — Sprint 104."""
    gw = _gw()
    _verify_op_driver(gw, op_id, driver_id)
    gw.execute(
        """
        UPDATE RABAEV.RRL_TT_OPERATIONS
           SET FACT_START = SYSDATE
         WHERE ID = :op_id AND FACT_START IS NULL
        """,
        {"op_id": op_id},
    )
    return {"op_id": op_id, "status": "in_progress"}


@router.post("/ops/{op_id}/done", status_code=200)
def mark_op_done(op_id: int, driver_id: int = Query(...)) -> dict:
    """Зафиксировать завершение операции (fact_end = now) — Sprint 104."""
    gw = _gw()
    _verify_op_driver(gw, op_id, driver_id)
    gw.execute(
        """
        UPDATE RABAEV.RRL_TT_OPERATIONS
           SET FACT_START = NVL(FACT_START, SYSDATE),
               FACT_END   = SYSDATE
         WHERE ID = :op_id AND FACT_END IS NULL
        """,
        {"op_id": op_id},
    )
    return {"op_id": op_id, "status": "done"}


def _verify_op_driver(gw: OracleGateway, op_id: int, driver_id: int) -> None:
    rows = gw.fetch_all(
        """
        SELECT COUNT(*) AS CNT
          FROM RABAEV.RRL_TT_OPERATIONS OPS
          JOIN RABAEV.RRL_TRANSPORT_TASK TT ON TT.ID = OPS.TT_ID
         WHERE OPS.ID = :op_id AND TT.VODITEL_ID = :did
        """,
        {"op_id": op_id, "did": driver_id},
    )
    if int((rows[0] if rows else {}).get("cnt") or 0) == 0:
        raise HTTPException(status_code=403, detail="Operation not accessible to this driver")
