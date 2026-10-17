"""Latest pre-departure window cohort, observed arrival and native store receipt."""
from decimal import Decimal
from typing import Any
from ..contracts import StoreReceiptError

STAMP = "'YYYY-MM-DD\"T\"HH24:MI:SS.FF6TZH:TZM'"


def percent(numerator: int, denominator: int) -> str | None:
    return str((Decimal(numerator) * 100 / denominator).quantize(Decimal("0.001"))) if denominator else None


def read_report(gateway: Any, warehouse: int, start: str, finish: str, actor: str) -> dict[str, Any]:
    with gateway.transaction("Scoped delivery KPI window cohort") as q:
        q.execute("set transaction read only")
        q.execute("""select count(*)from RRL_WARES where ID=:w and
            RRL_ACCESS_API.allowed(:actor,'transport_dispatch_view','WAREHOUSE',:ware)=1""",
            w=warehouse, actor=actor, ware=str(warehouse))
        if q.fetchone()[0] != 1:
            raise StoreReceiptError("DELIVERY_KPI_WAREHOUSE_FORBIDDEN", "Current warehouse view required", 403)
        result = _cohort(q, {"warehouse": warehouse, "start_at": start, "finish_at": finish})
    for row in result:
        row["full_state"] = ("PENDING" if row["receipt_operation_id"] is None else
            "FULL" if row["receipt_state"] == "ACCEPTED" and row["line_count"] > 0 and row["issue_count"] == 0 else "WITH_ISSUES")
        row["on_time_state"] = row["on_time_state"] or ("NO_ARRIVAL" if row["window_operation_id"] else "NO_PLAN")
    timing = {key: sum(row["on_time_state"] == key for row in result) for key in ("ON_TIME", "EARLY", "LATE", "NO_ARRIVAL", "NO_PLAN")}
    receipt = {key: sum(row["full_state"] == key for row in result) for key in ("FULL", "WITH_ISSUES", "PENDING")}
    observed, received = sum(timing[key] for key in ("ON_TIME", "EARLY", "LATE")), receipt["FULL"] + receipt["WITH_ISSUES"]
    return {"warehouse_id": warehouse, "start_at": start, "finish_at": finish, "formula_version": "DELIVERY_KPI_V1",
        "cohort_basis": "LATEST_PLANNED_WINDOW_START_OR_UNPLANNED_OBSERVED_EVENT", "deliveries": result,
        "timing": {**timing, "observed_planned": observed, "on_time_percent_of_observed": percent(timing["ON_TIME"], observed)},
        "receipt": {**receipt, "received": received, "full_percent_of_received": percent(receipt["FULL"], received)},
        "source_limitations": ["NO_LEGACY_TIMEZONE_BACKFILL", "UNKNOWN_NOT_COUNTED_AS_SUCCESS", "PENDING_EXCLUDED_FROM_OBSERVED_PERCENT"],
        "stock_changed": False}


def _cohort(q: Any, binds: dict[str, Any]) -> list[dict[str, Any]]:
    q.execute("""with latest_window as(
        select w.*,row_number()over(partition by LOAD_OPERATION_ID,STORE_ADDR order by VERSION_NO desc) RN from RRL_DELIVERY_WINDOW w where WARE_ID=:warehouse),
        selected_keys as(
        select LOAD_OPERATION_ID,STORE_ADDR from latest_window where RN=1 and WINDOW_START>=to_timestamp_tz(:start_at,""" + STAMP + """)and WINDOW_START<to_timestamp_tz(:finish_at,""" + STAMP + """)
        union select s.LOAD_OPERATION_ID,s.STORE_ADDR from RRL_STORE_RECEIPT_FACT s join RRL_TT_HU_LOAD_FACT f on f.LOAD_OPERATION_ID=s.LOAD_OPERATION_ID
        where f.WARE_ID=:warehouse and s.RECEIVED_AT>=to_timestamp_tz(:start_at,""" + STAMP + """)and s.RECEIVED_AT<to_timestamp_tz(:finish_at,""" + STAMP + """)
        and not exists(select 1 from RRL_DELIVERY_WINDOW w where w.LOAD_OPERATION_ID=s.LOAD_OPERATION_ID and w.STORE_ADDR=s.STORE_ADDR)
        union select a.LOAD_OPERATION_ID,a.STORE_ADDR from RRL_DELIVERY_ARRIVAL a where a.WARE_ID=:warehouse
        and a.ARRIVED_AT>=to_timestamp_tz(:start_at,""" + STAMP + """)and a.ARRIVED_AT<to_timestamp_tz(:finish_at,""" + STAMP + """)
        and a.WINDOW_OPERATION_ID is null)
        select k.LOAD_OPERATION_ID,k.STORE_ADDR STORE_ADDRESS,f.TT_ID TRIP_ID,f.STATUS LOAD_STATUS,
        w.OPERATION_ID WINDOW_OPERATION_ID,w.VERSION_NO WINDOW_VERSION,
        to_char(w.WINDOW_START at time zone 'UTC',""" + STAMP + """) WINDOW_START,
        to_char(w.WINDOW_FINISH at time zone 'UTC',""" + STAMP + """) WINDOW_FINISH,
        a.OPERATION_ID ARRIVAL_OPERATION_ID,to_char(a.ARRIVED_AT at time zone 'UTC',""" + STAMP + """) ARRIVED_AT,a.ON_TIME_STATE,
        s.OPERATION_ID RECEIPT_OPERATION_ID,s.RECEIPT_STATE,to_char(s.RECEIVED_AT at time zone 'UTC',""" + STAMP + """) RECEIVED_AT,
        nvl(json_value(o.CANONICAL_REQUEST,'$.metadata.receipt_mode'),json_value(o.RESULT_JSON,'$.receipt_mode')) RECEIPT_MODE,
        (select count(*)from RRL_STORE_RECEIPT_LINE l where l.OPERATION_ID=s.OPERATION_ID) LINE_COUNT,
        (select count(*)from RRL_STORE_RECEIPT_LINE l where l.OPERATION_ID=s.OPERATION_ID and
         (l.ACCEPTED_BASE_QTY!=l.SHIPPED_BASE_QTY or l.MISSING_BASE_QTY>0 or l.REFUSED_BASE_QTY>0 or l.DAMAGED_BASE_QTY>0 or l.REPORTED_EXTRA_BASE_QTY>0)) ISSUE_COUNT
        from selected_keys k join RRL_TT_HU_LOAD_FACT f on f.LOAD_OPERATION_ID=k.LOAD_OPERATION_ID and f.WARE_ID=:warehouse
        left join latest_window w on w.LOAD_OPERATION_ID=k.LOAD_OPERATION_ID and w.STORE_ADDR=k.STORE_ADDR and w.RN=1
        left join RRL_DELIVERY_ARRIVAL a on a.LOAD_OPERATION_ID=k.LOAD_OPERATION_ID and a.STORE_ADDR=k.STORE_ADDR
        left join RRL_STORE_RECEIPT_FACT s on s.LOAD_OPERATION_ID=k.LOAD_OPERATION_ID and s.STORE_ADDR=k.STORE_ADDR
        left join RRL_STOCK_OPERATION o on o.OPERATION_ID=s.OPERATION_ID and o.STATE='APPLIED'
        order by k.LOAD_OPERATION_ID,k.STORE_ADDR fetch first 501 rows only""", binds)
    keys = [item[0].lower() for item in q.description]
    result = [dict(zip(keys, row)) for row in q.fetchall()]
    if len(result) > 500:
        raise StoreReceiptError("DELIVERY_KPI_BOUND_500", "Narrow the period", 422)
    return result
