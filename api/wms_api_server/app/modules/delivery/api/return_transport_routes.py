from typing import Any
from fastapi import APIRouter,Depends
from pydantic import BaseModel,ConfigDict,Field
from ...platform.public import AdminUser,require_permission
from ..contracts import StoreReceiptError
from ..contracts_return_transport import ReturnTransportPort,return_transport_service
from .store_receipt_routes import failure

router=APIRouter(prefix="/api/delivery/store-return-transport",tags=["store-return-transport"])


class ReturnPlan(BaseModel):
    model_config=ConfigDict(extra="forbid")
    operation_id: str=Field(strict=True,min_length=1,max_length=100,pattern=r"^[A-Za-z0-9_.:-]+$")
    approval_operation_id: str=Field(strict=True,min_length=1,max_length=100)
    task_id: int=Field(strict=True,ge=1)
    gross_weight_kg: str=Field(strict=True,pattern=r"^[0-9]{1,18}(\.[0-9]{1,9})?$")
    physical_places: int=Field(strict=True,ge=1,le=200)


@router.post("/plan")
def plan(body: ReturnPlan,user: AdminUser=Depends(require_permission("store_return_transport")),
         service: ReturnTransportPort=Depends(return_transport_service)) -> dict[str,Any]:
    try:
        return service.plan(body.operation_id,body.approval_operation_id,body.model_dump(exclude={"operation_id","approval_operation_id"}),user.username)
    except StoreReceiptError as exc:
        raise failure(exc) from exc


@router.get("/eligible")
def eligible(user: AdminUser=Depends(require_permission("store_return_transport")),
             service: ReturnTransportPort=Depends(return_transport_service)) -> list[dict[str,Any]]:
    return service.eligible()


@router.get("/trips/{task_id}")
def trip(task_id: int,user: AdminUser=Depends(require_permission("store_return_transport")),
         service: ReturnTransportPort=Depends(return_transport_service)) -> list[dict[str,Any]]:
    try:
        return service.trip(task_id)
    except StoreReceiptError as exc:
        raise failure(exc) from exc
