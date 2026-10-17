from typing import Protocol
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from ...platform.public import AdminUser, require_permission, get_current_user
from ..contracts_stock import StockPostingError


class WavePickPort(Protocol):
    def preview(self, wave_id: int, actor: str) -> dict: ...
    def release(self, wave_id: int, operation_id: str, actor: str) -> dict: ...


router = APIRouter(prefix="/api/picking/waves", tags=["wave-pick-admission"])


def wave_pick_service() -> WavePickPort:
    raise RuntimeError("Wave picking service not wired")


class PickReleaseRequest(BaseModel):
    operation_id: str = Field(min_length=1, max_length=100, pattern=r"^[A-Za-z0-9_.:-]+$")


@router.get("/{wave_id}/pick-readiness")
def preview(wave_id: int, user: AdminUser = Depends(get_current_user),
            service: WavePickPort = Depends(wave_pick_service)) -> dict:
    if wave_id < 1:
        raise HTTPException(422, "Positive wave ID required")
    return service.preview(wave_id, user.username)


@router.post("/{wave_id}/release-picking")
def release(wave_id: int, body: PickReleaseRequest,
            user: AdminUser = Depends(require_permission("pick_wave_launch")),
            service: WavePickPort = Depends(wave_pick_service)) -> dict:
    if wave_id < 1:
        raise HTTPException(422, "Positive wave ID required")
    try:
        return service.release(wave_id, body.operation_id, user.username)
    except StockPostingError as exc:
        uncertain = exc.code in {"RESULT_UNCERTAIN", "REQUEST_DEADLINE", "CONNECTION_UNUSABLE", "LOCK_RETRY_EXHAUSTED"}
        raise HTTPException(503 if uncertain else 403 if exc.oracle_code == 20882 else 409, detail={
            "code": exc.code, "operation_id": exc.operation_id, "reason": exc.rule_reason,
            "outcome_confirmed": not uncertain, "retry_same_operation_id": uncertain,
        }) from exc
