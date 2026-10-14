from datetime import datetime
from decimal import Decimal
from typing import Any, Literal, Annotated
from fastapi import APIRouter,Depends,HTTPException,Query
from pydantic import BaseModel,ConfigDict,Field,model_validator
from ...platform.public import AdminUser,require_permission
from ..contracts_interwarehouse import InterwarehousePort,interwarehouse_service
from ..contracts_store_returns import StoreReturnReceiveError

from .task_scan_routes import UnitScan

router = APIRouter(prefix="/api/inventory/interwarehouse",tags=["interwarehouse"])

@router.get("/source-loads/{load_id}/group-composition")
def group_source(load_id: str,user: AdminUser=Depends(require_permission("transport_dispatch_edit")),service: InterwarehousePort=Depends(interwarehouse_service))->dict[str,Any]:
    try:
        return service.group_source(load_id,user.username)
    except StoreReturnReceiveError as exc:
        raise HTTPException(exc.status,{"code":exc.code,"message":str(exc)})from exc

@router.get("/group-warehouses/{ware_id}")
def group_queue(ware_id: int,limit: int=Query(default=200,ge=1,le=200),after_operation_id: str|None=Query(default=None,min_length=1,max_length=100),user: AdminUser=Depends(require_permission("transport_dispatch_view")),service: InterwarehousePort=Depends(interwarehouse_service))->list[dict[str,Any]]:
    try:return service.group_queue(ware_id,user.username,limit,after_operation_id)
    except StoreReturnReceiveError as exc:raise HTTPException(exc.status,{"code":exc.code,"message":str(exc)})from exc

@router.get("/group-plans/{plan_id}")
def group_detail(plan_id: str,user: AdminUser=Depends(require_permission("transport_dispatch_view")),service: InterwarehousePort=Depends(interwarehouse_service))->dict[str,Any]:
    try:return service.group_detail(plan_id,user.username)
    except StoreReturnReceiveError as exc:raise HTTPException(exc.status,{"code":exc.code,"message":str(exc)})from exc

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

class GroupPlan(Plan):
    expected_source_signature: str=Field(strict=True,min_length=64,max_length=64,pattern=r"^[0-9a-f]{64}$")

@router.get("/source-loads/{load_id}/group-proof")
def group_proof(load_id: str,user: AdminUser=Depends(require_permission("transport_dispatch_edit")),service: InterwarehousePort=Depends(interwarehouse_service))->dict[str,Any]:
    try:
        return service.group_source_proof(load_id,user.username)
    except StoreReturnReceiveError as exc:
        raise HTTPException(exc.status,{"code":exc.code,"message":str(exc)})from exc

@router.post("/group-plan")
def group_plan(body: GroupPlan,user: AdminUser=Depends(require_permission("transport_dispatch_edit")),service: InterwarehousePort=Depends(interwarehouse_service))->dict[str,Any]:
    try:
        return service.plan_group(body.operation_id,body.model_dump(exclude={"operation_id"}),user.username)
    except StoreReturnReceiveError as exc:
        raise HTTPException(exc.status,{"code":exc.code,"message":str(exc),"operation_id":body.operation_id,"outcome_confirmed":True})from exc

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

class AggregationScan(UnitScan):
    level: Literal['BOX','PALLET']

class Receive(PhysicalAction):
    scans: list[UnitScan] = Field(default_factory=list,max_length=20000)
    aggregation_scans: list[AggregationScan] = Field(default_factory=list,max_length=1000)
    scan_cell: str = Field(strict=True,min_length=1,max_length=60)
    scan_article: str = Field(strict=True,min_length=1,max_length=128)
    article: str = Field(strict=True,min_length=1,max_length=160)
    quantity: str = Field(strict=True,min_length=1,max_length=40,pattern=r"^[0-9]+(\.[0-9]+)?$")
    base_uom: str = Field(strict=True,min_length=1,max_length=20)
    partial_receipt: bool | None = Field(strict=True,default=None)
    unit_keys: list[str] | None = Field(default=None,max_length=10000)
    receipt_pallet_identifier: str | None = Field(strict=True,default=None,min_length=1,max_length=50)
    gross_weight_kg: str | None = Field(strict=True,default=None,pattern=r"^[0-9]{1,18}(\.[0-9]{1,9})?$")
    discrepancy_reason: str | None = Field(strict=True,default=None,min_length=8,max_length=1000)
    discrepancy_reference: str | None = Field(strict=True,default=None,min_length=1,max_length=255)

    @model_validator(mode="after")
    def partial_fields(self) -> "Receive":
        fields=(self.receipt_pallet_identifier,self.gross_weight_kg,self.discrepancy_reason,self.discrepancy_reference)
        if self.partial_receipt:
            if any(value is None for value in fields):
                raise ValueError("При частичной приёмке укажите новую паллету, вес, причину и документ расхождения")
        elif any(value is not None for value in fields):
            raise ValueError("Поля расхождения требуют явного режима частичной приёмки")
        return self


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

class GroupReceiveItem(BaseModel):
    model_config=ConfigDict(extra="forbid")
    uid: str=Field(strict=True,min_length=1,max_length=200)
    article: str=Field(strict=True,min_length=1,max_length=160)
    scan_article: str=Field(strict=True,min_length=1,max_length=128)
    quantity: str=Field(strict=True,pattern=r"^[0-9]+(\.[0-9]+)?$",max_length=40)
    base_uom: str=Field(strict=True,min_length=1,max_length=20)

class GroupReceive(PhysicalAction):
    aggregation_scans: list[AggregationScan]=Field(default_factory=list,max_length=1000)
    scan_cell: str=Field(strict=True,min_length=1,max_length=60)
    items: list[GroupReceiveItem]=Field(min_length=2,max_length=200)
    scans: list[UnitScan]=Field(default_factory=list,max_length=20000)

    @model_validator(mode="after")
    def distinct_items(self)->"GroupReceive":
        if len({item.uid for item in self.items})!=len(self.items):
            raise ValueError("Each stock leaf must occur once")
        return self

@router.post("/group-receive")
def group_receive(body: GroupReceive,user: AdminUser=Depends(require_permission("interwarehouse_receive")),service: InterwarehousePort=Depends(interwarehouse_service))->dict[str,Any]:
    return physical("INTERWARE_RECEIVE",body,user,service)

class PlacementPlan(BaseModel):
    model_config = ConfigDict(extra="forbid")
    operation_id: str = Field(strict=True,min_length=1,max_length=100,pattern=r"^[A-Za-z0-9_.:-]+$")
    receipt_operation_id: str = Field(strict=True,min_length=1,max_length=100)

class GroupMeasurements(BaseModel):
    model_config=ConfigDict(extra="forbid")
    origin: Literal["MANUAL_CONFIRMED"]
    content_version: int=Field(strict=True,ge=0)
    gross_weight_kg: Decimal=Field(gt=0,max_digits=18,decimal_places=9)
    width_m: Decimal=Field(gt=0,max_digits=18,decimal_places=9)
    depth_m: Decimal=Field(gt=0,max_digits=18,decimal_places=9)
    height_m: Decimal=Field(gt=0,max_digits=18,decimal_places=9)

class GroupPlacement(BaseModel):
    model_config=ConfigDict(extra="forbid")
    operation_id: str=Field(strict=True,min_length=1,max_length=100,pattern=r"^[A-Za-z0-9_.:-]+$")
    receipt_operation_id: str=Field(strict=True,min_length=1,max_length=100)
    expected_version: int=Field(strict=True,ge=0)
    scan_container: str=Field(strict=True,min_length=1,max_length=200)
    scanned_from_cell: str=Field(strict=True,min_length=1,max_length=60)
    scanned_to_cell: str=Field(strict=True,min_length=1,max_length=60)
    measurements: GroupMeasurements
    target_slot_id: int|None=Field(default=None,strict=True,gt=0)
    scanned_to_slot_code: str|None=Field(default=None,strict=True,min_length=1,max_length=100)

@router.post("/group-placement")
def group_placement(body: GroupPlacement,user: AdminUser=Depends(require_permission("warehouse_task_execute")),service: InterwarehousePort=Depends(interwarehouse_service))->dict[str,Any]:
    from ..contracts_stock import StockPostingError
    try:
        return service.plan_group_placement(body.operation_id,body.receipt_operation_id,body.model_dump(mode="json",exclude={"operation_id","receipt_operation_id"},exclude_none=True),user.username)
    except StoreReturnReceiveError as exc:
        raise HTTPException(exc.status,{"code":exc.code,"message":str(exc),"operation_id":body.operation_id,"outcome_confirmed":True})from exc
    except StockPostingError as exc:
        confirmed=exc.oracle_code is not None and 20800<=exc.oracle_code<=20999
        raise HTTPException(403 if exc.oracle_code==20882 else 409 if confirmed else 503,{"code":exc.code,"message":exc.rule_reason or str(exc),"operation_id":body.operation_id,"outcome_confirmed":confirmed})from exc

class GroupOnward(PlacementPlan):
    reason: str=Field(strict=True,min_length=1,max_length=500)
    decision_reference: str=Field(strict=True,min_length=1,max_length=60)

@router.post("/group-onward")
def group_onward(body: GroupOnward,user: AdminUser=Depends(require_permission("outgoing_pallet_edit")),service: InterwarehousePort=Depends(interwarehouse_service))->dict[str,Any]:
    try:return service.prepare_group_onward(body.operation_id,body.receipt_operation_id,body.reason,body.decision_reference,user.username)
    except StoreReturnReceiveError as exc:raise HTTPException(exc.status,{"code":exc.code,"message":str(exc),"operation_id":body.operation_id,"outcome_confirmed":True})from exc

class PlacementReplan(PlacementPlan):
    superseded_task_id: int | None = Field(default=None,strict=True,gt=0)
    replan_reason: str | None = Field(default=None,strict=True,min_length=1,max_length=500)

    @model_validator(mode="after")
    def replan_contract(self) -> "PlacementReplan":
        if (self.superseded_task_id is None)!=(self.replan_reason is None) or self.replan_reason is not None and not self.replan_reason.strip():
            raise ValueError("Original unstarted task and replan reason required together")
        return self

@router.post("/placement")
def placement(body: PlacementReplan,user: AdminUser=Depends(require_permission("interwarehouse_receive")),service: InterwarehousePort=Depends(interwarehouse_service)) -> dict[str,Any]:
    from ..contracts_stock import StockPostingError
    try:
        return service.plan_placement(body.operation_id,body.receipt_operation_id,user.username,body.superseded_task_id,body.replan_reason)
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

    incident_kind: Literal["TRANSPORT_DELAY","MISSING_PALLET","IDENTIFIER_MISMATCH"] | None = None
    incident_detail: str | None = Field(default=None,strict=True,min_length=1,max_length=1000)
    evidence_reference: str | None = Field(default=None,strict=True,min_length=1,max_length=200)

    @model_validator(mode="after")
    def decision_contract(self) -> "DispatchDecision":
        if self.incident_kind is None and (self.incident_detail is not None or self.evidence_reference is not None) or self.incident_kind is not None and (not self.incident_detail or not self.incident_detail.strip() or not self.evidence_reference or not self.evidence_reference.strip()):
            raise ValueError("Incident kind, detail and evidence reference required together")
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

@router.get("/plans/{plan_id}/decisions")
def decisions(plan_id: str,after_revision: int=Query(default=0,ge=0,le=9999999999),user: AdminUser=Depends(require_permission("transport_dispatch_view")),service: InterwarehousePort=Depends(interwarehouse_service)) -> dict[str,Any]:
    try:
        return service.decisions(plan_id,user.username,after_revision)
    except StoreReturnReceiveError as exc:
        raise HTTPException(exc.status,{"code":exc.code,"message":str(exc)}) from exc


class IncidentClosure(BaseModel):
    model_config=ConfigDict(extra="forbid")
    operation_id: str=Field(strict=True,min_length=1,max_length=100,pattern=r"^[A-Za-z0-9_.:-]+$")
    incident_operation_id: str=Field(strict=True,min_length=1,max_length=100)
    incident_revision: int=Field(strict=True,ge=1)
    followup_receipt_operation_id: str=Field(strict=True,min_length=1,max_length=100)
    reason: str=Field(strict=True,min_length=8,max_length=500)
    evidence_reference: str=Field(strict=True,min_length=1,max_length=255)

@router.post("/incident-closures")
def close_incident(body: IncidentClosure,user: AdminUser=Depends(require_permission("transport_dispatch_edit")),
                   service: InterwarehousePort=Depends(interwarehouse_service)) -> dict:
    try:return service.close_incident(body.operation_id,body.model_dump(exclude={"operation_id"}),user.username)
    except StoreReturnReceiveError as exc:raise HTTPException(exc.status,{"code":exc.code,"message":str(exc),"operation_id":body.operation_id,"outcome_confirmed":exc.status==409})from exc

@router.get("/receipts/{receipt_id}/shortage")
def shortage(receipt_id: str,selected_request: str|None=Query(default=None,min_length=1,max_length=100),user: AdminUser=Depends(require_permission("transport_dispatch_view")),
             service: InterwarehousePort=Depends(interwarehouse_service)) -> dict:
    if len(receipt_id)>100:raise HTTPException(422,"receipt identifier bound")
    try:return service.shortage(receipt_id,user.username,selected_request)
    except StoreReturnReceiveError as exc:raise HTTPException(exc.status,{"code":exc.code,"message":str(exc)})from exc

class ShortageEvidence(BaseModel):
    model_config=ConfigDict(extra="forbid")
    operation_id: str=Field(strict=True,min_length=1,max_length=100,pattern=r"^[A-Za-z0-9_.:-]+$")
    quantity: str=Field(strict=True,min_length=1,max_length=60)
    reason: str=Field(strict=True,min_length=8,max_length=500)
    evidence_reference: str=Field(strict=True,min_length=1,max_length=255)

class ShortageReport(ShortageEvidence):
    receipt_operation_id: str=Field(strict=True,min_length=1,max_length=100)

class ShortageConfirmation(ShortageEvidence):
    request_operation_id: str=Field(strict=True,min_length=1,max_length=100)

def post_shortage(kind: str,body: ShortageEvidence,source_id: str,user: AdminUser,service: InterwarehousePort) -> dict:
    from ..contracts_stock import StockPostingError
    try:
        action=service.recovery_action if kind.startswith("INTERWARE_RECOVERY_")else service.shortage_action
        return action(kind,body.operation_id,source_id,body.model_dump(include={"quantity","reason","evidence_reference","unit_keys"},exclude_defaults=True),user.username)
    except StockPostingError as exc:
        confirmed=exc.oracle_code is not None and 20800<=exc.oracle_code<=20999
        raise HTTPException(403 if exc.oracle_code==20882 else 409 if confirmed else 503,{"code":exc.code,"message":exc.rule_reason or str(exc),"operation_id":body.operation_id,"outcome_confirmed":confirmed})from exc

@router.post("/shortage-reports")
def report_shortage(body: ShortageReport,user: AdminUser=Depends(require_permission("transport_dispatch_edit")),
                    service: InterwarehousePort=Depends(interwarehouse_service)) -> dict:
    return post_shortage("INTERWARE_SHORTAGE_REPORT",body,body.receipt_operation_id,user,service)

@router.post("/shortage-confirmations")
def confirm_shortage(body: ShortageConfirmation,user: AdminUser=Depends(require_permission("store_return_approve")),
                    service: InterwarehousePort=Depends(interwarehouse_service)) -> dict:
    return post_shortage("INTERWARE_SHORTAGE_CONFIRM",body,body.request_operation_id,user,service)

class RecoveryReport(ShortageEvidence):
    unit_keys: list[Annotated[str,Field(strict=True,min_length=1,max_length=64)]]=Field(default_factory=list,max_length=10000)
    loss_operation_id: str=Field(strict=True,min_length=1,max_length=100)

@router.post("/recovery-reports")
def report_recovery(body: RecoveryReport,user: AdminUser=Depends(require_permission("transport_dispatch_edit")),
                    service: InterwarehousePort=Depends(interwarehouse_service)) -> dict:
    return post_shortage("INTERWARE_RECOVERY_REPORT",body,body.loss_operation_id,user,service)

@router.post("/recovery-approvals")
def approve_recovery(body: ShortageConfirmation,user: AdminUser=Depends(require_permission("store_return_approve")),
                     service: InterwarehousePort=Depends(interwarehouse_service)) -> dict:
    return post_shortage("INTERWARE_RECOVERY_APPROVE",body,body.request_operation_id,user,service)

class RecoveryReceipt(BaseModel):
    model_config=ConfigDict(extra="forbid")
    operation_id: str=Field(strict=True,min_length=1,max_length=100,pattern=r"^[A-Za-z0-9_.:-]+$")
    approval_operation_id: str=Field(strict=True,min_length=1,max_length=100)
    receipt_pallet_identifier: str=Field(strict=True,min_length=1,max_length=50)
    quantity: str=Field(strict=True,min_length=1,max_length=60)
    gross_weight_kg: str=Field(strict=True,min_length=1,max_length=60)
    scan_source_pallet: str=Field(strict=True,min_length=1,max_length=200)
    scan_pallet: str=Field(strict=True,min_length=1,max_length=200)
    scan_cell: str=Field(strict=True,min_length=1,max_length=60)
    scan_article: str=Field(strict=True,min_length=1,max_length=160)
    article: str=Field(strict=True,min_length=1,max_length=160)
    base_uom: str=Field(strict=True,min_length=1,max_length=20)
    discrepancy_reason: str=Field(strict=True,min_length=8,max_length=1000)
    discrepancy_reference: str=Field(strict=True,min_length=1,max_length=255)
    scans: list[UnitScan]=Field(default_factory=list,max_length=20000)
    aggregation_scans: list[AggregationScan]=Field(default_factory=list,max_length=1000)

@router.post("/recovery-receipts")
def receive_recovery(body: RecoveryReceipt,user: AdminUser=Depends(require_permission("interwarehouse_receive")),
                     service: InterwarehousePort=Depends(interwarehouse_service)) -> dict:
    from ..contracts_stock import StockPostingError
    try:return service.receive_recovery(body.operation_id,body.approval_operation_id,body.model_dump(exclude={"operation_id","approval_operation_id"},exclude_defaults=True),user.username)
    except ValueError as exc:raise HTTPException(422,str(exc))from exc
    except StockPostingError as exc:
        confirmed=exc.oracle_code is not None and 20800<=exc.oracle_code<=20999
        raise HTTPException(403 if exc.oracle_code==20882 else 409 if confirmed else 503,{"code":exc.code,"message":exc.rule_reason or str(exc),"operation_id":body.operation_id,"outcome_confirmed":confirmed})from exc

class RecoveryPlacement(BaseModel):
    model_config=ConfigDict(extra="forbid")
    operation_id: str=Field(strict=True,min_length=1,max_length=100,pattern=r"^[A-Za-z0-9_.:-]+$")
    recovery_operation_id: str=Field(strict=True,min_length=1,max_length=100)

@router.post("/recovery-placement")
def recovery_placement(body: RecoveryPlacement,user: AdminUser=Depends(require_permission("interwarehouse_receive")),
                       service: InterwarehousePort=Depends(interwarehouse_service)) -> dict:
    from ..contracts_stock import StockPostingError
    try:return service.plan_recovery_placement(body.operation_id,body.recovery_operation_id,user.username)
    except StockPostingError as exc:
        confirmed=exc.oracle_code is not None and 20800<=exc.oracle_code<=20999
        raise HTTPException(403 if exc.oracle_code==20882 else 409 if confirmed else 503,{"code":exc.code,"message":exc.rule_reason or str(exc),"operation_id":body.operation_id,"outcome_confirmed":confirmed})from exc

class RecoveryOnward(RecoveryPlacement):
    target_trip_id: int=Field(strict=True,gt=0)
    reason: str=Field(strict=True,min_length=1,max_length=500)
    decision_reference: str=Field(strict=True,min_length=1,max_length=255)

@router.post("/prepare-recovery-onward")
def prepare_recovery_onward(body: RecoveryOnward,user: AdminUser=Depends(require_permission("transport_dispatch_edit")),
                            service: InterwarehousePort=Depends(interwarehouse_service)) -> dict:
    try:return service.prepare_recovery_onward(body.operation_id,body.recovery_operation_id,body.target_trip_id,body.reason,body.decision_reference,user.username)
    except StoreReturnReceiveError as exc:raise HTTPException(exc.status,{"code":exc.code,"message":str(exc)})from exc

@router.post("/recovery-cancellations")
def cancel_recovery(body: ShortageConfirmation,user: AdminUser=Depends(require_permission("store_return_approve")),
                    service: InterwarehousePort=Depends(interwarehouse_service)) -> dict:
    return post_shortage("INTERWARE_RECOVERY_CANCEL",body,body.request_operation_id,user,service)
