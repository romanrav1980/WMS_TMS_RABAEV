"""C-0176: places of one assembly read in one READ ONLY snapshot; removal through the native command in one transaction."""
import json
from typing import Any
import oracledb
from ...platform.public import read_oracle_json
from ..contracts_place_removal import PlaceRemovalCommand, PlaceRemovalError

_PLACES = """select sp.ID,sp.PALLET_UID,sp.ADDR,sp.TRANSTASK_ID,sp.CONDITION,sp.WARE_ID,
 (select count(*) from RRL_TT_HU_LOAD_ST ls where ls.SBORKA_PALLET_ID=sp.ID and ls.ACTIVE_FLAG=1)
 from RRL_SBORKA_PALLETS sp where sp.ST_NUMBER=:st order by sp.ID fetch first 1001 rows only"""
_OWNERS = """select distinct a.OWNER_ID from RRL_TRADE_STOCK_ATTR a join RRL_WMS_RECEIPT_UNIT u on u.PHYSICAL_UNIT_KEY=a.PHYSICAL_UNIT_KEY
 where u.CURRENT_UID in(select f.PICKED_PALLET_UID from RRL_CUSTOMER_ORDER_FULFILLMENT f join RRL_SBORKA_PALLETS sp on sp.ID=f.LEGACY_SBORKA_PALLET_ID where sp.ST_NUMBER=:st
  union select ct.SSCC from RRL_CASE_PICK_TASK ct join RRL_SBORKA_PALLETS sp on sp.ID=ct.LEGACY_SBORKA_PALLET_ID where sp.ST_NUMBER=:st)"""


def _error(exc: oracledb.DatabaseError) -> PlaceRemovalError:
    code = getattr(exc.args[0], "code", 0)
    text = str(exc.args[0]).split("\n", 1)[0].split(":", 1)[-1].strip()
    if code == 20882:
        return PlaceRemovalError(text or "ACCESS_DENIED", 403)
    if code == 20886:
        return PlaceRemovalError(text, 409)
    return PlaceRemovalError("PLACE_REMOVAL_RESULT_UNKNOWN", 503)  # never a refusal: repeat the same operation


class OraclePlaceRemoval:
    def __init__(self, gateway: Any) -> None:
        self.gateway = gateway

    def places(self, trip: int, st_number: str, actor: str) -> dict[str, Any]:
        try:
            with self.gateway.transaction("Assembly places READ ONLY") as cur:
                cur.execute("set transaction read only")
                cur.execute(_PLACES, st=st_number)
                rows = cur.fetchall()
                if not rows:
                    raise PlaceRemovalError("ST_ASSIGNMENT_NOT_FOUND", 404)
                if len(rows) > 1000:
                    raise PlaceRemovalError("ST_ASSIGNMENT_BATCH_BOUND", 409)
                if any(row[5] is None for row in rows):
                    raise PlaceRemovalError("ST_WAREHOUSE_REQUIRED", 409)
                wares = {int(r[5]) for r in rows}
                if len(wares) != 1:
                    raise PlaceRemovalError("ST_WAREHOUSE_AMBIGUOUS", 409)
                ware = wares.pop()
                cur.execute("select RRL_ACCESS_API.allowed(:a,'transport_dispatch_view','WAREHOUSE',:w)+RRL_ACCESS_API.allowed(:a,'transport_dispatch_edit','WAREHOUSE',:w) from dual",
                            a=actor, w=str(ware))
                if cur.fetchone()[0] < 1:
                    raise PlaceRemovalError("ACCESS_DENIED", 403)
                cur.execute(_OWNERS, st=st_number)
                for (owner,) in cur.fetchall():  # a hidden owner hides the whole assembly, not a part of it
                    cur.execute("select RRL_TRADE_STOCK_GUARD.owner_allowed(:a,:w,:o,0) from dual", a=actor, w=ware, o=owner)
                    if cur.fetchone()[0] != 1:
                        raise PlaceRemovalError("TRADE_OWNER_ACCESS_DENIED", 403)
                places = [dict(member_id=int(i), pallet_uid=uid, address=addr, on_trip=tt is not None and int(tt) == trip,
                               other_trip=int(tt) if tt and int(tt) != trip else None, loaded=bool(loaded), shipped=condition == 2)
                          for i, uid, addr, tt, condition, _, loaded in rows]
                cur.execute("select RRL_TT_PLACE_REMOVAL_API.source_hash(:t,:s) from dual", t=trip, s=st_number)
                return dict(trip_id=trip, st_number=st_number, warehouse_id=ware, on_trip=sum(p["on_trip"] for p in places), places=places,
                            source_hash=cur.fetchone()[0])
        except oracledb.DatabaseError as exc:
            raise _error(exc) from exc

    def remove(self, trip: int, body: PlaceRemovalCommand, actor: str) -> dict[str, Any]:
        request = json.dumps(dict(operation_id=body.operation_id, trip_id=trip, st_number=body.st_number, member_ids=body.member_ids,
                                  expected_source_hash=body.expected_source_hash, reason=body.reason), sort_keys=True, separators=(",", ":"), ensure_ascii=True)
        try:
            with self.gateway.transaction("Assembly place removal") as cur:
                wire = cur.var(oracledb.DB_TYPE_CLOB); wire.setvalue(0, request)
                result = cur.var(oracledb.DB_TYPE_CLOB)
                cur.callproc("RRL_TT_PLACE_REMOVAL_API.remove", [wire, actor, result])
                return read_oracle_json(result.getvalue())
        except oracledb.DatabaseError as exc:
            raise _error(exc) from exc
