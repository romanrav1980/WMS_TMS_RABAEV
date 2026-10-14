from typing import Any,Literal
from fastapi import APIRouter,Depends,HTTPException
from pydantic import BaseModel,ConfigDict,Field
from ...platform.public import AdminUser,require_permission
from ..contracts_forecast import ForecastQuery,WarehouseForecastError,WarehouseForecastPort,warehouse_forecast_service

router=APIRouter(prefix="/api/transport/warehouse-forecast",tags=["warehouse-forecast"])
class ForecastRequest(BaseModel):
    model_config=ConfigDict(extra="forbid")
    history_days: int=Field(default=28,strict=True,ge=1,le=90)
    horizon_days: int=Field(default=7,strict=True,ge=1,le=31)
    minimum_active_days: int=Field(default=3,strict=True,ge=1,le=90)
    include_current_day: bool=False
    scope: Literal["CASE_DISPATCH","FULLPAL_DISPATCH","OUTBOUND_WORKLOAD"]="CASE_DISPATCH"

@router.post("/warehouses/{ware_id}/view")
def forecast(ware_id: int,body: ForecastRequest,user: AdminUser=Depends(require_permission("transport_dispatch_view")),service: WarehouseForecastPort=Depends(warehouse_forecast_service)) -> dict[str,Any]:
    if ware_id<1:raise HTTPException(422,"Positive warehouse required")
    try:return service.get(ware_id,ForecastQuery(**body.model_dump()),user.username)
    except WarehouseForecastError as exc:raise HTTPException(exc.status,{"code":exc.code,"message":str(exc)}) from exc

@router.post("/warehouses/{ware_id}/project")
def project(ware_id: int,limit: int=50,user: AdminUser=Depends(require_permission("transport_dispatch_edit")),service: WarehouseForecastPort=Depends(warehouse_forecast_service)) -> dict[str,Any]:
    if ware_id<1 or not 1<=limit<=100:raise HTTPException(422,"Positive warehouse and batch1..100 required")
    try:return service.project(ware_id,limit,user.username)
    except WarehouseForecastError as exc:raise HTTPException(exc.status,{"code":exc.code,"message":str(exc)}) from exc

class ProjectLoad(BaseModel):
    model_config=ConfigDict(extra="forbid")
    source_load_operation_id: str=Field(strict=True,min_length=1,max_length=100)

@router.post("/source")
def project_source(body: ProjectLoad,user: AdminUser=Depends(require_permission("transport_dispatch_edit")),service: WarehouseForecastPort=Depends(warehouse_forecast_service)) -> dict[str,Any]:
    try:return service.project_load(body.source_load_operation_id,user.username)
    except WarehouseForecastError as exc:raise HTTPException(exc.status,{"code":exc.code,"message":str(exc)}) from exc
