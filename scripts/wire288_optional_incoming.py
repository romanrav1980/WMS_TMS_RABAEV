from pathlib import Path
import json
out={}
p=Path("api/wms_api_server/app/modules/inventory/infrastructure/interwarehouse_incoming.py");s=p.read_text(encoding="utf-8");s+='''

def read_optional_incoming_snapshot(cur: Any,trip_id: int,actor: str) -> dict[str,Any]:
    """Current native trip scope first; absent expectations are not ready deliveries."""
    import oracledb
    proof=cur.var(oracledb.DB_TYPE_CLOB)
    cur.callproc("RRL_TT_TIME_API.context",[trip_id,actor,proof])
    cur.execute("""select count(*)from(
        select OPERATION_ID from RRL_INTERWARE_PLAN where TARGET_TT_ID=:trip
        union select PLAN_OPERATION_ID from RRL_INTERWARE_DECISION where TARGET_TT_ID=:trip)
        where rownum<=1""",trip=trip_id)
    if cur.fetchone()[0]:
        return read_incoming_snapshot(cur,trip_id,actor)
    return {"trip_id":trip_id,"warehouse_id":None,"scope":"NO_INTERWARE_EXPECTATIONS",
        "expected_deliveries":0,"ready_deliveries":0,"incoming_ready":False,
        "departure_authorized":False,"plans":[],"expected_quantities":[]}
'''
out[p.as_posix()]=s
p=Path("api/wms_api_server/app/modules/inventory/public.py");s=p.read_text(encoding="utf-8");s+='\nfrom .infrastructure.interwarehouse_incoming import read_optional_incoming_snapshot as read_optional_interwarehouse_incoming_snapshot\n';out[p.as_posix()]=s
p=Path("api/wms_api_server/app/modules/transport/infrastructure/coordination_preflight.py");s=p.read_text(encoding="utf-8").replace("read_interwarehouse_incoming_snapshot","read_optional_interwarehouse_incoming_snapshot");out[p.as_posix()]=s
print(json.dumps(out,ensure_ascii=True))
