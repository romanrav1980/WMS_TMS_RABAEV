"""
transport_kpi.py — KPI-дашборд для руководства.

Sprint 108: операционные метрики (утилизация парка, рейсы по дням, регионы)
Sprint 109: финансовые метрики (биллинг по ТК, тренды)
"""

from datetime import date

from fastapi import APIRouter, Depends, Query

from ..auth import AdminUser, TRANSPORT_DISPATCH_VIEW_PERMISSION, require_permission
from ..oracle_gateway import OracleGateway

router = APIRouter(prefix="/api/admin/transport/kpi", tags=["transport-kpi"])


def _gw() -> OracleGateway:
    return OracleGateway()


# ---------------------------------------------------------------------------
# Sprint 108 — Операционные KPI
# ---------------------------------------------------------------------------

@router.get("/fleet")
def get_fleet_kpi(
    date_from: date = Query(...),
    date_to: date = Query(...),
    _user: AdminUser = Depends(require_permission(TRANSPORT_DISPATCH_VIEW_PERMISSION)),
) -> list[dict]:
    """Утилизация парка по дням — рейсов создано, паллет, вес (Sprint 108)."""
    rows = _gw().fetch_all(
        """
        SELECT TRUNC(TT.SHIPMENT_DATE) AS DAY,
               COUNT(DISTINCT TT.ID)        AS TRIPS_TOTAL,
               COUNT(DISTINCT CASE WHEN NVL(TT.CONDITION,'') IN ('Отгружен','Закрыт') THEN TT.ID END) AS TRIPS_CLOSED,
               SUM(SP.PALLET_COUNT)         AS PALLETS,
               SUM(SP.WEIGHT_KG)            AS WEIGHT_KG
          FROM RABAEV.RRL_TRANSPORT_TASK TT
          LEFT JOIN (
            SELECT TRANSTASK_ID,
                   COUNT(PALLET_UID) AS PALLET_COUNT,
                   SUM(ORDER_WEIGHT) AS WEIGHT_KG
              FROM RABAEV.RRL_SBORKA_PALLETS
             WHERE NVL(DELETED,0)=0
             GROUP BY TRANSTASK_ID
          ) SP ON SP.TRANSTASK_ID = TT.ID
         WHERE NVL(TT.DELETED,0)=0
           AND TRUNC(TT.SHIPMENT_DATE) BETWEEN :d1 AND :d2
         GROUP BY TRUNC(TT.SHIPMENT_DATE)
         ORDER BY 1
        """,
        {"d1": date_from, "d2": date_to},
    )
    return [
        {
            "day": str(r.get("day") or "")[:10],
            "trips_total": int(r.get("trips_total") or 0),
            "trips_closed": int(r.get("trips_closed") or 0),
            "pallets": int(r.get("pallets") or 0),
            "weight_kg": float(r.get("weight_kg") or 0),
        }
        for r in rows
    ]


@router.get("/summary")
def get_summary_kpi(
    date_from: date = Query(...),
    date_to: date = Query(...),
    _user: AdminUser = Depends(require_permission(TRANSPORT_DISPATCH_VIEW_PERMISSION)),
) -> dict:
    """Сводные KPI за период (Sprint 108)."""
    rows = _gw().fetch_all(
        """
        SELECT COUNT(DISTINCT TT.ID)     AS TRIPS_TOTAL,
               COUNT(DISTINCT CASE WHEN NVL(TT.CONDITION,'') IN ('Отгружен','Закрыт') THEN TT.ID END) AS TRIPS_CLOSED,
               COUNT(DISTINCT TT.TRANSPORT) AS VEHICLES_USED,
               SUM(SP.PALLET_COUNT)        AS PALLETS,
               SUM(SP.WEIGHT_KG)           AS WEIGHT_KG,
               AVG(SP.PALLET_COUNT)        AS AVG_PALLETS_PER_TRIP
          FROM RABAEV.RRL_TRANSPORT_TASK TT
          LEFT JOIN (
            SELECT TRANSTASK_ID, COUNT(PALLET_UID) AS PALLET_COUNT, SUM(ORDER_WEIGHT) AS WEIGHT_KG
              FROM RABAEV.RRL_SBORKA_PALLETS WHERE NVL(DELETED,0)=0 GROUP BY TRANSTASK_ID
          ) SP ON SP.TRANSTASK_ID = TT.ID
         WHERE NVL(TT.DELETED,0)=0
           AND TRUNC(TT.SHIPMENT_DATE) BETWEEN :d1 AND :d2
        """,
        {"d1": date_from, "d2": date_to},
    )
    r = rows[0] if rows else {}
    return {
        "trips_total": int(r.get("trips_total") or 0),
        "trips_closed": int(r.get("trips_closed") or 0),
        "vehicles_used": int(r.get("vehicles_used") or 0),
        "pallets": int(r.get("pallets") or 0),
        "weight_kg": float(r.get("weight_kg") or 0),
        "avg_pallets_per_trip": round(float(r.get("avg_pallets_per_trip") or 0), 1),
        "date_from": str(date_from),
        "date_to": str(date_to),
    }


@router.get("/regions")
def get_regions_kpi(
    trip_date: date = Query(default=None),
    date_from: date = Query(default=None),
    date_to: date = Query(default=None),
    _user: AdminUser = Depends(require_permission(TRANSPORT_DISPATCH_VIEW_PERMISSION)),
) -> list[dict]:
    """Топ регионов по паллетам (Sprint 108)."""
    from datetime import date as _date
    if trip_date:
        d1, d2 = trip_date, trip_date
    else:
        d1 = date_from or _date.today().replace(day=1)
        d2 = date_to or _date.today()

    rows = _gw().fetch_all(
        """
        SELECT SP.REGION,
               COUNT(DISTINCT TT.ID)   AS TRIPS,
               COUNT(SP.PALLET_UID)    AS PALLETS,
               SUM(SP.ORDER_WEIGHT)    AS WEIGHT_KG
          FROM RABAEV.RRL_SBORKA_PALLETS SP
          JOIN RABAEV.RRL_TRANSPORT_TASK TT ON TT.ID = SP.TRANSTASK_ID
         WHERE NVL(SP.DELETED,0)=0
           AND NVL(TT.DELETED,0)=0
           AND TRUNC(TT.SHIPMENT_DATE) BETWEEN :d1 AND :d2
         GROUP BY SP.REGION
         ORDER BY PALLETS DESC
         FETCH FIRST 15 ROWS ONLY
        """,
        {"d1": d1, "d2": d2},
    )
    return [
        {
            "region": str(r.get("region") or "—"),
            "trips": int(r.get("trips") or 0),
            "pallets": int(r.get("pallets") or 0),
            "weight_kg": float(r.get("weight_kg") or 0),
        }
        for r in rows
    ]


# ---------------------------------------------------------------------------
# Sprint 109 — Финансовые KPI (Биллинг)
# ---------------------------------------------------------------------------

@router.get("/billing")
def get_billing_kpi(
    date_from: date = Query(...),
    date_to: date = Query(...),
    _user: AdminUser = Depends(require_permission(TRANSPORT_DISPATCH_VIEW_PERMISSION)),
) -> dict:
    """Сводка биллинга за период (Sprint 109)."""
    rows = _gw().fetch_all(
        """
        SELECT COUNT(*)                  AS ORDERS_TOTAL,
               SUM(CASE WHEN PAYED=1 THEN 1 ELSE 0 END) AS ORDERS_PAID,
               SUM(CASE WHEN CLOSED=1 AND NVL(PAYED,0)=0 THEN 1 ELSE 0 END) AS ORDERS_CLOSED,
               SUM(NVL(TT_SUM.TOTAL,0)) AS TOTAL_AMOUNT,
               SUM(CASE WHEN PAYED=1 THEN NVL(TT_SUM.TOTAL,0) ELSE 0 END) AS PAID_AMOUNT
          FROM RABAEV.RRL_BILL_ORDERS BO
          LEFT JOIN (
            SELECT PAY_ORDER_ID, SUM(PRICE) AS TOTAL
              FROM RABAEV.RRL_TRANSPORT_TASK WHERE NVL(DELETED,0)=0 AND PAY_ORDER_ID IS NOT NULL
             GROUP BY PAY_ORDER_ID
          ) TT_SUM ON TT_SUM.PAY_ORDER_ID = BO.ID
         WHERE TRUNC(BO.DATEOFORDER) BETWEEN :d1 AND :d2
        """,
        {"d1": date_from, "d2": date_to},
    )
    r = rows[0] if rows else {}
    total = float(r.get("total_amount") or 0)
    paid = float(r.get("paid_amount") or 0)
    return {
        "orders_total": int(r.get("orders_total") or 0),
        "orders_paid": int(r.get("orders_paid") or 0),
        "orders_closed": int(r.get("orders_closed") or 0),
        "total_amount": total,
        "paid_amount": paid,
        "unpaid_amount": round(total - paid, 2),
        "date_from": str(date_from),
        "date_to": str(date_to),
    }


@router.get("/billing/by-company")
def get_billing_by_company(
    date_from: date = Query(...),
    date_to: date = Query(...),
    _user: AdminUser = Depends(require_permission(TRANSPORT_DISPATCH_VIEW_PERMISSION)),
) -> list[dict]:
    """Расходы на ТК по счетам за период (Sprint 109)."""
    rows = _gw().fetch_all(
        """
        SELECT BO.COMPANY,
               COUNT(DISTINCT BO.ID)    AS ORDERS,
               SUM(NVL(TT_SUM.TOTAL,0)) AS AMOUNT,
               SUM(CASE WHEN BO.PAYED=1 THEN NVL(TT_SUM.TOTAL,0) ELSE 0 END) AS PAID_AMOUNT
          FROM RABAEV.RRL_BILL_ORDERS BO
          LEFT JOIN (
            SELECT PAY_ORDER_ID, SUM(PRICE) AS TOTAL
              FROM RABAEV.RRL_TRANSPORT_TASK WHERE NVL(DELETED,0)=0 AND PAY_ORDER_ID IS NOT NULL
             GROUP BY PAY_ORDER_ID
          ) TT_SUM ON TT_SUM.PAY_ORDER_ID = BO.ID
         WHERE TRUNC(BO.DATEOFORDER) BETWEEN :d1 AND :d2
         GROUP BY BO.COMPANY
         ORDER BY AMOUNT DESC
        """,
        {"d1": date_from, "d2": date_to},
    )
    return [
        {
            "company": str(r.get("company") or "—"),
            "orders": int(r.get("orders") or 0),
            "amount": float(r.get("amount") or 0),
            "paid_amount": float(r.get("paid_amount") or 0),
        }
        for r in rows
    ]
