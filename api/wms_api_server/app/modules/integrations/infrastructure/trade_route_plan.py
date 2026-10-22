"""Route points of the bound warehouse trip linked to TRADECASE recipients by keys only (no name matching), one READ ONLY snapshot.

A point (native assembly pallet of the trip) is linked to an order through its CASE task (LEGACY_SBORKA_PALLET_ID) or the
done FULL_PALLET pick task of the same pallet; the order's trade link gives the recipient. Address and recipient-customer
consistency are checked, never used to create the link. Hidden owners hide the recipient; nothing is guessed.
"""
from typing import Any
import oracledb
from ...platform.public import read_oracle_json
from ..contracts_trade_transport import TradeTransportError

_POINTS = """select sp.ID,sp.ST_NUMBER,sp.WARE_ID,sp.ADDR,sp.ORD,to_char(sp.ZONE_TIME_PLAN_IN,'YYYY-MM-DD"T"HH24:MI:SS'),
 to_char(sp.ZONE_TIME_PLAN_OUT,'YYYY-MM-DD"T"HH24:MI:SS') from RRL_SBORKA_PALLETS sp where sp.TRANSTASK_ID=:tt order by sp.ORD nulls last,sp.ID fetch first 201 rows only"""
_ORDERS = """select distinct o.CUSTOMER_ORDER_ID,o.CUSTOMER_ID,l.EXTERNAL_ID,l.RECIPIENT_ID,l.WARE_ID from(
  select ct.CUSTOMER_ORDER_ID from RRL_CASE_PICK_TASK ct where ct.LEGACY_SBORKA_PALLET_ID=:sp
  union select pt.CUSTOMER_ORDER_ID from RRL_CUSTOMER_ORDER_FULFILLMENT ff
   join RRL_WAREHOUSE_TASK wh on wh.TASK_ID=ff.PICKED_WAREHOUSE_TASK_ID and wh.TASK_SOURCE='WAVE'and wh.SOURCE_DOC_TYPE='PICK_WAVE'
   join RRL_PICK_WAVE_TASK wt on wt.PICK_WAVE_TASK_ID=wh.SOURCE_TASK_ID and wt.PICK_WAVE_ID=wh.SOURCE_DOC_ID
   join RRL_PICK_TASK pt on pt.PICK_TASK_ID=wt.PICK_TASK_ID and pt.TASK_TYPE='FULL_PALLET'and pt.STATUS='DONE'
   where ff.LEGACY_SBORKA_PALLET_ID=:sp and ff.PICKED_PALLET_UID=pt.PALLET_UID)x join RRL_CUSTOMER_ORDER o on o.CUSTOMER_ORDER_ID=x.CUSTOMER_ORDER_ID
 left join RRL_TRADE_ORDER_LINK l on l.CUSTOMER_ORDER_ID=o.CUSTOMER_ORDER_ID"""
_ADDRESSES = "select ADDRESS_TYPE from RRL_CUSTOMER_ADDRESS where CUSTOMER_ID=:c and nvl(ACTIVE,1)=1 and trim(ADDRESS_TEXT)=trim(:a)"


def _visible(cur: Any, ware: int, order_id: str, actor: str) -> bool:
    cur.execute("select ol.SOURCE_OWNER_ID from RRL_TRADE_ORDER_LINK l join RRL_TRADE_ORDER_LINE ol on ol.CUSTOMER_ORDER_ID=l.CUSTOMER_ORDER_ID "
                "where l.WARE_ID=:w and l.EXTERNAL_ID=:o", w=ware, o=order_id)
    owners = {r[0] for r in cur.fetchall()}
    for owner in owners:
        cur.execute("select RRL_TRADE_STOCK_GUARD.owner_allowed(:a,:w,:o,0)from dual", a=actor, w=ware, o=owner)
        if cur.fetchone()[0] != 1:
            return False
    return bool(owners)


def _recipient(cur: Any, ware: int, recipient_id: str) -> dict | None:
    cur.execute("select BODY_JSON from RRL_TRADE_DOCUMENT where WARE_ID=:w and ENTITY_TYPE='RECIPIENT'and EXTERNAL_ID=:r and STATUS='ACCEPTED'",
                w=ware, r=recipient_id)
    row = cur.fetchone()
    return None if row is None else read_oracle_json(row[0])


def _link(cur: Any, ware: int, point_id: int, address: str | None, actor: str) -> dict:
    cur.execute(_ORDERS, sp=point_id)
    orders = cur.fetchall()
    trade = [o for o in orders if o[2] is not None]
    if not orders:
        return dict(link_status="UNLINKED", reason="NO_ORDER_FOR_POINT")
    if not trade:
        return dict(link_status="UNLINKED", reason="NOT_A_TRADECASE_ORDER")
    if len({o[4] for o in trade}) != 1 or trade[0][4] != ware:
        return dict(link_status="OTHER_WAREHOUSE")
    if not all(_visible(cur, ware, o[2], actor) for o in trade):
        return dict(link_status="HIDDEN")  # recipient, orders and quantities of hidden owners are not revealed
    if len({o[3] for o in trade}) != 1:
        return dict(link_status="AMBIGUOUS", reason="SEVERAL_RECIPIENTS")
    customer_ids = {o[1] for o in trade}
    recipient = _recipient(cur, ware, trade[0][3])
    out = dict(link_status="LINKED", recipient_id=trade[0][3], recipient_title=None if recipient is None else recipient.get("title"),
               order_ids=sorted(o[2] for o in trade), customer_consistent=None, address_status=None, address_type=None)
    if recipient is None:
        out.update(link_status="AMBIGUOUS", reason="RECIPIENT_DOCUMENT_MISSING")
        return out
    expected = recipient.get("wms_customer_id")
    out["customer_consistent"] = None if expected is None else customer_ids == {expected}
    if len(customer_ids) != 1 or not address:
        out["address_status"] = "UNKNOWN" if address else "ADDRESS_MISSING"
        return out
    cur.execute(_ADDRESSES, c=next(iter(customer_ids)), a=address)
    types = [r[0] for r in cur.fetchall()]
    out["address_status"] = "CONFIRMED" if len(types) == 1 else "AMBIGUOUS" if types else "NOT_IN_CUSTOMER_ADDRESSES"
    out["address_type"] = types[0] if len(types) == 1 else None
    return out


def route_points(gateway: Any, ware: int, trip: str, actor: str) -> dict[str, Any]:
    try:
        with gateway.transaction("TRADECASE route points READ ONLY") as cur:
            cur.execute("set transaction read only")
            cur.execute("select RRL_ACCESS_API.allowed(:a,'tradecase_view','WAREHOUSE',:w)from dual", a=actor, w=str(ware))
            if cur.fetchone()[0] != 1:
                raise TradeTransportError("TRADECASE_ACCESS_DENIED", 403)
            cur.execute("select count(*)from RRL_TRADE_DOCUMENT where WARE_ID=:w and ENTITY_TYPE='TRIP'and EXTERNAL_ID=:t and STATUS='ACCEPTED'", w=ware, t=trip)
            if cur.fetchone()[0] != 1:
                raise TradeTransportError("TRADE_ROUTE_SOURCE_MISSING:TRIP", 404)
            cur.execute("select NATIVE_TASK_ID from RRL_TRADE_TRIP_LINK where WARE_ID=:w and TRIP_ID=:t", w=ware, t=trip)
            link = cur.fetchone()
            if link is None:
                return dict(warehouse_id=ware, trip_id=trip, native_task_id=None, points=[], blocked_reason="TRIP_NOT_BOUND")
            cur.execute(_POINTS, tt=link[0])
            rows = cur.fetchall()
            points = []
            for point_id, st, point_ware, address, ordinal, window_from, window_to in rows:
                point = dict(point_id=int(point_id), st_number=st, route_ordinal=ordinal, window_from=window_from, window_to=window_to)
                detail = _link(cur, ware, int(point_id), address, actor) if int(point_ware)==ware else dict(link_status="OTHER_WAREHOUSE")
                if detail['link_status'] in ('HIDDEN','OTHER_WAREHOUSE'):
                    # A partial route would disclose hidden stop counts, addresses,
                    # shipment numbers and gaps in the native ordinal sequence.
                    return dict(warehouse_id=ware,trip_id=trip,native_task_id=link[0],points=[],
                                blocked_reason='ROUTE_POINTS_NOT_VISIBLE',route_executed=False)
                point.update(address=address, **detail)
                points.append(point)
            if len(rows) > 200:
                raise TradeTransportError("TRADE_ROUTE_POINT_BOUND_200", 409)
            linked = sum(p["link_status"] == "LINKED" for p in points)
            return dict(warehouse_id=ware, trip_id=trip, native_task_id=int(link[0]), points=points,
                        blocked_reason=None if points and linked == len([p for p in points if p["link_status"] != "OTHER_WAREHOUSE"]) else "POINT_RECIPIENT_LINK_INCOMPLETE",
                        link_basis="CASE_TASK_OR_FULL_PALLET_TASK", route_executed=False)
    except oracledb.DatabaseError as exc:
        raise TradeTransportError("TRADE_ROUTE_READ_FAILED", 503) from exc
