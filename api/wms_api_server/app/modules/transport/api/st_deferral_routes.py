from typing import Literal
from datetime import date,datetime
from fastapi import APIRouter,Depends,HTTPException,Query
from pydantic import BaseModel,Field,ConfigDict
from ...platform.public import AdminUser,require_permission
from ..contracts_plan import TransportPlanError
from ..contracts_st_deferral import StDeferralPort,st_deferral_service
router=APIRouter(prefix="/api/transport/st-deferrals",tags=["existing-st-deferral"])

class DeferralBody(BaseModel):
    model_config=ConfigDict(extra="forbid")
    operation_id: str=Field(min_length=1,max_length=100,pattern=r"^[A-Za-z0-9_.:-]+$")
    st_number: str=Field(min_length=1,max_length=100)
    target_trip_id: int=Field(strict=True,gt=0)
    expected_version: int=Field(strict=True,ge=0)
    source_hash: str=Field(pattern=r"^[a-f0-9]{64}$")
    reason: str=Field(min_length=8,max_length=500)
    reference: str=Field(min_length=8,max_length=500)

@router.get("/context")
def context(st_number: str=Query(min_length=1,max_length=100),user: AdminUser=Depends(require_permission("transport_dispatch_view")),
            service: StDeferralPort=Depends(st_deferral_service)) -> dict:
    try:return service.context(st_number,user.username)
    except TransportPlanError as exc:raise HTTPException(exc.status,{"code":exc.code,"message":str(exc)})from exc

@router.post("")
def defer(body: DeferralBody,user: AdminUser=Depends(require_permission("transport_dispatch_edit")),
          service: StDeferralPort=Depends(st_deferral_service)) -> dict:
    try:return service.defer(body.operation_id,body.model_dump(mode="json",exclude={"operation_id"}),user.username)
    except TransportPlanError as exc:raise HTTPException(exc.status,{"code":exc.code,"message":str(exc)})from exc

@router.get("/history")
def history(st_number: str=Query(min_length=1,max_length=100),after_version: int=Query(default=0,ge=0),
            user: AdminUser=Depends(require_permission("transport_dispatch_view")),
            service: StDeferralPort=Depends(st_deferral_service)) -> dict:
    try:return service.history(st_number,after_version,user.username)
    except TransportPlanError as exc:raise HTTPException(exc.status,{"code":exc.code,"message":str(exc)})from exc

@router.get("/trip-candidates")
def trip_candidates(st_number: str=Query(min_length=1,max_length=100),
                    date_from: date|None=None,date_to: date|None=None,
                    district: str|None=Query(default=None,max_length=80),
                    store_code: str|None=Query(default=None,max_length=80),
                    after_date: datetime|None=None,after_trip_id: int=Query(default=0,ge=0),
                    limit: int=Query(default=50,ge=1,le=100),
                    purpose: Literal["DEFER","ASSIGN"]="DEFER",
                    user: AdminUser=Depends(require_permission("transport_dispatch_view")),
                    service: StDeferralPort=Depends(st_deferral_service)) -> dict:
    try:
        return service.candidates(st_number,user.username,date_from,date_to,district,store_code,after_date,after_trip_id,limit,purpose)
    except TransportPlanError as exc:
        raise HTTPException(exc.status,{"code":exc.code,"message":str(exc)}) from exc
