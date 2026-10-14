from datetime import date
from typing import Any,Literal
from fastapi import APIRouter,Depends,HTTPException,Query
from pydantic import BaseModel,ConfigDict,Field
from ...platform.public import AdminUser,require_permission
from ..contracts import LogisticsCostPort,LogisticsCostError,logistics_cost_service
router=APIRouter(prefix="/api/finance/logistics-costs",tags=["existing-billing-costs"])

class Rate(BaseModel):
    model_config=ConfigDict(extra="forbid")
    warehouse_id: int=Field(strict=True,gt=0)
    currency: str=Field(strict=True,pattern=r"^[A-Z]{3}$")
    rate: str=Field(strict=True,min_length=1,max_length=40)
    effective_from: date
    expected_version: int=Field(strict=True,ge=0)
    reason: str=Field(strict=True,min_length=1,max_length=500)
    decision_reference: str=Field(strict=True,min_length=1,max_length=60)

class MonthlyRate(BaseModel):
    model_config=ConfigDict(extra="forbid")
    warehouse_id: int=Field(strict=True,gt=0)
    currency: str=Field(strict=True,pattern=r"^[A-Z]{3}$")
    month: str=Field(strict=True,pattern=r"^[0-9]{4}-[0-9]{2}$")
    picking_rate: str=Field(strict=True,min_length=1,max_length=40)
    common_work_amount: str=Field(strict=True,min_length=1,max_length=40)
    basis_boxes: str=Field(strict=True,pattern=r"^[0-9]{1,12}$")
    expected_version: int=Field(strict=True,ge=0)
    reason: str=Field(strict=True,min_length=1,max_length=500)
    decision_reference: str=Field(strict=True,min_length=1,max_length=60)

class Calculate(BaseModel):
    model_config=ConfigDict(extra="forbid")
    operation_id: str=Field(strict=True,min_length=1,max_length=100,pattern=r"^[A-Za-z0-9_.:-]+$")
    trip_id: int=Field(strict=True,gt=0)
    warehouse_id: int=Field(strict=True,gt=0)
    currency: str=Field(strict=True,pattern=r"^[A-Z]{3}$")

def failure(exc: LogisticsCostError,op: str|None=None) -> HTTPException:
    return HTTPException(exc.status,{"code":exc.code,"message":str(exc),"operation_id":op,"outcome_confirmed":exc.status==409})

@router.post("/rates")
def rate(body: Rate,user: AdminUser=Depends(require_permission("create_tt_price")),service: LogisticsCostPort=Depends(logistics_cost_service)) -> dict[str,Any]:
    try:return service.rate(body.warehouse_id,body.currency,body.rate,body.effective_from.isoformat(),body.expected_version,body.reason,body.decision_reference,user.username)
    except LogisticsCostError as exc:raise failure(exc) from exc

@router.post("/rates/monthly")
def monthly_rate(body: MonthlyRate,user: AdminUser=Depends(require_permission("create_tt_price")),service: LogisticsCostPort=Depends(logistics_cost_service)) -> dict[str,Any]:
    try:return service.monthly_rate(body.warehouse_id,body.currency,body.month,body.picking_rate,body.common_work_amount,body.basis_boxes,body.expected_version,body.reason,body.decision_reference,user.username)
    except LogisticsCostError as exc:raise failure(exc) from exc

@router.get("/warehouses/{ware_id}/rates")
def rates(ware_id: int,user: AdminUser=Depends(require_permission("transport_dispatch_view")),service: LogisticsCostPort=Depends(logistics_cost_service)) -> list[dict[str,Any]]:
    try:return service.rates(ware_id,user.username)
    except LogisticsCostError as exc:raise failure(exc) from exc

@router.get("/warehouses/{ware_id}/rates/history")
def rate_history(ware_id: int,currency: str=Query(pattern=r"^[A-Z]{3}$"),before_version: int=Query(default=0,ge=0),limit: int=Query(default=25,ge=1,le=100),user: AdminUser=Depends(require_permission("transport_dispatch_view")),service: LogisticsCostPort=Depends(logistics_cost_service)) -> dict[str,Any]:
    try:return service.rate_history(ware_id,currency,before_version,limit,user.username)
    except LogisticsCostError as exc:raise failure(exc) from exc

@router.post("/calculate")
def calculate(body: Calculate,user: AdminUser=Depends(require_permission("calc_tt_price")),service: LogisticsCostPort=Depends(logistics_cost_service)) -> dict[str,Any]:
    try:return service.calculate(body.operation_id,body.trip_id,body.warehouse_id,body.currency,user.username)
    except LogisticsCostError as exc:raise failure(exc,body.operation_id) from exc

@router.get("/trips/{trip_id}")
def trip(trip_id: int,user: AdminUser=Depends(require_permission("transport_dispatch_view")),service: LogisticsCostPort=Depends(logistics_cost_service)) -> dict[str,Any]:
    try:return service.trip(trip_id,user.username)
    except LogisticsCostError as exc:raise failure(exc) from exc

@router.get("/billing-orders/{invoice_id}")
def invoice(invoice_id: int,user: AdminUser=Depends(require_permission("transport_dispatch_view")),service: LogisticsCostPort=Depends(logistics_cost_service)) -> list[dict[str,Any]]:
    try:return service.invoice(invoice_id,user.username)
    except LogisticsCostError as exc:raise failure(exc) from exc


@router.get("/trips/{trip_id}/assembly-period")
def assembly_period(trip_id: int,warehouse_id: int=Query(gt=0),timezone_region: str=Query(min_length=1,max_length=64,pattern=r"^[A-Za-z0-9_/+:-]+$"),user: AdminUser=Depends(require_permission("transport_dispatch_view")),service: LogisticsCostPort=Depends(logistics_cost_service)) -> dict[str,Any]:
    try:return service.assembly_period(trip_id,warehouse_id,timezone_region,user.username)
    except LogisticsCostError as exc:raise failure(exc)from exc


class PeriodPolicy(BaseModel):
    model_config=ConfigDict(extra="forbid")
    operation_id: str=Field(strict=True,min_length=1,max_length=100,pattern=r"^[A-Za-z0-9_.:-]+$")
    period_mode: str=Field(strict=True,pattern=r"^(LOADED_UTC|CASE_ASSEMBLY)$")
    timezone_region: str|None=Field(default=None,strict=True,min_length=1,max_length=64,pattern=r"^[A-Za-z0-9_/+:-]+$")
    expected_version: int=Field(strict=True,ge=0)
    reason: str=Field(strict=True,min_length=1,max_length=500)
    decision_reference: str=Field(strict=True,min_length=1,max_length=60)

@router.get("/warehouses/{ware_id}/period-policy")
def period_policy(ware_id: int,user: AdminUser=Depends(require_permission("transport_dispatch_view")),service: LogisticsCostPort=Depends(logistics_cost_service)) -> dict[str,Any]:
    try:return service.period_policy(ware_id,user.username)
    except LogisticsCostError as exc:raise failure(exc)from exc

@router.post("/warehouses/{ware_id}/period-policy")
def configure_period(ware_id: int,body: PeriodPolicy,user: AdminUser=Depends(require_permission("create_tt_price")),service: LogisticsCostPort=Depends(logistics_cost_service)) -> dict[str,Any]:
    try:return service.configure_period(body.operation_id,ware_id,body.period_mode,body.timezone_region,body.expected_version,body.reason,body.decision_reference,user.username)
    except LogisticsCostError as exc:raise failure(exc,body.operation_id)from exc

@router.get("/billing-orders/{invoice_id}/summary")
def invoice_summary(invoice_id: int,user: AdminUser=Depends(require_permission("transport_dispatch_view")),service: LogisticsCostPort=Depends(logistics_cost_service))->dict[str,Any]:
    try:return service.invoice_summary(invoice_id,user.username)
    except LogisticsCostError as exc:raise failure(exc)from exc

@router.get("/trips/{trip_id}/transport-tariff-sources")
def transport_tariff_sources(trip_id: int,warehouse_id: int=Query(gt=0),
                             user: AdminUser=Depends(require_permission("transport_dispatch_view")),
                             service: LogisticsCostPort=Depends(logistics_cost_service))->dict[str,Any]:
    try:return service.transport_tariff_sources(trip_id,warehouse_id,user.username)
    except LogisticsCostError as exc:raise failure(exc)from exc

class TransportNorm(BaseModel):
    model_config=ConfigDict(extra="forbid")
    operation_id: str=Field(strict=True,min_length=1,max_length=100,pattern=r"^[A-Za-z0-9_.:-]+$")
    source_price_id: int=Field(strict=True,gt=0)
    warehouse_id: int=Field(strict=True,gt=0)
    currency: str=Field(strict=True,pattern=r"^[A-Z]{3}$")
    effective_from: date
    timezone_region: str=Field(strict=True,min_length=1,max_length=64,pattern=r"^[A-Za-z0-9_/+:-]+$")
    vehicle_type: str=Field(strict=True,min_length=1,max_length=40)
    vehicle_size_class: str=Field(strict=True,min_length=1,max_length=40)
    unload_charge_basis: Literal["POINT","PLACE"]|None=None
    pallet_unload_rate: str|None=Field(default=None,strict=True,pattern=r"^[0-9]{1,18}(\.[0-9]{1,9})?$")
    rolling_unload_rate: str=Field(strict=True,pattern=r"^[0-9]{1,18}(\.[0-9]{1,9})?$")
    manual_unload_rate: str=Field(strict=True,pattern=r"^[0-9]{1,18}(\.[0-9]{1,9})?$")
    loader_rate: str=Field(strict=True,pattern=r"^[0-9]{1,18}(\.[0-9]{1,9})?$")
    expected_version: int=Field(strict=True,ge=0)
    reason: str=Field(strict=True,min_length=1,max_length=500)
    decision_reference: str=Field(strict=True,min_length=1,max_length=60)


@router.post("/transport-norms")
def publish_transport_norm(body: TransportNorm,user: AdminUser=Depends(require_permission("create_tt_price")),
                           service: LogisticsCostPort=Depends(logistics_cost_service))->dict[str,Any]:
    try:return service.publish_transport_norm(body.model_dump(mode="json",exclude_none=True),user.username)
    except LogisticsCostError as exc:raise failure(exc,body.operation_id)from exc


@router.get("/warehouses/{ware_id}/transport-norms/{source_price_id}/history")
def transport_norm_history(ware_id: int,source_price_id: int,before_version: int|None=Query(default=None,gt=0),
                           limit: int=Query(default=30,ge=1,le=100),
                           user: AdminUser=Depends(require_permission("transport_dispatch_view")),
                           service: LogisticsCostPort=Depends(logistics_cost_service))->dict[str,Any]:
    try:return service.transport_norm_history(ware_id,source_price_id,before_version,limit,user.username)
    except LogisticsCostError as exc:raise failure(exc)from exc


@router.get("/trips/{trip_id}/transport-cost-facts")
def transport_cost_facts(trip_id: int,warehouse_id: int=Query(gt=0),
                         user: AdminUser=Depends(require_permission("transport_dispatch_view")),
                         service: LogisticsCostPort=Depends(logistics_cost_service))->dict[str,Any]:
    if trip_id<1:raise HTTPException(422,"Укажите рейс")
    try:return service.transport_facts(trip_id,warehouse_id,user.username)
    except LogisticsCostError as exc:raise failure(exc)from exc


@router.get("/trips/{trip_id}/transport-cost-preview")
def transport_cost_preview(trip_id: int,warehouse_id: int=Query(gt=0),source_price_id: int=Query(gt=0),
                           user: AdminUser=Depends(require_permission("transport_dispatch_view")),
                           service: LogisticsCostPort=Depends(logistics_cost_service))->dict[str,Any]:
    if trip_id<1:raise HTTPException(422,"Positive trip ID required")
    try:return service.transport_cost_preview(trip_id,warehouse_id,source_price_id,user.username)
    except LogisticsCostError as exc:raise failure(exc)from exc


class TransportCostConduct(BaseModel):
    model_config=ConfigDict(extra="forbid")
    operation_id: str=Field(strict=True,min_length=1,max_length=100,pattern=r"^[A-Za-z0-9_.:-]+$")
    trip_id: int=Field(strict=True,gt=0)
    warehouse_id: int=Field(strict=True,gt=0)
    source_price_id: int=Field(strict=True,gt=0)
    expected_norm_version: int=Field(strict=True,gt=0)
    currency: str=Field(strict=True,pattern=r"^[A-Z]{3}$")

@router.post("/transport-costs/conduct")
def conduct_transport_cost(body: TransportCostConduct,
                           user: AdminUser=Depends(require_permission("calc_tt_price")),
                           service: LogisticsCostPort=Depends(logistics_cost_service))->dict[str,Any]:
    try:return service.conduct_transport_cost(body.model_dump(mode="json"),user.username)
    except LogisticsCostError as exc:raise failure(exc,body.operation_id)from exc


@router.get("/trips/{trip_id}/transport-costs")
def transport_costs(trip_id: int,warehouse_id: int=Query(gt=0),
                    user: AdminUser=Depends(require_permission("transport_dispatch_view")),
                    service: LogisticsCostPort=Depends(logistics_cost_service))->dict[str,Any]:
    if trip_id<1:raise HTTPException(422,"Positive trip ID required")
    try:return service.transport_costs(trip_id,warehouse_id,user.username)
    except LogisticsCostError as exc:raise failure(exc)from exc


@router.get("/billing-orders/{invoice_id}/transport-costs")
def invoice_transport_costs(invoice_id: int,
                            user: AdminUser=Depends(require_permission("transport_dispatch_view")),
                            service: LogisticsCostPort=Depends(logistics_cost_service))->dict[str,Any]:
    if invoice_id<1:raise HTTPException(422,"Positive invoice ID required")
    try:return service.invoice_transport_costs(invoice_id,user.username)
    except LogisticsCostError as exc:raise failure(exc)from exc
