from typing import Any
from fastapi import APIRouter,Depends,Query
from pydantic import BaseModel,ConfigDict,Field
from ...platform.public import AdminUser,require_permission
from ..contracts import StoreReceiptError
from ..contracts_return_custody import ReturnCustodyPort,return_custody_service
from .store_receipt_routes import failure

router=APIRouter(prefix="/api/delivery/store-return-custody",tags=["return-custody"])


class CustodyCommand(BaseModel):
    model_config=ConfigDict(extra="forbid")
    operation_id: str=Field(strict=True,min_length=1,max_length=100,pattern=r"^[A-Za-z0-9_.:-]+$")


class Handover(CustodyCommand):
    transport_operation_id: str=Field(strict=True,min_length=1,max_length=100)
    pallet_identifier: str=Field(strict=True,min_length=1,max_length=200)
    quantity: str=Field(strict=True,pattern=r"^[0-9]{1,18}(\.[0-9]{1,9})?$")
    base_uom: str=Field(strict=True,min_length=1,max_length=20)
    gross_weight_kg: str=Field(strict=True,pattern=r"^[0-9]{1,18}(\.[0-9]{1,9})?$")
    physical_places: int=Field(strict=True,ge=1,le=200)


class Pickup(CustodyCommand):
    handover_operation_id: str=Field(strict=True,min_length=1,max_length=100)
    scan_vehicle: str=Field(strict=True,min_length=1,max_length=50)
    scan_pallet: str=Field(strict=True,min_length=1,max_length=200)


@router.post("/handover")
def handover(body: Handover,user: AdminUser=Depends(require_permission("store_return_handover")),
             service: ReturnCustodyPort=Depends(return_custody_service)) -> dict[str,Any]:
    try:
        return service.handover(body.operation_id,body.transport_operation_id,body.model_dump(exclude={"operation_id","transport_operation_id"}),user.username)
    except StoreReceiptError as exc:
        raise failure(exc) from exc


@router.post("/pickup")
def pickup(body: Pickup,user: AdminUser=Depends(require_permission("driver_return_accept")),
           service: ReturnCustodyPort=Depends(return_custody_service)) -> dict[str,Any]:
    try:
        return service.pickup(body.operation_id,body.handover_operation_id,body.model_dump(exclude={"operation_id","handover_operation_id"}),user.username)
    except StoreReceiptError as exc:
        raise failure(exc) from exc


@router.get("/store")
def store(store_address: str=Query(min_length=1,max_length=255),task_id: int | None=Query(default=None,ge=1),user: AdminUser=Depends(require_permission("store_return_handover")),
          service: ReturnCustodyPort=Depends(return_custody_service)) -> list[dict[str,Any]]:
    try:
        return service.store_pending(store_address,user.username,task_id)
    except StoreReceiptError as exc:
        raise failure(exc) from exc


@router.get("/driver")
def driver(task_id: int | None=Query(default=None,ge=1),user: AdminUser=Depends(require_permission("driver_return_accept")),
           service: ReturnCustodyPort=Depends(return_custody_service)) -> list[dict[str,Any]]:
    return service.driver_pending(user.username,task_id)
