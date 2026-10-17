from ...master_data.contracts import MarkingProfileCode
from datetime import date
from decimal import Decimal
"""Lot-specific inventory observations; the Oracle command owns all stock writes."""
from typing import Annotated, Any
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, ConfigDict, Field
from ...platform.public import AdminUser, get_current_user, require_permission
from ..contracts_stock import StockPostingError

from ..contracts_observations import (CountSubmission, InventoryObservationsPort, InventoryObservationError, inventory_observations_service)

router = APIRouter(prefix="/api/inventory/stock-posting", tags=["stock-posting"])
Identity = Annotated[str, Field(strict=True, min_length=1, max_length=200, pattern=r"^[^\x00]+$")]

class InventoryScan(BaseModel):
    model_config = ConfigDict(extra="forbid")
    system_code: str = Field(strict=True, min_length=1, max_length=40)
    profile_code: MarkingProfileCode
    code: str = Field(strict=True, min_length=1, max_length=4000)

class CountLine(BaseModel):
    model_config = ConfigDict(extra="forbid")
    uid: Identity
    cell: str = Field(strict=True, min_length=1, max_length=60, pattern=r"^[^\x00]+$")
    article: str = Field(strict=True, min_length=1, max_length=160)
    unit: str = Field(strict=True, min_length=1, max_length=20)
    quantity: str = Field(strict=True, pattern=r"^[0-9]{1,18}(\.[0-9]{1,9})?$", max_length=28)
    expected_stock_version: int = Field(strict=True, ge=0)
    scans: list[InventoryScan] = Field(default_factory=list, max_length=10000)
    unit_keys: list[Identity] = Field(default_factory=list, max_length=10000)

class CountRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    operation_id: str = Field(strict=True, min_length=1, max_length=100)
    revision_id: int = Field(strict=True, ge=1)
    reason: str = Field(strict=True, min_length=1, max_length=1000)
    inventory_task_id: int | None = Field(default=None, strict=True, ge=1)
    counts: list[CountLine] = Field(min_length=0, max_length=200)

@router.get("/inventory/{revision_id}/lots")
def inventory_lots(revision_id: int, cell: str, article: str | None = None, inventory_task_id: Annotated[int | None, Query(gt=0)] = None, user: AdminUser = Depends(get_current_user), service: InventoryObservationsPort = Depends(inventory_observations_service)) -> dict[str, Any]:
    if revision_id < 1 or not cell or len(cell) > 60 or (article is not None and (not article or len(article)>160)):
        raise HTTPException(422, detail="Invalid revision or cell")
    try:
        if inventory_task_id is not None:
            return service.lots(revision_id,cell,article,user.username,task_id=inventory_task_id)
        return service.lots(revision_id,cell,article,user.username)
    except InventoryObservationError as exc:
        raise HTTPException(exc.status,detail={"code":exc.code}) from exc

@router.post("/inventory/counts")
def inventory_count(request: CountRequest, user: AdminUser = Depends(get_current_user), service: InventoryObservationsPort = Depends(inventory_observations_service)) -> dict[str, Any]:
    if not request.counts and request.inventory_task_id is None:
        raise HTTPException(422, detail={"code": "INVENTORY_COUNT_BATCH_REQUIRED"})
    counts = [line.model_dump(exclude={"scans"}) for line in request.counts]
    requested = [line.model_dump() for line in request.counts]
    if len({(line.uid, line.cell) for line in request.counts}) != len(counts):
        raise HTTPException(422, detail={"code": "INVENTORY_LOT_REPEATED"})
    if any(len(set(line.unit_keys)) != len(line.unit_keys) for line in request.counts):
        raise HTTPException(422, detail={"code": "INVENTORY_UNIT_REPEATED"})
    if sum(len(line.scans) + len(line.unit_keys) for line in request.counts) > 10000:
        raise HTTPException(422, detail={"code": "INVENTORY_UNIT_BATCH_BOUND"})
    try:
        import json
        if len(json.dumps(requested, ensure_ascii=True).encode()) > 2 * 1024 * 1024:
            raise ValueError("Inventory scans exceed 2 MiB")
        return service.count(CountSubmission.from_wire(request.model_dump()),user.username)
    except InventoryObservationError as exc:
        raise HTTPException(exc.status,detail={"code":exc.code,"operation_id":exc.operation_id}) from exc
    except ValueError as exc:
        raise HTTPException(422, detail={"code": "COMMAND_INVALID", "message": str(exc)}) from exc
    except StockPostingError as exc:
        status = 403 if exc.oracle_code == 20882 else 503 if exc.code in {"STOCK_RELEASE_NOT_ACTIVE", "REQUEST_DEADLINE", "LOCK_RETRY_EXHAUSTED", "CONNECTION_UNUSABLE", "RESULT_UNCERTAIN"} else 409
        raise HTTPException(status, detail={"code": exc.code, "operation_id": exc.operation_id,
            "oracle_code": exc.oracle_code, "retry_same_operation_id": True,
            "outcome_confirmed": exc.code != "RESULT_UNCERTAIN"}) from exc


class RevisionRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    warehouse_id: int = Field(strict=True, ge=1)

@router.post("/inventory/revisions")
def create_inventory_revision(request: RevisionRequest, user: AdminUser = Depends(require_permission("stock_inventory_count")), service: InventoryObservationsPort = Depends(inventory_observations_service)) -> dict[str, Any]:
    try:
        return service.create_revision(request.warehouse_id,user.username)
    except InventoryObservationError as exc:
        raise HTTPException(exc.status,detail={"code":exc.code}) from exc



class InventoryLotBirthRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    operation_id: str = Field(min_length=1,max_length=100)
    revision_id: int = Field(strict=True,ge=1)
    uid: str = Field(min_length=1,max_length=150)
    cell: str = Field(min_length=1,max_length=60)
    article: str = Field(min_length=1,max_length=160)
    quantity: Decimal = Field(gt=0,max_digits=27,decimal_places=9,allow_inf_nan=False)
    expiry_date: date
    price: Decimal = Field(ge=0,max_digits=27,decimal_places=9,allow_inf_nan=False)
    reason: str = Field(min_length=1,max_length=1000)
    capture: dict[str, Any] | None = None


@router.post("/inventory/lots")
def register_inventory_lot(request: InventoryLotBirthRequest,
    user: AdminUser=Depends(require_permission("stock_inventory_count")),
    service: InventoryObservationsPort=Depends(inventory_observations_service)) -> dict[str, Any]:
    metadata=request.model_dump(mode="json",exclude={"operation_id","revision_id","capture"})
    if request.capture is not None:metadata["birth_captures"]={request.uid:request.capture}
    try:
        return service.register_lot(request.operation_id,request.revision_id,metadata,user.username)
    except InventoryObservationError as exc:
        raise HTTPException(exc.status,detail={"code":exc.code,"operation_id":exc.operation_id,"outcome_confirmed":exc.status in {409,422}}) from exc
