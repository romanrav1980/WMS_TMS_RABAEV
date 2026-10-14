from datetime import date, timedelta
from pathlib import Path
from typing import Any
from .available_sts_page import page_available_sts

QUERY = Path(__file__).with_suffix(".sql").read_text(encoding="utf-8")

verify_expr = (
    "ROUND(COUNT(DISTINCT CASE WHEN NVL(P.PROOVED,0) = 1 OR NVL(P.PROOVED_BY_SCAN,0) = 1 "
    "THEN P.ID END) * 100 / NULLIF(COUNT(DISTINCT P.ID), 0), 0)"
)
weight_expr = "ROUND(SUM(NVL(R.ORDER_WEIGHT, 0)), 0)"
volume_expr = "ROUND(SUM(NVL(R.TARESIZE, 0) * NVL(R.PACK_COUNT, 0)) / 1000000, 2)"


def available_sts_query(
        stdate: date | None = None,
        date_to: date | None = None,
        unassigned_only: bool = True,
        ware_id: int | None = None,
        ware_ids: list[int] | None = None,
        addr_mask: str | None = None,
        st_mask: str | None = None,
        st_mask_exclude: bool = False,
        transport_type: str | None = None,
        assembled_only: bool = False,
        not_assembled_only: bool = False,
        max_weight_kg: float | None = None,
        max_volume_m3: float | None = None,
        articul: str | None = None,
        raion: str | None = None,
        page: int | None = None,
        page_size: int | None = None,
    ) -> tuple[str, dict[str, Any]]:
    conditions: list[str] = ["P.CONDITION <> 2"]
    having: list[str] = []
    params: dict[str, Any] = {}

    if unassigned_only:
        conditions.append("P.TRANSTASK_ID IS NULL")

    # Дата СТ: точное равенство или диапазон
    if stdate is not None and date_to is None:
        conditions.append("P.STDATE >= :stdate AND P.STDATE < :stdate_next")
        params["stdate"] = stdate
        params["stdate_next"] = stdate + timedelta(days=1)
    elif stdate is not None and date_to is not None:
        conditions.append("P.STDATE >= :stdate AND P.STDATE < :date_to_next")
        params["stdate"] = stdate
        params["date_to_next"] = date_to + timedelta(days=1)
    elif date_to is not None:
        conditions.append("P.STDATE < :date_to_next")
        params["date_to_next"] = date_to + timedelta(days=1)

    # Фильтр по складам: ware_ids приоритетнее одиночного ware_id
    effective_ware_ids = ware_ids or ([ware_id] if ware_id is not None else None)
    if effective_ware_ids:
        placeholders = ", ".join(f":wid{i}" for i in range(len(effective_ware_ids)))
        conditions.append(f"P.WARE_ID IN ({placeholders})")
        for i, wid in enumerate(effective_ware_ids):
            params[f"wid{i}"] = wid

    if addr_mask:
        conditions.append(
            "(P.ADDR LIKE :addr_mask OR A.REGION LIKE :addr_mask OR A.RAION LIKE :addr_mask)"
        )
        params["addr_mask"] = f"%{addr_mask}%"

    if st_mask:
        op = "NOT LIKE" if st_mask_exclude else "LIKE"
        conditions.append(f"UPPER(P.ST_NUMBER) {op} UPPER(:st_mask)")
        params["st_mask"] = f"%{st_mask}%"

    if transport_type:
        conditions.append("NVL(A.TRANSPORT_TYPE, '0') = :transport_type")
        params["transport_type"] = transport_type

    if articul:
        conditions.append(
            """EXISTS (
                SELECT 1
                  FROM RABAEV.RRL_SBORKA_PALLETS SP2
                  JOIN RABAEV.RRL_SBORKA_PALLET_ROWS R2 ON R2.PALLET_UID = SP2.PALLET_UID
                 WHERE SP2.ST_NUMBER = P.ST_NUMBER
                   AND UPPER(R2.ARTICUL) LIKE UPPER(:articul)
            )"""
        )
        params["articul"] = f"%{articul}%"

    if assembled_only:
        having.append(f"{verify_expr} > 0")
    elif not_assembled_only:
        having.append(f"NVL({verify_expr}, 0) = 0")

    if max_weight_kg is not None:
        having.append(f"{weight_expr} < :max_weight_kg")
        params["max_weight_kg"] = max_weight_kg

    if max_volume_m3 is not None:
        having.append(f"{volume_expr} < :max_volume_m3")
        params["max_volume_m3"] = max_volume_m3

    if raion:
        if raion == "(без района)":
            conditions.append("A.RAION IS NULL")
        else:
            conditions.append("A.RAION = :raion")
            params["raion"] = raion

    where_sql = "WHERE " + " AND ".join(conditions) if conditions else ""
    having_sql = "HAVING " + " AND ".join(having) if having else ""

    sql = QUERY.format(where_sql=where_sql,having_sql=having_sql,weight_expr=weight_expr,volume_expr=volume_expr,verify_expr=verify_expr)
    return page_available_sts(sql,where_sql,bool(having),page,page_size,params), params
