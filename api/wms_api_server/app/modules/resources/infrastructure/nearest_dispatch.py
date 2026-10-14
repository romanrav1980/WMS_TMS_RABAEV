"""Atomic nearest assignment through the existing warehouse task service."""
from typing import Any, Callable
from fastapi import HTTPException
from .qualified_candidates import QualifiedCandidates

def dispatch_warehouse(gateway: Any, task_id: int, actor: str, assign: Callable[[Any,int,Any],None]) -> dict[str, Any]:
    from ....transaction_gateway import TransactionGateway
    from ....schemas import WarehouseTaskStatusRequest
    with gateway.transaction("Assign nearest qualified warehouse resource") as cursor:
        try:
            cursor.execute("begin RRL_STOCK_METADATA_TX.begin_change(:actor,'warehouse_task_assign');end;", {"actor": actor})
            cursor.execute("select RRL_HAS_WRIGHT(:actor,'resource_dispatch_manage') from dual", {"actor": actor})
            if cursor.fetchone()[0] != 1:
                raise HTTPException(403, detail="resource_dispatch_manage permission required")
            cursor.execute("select STATUS from RRL_WAREHOUSE_TASK where TASK_ID=:id for update", {"id": task_id})
            row = cursor.fetchone()
            if row is None:
                raise HTTPException(404, detail="Task not found")
            if row[0] != "PLANNED":
                raise HTTPException(409, detail="Only an unstarted planned task can be dispatched")
            bound = TransactionGateway(cursor)
            candidates = QualifiedCandidates(bound).warehouse(task_id, 1)
            if not candidates:
                raise HTTPException(409, detail="NO_FREE_QUALIFIED_RESOURCE_WITH_FRESH_POSITION")
            choice = candidates[0]
            request = WarehouseTaskStatusRequest(updated_by=actor, assigned_to=choice["assigned_to"],
                resource_id=choice["resource_id"],resource_session_id=choice["resource_session_id"],
                equipment_id=choice["equipment_id"])
            assign(bound,task_id,request)
            return {"task_id":task_id,"status":"ASSIGNED",**choice}
        finally:
            cursor.execute("begin RRL_STOCK_METADATA_TX.end_change;end;")
