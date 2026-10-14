from fastapi import APIRouter,Depends,HTTPException,Query
from ...platform.public import AdminUser,require_permission
from ..contracts_waiting_tasks import WaitingTaskRequest,WaitingTaskPort,WaitingTaskError,waiting_task_dependency

router=APIRouter(prefix="/api/receiving/st-deferrals",tags=["existing-st-waiting-tasks"])

@router.post("/waiting-tasks")
def plan_waiting(request: WaitingTaskRequest,user: AdminUser=Depends(require_permission("warehouse_task_edit")),
                 service: WaitingTaskPort=Depends(waiting_task_dependency)) -> dict:
    try:
        return service.plan(request,user.username)
    except WaitingTaskError as exc:
        raise HTTPException(exc.status,{"code":exc.code,"message":str(exc)}) from exc

@router.get("/waiting-tasks")
def read_waiting(decision_operation_id: str=Query(min_length=1,max_length=100,pattern=r"^[A-Za-z0-9_.:-]+$"),
                 after_task_id: int=Query(default=0,ge=0),limit: int=Query(default=100,ge=1,le=200),
                 user: AdminUser=Depends(require_permission("warehouse_task_view")),
                 service: WaitingTaskPort=Depends(waiting_task_dependency)) -> dict:
    try:
        return service.read(decision_operation_id,user.username,after_task_id,limit)
    except WaitingTaskError as exc:
        raise HTTPException(exc.status,{"code":exc.code,"message":str(exc)}) from exc
