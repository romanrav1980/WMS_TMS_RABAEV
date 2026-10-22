from fastapi import APIRouter,Depends,HTTPException
from pydantic import BaseModel,Field,ConfigDict
from ...platform.public import AdminUser,get_current_user
from ..contracts_depot import WarehouseDepotPort,warehouse_depot_service
from ..contracts_plan import TransportPlanError
router=APIRouter(prefix="/api/transport/warehouse-depots",tags=["warehouse-origin"])
class DepotSetting(BaseModel):
    model_config=ConfigDict(extra="forbid")
    operation_id: str=Field(min_length=1,max_length=100,pattern=r"^[A-Za-z0-9_.:-]+$")
    warehouse_id: int=Field(strict=True,gt=0)
    expected_version: int=Field(strict=True,ge=0)
    depot_address: str | None=Field(default=None,min_length=1,max_length=200)
    reason: str=Field(min_length=8,max_length=500)
@router.get("/{warehouse_id}")
def context(warehouse_id: int,user: AdminUser=Depends(get_current_user),
            service: WarehouseDepotPort=Depends(warehouse_depot_service)) -> dict:
    if warehouse_id<1:raise HTTPException(422,"Positive warehouse required")
    try:return service.context(warehouse_id,user.username)
    except TransportPlanError as exc:raise HTTPException(exc.status,{"code":exc.code,"message":str(exc)})from exc
@router.post("")
def configure(body: DepotSetting,user: AdminUser=Depends(get_current_user),
              service: WarehouseDepotPort=Depends(warehouse_depot_service)) -> dict:
    try:return service.apply(body.operation_id,body.model_dump(mode="json",exclude={"operation_id"}),user.username)
    except TransportPlanError as exc:raise HTTPException(exc.status,{"code":exc.code,"message":str(exc)})from exc

@router.post("/resolve")
def resolve(body: DepotSetting,user: AdminUser=Depends(get_current_user),
            service: WarehouseDepotPort=Depends(warehouse_depot_service)) -> dict:
    try:return service.resolve(body.operation_id,body.model_dump(mode="json",exclude={"operation_id"}),user.username)
    except TransportPlanError as exc:raise HTTPException(exc.status,{"code":exc.code,"message":str(exc)})from exc
