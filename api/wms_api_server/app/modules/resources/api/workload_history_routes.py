from typing import Any
from fastapi import APIRouter, Depends, HTTPException, Path, Query
from ...platform.public import AdminUser, require_permission
from ..contracts_workload import WorkloadHistoryPort, WorkloadError, workload_history_service

router=APIRouter(prefix="/api/resources/workload",tags=["resource-workload"])

@router.get("/warehouses/{ware_id}/attendance/{plan_id}/history")
def history(ware_id: int=Path(gt=0),plan_id: str=Path(min_length=1,max_length=100),
    limit: int=Query(25,ge=1,le=50),user: AdminUser=Depends(require_permission("resource_shift_view")),
    service: WorkloadHistoryPort=Depends(workload_history_service)) -> dict[str,Any]:
    try:return service.read(ware_id,plan_id,limit,user.username)
    except WorkloadError as exc:raise HTTPException(exc.status,{"code":exc.code,"message":str(exc)}) from exc
