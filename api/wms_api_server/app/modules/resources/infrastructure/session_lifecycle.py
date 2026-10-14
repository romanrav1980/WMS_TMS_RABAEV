"""Session capacity and end-of-shift handover without changing stock."""
from typing import Any, Callable
from fastapi import HTTPException
from ....transaction_gateway import TransactionGateway

def open_session(gateway: Any, request: Any, create: Callable[[Any, Any], int]) -> int:
    with gateway.transaction("Open existing resource session with shift capacity") as cursor:
        cursor.execute("""select WARE_ID,REACH_SHIFT_ROLE,EXPECTED_DRIVERS,STATUS
            from RRL_RESOURCE_SHIFT where SHIFT_ID=:id for update""", {"id": request.shift_id})
        shift = cursor.fetchone()
        if shift is None:
            raise HTTPException(404, detail="Resource shift not found")
        ware, role, expected, status = shift
        if role in {"MAIN", "DUTY"}:
            if status != "OPEN":
                raise HTTPException(409, detail="Reachtruck shift is not open")
            cursor.execute("select WARE_ID,ACTIVE from RRL_RESOURCE where RESOURCE_ID=:id", {"id": request.resource_id})
            resource = cursor.fetchone()
            if resource is None or resource[0] != ware or resource[1] != 1:
                raise HTTPException(409, detail="Resource must be active in this warehouse")
            cursor.execute("""select count(*) from RRL_RESOURCE_SESSION where SHIFT_ID=:id
                and STATUS in('ACTIVE','PAUSED')""", {"id": request.shift_id})
            if expected is None or cursor.fetchone()[0] >= expected:
                raise HTTPException(409, detail="REACH_SHIFT_DRIVER_CAPACITY_REACHED")
        return create(TransactionGateway(cursor), request)

def close_session(gateway: Any, session_id: int, actor: str) -> None:
    with gateway.transaction("End resource shift after physical step or handover") as cursor:
        cursor.execute("""select STATUS,OPERATOR_USER_ID from RRL_RESOURCE_SESSION
            where SESSION_ID=:id for update""", {"id": session_id})
        session = cursor.fetchone()
        if session is None or session[0] not in {"ACTIVE", "PAUSED", "ERROR"}:
            raise HTTPException(404, detail="Open resource session not found")
        cursor.execute("""select TASK_ID from RRL_WAREHOUSE_TASK
            where (RESOURCE_SESSION_ID=:session_id or ASSIGNED_TO=:owner)
             and STATUS in('ASSIGNED','IN_PROGRESS') order by TASK_ID fetch first 20 rows only""",
            {"session_id": session_id, "owner": session[1]})
        warehouse = [int(row[0]) for row in cursor.fetchall()]
        cursor.execute("""select INVENTORY_TASK_ID from RRL_INVENTORY_TASK
            where (RESOURCE_SESSION_ID=:session_id or ASSIGNED_TO=:owner)
             and STATUS in('ASSIGNED','IN_PROGRESS') order by INVENTORY_TASK_ID fetch first 20 rows only""",
            {"session_id": session_id, "owner": session[1]})
        inventory = [int(row[0]) for row in cursor.fetchall()]
        cursor.execute("""select CASE_PICK_TASK_ID from RRL_CASE_PICK_TASK where ASSIGNED_TO=:owner
             and STATUS in('ASSIGNED','IN_PROGRESS','PARTIAL','WAIT_REPLENISHMENT')
             order by CASE_PICK_TASK_ID fetch first 20 rows only""", {"owner": session[1]})
        cases = [int(row[0]) for row in cursor.fetchall()]
        if warehouse or inventory or cases:
            raise HTTPException(409, detail={"code": "SHIFT_HANDOVER_REQUIRED", "warehouse_tasks": warehouse,
                "inventory_tasks": inventory, "case_tasks": cases,
                "message": "Finish the current physical step; transfer unstarted tasks or the CASE carrier before leaving"})
        cursor.execute("""update RRL_RESOURCE_SESSION set STATUS='CLOSED',LOGOUT_AT=systimestamp,
            CLOSED_BY=:actor,CURRENT_TASK_ID=null,CURRENT_INVENTORY_TASK_ID=null where SESSION_ID=:id""",
            {"id": session_id, "actor": actor})
