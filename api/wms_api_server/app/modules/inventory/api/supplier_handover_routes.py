from typing import Any
from fastapi import APIRouter,Depends,HTTPException
from pydantic import BaseModel,ConfigDict,Field
from ...platform.public import AdminUser,require_permission
from ..contracts_store_returns import StoreReturnReceiveError
from ..contracts_supplier_handover import SupplierHandoverPort,supplier_handover_service
router=APIRouter(prefix="/api/inventory/supplier-handover",tags=["supplier-handover"])

class Operation(BaseModel):
    model_config=ConfigDict(extra="forbid")
    operation_id: str=Field(strict=True,min_length=1,max_length=100,pattern=r"^[A-Za-z0-9_.:-]+$")
    document_reference: str=Field(strict=True,min_length=1,max_length=60)

class Record(Operation):
    dispatch_operation_id: str=Field(strict=True,min_length=1,max_length=100)
    document_sha256: str=Field(strict=True,pattern=r"^[0-9a-f]{64}$")
    receiver_name: str=Field(strict=True,min_length=1,max_length=150)

class Confirm(Operation):
    handover_operation_id: str=Field(strict=True,min_length=1,max_length=100)
    reason: str=Field(strict=True,min_length=1,max_length=500)

def failure(exc: StoreReturnReceiveError,op: str|None=None) -> HTTPException:
    return HTTPException(exc.status,{"code":exc.code,"message":str(exc),"operation_id":op,"outcome_confirmed":exc.status==409})

@router.post("/record")
def record(body: Record,user: AdminUser=Depends(require_permission("warehouse_return_dispatch")),service: SupplierHandoverPort=Depends(supplier_handover_service)) -> dict[str,Any]:
    try:return service.record(body.operation_id,body.dispatch_operation_id,body.document_reference,body.document_sha256,body.receiver_name,user.username)
    except StoreReturnReceiveError as exc:raise failure(exc,body.operation_id) from exc

@router.post("/confirm")
def confirm(body: Confirm,user: AdminUser=Depends(require_permission("store_return_approve")),service: SupplierHandoverPort=Depends(supplier_handover_service)) -> dict[str,Any]:
    try:return service.confirm(body.operation_id,body.handover_operation_id,body.document_reference,body.reason,user.username)
    except StoreReturnReceiveError as exc:raise failure(exc,body.operation_id) from exc

@router.get("/warehouses/{ware_id}")
def pending(ware_id: int,user: AdminUser=Depends(require_permission("warehouse_return_dispatch")),service: SupplierHandoverPort=Depends(supplier_handover_service)) -> list[dict[str,Any]]:
    try:return service.pending(ware_id,user.username)
    except StoreReturnReceiveError as exc:raise failure(exc) from exc
