from datetime import date
from decimal import Decimal
"""Lot-specific inventory observations; the Oracle command owns all stock writes."""
from typing import Annotated, Any
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, ConfigDict, Field
from ....auth import AdminUser, require_permission
from ....oracle_gateway import OracleGateway
from ..contracts_stock import StockCommand, StockPostingError
from ..infrastructure.stock_posting_uow import StockPosting

router = APIRouter(prefix="/api/inventory/stock-posting", tags=["stock-posting"])
Identity = Annotated[str, Field(strict=True, min_length=1, max_length=200, pattern=r"^[^\x00]+$")]

class InventoryScan(BaseModel):
    model_config = ConfigDict(extra="forbid")
    system_code: str = Field(strict=True, min_length=1, max_length=40)
    profile_code: str = Field(strict=True, min_length=1, max_length=60)
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
    counts: list[CountLine] = Field(min_length=1, max_length=200)

@router.get("/inventory/{revision_id}/lots")
def inventory_lots(revision_id: int, cell: str, user: AdminUser = Depends(require_permission("stock_inventory_count"))) -> dict[str, Any]:
    if revision_id < 1 or not cell or len(cell) > 60:
        raise HTTPException(422, detail="Invalid revision or cell")
    gateway = OracleGateway()
    rows = gateway.fetch_all("""
        select r.UID_POLETA UID,p.ARTICUL ARTICLE,r.CELL,to_char(r.REMAIN,'TM9','NLS_NUMERIC_CHARACTERS=''.,''') PHYSICAL_QTY,
               to_char(r.HARD_RESERVED_BASE,'TM9','NLS_NUMERIC_CHARACTERS=''.,''') HARD_QTY,r.STOCK_VERSION,p.EXPIRY_DATE,
               r.BASE_UOM UNIT
          from RRL_REMAINS r join RRL_PALLETS p on p.UID_PALLET=r.UID_POLETA
         where r.CELL=:cell and exists(
           select 1 from RRL_REVIZION d join RRL_CELLS c on c.CELL=r.CELL
            where d.ID=:revision and d.WARE_ID=c.WARE_ID and d.CONDITION in (0,1))
         order by p.ARTICUL,p.EXPIRY_DATE,r.UID_POLETA fetch first 201 rows only
    """, {"cell": cell, "revision": revision_id})
    if len(rows) > 200:
        raise HTTPException(409, detail={"code": "INVENTORY_CELL_BATCH_BOUND"})
    articles = sorted({row["article"] for row in rows})
    if articles:
        params = {"article" + str(index): article for index, article in enumerate(articles)}
        profiles = gateway.fetch_all("select ARTICUL,SYSTEM_CODE,PROFILE_CODE from RRL_SKU_RECEIPT_PROFILE where ARTICUL in (" + ",".join(":" + key for key in params) + ") order by ARTICUL,SYSTEM_CODE,PROFILE_CODE", params)
        for row in rows:
            row["marking_profiles"] = [{"system_code": profile["system_code"], "profile_code": profile["profile_code"]} for profile in profiles if profile["articul"] == row["article"]]
    return {"revision_id": revision_id, "cell": cell, "lots": rows}

@router.post("/inventory/counts")
def inventory_count(request: CountRequest, user: AdminUser = Depends(require_permission("stock_inventory_count"))) -> dict[str, Any]:
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
        from ..infrastructure.inventory_scan_codes import resolve_count_codes
        gateway = OracleGateway()
        saved = gateway.fetch_all("select CANONICAL_REQUEST from RRL_STOCK_OPERATION where OPERATION_ID=:operation and ACTOR=:actor", {"operation": request.operation_id, "actor": user.username})
        if saved:
            payload = saved[0]["canonical_request"]
            payload = json.loads(payload.read() if hasattr(payload, "read") else payload)
            old = payload["metadata"]
            original = old.get("requested_counts", [{**line, "scans": []} for line in old.get("counts", [])])
            if payload["command_type"] != "INVENTORY_COUNT" or payload["source"] != {"revision_id": request.revision_id} or old.get("reason") != request.reason or original != requested:
                raise HTTPException(409, detail={"code": "OPERATION_CONTENT_CONFLICT", "operation_id": request.operation_id})
            metadata = old
        else:
            for index, keys in enumerate(resolve_count_codes(gateway, request.counts)):
                counts[index]["unit_keys"] = keys
            metadata = {"reason": request.reason, "counts": counts, "requested_counts": requested}
        return StockPosting().post(StockCommand(
            operation_id=request.operation_id, command_type="INVENTORY_COUNT", actor=user.username,
            source={"revision_id": request.revision_id}, lines=(),
            metadata=metadata,
        ))
    except ValueError as exc:
        raise HTTPException(422, detail={"code": "COMMAND_INVALID", "message": str(exc)}) from exc
    except StockPostingError as exc:
        status = 503 if exc.code in {"STOCK_RELEASE_NOT_ACTIVE", "REQUEST_DEADLINE", "LOCK_RETRY_EXHAUSTED", "CONNECTION_UNUSABLE"} else 409
        raise HTTPException(status, detail={"code": exc.code, "operation_id": exc.operation_id,
            "oracle_code": exc.oracle_code, "retry_same_operation_id": True,
            "outcome_confirmed": exc.code != "RESULT_UNCERTAIN"}) from exc


class RevisionRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    warehouse_id: int = Field(strict=True, ge=1)

@router.post("/inventory/revisions")
def create_inventory_revision(request: RevisionRequest, user: AdminUser = Depends(require_permission("stock_inventory_count"))) -> dict[str, Any]:
    gateway = OracleGateway()
    cells = gateway.fetch_all("select 1 PRESENT from RRL_CELLS where WARE_ID=:ware fetch first 1 row only", {"ware": request.warehouse_id})
    if not cells:
        raise HTTPException(422, detail={"code": "WAREHOUSE_HAS_NO_CELLS"})
    revision = gateway.call_number_plsql("begin :result:=REVIZION.create_revizion(:ware,:actor);end;", {"ware": request.warehouse_id, "actor": user.username})
    return {"revision_id": revision, "warehouse_id": request.warehouse_id}


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
    user: AdminUser=Depends(require_permission("stock_inventory_count"))) -> dict:
    from ..infrastructure.stock_posting_uow import StockPosting
    metadata=request.model_dump(mode="json",exclude={"operation_id","revision_id","capture"})
    if request.capture is not None:metadata["birth_captures"]={request.uid:request.capture}
    return StockPosting().post(StockCommand(operation_id=request.operation_id,
        command_type="INVENTORY_REGISTER_LOT",actor=user.username,lines=(),
        source={"revision_id":request.revision_id},metadata=metadata))
