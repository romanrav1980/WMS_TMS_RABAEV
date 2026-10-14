from datetime import timezone
from typing import Any,Literal
from fastapi import APIRouter,Depends,HTTPException,Path
from pydantic import BaseModel,ConfigDict,Field,AwareDatetime,model_validator
from ...platform.public import AdminUser,require_permission
from ..contracts_wave_time import WaveTimePort,wave_time_service
from ..contracts_workload import WorkloadError

class WaveTimeApproval(BaseModel):
    model_config=ConfigDict(extra="forbid")
    operation_id: str=Field(min_length=1,max_length=100,pattern=r"^[A-Za-z0-9_.:-]+$")
    wave_id: int=Field(strict=True,gt=0)
    expected_version: int=Field(strict=True,ge=0)
    source_token: str=Field(pattern=r"^[a-f0-9]{64}$")
    start_at: AwareDatetime
    finish_at: AwareDatetime
    time_zone: Literal["UTC","Europe/Moscow","Asia/Tbilisi"]
    reason: str=Field(min_length=8,max_length=500)
    @model_validator(mode="after")
    def bounded_period(self) -> "WaveTimeApproval":
        if self.finish_at<=self.start_at or (self.finish_at-self.start_at).total_seconds()>86400:
            raise ValueError("Positive interval at most24hours")
        return self

router=APIRouter(prefix="/api/resources/workload/waves",tags=["resource-workload"])

@router.get("/{wave_id}/time-context")
def context(wave_id: int=Path(gt=0),user: AdminUser=Depends(require_permission("pick_wave_view")),service: WaveTimePort=Depends(wave_time_service)) -> dict[str,Any]:
    try:return service.context(wave_id,user.username)
    except WorkloadError as exc:raise HTTPException(exc.status,{"code":exc.code,"message":str(exc)}) from exc

@router.post("/approve-time")
def approve(request: WaveTimeApproval,user: AdminUser=Depends(require_permission("pick_wave_launch")),service: WaveTimePort=Depends(wave_time_service)) -> dict[str,Any]:
    body=request.model_dump(exclude={"operation_id"},mode="json")
    for key in ("start_at","finish_at"):
        body[key]=getattr(request,key).astimezone(timezone.utc).isoformat(timespec="microseconds")
    try:return service.approve(request.operation_id,body,user.username)
    except WorkloadError as exc:raise HTTPException(exc.status,{"code":exc.code,"message":str(exc)}) from exc
