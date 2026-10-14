"""Release only the attached warehouse task's current session ownership."""
import json
from typing import Any
import oracledb
from ....transaction_gateway import TransactionGateway

def release_cancelled_task(
    gateway: TransactionGateway,task: dict[str,Any],actor: str,reason: str | None,
) -> None:
    cursor=gateway.cursor
    cursor.execute("begin RRL_STOCK_LOCK_API.assert_policy(RRL_STOCK_LOCK_API.resource_key('CONFIG','WAREHOUSE'),6);end;")
    task_id=task["task_id"]
    session=task.get("resource_session_id")
    resource=task.get("resource_id")
    equipment=task.get("equipment_id")
    if session is None and resource is None and equipment is None:
        return
    released=False
    if session is not None:
        rows=gateway.fetch_all("select SESSION_ID,CURRENT_TASK_ID from RRL_RESOURCE_SESSION where SESSION_ID=:session_id for update",{"session_id":session})
        if not rows:
            raise RuntimeError("TASK_ATTACHED_RESOURCE_SESSION_MISSING")
        if rows[0]["current_task_id"]==task_id:
            released=gateway.execute("update RRL_RESOURCE_SESSION set CURRENT_TASK_ID=null where SESSION_ID=:session_id and CURRENT_TASK_ID=:task_id",{"session_id":session,"task_id":task_id})==1
    payload=json.dumps({"reason":reason,"equipment_id":equipment,"session_task_released":released},ensure_ascii=False,separators=(",",":"))
    payload_bind=cursor.var(oracledb.DB_TYPE_CLOB)
    payload_bind.setvalue(0,payload)
    gateway.execute("""insert into RRL_RESOURCE_FACT_EVENT(EVENT_ID,TASK_ID,SESSION_ID,RESOURCE_ID,EVENT_TYPE,EVENT_AT,EVENT_BY,PAYLOAD_JSON)
        values(RRL_RESOURCE_FACT_EVENT_SQ.nextval,:task_id,:session_id,:resource_id,'CANCELLED',systimestamp,:actor,:payload)""",
        {"task_id":task_id,"session_id":session,"resource_id":resource,"actor":actor,"payload":payload_bind})
