from datetime import datetime
from decimal import Decimal
from typing import Any, Literal
from fastapi import APIRouter,Depends,HTTPException,Query
from pydantic import BaseModel,ConfigDict,Field,model_validator
from ...platform.public import AdminUser,require_permission
from ..contracts_interwarehouse import InterwarehousePort,interwarehouse_service
from ..contracts_store_returns import StoreReturnReceiveError

from .task_scan_routes import UnitScan

router = APIRouter(prefix="/api/inventory/interwarehouse",tags=["interwarehouse"])

class Plan(BaseModel):
    model_config = ConfigDict(extra="forbid")
    operation_id: str = Field(strict=True,min_length=1,max_length=100,pattern=r"^[A-Za-z0-9_.:-]+$")
    source_load_operation_id: str = Field(strict=True,min_length=1,max_length=100)
    target_warehouse_id: int = Field(strict=True,gt=0)
    target_trip_id: int = Field(strict=True,gt=0)
    inbound_dock: str = Field(strict=True,min_length=1,max_length=60)
    arrival_due: datetime
    ready_due: datetime
    reason: str = Field(strict=True,min_length=1,max_length=500)
    decision_reference: str = Field(strict=True,min_length=1,max_length=60)

    @model_validator(mode="after")
    def deadlines(self) -> "Plan":
        if any(value.utcoffset() is None for value in (self.arrival_due,self.ready_due)) or self.ready_due < self.arrival_due:
            raise ValueError("Timezone-aware ordered deadlines required")
        return self

@router.post("/plan")
def plan(body: Plan,user: AdminUser=Depends(require_permission("transport_dispatch_edit")),service: InterwarehousePort=Depends(interwarehouse_service)) -> dict[str,Any]:
    try:
        return service.plan(body.operation_id,body.source_load_operation_id,body.target_warehouse_id,body.target_trip_id,body.inbound_dock,body.arrival_due,body.ready_due,body.reason,body.decision_reference,user.username)
    except StoreReturnReceiveError as exc:
        raise HTTPException(exc.status,{"code":exc.code,"message":str(exc),"operation_id":body.operation_id,"outcome_confirmed":exc.status==409}) from exc

@router.get("/warehouses/{ware_id}")
def queue(ware_id: int,include_completed: bool=Query(default=False),user: AdminUser=Depends(require_permission("transport_dispatch_view")),service: InterwarehousePort=Depends(interwarehouse_service)) -> list[dict[str,Any]]:
    try:
        return service.queue(ware_id,user.username,include_completed)
    except StoreReturnReceiveError as exc:
        raise HTTPException(exc.status,{"code":exc.code,"message":str(exc)}) from exc


class PhysicalAction(BaseModel):
    model_config = ConfigDict(extra="forbid")
    operation_id: str = Field(strict=True,min_length=1,max_length=100,pattern=r"^[A-Za-z0-9_.:-]+$")
    plan_operation_id: str = Field(strict=True,min_length=1,max_length=100)
    scan_pallet: str = Field(strict=True,min_length=1,max_length=200)

class Unload(PhysicalAction):
    scan_vehicle: str = Field(strict=True,min_length=1,max_length=60)
    scan_dock: str = Field(strict=True,min_length=1,max_length=60)

class Receive(PhysicalAction):
    scans: list[UnitScan] = Field(default_factory=list,max_length=20000)
    scan_cell: str = Field(strict=True,min_length=1,max_length=60)
    scan_article: str = Field(strict=True,min_length=1,max_length=128)
    article: str = Field(strict=True,min_length=1,max_length=160)
    quantity: str = Field(strict=True,min_length=1,max_length=40,pattern=r"^[0-9]+(\.[0-9]+)?$")
    base_uom: str = Field(strict=True,min_length=1,max_length=20)

def physical(kind: str,body: PhysicalAction,user: AdminUser,service: InterwarehousePort) -> dict[str,Any]:
    from ..contracts_stock import StockPostingError
    try:
        return service.receive_action(kind,body.operation_id,body.plan_operation_id,body.model_dump(exclude={"operation_id","plan_operation_id"},exclude_defaults=True),user.username)
    except StoreReturnReceiveError as exc:
        raise HTTPException(exc.status,{"code":exc.code,"message":str(exc),"operation_id":body.operation_id,"outcome_confirmed":True}) from exc
    except StockPostingError as exc:
        confirmed = exc.oracle_code is not None and 20800<=exc.oracle_code<=20999
        raise HTTPException(403 if exc.oracle_code==20882 else 409 if confirmed else 503,{"code":exc.code,"message":exc.rule_reason or str(exc),"operation_id":body.operation_id,"outcome_confirmed":confirmed}) from exc

@router.post("/unload")
def unload(body: Unload,user: AdminUser=Depends(require_permission("interwarehouse_receive")),service: InterwarehousePort=Depends(interwarehouse_service)) -> dict[str,Any]:
    return physical("INTERWARE_UNLOAD",body,user,service)

@router.post("/receive")
def receive(body: Receive,user: AdminUser=Depends(require_permission("interwarehouse_receive")),service: InterwarehousePort=Depends(interwarehouse_service)) -> dict[str,Any]:
    return physical("INTERWARE_RECEIVE",body,user,service)

class PlacementPlan(BaseModel):
    model_config = ConfigDict(extra="forbid")
    operation_id: str = Field(strict=True,min_length=1,max_length=100,pattern=r"^[A-Za-z0-9_.:-]+$")
    receipt_operation_id: str = Field(strict=True,min_length=1,max_length=100)

@router.post("/placement")
def placement(body: PlacementPlan,user: AdminUser=Depends(require_permission("interwarehouse_receive")),service: InterwarehousePort=Depends(interwarehouse_service)) -> dict[str,Any]:
    from ..contracts_stock import StockPostingError
    try:
        return service.plan_placement(body.operation_id,body.receipt_operation_id,user.username)
    except StockPostingError as exc:
        confirmed = exc.oracle_code is not None and 20800<=exc.oracle_code<=20999
        raise HTTPException(403 if exc.oracle_code==20882 else 409 if confirmed else 503,{"code":exc.code,"message":exc.rule_reason or str(exc),"operation_id":body.operation_id,"outcome_confirmed":confirmed}) from exc

@router.post("/release-custody")
def release_custody(body: PlacementPlan,user: AdminUser=Depends(require_permission("interwarehouse_receive")),service: InterwarehousePort=Depends(interwarehouse_service)) -> dict[str,Any]:
    from ..contracts_stock import StockPostingError
    try:
        return service.release_custody(body.operation_id,body.receipt_operation_id,user.username)
    except StockPostingError as exc:
        confirmed = exc.oracle_code is not None and 20800<=exc.oracle_code<=20999
        raise HTTPException(403 if exc.oracle_code==20882 else 409 if confirmed else 503,{"code":exc.code,"message":exc.rule_reason or str(exc),"operation_id":body.operation_id,"outcome_confirmed":confirmed}) from exc

class OnwardPlan(PlacementPlan):
    accept_legacy_address: bool = Field(default=False,strict=True)
    reason: str = Field(strict=True,min_length=1,max_length=500)
    decision_reference: str = Field(strict=True,min_length=1,max_length=60)

@router.post("/prepare-onward")
def prepare_onward(body: OnwardPlan,user: AdminUser=Depends(require_permission("outgoing_pallet_edit")),service: InterwarehousePort=Depends(interwarehouse_service)) -> dict[str,Any]:
    try:
        return service.prepare_onward(body.operation_id,body.receipt_operation_id,body.reason,body.decision_reference,user.username,body.accept_legacy_address)
    except StoreReturnReceiveError as exc:
        raise HTTPException(exc.status,{"code":exc.code,"message":str(exc),"operation_id":body.operation_id,"outcome_confirmed":exc.status==409}) from exc

@router.get("/plans/{plan_id}/units")
def source_units(plan_id: str,user: AdminUser=Depends(require_permission("interwarehouse_receive")),service: InterwarehousePort=Depends(interwarehouse_service)) -> dict[str,Any]:
    try:
        return service.unit_manifest(plan_id,user.username)
    except StoreReturnReceiveError as exc:
        raise HTTPException(exc.status,{"code":exc.code,"message":str(exc)}) from exc


class DispatchDecision(BaseModel):
    model_config = ConfigDict(extra="forbid")
    operation_id: str = Field(strict=True,min_length=1,max_length=100,pattern=r"^[A-Za-z0-9_.:-]+$")
    plan_operation_id: str = Field(strict=True,min_length=1,max_length=100)
    decision_kind: Literal["WAIT","DEFER"]
    expected_revision: int = Field(strict=True,ge=0)
    expected_arrival: datetime
    target_trip_id: int | None = Field(default=None,strict=True,gt=0)
    ready_due: datetime | None = None
    reason: str = Field(strict=True,min_length=1,max_length=500)
    decision_reference: str = Field(strict=True,min_length=1,max_length=60)

    @model_validator(mode="after")
    def decision_contract(self) -> "DispatchDecision":
        if self.expected_arrival.utcoffset() is None:
            raise ValueError("Timezone-aware expected arrival required")
        if self.decision_kind == "WAIT":
            if self.target_trip_id is not None or self.ready_due is not None:
                raise ValueError("WAIT preserves the current trip and deadline")
        elif self.target_trip_id is None or self.ready_due is None or self.ready_due.utcoffset() is None or self.ready_due < self.expected_arrival:
            raise ValueError("DEFER requires existing trip and aware ready deadline after expected arrival")
        if not self.reason.strip() or not self.decision_reference.strip():
            raise ValueError("Reason and decision reference required")
        return self

@router.post("/decisions")
def dispatch_decision(body: DispatchDecision,user: AdminUser=Depends(require_permission("transport_dispatch_edit")),service: InterwarehousePort=Depends(interwarehouse_service)) -> dict[str,Any]:
    try:
        return service.record_decision(body.operation_id,body.model_dump(exclude={"operation_id"},exclude_none=True),user.username)
    except StoreReturnReceiveError as exc:
        raise HTTPException(exc.status,{"code":exc.code,"message":str(exc),"operation_id":body.operation_id,"outcome_confirmed":exc.status==409}) from exc

class ThermalDecision(BaseModel):
    model_config = ConfigDict(extra="forbid")
    operation_id: str = Field(strict=True,min_length=1,max_length=100,pattern=r"^[A-Za-z0-9_.:-]+$")
    plan_operation_id: str = Field(strict=True,min_length=1,max_length=100)
    decision_kind: Literal["HOLD","PROCEED"]
    expected_revision: int = Field(strict=True,ge=0)
    observed_c: Decimal = Field(ge=-100,le=100,max_digits=6,decimal_places=3)
    observation_reference: str = Field(strict=True,min_length=1,max_length=200)
    task_temp_min: Decimal | None = Field(default=None,ge=-100,le=100,max_digits=6,decimal_places=3)
    task_temp_max: Decimal | None = Field(default=None,ge=-100,le=100,max_digits=6,decimal_places=3)
    reason: str = Field(strict=True,min_length=1,max_length=500)
    decision_reference: str = Field(strict=True,min_length=1,max_length=60)

    @model_validator(mode="after")
    def thermal_contract(self) -> "ThermalDecision":
        if (self.task_temp_min is None)!=(self.task_temp_max is None) or self.task_temp_min is not None and self.task_temp_min>self.task_temp_max:
            raise ValueError("Both ordered task temperature limits required")
        if not self.observation_reference.strip() or not self.reason.strip() or not self.decision_reference.strip():
            raise ValueError("Observation and decision references required")
        return self

@router.post("/temperature-decisions")
def temperature_decision(body: ThermalDecision,user: AdminUser=Depends(require_permission("transport_dispatch_edit")),service: InterwarehousePort=Depends(interwarehouse_service)) -> dict[str,Any]:
    try:
        return service.record_temperature(body.operation_id,body.model_dump(mode="json",exclude={"operation_id"},exclude_none=True),user.username)
    except StoreReturnReceiveError as exc:
        raise HTTPException(exc.status,{"code":exc.code,"message":str(exc),"operation_id":body.operation_id,"outcome_confirmed":exc.status==409}) from exc


@router.get("/trips/{trip_id}/incoming")
def incoming(trip_id: int,user: AdminUser=Depends(require_permission("transport_dispatch_view")),service: InterwarehousePort=Depends(interwarehouse_service)) -> dict[str,Any]:
    try:
        return service.incoming(trip_id,user.username)
    except StoreReturnReceiveError as exc:
        raise HTTPException(exc.status,{"code":exc.code,"message":str(exc)}) from exc
