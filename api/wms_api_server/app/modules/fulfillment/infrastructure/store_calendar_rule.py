"""Single native calendar authority reused by import, ERP admission and original preparation."""
from datetime import date
from typing import Any
import oracledb
from ...platform.public import read_oracle_json
from ..application.ports import StoreOrderConflict


def delivery_rule(cur: Any, warehouse: int, store: int, day: date) -> dict[str, Any]:
    offset = cur.var(oracledb.DB_TYPE_NUMBER)
    allowed = cur.var(oracledb.DB_TYPE_NUMBER)
    proof = cur.var(oracledb.DB_TYPE_CLOB)
    cur.callproc("RRL_STORE_CALENDAR_API.delivery_rule", [warehouse, store, day, offset, allowed, proof])
    return read_oracle_json(proof.getvalue())


def assert_current_order_calendar(cur: Any, order: int) -> None:
    cur.execute("""select c.WARE_ID,c.CUSTOMER_STORE_MAP_ID,s.DELIVERY_DATE,s.UTC_OFFSET_MINUTES,
            case when from_tz(cast(s.PICKING_FINISH_AT as timestamp),
                case when s.UTC_OFFSET_MINUTES<0 then '-' else '+' end||
                lpad(trunc(abs(s.UTC_OFFSET_MINUTES)/60),2,'0')||':'||
                lpad(mod(abs(s.UTC_OFFSET_MINUTES),60),2,'0'))>systimestamp then 1 else 0 end
        from RRL_CUSTOMER_ORDER c join RRL_SAP_STORE_ORDER s on s.CUSTOMER_ORDER_ID=c.CUSTOMER_ORDER_ID
        where c.CUSTOMER_ORDER_ID=:order_id""", order_id=order)
    row = cur.fetchone()
    if row is None:
        raise LookupError("Original SAP source order not found")
    proof = delivery_rule(cur, row[0], row[1], row[2])
    if not proof["allowed"] or proof["utc_offset_minutes"] != row[3]:
        raise StoreOrderConflict("SAP order current calendar is not admitted")

    if row[4] != 1:
        raise StoreOrderConflict("SAP order picking deadline has passed")
