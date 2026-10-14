from typing import Any
from fastapi import APIRouter,Depends,HTTPException
from pydantic import BaseModel,ConfigDict,Field
from ...platform.public import AdminUser,require_permission
from ..contracts import LogisticsCostError
from ..contracts_allocation import ExpenseAllocationPort,expense_allocation_service
router=APIRouter(prefix="/api/finance/expense-allocation",tags=["actual-trip-cost-allocation"])

class Allocate(BaseModel):
    model_config=ConfigDict(extra="forbid")
    operation_id: str=Field(strict=True,min_length=1,max_length=100,pattern=r"^[A-Za-z0-9_.:-]+$")
    expense_operation_id: str=Field(strict=True,min_length=1,max_length=100)

@router.post("")
def allocate(body: Allocate,user: AdminUser=Depends(require_permission("calc_tt_price")),service: ExpenseAllocationPort=Depends(expense_allocation_service)) -> dict[str,Any]:
    try:return service.allocate(body.operation_id,body.expense_operation_id,user.username)
    except LogisticsCostError as exc:raise HTTPException(exc.status,{"code":exc.code,"message":str(exc),"operation_id":body.operation_id,"outcome_confirmed":exc.status==409}) from exc

@router.get("/billing-orders/{invoice_id}")
def invoice(invoice_id: int,user: AdminUser=Depends(require_permission("transport_dispatch_view")),service: ExpenseAllocationPort=Depends(expense_allocation_service)) -> list[dict[str,Any]]:
    return service.invoice(invoice_id,user.username)
