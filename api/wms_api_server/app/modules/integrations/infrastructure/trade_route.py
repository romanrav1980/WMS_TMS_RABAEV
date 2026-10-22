"""Coverage of one external trip by its real order lines, read in one Oracle READ ONLY snapshot.

Ordered comes from the current TRIP/ORDER documents; reserved/picked from the native line snapshot; loaded/departed from
physical load facts of the bound warehouse trip. A missing source is reported as unknown (null), never as zero.
"""
from decimal import Decimal
from typing import Any
import oracledb
from ...platform.public import read_oracle_json
from ..contracts_trade_transport import TradeTransportError

# Load composition is frozen. Do not infer delivered quantities from mutable CASE totals or a reused pallet UID.
_FROZEN = """with facts as(
 select f.LOAD_OPERATION_ID,f.STATUS,f.CUSTODY_RELEASED_AT,f.COMPOSITION_JSON
 from RRL_TT_HU_LOAD_FACT f where f.TT_ID=:tt and f.WARE_ID=:w and f.STATUS in('LOADED','DEPARTED')),
 leaves as(
 select f.LOAD_OPERATION_ID,n.NODE_UID,n.QTY from facts f cross apply json_table(f.COMPOSITION_JSON,'$.nodes[*]'columns(
  NODE_UID varchar2(200)path'$.uid',KIND varchar2(20)path'$.kind',QTY number path'$.quantity'))n
 where n.KIND='STOCK'and n.QTY>0),
 candidates as(
 select n.LOAD_OPERATION_ID,n.NODE_UID,pl.CUSTOMER_ORDER_ROW_ID ROW_ID,n.QTY
 from leaves n join RRL_CASE_CARRIER_LOT lot on lot.LOT_UID=n.NODE_UID
 join RRL_CASE_PICK_LINE cl on cl.CASE_PICK_LINE_ID=lot.CASE_PICK_LINE_ID
 join RRL_CASE_PICK_TASK ct on ct.CASE_PICK_TASK_ID=cl.CASE_PICK_TASK_ID and ct.WARE_ID=:w
 join RRL_PICK_PLAN_LINE pl on pl.PICK_PLAN_LINE_ID=cl.PICK_PLAN_LINE_ID
 union all
 select n.LOAD_OPERATION_ID,n.NODE_UID,pl.CUSTOMER_ORDER_ROW_ID,n.QTY
 from leaves n join RRL_TT_HU_LOAD_ST ls on ls.LOAD_OPERATION_ID=n.LOAD_OPERATION_ID
 join RRL_CUSTOMER_ORDER_FULFILLMENT ff on ff.LEGACY_SBORKA_PALLET_ID=ls.SBORKA_PALLET_ID and ff.PICKED_PALLET_UID=n.NODE_UID
 join RRL_WAREHOUSE_TASK wh on wh.TASK_ID=ff.PICKED_WAREHOUSE_TASK_ID and wh.TASK_SOURCE='WAVE'and wh.SOURCE_DOC_TYPE='PICK_WAVE'
 join RRL_PICK_WAVE_TASK wt on wt.PICK_WAVE_TASK_ID=wh.SOURCE_TASK_ID and wt.PICK_WAVE_ID=wh.SOURCE_DOC_ID
 join RRL_PICK_WAVE pw on pw.PICK_WAVE_ID=wt.PICK_WAVE_ID and pw.WARE_ID=:w
 join RRL_PICK_TASK pt on pt.PICK_TASK_ID=wt.PICK_TASK_ID and pt.TASK_TYPE='FULL_PALLET'and pt.STATUS='DONE'
 join RRL_PICK_PLAN_LINE pl on pl.PICK_PLAN_LINE_ID=pt.PICK_PLAN_LINE_ID
 where not exists(select 1 from RRL_CASE_CARRIER_LOT lot where lot.LOT_UID=n.NODE_UID)),
 mapped as(select LOAD_OPERATION_ID,NODE_UID,min(ROW_ID)ROW_ID,max(QTY)QTY from candidates
 group by LOAD_OPERATION_ID,NODE_UID having count(*)=1)
 """
_LOADS = _FROZEN + """select m.ROW_ID,f.STATUS,case when f.CUSTODY_RELEASED_AT is not null then 1 else 0 end RELEASED,sum(m.QTY)QTY
 from facts f join mapped m on m.LOAD_OPERATION_ID=f.LOAD_OPERATION_ID
 group by m.ROW_ID,f.STATUS,case when f.CUSTODY_RELEASED_AT is not null then 1 else 0 end"""
_UNATTRIBUTED = _FROZEN + """select count(*) UNATTRIBUTED_LOADS from facts f
 where not exists(select 1 from leaves n where n.LOAD_OPERATION_ID=f.LOAD_OPERATION_ID)
 or exists(select 1 from leaves n where n.LOAD_OPERATION_ID=f.LOAD_OPERATION_ID
  and not exists(select 1 from mapped m where m.LOAD_OPERATION_ID=n.LOAD_OPERATION_ID and m.NODE_UID=n.NODE_UID))"""


def _document(cur: Any, ware: int, kind: str, key: str) -> tuple[dict, int]:
    """Current accepted document; a cancelled one is still returned so its lines are shown as cancelled, not dropped."""
    cur.execute("select BODY_JSON,VERSION_NO from RRL_TRADE_DOCUMENT where WARE_ID=:w and ENTITY_TYPE=:k and EXTERNAL_ID=:id and STATUS='ACCEPTED'",
                w=ware, k=kind, id=key)
    row = cur.fetchone()
    if row is None:
        raise TradeTransportError("TRADE_ROUTE_SOURCE_MISSING:" + kind, 404 if kind == "TRIP" else 409)
    return read_oracle_json(row[0]), int(row[1])


def _text(value: Any) -> str | None:
    return None if value is None else format(Decimal(str(value)).normalize(), "f")


def _line(cur: Any, ware: int, assignment: dict, order: dict, order_version: int, line: dict) -> dict:
    sku, _ = _document(cur, ware, "SKU", line["sku_id"])
    quantity = Decimal(str(assignment["quantity"]))
    ordered = quantity * sku["units_per_box"] if line["uom"] == "BOX" else quantity
    cur.execute("select ol.CUSTOMER_ORDER_ROW_ID,l.DOCUMENT_VERSION from RRL_TRADE_ORDER_LINK l join RRL_TRADE_ORDER_LINE ol on ol.CUSTOMER_ORDER_ID=l.CUSTOMER_ORDER_ID "
                "where l.WARE_ID=:w and l.EXTERNAL_ID=:o and ol.EXTERNAL_LINE_ID=:line", w=ware, o=assignment["order_id"], line=assignment["line_id"])
    bound = cur.fetchone()
    item = dict(order_id=assignment["order_id"], line_id=assignment["line_id"], order_kind=order.get("order_kind", "OUTBOUND"), recipient_id=order["recipient_id"],
                order_cancelled=bool(order.get("cancelled")), native_error=None,
                sku_id=line["sku_id"], source_owner_id=line["source_owner_id"], mrc=_text(line["mrc"]), uom=line["uom"], units_per_box=sku["units_per_box"],
                ordered_base=_text(ordered), native_row_id=None, binding_current=None, requested_base=None, reserved_base=None, picked_base=None,
                unallocated_base=None, loaded_base=None, departed_base=None, released_base=None)
    if bound is None:
        return item  # not bound to a native order yet: reservation/picking/loading are unknown, not zero
    item.update(native_row_id=int(bound[0]), binding_current=int(bound[1]) == order_version)
    try:
        snap = read_oracle_json(cur.callfunc("RRL_STOCK_POOL_READ.line_snapshot_json", oracledb.DB_TYPE_CLOB, [bound[0]]))
    except oracledb.DatabaseError as exc:
        code = getattr(exc.args[0], "code", 0)
        if not 20800 <= code <= 20999:
            raise
        item["native_error"] = str(exc.args[0]).split("\n", 1)[0].split(":", 1)[-1].strip()  # this line is unknown; others stay readable
        return item
    item.update(requested_base=snap["requested_base_quantity"],
                reserved_base=snap["hard_quantity"], picked_base=snap["picked_quantity"], unallocated_base=snap["quantity"])
    return item


def trip_coverage(gateway: Any, ware: int, trip_id: str, actor: str) -> dict[str, Any]:
    try:
        with gateway.transaction("TRADECASE trip route coverage READ ONLY") as cur:
            cur.execute("set transaction read only")
            cur.execute("select RRL_ACCESS_API.allowed(:a,'tradecase_view','WAREHOUSE',:w)from dual", a=actor, w=str(ware))
            if cur.fetchone()[0] != 1:
                raise TradeTransportError("TRADECASE_ACCESS_DENIED", 403)
            trip, trip_version = _document(cur, ware, "TRIP", trip_id)
            cur.execute("select NATIVE_TASK_ID,TRIP_VERSION from RRL_TRADE_TRIP_LINK where WARE_ID=:w and TRIP_ID=:t", w=ware, t=trip_id)
            link = cur.fetchone()
            lines, hidden, orders = [], False, {}
            for assignment in trip["orders"]:
                if assignment["order_id"] not in orders:
                    orders[assignment["order_id"]] = _document(cur, ware, "ORDER", assignment["order_id"])
                order, version = orders[assignment["order_id"]]
                line = next((x for x in order["lines"] if x["line_id"] == assignment["line_id"]), None)
                if line is None:
                    raise TradeTransportError("TRADE_ROUTE_ORDER_LINE_MISSING", 409)
                cur.execute("select RRL_TRADE_STOCK_GUARD.owner_allowed(:a,:w,:o,0)from dual", a=actor, w=ware, o=line["source_owner_id"])
                if cur.fetchone()[0] != 1:
                    hidden = True  # the hidden part is not revealed, not even by counts
                    continue
                lines.append(_line(cur, ware, assignment, order, version, line))
            unattributed = None
            loading_complete = False
            if link is not None:
                cur.execute(_LOADS, tt=link[0], w=ware)
                by_row: dict[int, dict[str, Decimal]] = {}
                for row_id, status, released, qty in cur:
                    bucket = by_row.setdefault(int(row_id), {"LOADED": Decimal(0), "DEPARTED": Decimal(0), "RELEASED": Decimal(0)})
                    if status in ("LOADED", "DEPARTED"):
                        bucket[status] += Decimal(str(qty or 0))
                        if released:
                            bucket["RELEASED"] += Decimal(str(qty or 0))
                for item in lines:
                    if item["native_row_id"] is not None:
                        bucket = by_row.get(item["native_row_id"], {"LOADED": Decimal(0), "DEPARTED": Decimal(0), "RELEASED": Decimal(0)})
                        item.update(loaded_base=_text(bucket["LOADED"]), departed_base=_text(bucket["DEPARTED"]), released_base=_text(bucket["RELEASED"]))
                cur.execute(_UNATTRIBUTED, tt=link[0], w=ware)
                missing = int(cur.fetchone()[0])
                loading_complete = missing == 0
                if not hidden:
                    unattributed = missing
                if not loading_complete:
                    for item in lines:
                        item.update(loaded_base=None, departed_base=None, released_base=None)
            return dict(warehouse_id=ware, trip_id=trip_id, trip_version=trip_version, planned_departure_at=trip["planned_departure_at"],
                        native_task_id=None if link is None else int(link[0]), binding_trip_version=None if link is None else int(link[1]),
                        lines=lines, owner_scope_filtered=hidden, unattributed_loads=unattributed, load_coverage_complete=loading_complete,
                        quantity_unit="BASE", route_source="NATIVE_TRANSPORT_ROUTE_CONTEXT", route_executed=False)
    except oracledb.DatabaseError as exc:
        raise TradeTransportError("TRADE_ROUTE_READ_FAILED", 503) from exc
