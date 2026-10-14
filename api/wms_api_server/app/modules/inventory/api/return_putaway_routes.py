from typing import Any
from fastapi import APIRouter,Depends,Query
from pydantic import BaseModel,ConfigDict,Field
from ...platform.public import AdminUser,require_permission
from ..contracts_store_returns import StoreReturnReceiveError
from ..contracts_return_putaway import ReturnPutawayPort,return_putaway_service
from .store_return_receiving_routes import failure

router=APIRouter(prefix="/api/inventory/store-return-putaway",tags=["existing-return-putaway"])


class ReturnTargets(BaseModel):
    model_config=ConfigDict(extra="forbid")
    supplier_target_cell: str=Field(strict=True,min_length=1,max_length=60)
    disposal_target_cell: str=Field(strict=True,min_length=1,max_length=60)
    expected_version: int=Field(strict=True,ge=1)


class ReturnTaskPlan(BaseModel):
    model_config=ConfigDict(extra="forbid")
    operation_id: str=Field(strict=True,min_length=1,max_length=100,pattern=r"^[A-Za-z0-9_.:-]+$")
    receipt_operation_id: str=Field(strict=True,min_length=1,max_length=100)


@router.put("/warehouses/{ware_id}/targets")
def targets(ware_id: int,body: ReturnTargets,user: AdminUser=Depends(require_permission("warehouse_settings_edit")),
            service: ReturnPutawayPort=Depends(return_putaway_service)) -> dict[str,Any]:
    try:
        return service.configure(ware_id,body.supplier_target_cell,body.disposal_target_cell,body.expected_version,user.username)
    except StoreReturnReceiveError as exc:
        raise failure(exc) from exc


@router.get("/warehouses/{ware_id}/pending")
def pending(ware_id: int,receipt_operation_id: str | None=Query(default=None,min_length=1,max_length=100),user: AdminUser=Depends(require_permission("warehouse_return_place")),
            service: ReturnPutawayPort=Depends(return_putaway_service)) -> list[dict[str,Any]]:
    try:
        return service.pending(ware_id,user.username,receipt_operation_id)
    except StoreReturnReceiveError as exc:
        raise failure(exc) from exc


@router.post("/plan")
def plan(body: ReturnTaskPlan,user: AdminUser=Depends(require_permission("warehouse_return_place")),
         service: ReturnPutawayPort=Depends(return_putaway_service)) -> dict[str,Any]:
    try:
        return service.plan(body.operation_id,body.receipt_operation_id,user.username)
    except StoreReturnReceiveError as exc:
        raise failure(exc) from exc
