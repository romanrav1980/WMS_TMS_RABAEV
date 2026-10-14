"""Original ARM fact endpoint, through the transport public port."""
from typing import Any
from fastapi import APIRouter, Depends, HTTPException
from ..contracts import OperationFactUpdate
from ...platform.public import AdminUser, require_permission
from ..contracts_operation_fact import OperationFactPort, operation_fact_service
from ..contracts_plan import TransportPlanError

router=APIRouter(prefix="/api/admin/transport",tags=["transport"])

@router.patch("/operations/{op_id}/fact")
def update_operation_fact(op_id: int,data: OperationFactUpdate,
    user: AdminUser=Depends(require_permission("transport_dispatch_edit")),
    service: OperationFactPort=Depends(operation_fact_service)) -> dict[str,Any]:
    fields=data.model_dump(exclude_none=True,mode="json")
    if not fields:raise HTTPException(400,detail="Нет полей для обновления")
    try:return service.write(op_id,fields,user.username)
    except TransportPlanError as exc:
        raise HTTPException(exc.status,detail={"code":exc.code,"message":str(exc)}) from exc
