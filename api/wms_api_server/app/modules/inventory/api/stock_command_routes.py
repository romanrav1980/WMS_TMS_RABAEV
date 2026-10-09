"""Explicit bounded command; stays unavailable while Oracle release is PREPARED."""
from typing import Annotated, Any
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, ConfigDict, Field
from ....auth import AdminUser, require_permission
from ..application.stock_commands import ManualStockMove, ReceiptReverse
from ..contracts_stock import StockLine, StockPostingError

router = APIRouter(prefix="/api/inventory/stock-posting", tags=["stock-posting"])
Identifier = Annotated[str, Field(strict=True, min_length=1, max_length=200, pattern=r"^[^\x00]+$")]
Cell = Annotated[str, Field(strict=True, min_length=1, max_length=60, pattern=r"^[^\x00]+$")]


class ManualMoveLine(BaseModel):
    model_config = ConfigDict(extra="forbid")
    line_number: int = Field(strict=True, ge=1)
    uid: Identifier
    article: str = Field(strict=True, min_length=1, max_length=160)
    quantity: str = Field(strict=True, min_length=1, max_length=28, pattern=r"^[0-9]{1,18}(\.[0-9]{1,9})?$")
    unit: str = Field(strict=True, min_length=1, max_length=20)
    source_cell: Cell
    target_cell: Cell
    expected_stock_version: int | None = Field(default=None, strict=True, ge=0)


class ManualMoveRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    operation_id: str = Field(strict=True, min_length=1, max_length=100)
    warehouse_id: int = Field(strict=True, ge=1)
    reason: str = Field(strict=True, min_length=1, max_length=1000)
    lines: list[ManualMoveLine] = Field(min_length=1, max_length=200)


def manual_stock_move_service() -> ManualStockMove:
    raise RuntimeError("Manual stock command service not wired")


@router.post("/manual-moves")
def manual_move(
    request: ManualMoveRequest,
    user: AdminUser = Depends(require_permission("stock_posting_manual_move")),
    service: ManualStockMove = Depends(manual_stock_move_service),
) -> dict[str, Any]:
    try:
        return service.execute(
            request.operation_id, user.username, request.warehouse_id, request.reason,
            tuple(StockLine(**line.model_dump()) for line in request.lines),
        )
    except ValueError as exc:
        raise HTTPException(422, detail={"code": "COMMAND_INVALID", "message": str(exc)}) from exc
    except StockPostingError as exc:
        status = 503 if exc.code in {"STOCK_RELEASE_NOT_ACTIVE", "REQUEST_DEADLINE",
                                    "LOCK_RETRY_EXHAUSTED", "CONNECTION_UNUSABLE"} else 409
        detail = {"code": exc.code, "operation_id": exc.operation_id}
        if exc.oracle_code is not None:
            detail["oracle_code"] = exc.oracle_code
        if exc.code == "RESULT_UNCERTAIN":
            detail["outcome_confirmed"] = False
            detail["retry_same_operation_id"] = True
        raise HTTPException(status, detail=detail) from exc


class CompatibilitySettingRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    enabled: bool = Field(strict=True)
    reason: str = Field(strict=True, min_length=1, max_length=1000)


@router.post("/compatibility-setting")
def set_compatibility(
    request: CompatibilitySettingRequest,
    user: AdminUser = Depends(require_permission("stock_compatibility_admin")),
) -> dict[str, Any]:
    from ....oracle_gateway import OracleGateway
    gateway = OracleGateway()
    gateway.execute(
        "begin RRL_STOCK_SETTING_API.set_compatibility(:value,:reason,:actor); end;",
        {"value": "1" if request.enabled else "0", "reason": request.reason, "actor": user.username},
    )
    return {"enabled": request.enabled, "scope": "DATABASE"}


@router.post("/compatibility/manual-moves")
def compatibility_manual_move(
    request: ManualMoveRequest,
    user: AdminUser = Depends(require_permission("stock_posting_manual_move")),
    service: ManualStockMove = Depends(manual_stock_move_service),
) -> dict[str, Any]:
    try:
        return service.execute(
            request.operation_id, user.username, request.warehouse_id, request.reason,
            tuple(StockLine(**line.model_dump()) for line in request.lines), compatibility=True)
    except ValueError as exc:
        raise HTTPException(422, detail={"code": "COMMAND_INVALID", "message": str(exc)}) from exc
    except StockPostingError as exc:
        raise HTTPException(409, detail={"code": exc.code, "operation_id": exc.operation_id,
                                       "oracle_code": exc.oracle_code}) from exc


def receipt_reverse_service() -> ReceiptReverse:
    raise RuntimeError("Receipt reversal service not wired")


class ReceiptReverseRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    operation_id: str = Field(strict=True, min_length=1, max_length=100)
    reason: str = Field(strict=True, min_length=1, max_length=1000)


@router.post("/receipt-documents/{document_id}/reverse")
def reverse_receipt(
    document_id: int,
    request: ReceiptReverseRequest,
    user: AdminUser = Depends(require_permission("stock_receipt_reverse")),
    service: ReceiptReverse = Depends(receipt_reverse_service),
) -> dict[str, Any]:
    if document_id < 1:
        raise HTTPException(422, detail="Positive receipt document ID required")
    try:
        return service.execute(request.operation_id, user.username, document_id, request.reason)
    except ValueError as exc:
        raise HTTPException(422, detail={"code": "COMMAND_INVALID", "message": str(exc)}) from exc
    except StockPostingError as exc:
        uncertain = exc.code in {"RESULT_UNCERTAIN", "REQUEST_DEADLINE",
            "CONNECTION_UNUSABLE", "LOCK_RETRY_EXHAUSTED", "STOCK_RELEASE_NOT_ACTIVE"}
        raise HTTPException(503 if uncertain else 409, detail={
            "code": exc.code, "operation_id": exc.operation_id,
            "oracle_code": exc.oracle_code, "outcome_confirmed": not uncertain,
            "retry_same_operation_id": uncertain,
        }) from exc