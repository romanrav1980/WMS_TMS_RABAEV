from typing import Protocol, Literal
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field, ConfigDict, model_validator
from ...platform.public import AdminUser, require_permission, get_current_user
from ..contracts_stock import StockPostingError


class WaveExecutionPort(Protocol):
    def preview(self, wave_id: int, actor: str) -> dict: ...
    def finish(self, wave_id: int, operation_id: str, actor: str, disposition: str | None = None, reason: str | None = None) -> dict: ...


router = APIRouter(prefix="/api/picking/waves", tags=["wave-execution"])


def wave_execution_service() -> WaveExecutionPort:
    raise RuntimeError("Wave execution service not wired")


class FinishRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    disposition: Literal["RETURNED_TO_PLANNING", "PARTIAL_SHIPPED_RETURNED"] | None = None
    reason: str | None = Field(default=None, min_length=1, max_length=1000)

    @model_validator(mode="after")
    def require_reason(self) -> "FinishRequest":
        if self.disposition and not (self.reason or "").strip():
            raise ValueError("Reason required for returned demand")
        return self

    operation_id: str = Field(min_length=1, max_length=100, pattern=r"^[A-Za-z0-9_.:-]+$")


@router.get("/{wave_id}/execution")
def preview(wave_id: int, user: AdminUser = Depends(get_current_user),
            service: WaveExecutionPort = Depends(wave_execution_service)) -> dict:
    if wave_id < 1:
        raise HTTPException(422, "Positive wave ID required")
    return service.preview(wave_id, user.username)


@router.post("/{wave_id}/finish-execution")
def finish(wave_id: int, body: FinishRequest,
           user: AdminUser = Depends(require_permission("pick_wave_launch")),
           service: WaveExecutionPort = Depends(wave_execution_service)) -> dict:
    if wave_id < 1:
        raise HTTPException(422, "Positive wave ID required")
    try:
        return service.finish(wave_id, body.operation_id, user.username, body.disposition, body.reason)
    except StockPostingError as exc:
        uncertain = exc.code in {"RESULT_UNCERTAIN", "REQUEST_DEADLINE", "CONNECTION_UNUSABLE", "LOCK_RETRY_EXHAUSTED"}
        raise HTTPException(503 if uncertain else 403 if exc.oracle_code == 20882 else 409, detail={
            "code": exc.code, "operation_id": exc.operation_id, "reason": exc.rule_reason,
            "outcome_confirmed": not uncertain, "retry_same_operation_id": uncertain}) from exc
