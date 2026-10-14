from typing import Any
from fastapi import APIRouter,Depends,HTTPException
from pydantic import BaseModel,ConfigDict,Field
from ...platform.public import AdminUser,require_permission
from ..contracts_store_returns import StoreReturnReceiveError
from ..contracts_supplier_return import SupplierReturnPort,supplier_return_service
router=APIRouter(prefix="/api/inventory/supplier-returns",tags=["existing-supplier-return"])

class Preparation(BaseModel):
    model_config=ConfigDict(extra="forbid")
    operation_id: str=Field(strict=True,min_length=1,max_length=100,pattern=r"^[A-Za-z0-9_.:-]+$")
    receipt_operation_id: str=Field(strict=True,min_length=1,max_length=100)
    supplier_inn: str=Field(strict=True,pattern=r"^(?:[0-9]{10}|[0-9]{12})$")
    reason: str=Field(strict=True,min_length=1,max_length=500)
    decision_reference: str=Field(strict=True,min_length=1,max_length=60)

def failure(exc: StoreReturnReceiveError,operation_id: str|None=None) -> HTTPException:
    return HTTPException(exc.status,{"code":exc.code,"message":str(exc),"operation_id":operation_id,"outcome_confirmed":exc.status==409})

@router.post("/prepare")
def prepare(body: Preparation,user: AdminUser=Depends(require_permission("store_return_approve")),service: SupplierReturnPort=Depends(supplier_return_service)) -> dict[str,Any]:
    try:return service.prepare(body.operation_id,body.receipt_operation_id,body.supplier_inn,body.reason,body.decision_reference,user.username)
    except StoreReturnReceiveError as exc:raise failure(exc,body.operation_id) from exc

@router.get("/warehouses/{ware_id}")
def pending(ware_id: int,user: AdminUser=Depends(require_permission("warehouse_return_dispatch")),service: SupplierReturnPort=Depends(supplier_return_service)) -> list[dict[str,Any]]:
    try:return service.pending(ware_id,user.username)
    except StoreReturnReceiveError as exc:raise failure(exc) from exc

@router.get("/suppliers")
def suppliers(user: AdminUser=Depends(require_permission("store_return_approve")),service: SupplierReturnPort=Depends(supplier_return_service)) -> list[dict[str,Any]]:
    return service.suppliers()
