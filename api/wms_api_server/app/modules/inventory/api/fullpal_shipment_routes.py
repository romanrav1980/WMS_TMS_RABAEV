from typing import Protocol
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from ...platform.public import AdminUser, require_permission, get_current_user
from ..contracts_stock import StockPostingError


class FullPalletPort(Protocol):
    def preview(self, task_id: int, actor: str | None = None) -> dict: ...
    def bind(self, task_id: int, body: dict, actor: str) -> dict: ...


router = APIRouter(prefix="/api/warehouse-tasks", tags=["full-pallet-shipment"])


def fullpal_shipment_service() -> FullPalletPort:
    raise RuntimeError("Full-pallet shipment service not wired")


class FullPalletBindingRequest(BaseModel):
    operation_id: str = Field(min_length=1, max_length=100, pattern=r"^[A-Za-z0-9_.:-]+$")
    shipment_identifier: str = Field(min_length=1, max_length=150)
    scanned_pallet: str = Field(min_length=1, max_length=150)
    expected_stock_version: int = Field(ge=0, strict=True)


@router.get("/{task_id}/full-pallet-shipment")
def preview(task_id: int, _user: AdminUser = Depends(get_current_user),
            service: FullPalletPort = Depends(fullpal_shipment_service)) -> dict:
    if task_id < 1:
        raise HTTPException(422, "Positive task ID required")
    try:
        return service.preview(task_id, _user.username)
    except ValueError as exc:
        raise HTTPException(409, str(exc)) from exc
    except StockPostingError as exc:
        raise HTTPException(403 if exc.oracle_code == 20882 else 409, detail={"code": exc.code}) from exc


@router.post("/{task_id}/full-pallet-shipment")
def bind(task_id: int, body: FullPalletBindingRequest,
         user: AdminUser = Depends(get_current_user),
         service: FullPalletPort = Depends(fullpal_shipment_service)) -> dict:
    if task_id < 1:
        raise HTTPException(422, "Positive task ID required")
    try:
        return service.bind(task_id, body.model_dump(mode="json"), user.username)
    except StockPostingError as exc:
        uncertain = exc.code in {"RESULT_UNCERTAIN","REQUEST_DEADLINE","CONNECTION_UNUSABLE","LOCK_RETRY_EXHAUSTED"}
        raise HTTPException(503 if uncertain else 409, detail={
            "code":exc.code,"message":exc.rule_reason,"operation_id":exc.operation_id,"outcome_confirmed":not uncertain,
            "retry_same_operation_id":uncertain,
        }) from exc
