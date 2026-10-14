"""One read-only snapshot for current trip scope and all bounded incoming promises."""
from pathlib import Path
from typing import Any
from ..contracts_store_returns import StoreReturnReceiveError
from ..domain.interwarehouse_readiness import incoming_readiness

INCOMING_SQL=Path(__file__).with_suffix(".sql").read_text(encoding="utf-8")
GROUP_INCOMING_SQL=Path(__file__).with_name("interwarehouse_group_incoming.sql").read_text(encoding="utf-8")

class InterwarehouseIncoming:
    def __init__(self,gateway: Any) -> None:
        self.gateway=gateway

    def read(self,trip_id: int,actor: str) -> dict[str,Any]:
        with self.gateway.transaction("Interwarehouse trip incoming readiness") as cur:
            cur.execute("set transaction read only")
            return read_incoming_snapshot(cur, trip_id, actor)

def read_incoming_snapshot(cur: Any,trip_id: int,actor: str) -> dict[str,Any]:
    cur.execute("""select d.WARE_ID from RRL_TRANSPORT_TASK t join RRL_TT_DOCK d on d.DOCK=t.DOCK
        join RUSERS u on u.ID=:actor where t.ID=:trip and nvl(t.DELETED,0)=0 and nvl(u.DELETED,0)=0
        and RRL_HAS_WRIGHT(u.ID,'transport_dispatch_view')=1
        and(u.WARE_ID=d.WARE_ID or upper(trim(u.USER_GROUP))='GLOBAL_ADMIN')""",trip=trip_id,actor=actor)
    scope=cur.fetchone()
    if scope is None:
        raise StoreReturnReceiveError("INTERWARE_TRIP_SCOPE_REQUIRED","Текущий диспетчер склада рейса обязателен",403)
    cur.execute(INCOMING_SQL,trip=trip_id)
    columns=[column[0].lower() for column in cur.description]
    rows=[dict(zip(columns,values)) for values in cur.fetchall()]
    cur.execute(GROUP_INCOMING_SQL,trip=trip_id)
    columns=[column[0].lower()for column in cur.description]
    rows.extend(dict(zip(columns,values))for values in cur.fetchall())
    if len(rows)>200:
        raise StoreReturnReceiveError("INTERWARE_INCOMING_BOUND_200","Разделите план: более 200 межскладских поставок в рейсе",409)
    return incoming_readiness(trip_id,int(scope[0]),rows)


def read_optional_incoming_snapshot(cur: Any,trip_id: int,actor: str) -> dict[str,Any]:
    """Current native trip scope first; absent expectations are not ready deliveries."""
    import oracledb
    proof=cur.var(oracledb.DB_TYPE_CLOB)
    cur.callproc("RRL_TT_TIME_API.context",[trip_id,actor,proof])
    cur.execute("""select count(*)from(
        select OPERATION_ID from RRL_INTERWARE_PLAN where TARGET_TT_ID=:trip
        union select PLAN_OPERATION_ID from RRL_INTERWARE_DECISION where TARGET_TT_ID=:trip
        union select OPERATION_ID from RRL_IW_GROUP_PLAN where TARGET_TT_ID=:trip)
        where rownum<=1""",trip=trip_id)
    if cur.fetchone()[0]:
        return read_incoming_snapshot(cur,trip_id,actor)
    return {"trip_id":trip_id,"warehouse_id":None,"scope":"NO_INTERWARE_EXPECTATIONS",
        "expected_deliveries":0,"ready_deliveries":0,"incoming_ready":False,
        "departure_authorized":False,"plans":[],"expected_quantities":[]}
