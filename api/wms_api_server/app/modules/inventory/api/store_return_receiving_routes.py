from ..contracts_aggregation_scans import AggregationCodeScan
from typing import Any
from fastapi import APIRouter,Depends,HTTPException,Query
from pydantic import BaseModel,ConfigDict,Field
from ...platform.public import AdminUser,require_permission
from ..contracts_store_returns import StoreReturnReceivePort,StoreReturnReceiveError,store_return_receive_service

from .task_scan_routes import UnitScan

router=APIRouter(prefix="/api/inventory/store-returns",tags=["warehouse-store-return"])


class ReturnWarePolicy(BaseModel):
    model_config=ConfigDict(extra="forbid")
    supplier_receive_cell: str=Field(strict=True,min_length=1,max_length=60)
    disposal_receive_cell: str=Field(strict=True,min_length=1,max_length=60)
    expected_version: int=Field(strict=True,ge=0)


class ReceiveStoreReturn(BaseModel):
    aggregation_scans: list[AggregationCodeScan]=Field(default_factory=list,max_length=1000)
    scans: list[UnitScan]=Field(default_factory=list,max_length=20000)
    model_config=ConfigDict(extra="forbid")
    operation_id: str=Field(strict=True,min_length=1,max_length=100,pattern=r"^[A-Za-z0-9_.:-]+$")
    pickup_operation_id: str=Field(strict=True,min_length=1,max_length=100)
    scan_pallet: str=Field(strict=True,min_length=1,max_length=50)
    scan_vehicle: str=Field(strict=True,min_length=1,max_length=50)
    scan_cell: str=Field(strict=True,min_length=1,max_length=60)
    scan_article: str=Field(default='',strict=True,max_length=128)
    article: str=Field(strict=True,min_length=1,max_length=160)
    quantity: str=Field(strict=True,pattern=r"^[0-9]{1,18}(\.[0-9]{1,9})?$")
    base_uom: str=Field(strict=True,min_length=1,max_length=20)
    expiry_date: str=Field(strict=True,pattern=r"^[0-9]{4}-[0-9]{2}-[0-9]{2}$")
    supplier_batch: str=Field(strict=True,min_length=1,max_length=100)
    gross_weight_kg: str=Field(strict=True,pattern=r"^[0-9]{1,18}(\.[0-9]{1,9})?$")
    net_weight_kg: str=Field(strict=True,pattern=r"^[0-9]{1,18}(\.[0-9]{1,9})?$")
    full_box_count: str|None=Field(default=None,strict=True,pattern=r"^[1-9][0-9]{0,17}$")
    complete_good_boxes: bool=Field(default=False,strict=True)


def failure(error: StoreReturnReceiveError) -> HTTPException:
    return HTTPException(error.status,{"code":error.code,"message":str(error),"operation_id":error.operation_id,
                                      "retry_same_operation_id":bool(error.operation_id),"outcome_confirmed":error.status<500})


@router.put("/warehouses/{ware_id}/policy")
def configure(ware_id: int,body: ReturnWarePolicy,user: AdminUser=Depends(require_permission("warehouse_settings_edit")),
              service: StoreReturnReceivePort=Depends(store_return_receive_service)) -> dict[str,Any]:
    try:
        return service.configure(ware_id,body.supplier_receive_cell,body.disposal_receive_cell,body.expected_version,user.username)
    except StoreReturnReceiveError as exc:
        raise failure(exc) from exc


@router.get("/warehouses/{ware_id}/policy")
def policy(ware_id: int,user: AdminUser=Depends(require_permission("warehouse_settings_edit")),
           service: StoreReturnReceivePort=Depends(store_return_receive_service)) -> dict[str,Any]:
    try:return service.policy(ware_id,user.username)
    except StoreReturnReceiveError as exc:raise failure(exc)from exc


@router.get("/warehouses/{ware_id}/pending")
def pending(ware_id: int,user: AdminUser=Depends(require_permission("warehouse_return_receive")),
            service: StoreReturnReceivePort=Depends(store_return_receive_service)) -> list[dict[str,Any]]:
    try:
        return service.pending(ware_id,user.username)
    except StoreReturnReceiveError as exc:
        raise failure(exc) from exc


@router.post("/receive")
def receive(body: ReceiveStoreReturn,user: AdminUser=Depends(require_permission("warehouse_return_receive")),
            service: StoreReturnReceivePort=Depends(store_return_receive_service)) -> dict[str,Any]:
    try:
        return service.confirm(body.operation_id,body.pickup_operation_id,body.model_dump(exclude={"operation_id","pickup_operation_id"},exclude_defaults=True),user.username)
    except StoreReturnReceiveError as exc:
        raise failure(exc) from exc


class ReuseZone(BaseModel):
    model_config=ConfigDict(extra="forbid")
    receive_cell: str=Field(strict=True,min_length=1,max_length=60)
    expected_version: int=Field(strict=True,ge=1)

@router.put("/warehouses/{ware_id}/reuse-receiving")
def reuse_zone(ware_id: int,body: ReuseZone,user: AdminUser=Depends(require_permission("warehouse_settings_edit")),service: StoreReturnReceivePort=Depends(store_return_receive_service)) -> dict[str,Any]:
    try:return service.configure_reuse(ware_id,body.receive_cell,body.expected_version,user.username)
    except StoreReturnReceiveError as exc:raise failure(exc) from exc

@router.get("/warehouses/{ware_id}/pending-page")
def pending_page(ware_id: int,after: str=Query(default="",max_length=100),limit: int=Query(default=20,ge=1,le=100),
                 user: AdminUser=Depends(require_permission("warehouse_return_receive")),
                 service: StoreReturnReceivePort=Depends(store_return_receive_service)) -> dict:
    if ware_id<1:raise HTTPException(422,"Positive warehouse required")
    try:return service.page(ware_id,after,limit,user.username)
    except StoreReturnReceiveError as exc:raise failure(exc)from exc

@router.get("/warehouses/{ware_id}/pickups/{pickup_id}/source")
def selected_source(ware_id: int,pickup_id: str,user: AdminUser=Depends(require_permission("warehouse_return_receive")),
                    service: StoreReturnReceivePort=Depends(store_return_receive_service)) -> dict:
    if ware_id<1 or not 1<=len(pickup_id)<=100:raise HTTPException(422,"Positive warehouse and pickup required")
    try:return service.source(ware_id,pickup_id,user.username)
    except StoreReturnReceiveError as exc:raise failure(exc)from exc
