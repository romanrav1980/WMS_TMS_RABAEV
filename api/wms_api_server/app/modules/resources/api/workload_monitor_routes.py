from datetime import datetime,timezone
from typing import Any,Protocol
from fastapi import APIRouter,Depends,HTTPException,Path
from pydantic import BaseModel,ConfigDict,Field,AwareDatetime,model_validator
from ...platform.public import AdminUser,require_permission
from ..contracts_workload import WorkloadError

class WorkloadMonitorPort(Protocol):
    def preview(self,ware: int,site: str,start: datetime,end: datetime,minutes: int,windows: list[dict[str,Any]],actor: str) -> dict[str,Any]: ...

def workload_monitor_service() -> WorkloadMonitorPort:
    raise RuntimeError("Live workload monitor not wired")

class WindowInput(BaseModel):
    model_config=ConfigDict(extra="forbid")
    start_at: AwareDatetime
    finish_at: AwareDatetime
    @model_validator(mode="after")
    def bounded_interval(self) -> "WindowInput":
        if self.finish_at<=self.start_at or (self.finish_at-self.start_at).total_seconds()>86400:
            raise ValueError("Positive interval, at most24hours")
        return self

class WaveWindow(WindowInput):
    wave_id: int=Field(strict=True,gt=0)

class MonitorInput(WindowInput):
    site_code: str=Field(strict=True,min_length=1,max_length=50)
    interval_minutes: int=Field(default=60,strict=True,ge=15,le=120)
    wave_windows: list[WaveWindow]=Field(default_factory=list,max_length=1000)

router=APIRouter(prefix="/api/resources/workload",tags=["resource-workload"])

@router.post("/warehouses/{ware_id}/preview")
def preview(request: MonitorInput,ware_id: int=Path(gt=0),user: AdminUser=Depends(require_permission("resource_shift_view")),service: WorkloadMonitorPort=Depends(workload_monitor_service)) -> dict[str,Any]:
    windows=[{"wave_id":row.wave_id,"start_at":row.start_at.astimezone(timezone.utc),"finish_at":row.finish_at.astimezone(timezone.utc)}for row in request.wave_windows]
    try:return service.preview(ware_id,request.site_code,request.start_at.astimezone(timezone.utc),request.finish_at.astimezone(timezone.utc),request.interval_minutes,windows,user.username)
    except WorkloadError as exc:raise HTTPException(exc.status,{"code":exc.code,"message":str(exc)}) from exc
