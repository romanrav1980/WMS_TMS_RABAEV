from typing import Any
from fastapi import APIRouter,Depends,HTTPException
from pydantic import BaseModel,ConfigDict,Field
from ...platform.public import AdminUser,require_permission
from ..contracts_stock import StockPostingError
from ..contracts_store_returns import StoreReturnReceiveError
from ..contracts_disposal import ReturnDisposalPort,return_disposal_service
from .task_scan_routes import UnitScan
router=APIRouter(prefix="/api/inventory/return-disposal",tags=["return-disposal"])

class Operation(BaseModel):
    model_config=ConfigDict(extra="forbid")
    operation_id: str=Field(strict=True,min_length=1,max_length=100,pattern=r"^[A-Za-z0-9_.:-]+$")

class Report(Operation):
    receipt_operation_id: str=Field(strict=True,min_length=1,max_length=100)
    document_reference: str=Field(strict=True,min_length=1,max_length=60)
    document_sha256: str=Field(strict=True,pattern=r"^[0-9a-f]{64}$")
    reason: str=Field(strict=True,min_length=1,max_length=500)

class Dispose(Operation):
    scans: list[UnitScan]=Field(default_factory=list,max_length=20000)
    request_operation_id: str=Field(strict=True,min_length=1,max_length=100)
    expected_stock_version: int=Field(strict=True,ge=0)
    scan_pallet: str=Field(strict=True,min_length=1,max_length=200)
    scan_cell: str=Field(strict=True,min_length=1,max_length=60)
    decision_reference: str=Field(strict=True,min_length=1,max_length=60)

def failure(exc: StoreReturnReceiveError,op: str|None=None) -> HTTPException:
    return HTTPException(exc.status,{"code":exc.code,"message":str(exc),"operation_id":op,"outcome_confirmed":exc.status==409})

@router.post("/report")
def report(body: Report,user: AdminUser=Depends(require_permission("warehouse_return_dispatch")),service: ReturnDisposalPort=Depends(return_disposal_service)) -> dict[str,Any]:
    try:return service.report(body.operation_id,body.receipt_operation_id,body.document_reference,body.document_sha256,body.reason,user.username)
    except StoreReturnReceiveError as exc:raise failure(exc,body.operation_id) from exc

@router.post("/dispose")
def dispose(body: Dispose,user: AdminUser=Depends(require_permission("store_return_approve")),service: ReturnDisposalPort=Depends(return_disposal_service)) -> dict[str,Any]:
    try:return service.dispose(body.operation_id,body.request_operation_id,body.expected_stock_version,body.scan_pallet,body.scan_cell,body.decision_reference,user.username,[item.model_dump()for item in body.scans])
    except StockPostingError as exc:raise HTTPException(403 if exc.oracle_code==20882 else 409 if exc.oracle_code is not None and 20800<=exc.oracle_code<=20999 else 503,{"code":exc.code,"message":exc.rule_reason or str(exc),"operation_id":body.operation_id,"outcome_confirmed":exc.oracle_code is not None and 20800<=exc.oracle_code<=20999}) from exc
    except StoreReturnReceiveError as exc:raise failure(exc,body.operation_id) from exc

@router.get("/warehouses/{ware_id}")
def pending(ware_id: int,user: AdminUser=Depends(require_permission("warehouse_return_dispatch")),service: ReturnDisposalPort=Depends(return_disposal_service)) -> list[dict[str,Any]]:
    try:return service.pending(ware_id,user.username)
    except StoreReturnReceiveError as exc:raise failure(exc) from exc
