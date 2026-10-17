from datetime import date
from typing import Any,Literal
from fastapi import APIRouter,Depends,HTTPException,Query
from pydantic import BaseModel,ConfigDict,Field
from ...platform.public import AdminUser,require_permission,get_current_user
from ..contracts import LogisticsCostError
from ..contracts_expenses import LogisticsExpensePort,logistics_expense_service
router=APIRouter(prefix="/api/finance/logistics-expenses",tags=["existing-billing-extra-expenses"])

class Article(BaseModel):
    model_config=ConfigDict(extra="forbid")
    code: str=Field(strict=True,min_length=1,max_length=40,pattern=r"^[A-Z0-9_.:-]+$")
    name: str=Field(strict=True,min_length=1,max_length=120)
    scope: Literal["TRIP","VEHICLE","BOTH"]
    included_in_rate: bool=Field(strict=True)
    active: bool=Field(strict=True)
    expected_version: int=Field(strict=True,ge=0)

class Operation(BaseModel):
    model_config=ConfigDict(extra="forbid")
    operation_id: str=Field(strict=True,min_length=1,max_length=100,pattern=r"^[A-Za-z0-9_.:-]+$")

class Report(Operation):
    cost_correction_of_operation_id: str|None=Field(default=None,strict=True,min_length=1,max_length=100)
    warehouse_id: int=Field(strict=True,gt=0)
    article_code: str=Field(strict=True,min_length=1,max_length=40)
    object_kind: Literal["TRIP","VEHICLE"]
    object_id: int=Field(strict=True,gt=0)
    amount: str=Field(strict=True,min_length=1,max_length=40)
    currency: str=Field(strict=True,pattern=r"^[A-Z]{3}$")
    expense_date: date
    correction_of_operation_id: str|None=Field(default=None,strict=True,min_length=1,max_length=100)
    expected_confirmed_total: str|None=Field(default=None,strict=True,min_length=1,max_length=40)
    document_reference: str=Field(strict=True,min_length=1,max_length=60)
    reason: str=Field(strict=True,min_length=1,max_length=500)

class Decision(Operation):
    expense_operation_id: str=Field(strict=True,min_length=1,max_length=100)
    phase: Literal["LOGIST","FINANCE"]
    outcome: Literal["APPROVE","REJECT"]
    distribution_basis: Literal["NONE","BASE_QUANTITY","WEIGHT"]
    decision_reference: str=Field(strict=True,min_length=1,max_length=60)
    reason: str=Field(strict=True,min_length=1,max_length=500)

def failure(exc: LogisticsCostError,op: str|None=None) -> HTTPException:
    return HTTPException(exc.status,{"code":exc.code,"message":str(exc),"operation_id":op,"outcome_confirmed":exc.status==409})

@router.get("/articles")
def articles(user: AdminUser=Depends(require_permission("transport_dispatch_view")),service: LogisticsExpensePort=Depends(logistics_expense_service)) -> list[dict[str,Any]]:
    return service.articles()

@router.post("/articles")
def article(body: Article,user: AdminUser=Depends(require_permission("create_tt_price")),service: LogisticsExpensePort=Depends(logistics_expense_service)) -> dict[str,Any]:
    try:return service.article(body.code,body.name,body.scope,body.included_in_rate,body.active,body.expected_version,user.username)
    except LogisticsCostError as exc:raise failure(exc) from exc

@router.post("/report")
def report(body: Report,user: AdminUser=Depends(get_current_user),service: LogisticsExpensePort=Depends(logistics_expense_service)) -> dict[str,Any]:
    try:return service.report(body.operation_id,body.warehouse_id,body.article_code,body.object_kind,body.object_id,body.amount,body.currency,body.expense_date.isoformat(),body.document_reference,body.reason,user.username,body.correction_of_operation_id,body.expected_confirmed_total,body.cost_correction_of_operation_id)
    except LogisticsCostError as exc:raise failure(exc,body.operation_id) from exc

@router.post("/decide")
def decide(body: Decision,user: AdminUser=Depends(get_current_user),service: LogisticsExpensePort=Depends(logistics_expense_service)) -> dict[str,Any]:
    try:return service.decide(body.operation_id,body.expense_operation_id,body.phase,body.outcome,body.distribution_basis,body.decision_reference,body.reason,user.username)
    except LogisticsCostError as exc:raise failure(exc,body.operation_id) from exc

@router.get("/warehouses/{ware_id}")
def pending(ware_id: int,operation_id: str|None=Query(default=None,min_length=1,max_length=100),user: AdminUser=Depends(get_current_user),service: LogisticsExpensePort=Depends(logistics_expense_service)) -> list[dict[str,Any]]:
    try:return service.pending(ware_id,user.username,operation_id)
    except LogisticsCostError as exc:raise failure(exc) from exc


@router.get("/warehouses/{ware_id}/normative-costs")
def normative_cost_sources(ware_id: int,cost_operation_id: str|None=Query(default=None,min_length=1,max_length=100),user: AdminUser=Depends(require_permission("transport_dispatch_view")),
                           service: LogisticsExpensePort=Depends(logistics_expense_service))->list[dict[str,Any]]:
    if ware_id<1:raise HTTPException(422,"Positive warehouse required")
    try:return service.normative_cost_sources(ware_id,user.username,cost_operation_id)
    except LogisticsCostError as exc:raise failure(exc)from exc
