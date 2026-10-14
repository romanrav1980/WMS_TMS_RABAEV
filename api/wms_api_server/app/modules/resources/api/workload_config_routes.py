from datetime import datetime,timezone
from typing import Any,Literal
from fastapi import APIRouter,Depends,HTTPException,Path,Query
from pydantic import BaseModel,ConfigDict,Field,AwareDatetime,model_validator
from ...platform.public import AdminUser,require_permission
from ..contracts_workload import WorkloadConfigPort,WorkloadError,workload_config_service

router=APIRouter(prefix="/api/resources/workload",tags=["resource-workload"])
class CommandInput(BaseModel):
    model_config=ConfigDict(extra="forbid")
    operation_id: str=Field(strict=True,min_length=1,max_length=100)
    warehouse_id: int=Field(strict=True,gt=0)
    reason: str=Field(strict=True,min_length=3,max_length=500)

class NormInput(CommandInput):
    site_code: str=Field(strict=True,min_length=1,max_length=50)
    article: str=Field(strict=True,min_length=1,max_length=160)
    base_uom: str=Field(strict=True,min_length=1,max_length=20)
    base_per_hour: str=Field(strict=True,pattern=r"^[0-9]{1,29}(\.[0-9]{1,9})?$")
    expected_version: int=Field(strict=True,ge=0)
    active: bool=True

class AttendanceInput(CommandInput):
    site_code: str=Field(strict=True,min_length=1,max_length=50)
    resource_id: int=Field(strict=True,gt=0)
    start_at: AwareDatetime
    finish_at: AwareDatetime

    @model_validator(mode="after")
    def valid_interval(self) -> "AttendanceInput":
        if self.finish_at<=self.start_at or (self.finish_at-self.start_at).total_seconds()>86400:
            raise ValueError("Attendance interval must be positive and at most24 hours")
        return self

class ReplaceAttendanceInput(AttendanceInput):
    plan_operation_id: str=Field(strict=True,min_length=1,max_length=100)
    reason: str=Field(strict=True,min_length=8,max_length=500)

class CancelInput(CommandInput):
    plan_operation_id: str=Field(strict=True,min_length=1,max_length=100)

def invoke(request: CommandInput,action: str,user: AdminUser,service: WorkloadConfigPort) -> dict[str,Any]:
    body=request.model_dump(exclude={"operation_id"})
    for key,value in list(body.items()):
        if isinstance(value,datetime):
            body[key]=value.astimezone(timezone.utc).isoformat(timespec="microseconds")
    try:return service.command(request.operation_id,action,body,user.username)
    except WorkloadError as exc:raise HTTPException(exc.status,{"code":exc.code,"message":str(exc)}) from exc

@router.post("/norms")
def save_norm(request: NormInput,user: AdminUser=Depends(require_permission("resource_shift_edit")),service: WorkloadConfigPort=Depends(workload_config_service)) -> dict[str,Any]:
    return invoke(request,"NORM",user,service)

@router.post("/attendance")
def plan_attendance(request: AttendanceInput,user: AdminUser=Depends(require_permission("resource_shift_edit")),service: WorkloadConfigPort=Depends(workload_config_service)) -> dict[str,Any]:
    return invoke(request,"ATTENDANCE",user,service)

@router.post("/attendance/replace")
def replace_attendance(request: ReplaceAttendanceInput,user: AdminUser=Depends(require_permission("resource_shift_edit")),service: WorkloadConfigPort=Depends(workload_config_service)) -> dict[str,Any]:
    return invoke(request,"REPLACE_ATTENDANCE",user,service)

@router.post("/attendance/cancel")
def cancel_attendance(request: CancelInput,user: AdminUser=Depends(require_permission("resource_shift_edit")),service: WorkloadConfigPort=Depends(workload_config_service)) -> dict[str,Any]:
    return invoke(request,"CANCEL_ATTENDANCE",user,service)

@router.get("/warehouses/{ware_id}")
def read_configuration(ware_id: int=Path(gt=0),site_code: str | None=Query(None,min_length=1,max_length=50),
                       start_at: AwareDatetime | None=None,finish_at: AwareDatetime | None=None,
                       user: AdminUser=Depends(require_permission("resource_shift_view")),
                       service: WorkloadConfigPort=Depends(workload_config_service)) -> dict[str,Any]:
    if (start_at is None)!=(finish_at is None):
        raise HTTPException(422,"Укажите обе границы периода плановых выходов")
    if start_at is not None and (finish_at<=start_at or (finish_at-start_at).total_seconds()>31*86400):
        raise HTTPException(422,"Период должен быть положительным и не длиннее 31 дня")
    try:return service.configuration(ware_id,user.username,site_code,start_at,finish_at)
    except WorkloadError as exc:raise HTTPException(exc.status,{"code":exc.code,"message":str(exc)}) from exc


class ForecastScopeInput(CommandInput):
    work_scope: Literal["CASE_DISPATCH","FULLPAL_DISPATCH","OUTBOUND_WORKLOAD"]
    site_code: str=Field(strict=True,min_length=1,max_length=50)
    expected_version: int=Field(strict=True,ge=0)
    active: bool=Field(strict=True)

@router.post("/forecast-scopes")
def save_forecast_scope(request: ForecastScopeInput,user: AdminUser=Depends(require_permission("resource_shift_edit")),service: WorkloadConfigPort=Depends(workload_config_service)) -> dict[str,Any]:
    return invoke(request,"FORECAST_SCOPE",user,service)
