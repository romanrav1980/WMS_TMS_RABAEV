from typing import Any
from fastapi import APIRouter, Depends, HTTPException, Path
from pydantic import BaseModel, ConfigDict, Field
from ...platform.public import AdminUser, require_permission
from ...inventory.public import StockPostingError
from ..contracts_prepared_layout import PreparedLayoutPort, prepared_layout_service

router = APIRouter(prefix="/api/customer-orders", tags=["existing-prepared-st-layout"])


class LayoutPreview(BaseModel):
    model_config = ConfigDict(extra="forbid")
    row_id: int = Field(strict=True, ge=1)
    target_shipment_id: int = Field(strict=True, ge=1)


class LayoutMove(LayoutPreview):
    operation_id: str = Field(strict=True, min_length=1, max_length=100, pattern=r"^[A-Za-z0-9_.:-]+$")
    expected_signature: str = Field(strict=True, pattern=r"^[A-F0-9]{64}$")
    reason: str = Field(strict=True, min_length=1, max_length=500, pattern=r"\S")


def failure(exc: StockPostingError) -> HTTPException:
    uncertain = exc.code in {"RESULT_UNCERTAIN", "REQUEST_DEADLINE", "LOCK_RETRY_EXHAUSTED", "CONNECTION_UNUSABLE"}
    return HTTPException(503 if uncertain else 403 if exc.oracle_code == 20882 else 409,
        {"code": exc.code, "message": exc.rule_reason or str(exc), "operation_id": exc.operation_id,
         "outcome_confirmed": not uncertain, "retry_same_operation_id": uncertain})


@router.get("/{order_id}/prepared-layout")
def read(order_id: int = Path(ge=1), user: AdminUser = Depends(require_permission("customer_order_view")),
         service: PreparedLayoutPort = Depends(prepared_layout_service)) -> dict[str, Any]:
    try:
        return service.read(order_id, user.username)
    except StockPostingError as exc:
        raise failure(exc) from exc


@router.post("/{order_id}/prepared-layout/preview")
def preview(body: LayoutPreview, order_id: int = Path(ge=1),
            user: AdminUser = Depends(require_permission("customer_order_view")),
            service: PreparedLayoutPort = Depends(prepared_layout_service)) -> dict[str, Any]:
    try:
        return service.preview(order_id, body.row_id, body.target_shipment_id, user.username)
    except StockPostingError as exc:
        raise failure(exc) from exc


@router.post("/{order_id}/prepared-layout/move-row")
def move(body: LayoutMove, order_id: int = Path(ge=1),
         user: AdminUser = Depends(require_permission("outgoing_pallet_edit")),
         service: PreparedLayoutPort = Depends(prepared_layout_service)) -> dict[str, Any]:
    try:
        return service.move(order_id, body.model_dump(), user.username)
    except StockPostingError as exc:
        raise failure(exc) from exc
