from datetime import datetime
from typing import Any
from fastapi import APIRouter,Depends,HTTPException
from pydantic import BaseModel,ConfigDict,Field,model_validator
from ...platform.public import AdminUser,require_permission
from ..contracts_interwarehouse import InterwarehousePort,interwarehouse_service
from ..contracts_store_returns import StoreReturnReceiveError

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
def queue(ware_id: int,user: AdminUser=Depends(require_permission("transport_dispatch_view")),service: InterwarehousePort=Depends(interwarehouse_service)) -> list[dict[str,Any]]:
    try:
        return service.queue(ware_id,user.username)
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
    scan_cell: str = Field(strict=True,min_length=1,max_length=60)
    scan_article: str = Field(strict=True,min_length=1,max_length=128)
    article: str = Field(strict=True,min_length=1,max_length=160)
    quantity: str = Field(strict=True,min_length=1,max_length=40,pattern=r"^[0-9]+(\.[0-9]+)?$")
    base_uom: str = Field(strict=True,min_length=1,max_length=20)

def physical(kind: str,body: PhysicalAction,user: AdminUser,service: InterwarehousePort) -> dict[str,Any]:
    from ..contracts_stock import StockPostingError
    try:
        return service.receive_action(kind,body.operation_id,body.plan_operation_id,body.model_dump(exclude={"operation_id","plan_operation_id"}),user.username)
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
