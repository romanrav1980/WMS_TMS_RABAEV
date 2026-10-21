from decimal import Decimal
from typing import Literal, Protocol
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from ...platform.public import AdminUser, get_current_user, require_permission
from ..contracts_stock import StockPostingError


class WarehouseHuPort(Protocol):
    def preview(self, identifier: str, actor: str) -> dict: ...
    def target_slots(self, cell: str, warehouse: int, actor: str) -> list[dict]: ...
    def command(self, kind: str, uid: str, operation_id: str, metadata: dict, actor: str) -> dict: ...


router = APIRouter(prefix="/api/warehouse-hus", tags=["warehouse-hu"])


def warehouse_hu_service() -> WarehouseHuPort:
    raise RuntimeError("Warehouse HU service not wired")


class Command(BaseModel):
    operation_id: str = Field(min_length=1, max_length=100, pattern=r"^[A-Za-z0-9_.:-]+$")
    identifier: str = Field(min_length=1, max_length=200)


class Create(Command):
    cell: str = Field(min_length=1, max_length=60)
    warehouse: int = Field(ge=1)
    container_type: Literal["PALLET", "BOX", "ROLL_CAGE", "BAG"]
    tare_weight_kg: Decimal = Field(ge=0, max_digits=18, decimal_places=9)
    sscc: str | None = Field(default=None, pattern=r"^[0-9]{18}$")
    scan_container: str = Field(min_length=1, max_length=200)
    scan_cell: str = Field(min_length=1, max_length=60)


class Link(Command):
    child_uid: str = Field(min_length=1, max_length=200)
    expected_version: int = Field(ge=0)
    expected_child_version: int = Field(ge=0)
    scan_container: str = Field(min_length=1, max_length=200)
    scan_child: str = Field(min_length=1, max_length=200)
    reason: str | None = Field(default=None, max_length=1000)


class CaseLink(Command):
    retained_tare_booking_operation_id: str | None = Field(default=None, min_length=1, max_length=100)
    child_case_task_id: int = Field(ge=1)
    expected_version: int = Field(ge=0)
    expected_child_version: int = Field(ge=0)
    scan_container: str = Field(min_length=1, max_length=200)
    scan_child: str = Field(min_length=1, max_length=200)
    reason: str | None = Field(default=None, max_length=1000)


class Measurements(BaseModel):
    origin: Literal["MANUAL_CONFIRMED"]
    content_version: int = Field(ge=0)
    gross_weight_kg: Decimal = Field(gt=0, max_digits=18, decimal_places=9)
    width_m: Decimal = Field(gt=0, max_digits=18, decimal_places=9)
    depth_m: Decimal = Field(gt=0, max_digits=18, decimal_places=9)
    height_m: Decimal = Field(gt=0, max_digits=18, decimal_places=9)


class Move(Command):
    target_slot_id: int | None = Field(default=None, ge=1)
    scanned_to_slot_code: str | None = Field(default=None, min_length=1, max_length=100)
    measurements: Measurements | None = None
    target_cell: str = Field(min_length=1, max_length=60)
    expected_version: int = Field(ge=0)
    scan_container: str = Field(min_length=1, max_length=200)
    scanned_from_cell: str = Field(min_length=1, max_length=60)
    scanned_to_cell: str = Field(min_length=1, max_length=60)


def execute(service: WarehouseHuPort, kind: str, body: Command, actor: str) -> dict:
    try:
        metadata = body.model_dump(mode="json", exclude={"identifier", "operation_id"})
        # New optional fields must not alter canonical retries created before this extension.
        for field in ("target_slot_id", "scanned_to_slot_code", "measurements", "case_task_id", "retained_tare_booking_operation_id"):
            if metadata.get(field) is None:
                metadata.pop(field, None)
        return service.command(kind, body.identifier, body.operation_id, metadata, actor)
    except StockPostingError as exc:
        uncertain = exc.code in {"RESULT_UNCERTAIN", "REQUEST_DEADLINE", "CONNECTION_UNUSABLE", "LOCK_RETRY_EXHAUSTED"}
        unknown_outcome = uncertain or exc.oracle_code == 20882 or "OPERATION_CONFLICT" in (exc.rule_reason or "")
        raise HTTPException(403 if exc.oracle_code == 20882 else 503 if uncertain else 409, detail={
            "code": exc.code, "operation_id": exc.operation_id, "reason": exc.rule_reason, "oracle_code": exc.oracle_code,
            "outcome_confirmed": not unknown_outcome, "retry_same_operation_id": unknown_outcome}) from exc


@router.get("/composition")
def preview(identifier: str = Query(min_length=1, max_length=200),
            _user: AdminUser = Depends(get_current_user),
            service: WarehouseHuPort = Depends(warehouse_hu_service)) -> dict:
    return service.preview(identifier, _user.username)


@router.get("/target-slots")
def target_slots(cell: str = Query(min_length=1, max_length=60), warehouse: int = Query(ge=1),
                 _user: AdminUser = Depends(get_current_user),
                 service: WarehouseHuPort = Depends(warehouse_hu_service)) -> list[dict]:
    return service.target_slots(cell, warehouse, _user.username)


@router.post("/create")
def create(body: Create, user: AdminUser = Depends(get_current_user),
           service: WarehouseHuPort = Depends(warehouse_hu_service)) -> dict:
    return execute(service, "HU_CREATE", body, user.username)


@router.post("/attach")
def attach(body: Link, user: AdminUser = Depends(get_current_user),
           service: WarehouseHuPort = Depends(warehouse_hu_service)) -> dict:
    return execute(service, "HU_ATTACH", body, user.username)


@router.post("/detach")
def detach(body: Link, user: AdminUser = Depends(get_current_user),
           service: WarehouseHuPort = Depends(warehouse_hu_service)) -> dict:
    if not body.reason:
        raise HTTPException(422, "Укажите причину вскрытия")
    return execute(service, "HU_DETACH", body, user.username)


@router.post("/move")
def move(body: Move, user: AdminUser = Depends(get_current_user),
         service: WarehouseHuPort = Depends(warehouse_hu_service)) -> dict:
    return execute(service, "HU_MOVE", body, user.username)

@router.post("/plan-move")
def plan_move(body: Move, user: AdminUser = Depends(get_current_user),
              service: WarehouseHuPort = Depends(warehouse_hu_service)) -> dict:
    return execute(service, "HU_PLAN_MOVE", body, user.username)


@router.post("/attach-case")
def attach_case(body: CaseLink, user: AdminUser = Depends(get_current_user),
                service: WarehouseHuPort = Depends(warehouse_hu_service)) -> dict:
    return execute(service, "HU_ATTACH", body, user.username)


@router.post("/detach-case")
def detach_case(body: CaseLink, user: AdminUser = Depends(get_current_user),
                service: WarehouseHuPort = Depends(warehouse_hu_service)) -> dict:
    if not body.reason:
        raise HTTPException(422, "Укажите причину вскрытия")
    return execute(service, "HU_DETACH", body, user.username)


class Ship(Command):
    expected_version: int = Field(ge=0)
    scan_container: str = Field(min_length=1, max_length=200)
    scan_cell: str = Field(min_length=1, max_length=60)


@router.post("/ship")
def ship(body: Ship, user: AdminUser = Depends(get_current_user),
         service: WarehouseHuPort = Depends(warehouse_hu_service)) -> dict:
    return execute(service, "HU_SHIP", body, user.username)


class Unpack(Link):
    child_slot_id: int = Field(ge=1)
    scan_cell: str = Field(min_length=1,max_length=60)
    scan_parent_slot: str = Field(min_length=1,max_length=100)
    scan_child_slot: str = Field(min_length=1,max_length=100)
    parent_measurements: Measurements
    child_measurements: Measurements
    reason: str = Field(min_length=1,max_length=1000)


@router.post("/unpack")
def unpack(body: Unpack, user: AdminUser = Depends(get_current_user),
           service: WarehouseHuPort = Depends(warehouse_hu_service)) -> dict:
    return execute(service,"HU_UNPACK",body,user.username)


class RelocateSlot(Command):
    case_task_id: int | None = Field(default=None, ge=1)
    expected_version: int = Field(ge=0)
    target_slot_id: int = Field(ge=1)
    scan_container: str = Field(min_length=1,max_length=200)
    scan_cell: str = Field(min_length=1,max_length=60)
    scan_from_slot: str = Field(min_length=1,max_length=100)
    scan_to_slot: str = Field(min_length=1,max_length=100)
    measurements: Measurements
    reason: str = Field(min_length=1,max_length=1000)


@router.post("/relocate-slot")
def relocate_slot(body: RelocateSlot, user: AdminUser = Depends(get_current_user),
                  service: WarehouseHuPort = Depends(warehouse_hu_service)) -> dict:
    return execute(service,"HU_RELOCATE_SLOT",body,user.username)


class CaseUnpack(Command):
    child_case_task_id: int = Field(ge=1)
    expected_version: int = Field(ge=0)
    expected_child_version: int = Field(ge=0)
    scan_container: str = Field(min_length=1,max_length=200)
    scan_child: str = Field(min_length=1,max_length=200)
    child_slot_id: int = Field(ge=1)
    scan_cell: str = Field(min_length=1,max_length=60)
    scan_parent_slot: str = Field(min_length=1,max_length=100)
    scan_child_slot: str = Field(min_length=1,max_length=100)
    parent_measurements: Measurements
    child_measurements: Measurements
    reason: str = Field(min_length=1,max_length=1000)


@router.post("/unpack-case")
def unpack_case(body: CaseUnpack, user: AdminUser = Depends(get_current_user),
                service: WarehouseHuPort = Depends(warehouse_hu_service)) -> dict:
    return execute(service,"HU_UNPACK",body,user.username)
