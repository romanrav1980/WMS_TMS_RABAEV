"""Existing CASE assignment and handoff share the Oracle resource policy."""
import json
from typing import Any, Callable
from fastapi import HTTPException
import oracledb
from ....transaction_gateway import TransactionGateway

def context(gateway: Any, task_id: int, action: str, request: Any) -> dict[str,Any]:
    resource=request.to_resource_id if action=="TRANSFER" else getattr(request,"resource_id",None)
    session=request.to_resource_session_id if action=="TRANSFER" else getattr(request,"resource_session_id",None)
    equipment=request.to_equipment_id if action=="TRANSFER" else getattr(request,"equipment_id",None)
    if session is None and action!="TRANSFER":
        rows=gateway.fetch_all("select RESOURCE_SESSION_ID from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=:id",{"id":task_id})
        session=rows[0]["resource_session_id"] if rows else None
    if session is not None:
        gateway.fetch_all("select SESSION_ID from RRL_RESOURCE_SESSION where SESSION_ID=:id for update",{"id":session})
    try:
        row=gateway.fetch_all("""select RRL_CASE_RESOURCE_POLICY.context_json(
            :p_task,:p_action,:p_actor,:p_resource,:p_session,:p_equipment) CONTEXT_JSON from dual""",
            {"p_task":task_id,"p_action":action,"p_actor":request.actor,"p_resource":resource,
             "p_session":session,"p_equipment":equipment})[0]
        value=row["context_json"]
        return value if isinstance(value,dict) else json.loads(value)
    except oracledb.DatabaseError as exc:
        if exc.args[0].code in {20881,20882,20886}:
            raise HTTPException(403 if exc.args[0].code==20882 else 409,
                detail={"code":"CASE_RESOURCE_REJECTED","message":exc.args[0].message.split("\n")[0]}) from exc
        raise

def run_action(gateway: Any, task_id: int, action: str, request: Any, handler: Callable[[Any,int,Any],None]) -> None:
    with gateway.transaction("CASE resource "+action) as cursor:
        try:
            permission="case_pick_manage" if action=="transfer_task" else "case_pick_execute"
            cursor.execute("select RRL_HAS_WRIGHT(:actor,:permission) from dual",{"actor":request.actor,"permission":permission})
            if cursor.fetchone()[0]!=1:raise HTTPException(403,detail="CASE action permission required")
            cursor.execute("begin RRL_STOCK_METADATA_TX.begin_change(:actor,:permission);end;",{"actor":request.actor,"permission":permission})
            bound=TransactionGateway(cursor)
            task=bound.fetch_all("select PICK_WAVE_ID from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=:id",{"id":task_id})
            if not task:raise HTTPException(404,detail="CASE task not found")
            bound.fetch_all("select PICK_WAVE_ID from RRL_PICK_WAVE where PICK_WAVE_ID=:id for update",{"id":task[0]["pick_wave_id"]})
            bound.fetch_all("select CASE_PICK_TASK_ID from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=:id for update",{"id":task_id})
            if action=="transfer_task":
                from .case_handoff import replay
                if replay(bound,task_id,request):return
            handler(bound,task_id,request)
        except oracledb.DatabaseError as exc:
            code = getattr(exc.args[0], "code", 0)
            if 20800 <= code <= 20999:
                message = str(exc.args[0]).split("\n", 1)[0]
                raise HTTPException(403 if code == 20882 else 409,
                    detail={"code": "CASE_ACTION_REJECTED", "message": message}) from exc
            raise
        finally:
            cursor.execute("begin RRL_STOCK_METADATA_TX.end_change;end;")
