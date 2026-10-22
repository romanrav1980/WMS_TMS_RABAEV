"""TRADECASE quality exceptions: quarantine move, controller decision, approval and the native write-off posting of an approved case."""
from typing import Any, Literal, Protocol
from pydantic import BaseModel, ConfigDict, Field, model_validator

Operation = Field(min_length=8, max_length=100, pattern=r"^[A-Za-z0-9_.:-]+$")
Note = Field(min_length=3, max_length=1000)


class QuarantineMove(BaseModel):
    """Existing native MOVE_QUARANTINE: the whole pallet into or out of a quarantine cell."""
    model_config = ConfigDict(extra="forbid")
    operation_id: str = Operation
    pallet_uid: str = Field(min_length=1, max_length=200)
    target_cell: str = Field(min_length=1, max_length=60)
    reason: str = Note


class QualityCaseCommand(BaseModel):
    model_config = ConfigDict(extra="forbid")
    operation_id: str = Operation
    action: Literal["OPEN", "DECIDE", "APPROVE"]
    pallet_uid: str | None = Field(default=None, min_length=1, max_length=200)
    reason: str | None = Field(default=None, min_length=3, max_length=1000)
    case_id: int | None = Field(default=None, strict=True, gt=0)
    expected_version: int | None = Field(default=None, strict=True, gt=0)
    decision: Literal["DEFECT", "RELEASED"] | None = None
    note: str | None = Field(default=None, min_length=3, max_length=1000)

    @model_validator(mode="after")
    def arguments(self) -> "QualityCaseCommand":
        opening = (self.pallet_uid, self.reason)
        changing = (self.case_id, self.expected_version, self.note)
        if self.action == "OPEN":
            ok = all(v is not None for v in opening) and all(v is None for v in (*changing, self.decision))
        else:
            ok = all(v is not None for v in changing) and all(v is None for v in opening) and (self.action == "DECIDE") == (self.decision is not None)
        if not ok:
            raise ValueError("OPEN names pallet and reason; DECIDE/APPROVE name case, version and note; only DECIDE has a decision")
        return self


class QualityWriteOff(BaseModel):
    """Posting of an approved case (WAITING_POSTING): the native TRADE_QUALITY_WRITE_OFF writes the stock off in one transaction."""
    model_config = ConfigDict(extra="forbid")
    operation_id: str = Operation
    case_id: int = Field(strict=True, gt=0)
    expected_version: int = Field(strict=True, gt=0)


class QualityCaseError(RuntimeError):
    def __init__(self, code: str, status: int) -> None:
        self.code, self.status = code, status
        super().__init__(code)


class QualityCasePort(Protocol):
    def overview(self, ware: int, actor: str) -> dict[str, Any]: ...
    def detail(self, ware: int, case: int, actor: str) -> dict[str, Any]: ...
    def command(self, ware: int, body: QualityCaseCommand, actor: str) -> dict[str, Any]: ...
    def quarantine_move(self, ware: int, body: QuarantineMove, actor: str) -> dict[str, Any]: ...
    def write_off(self, ware: int, body: QualityWriteOff, actor: str) -> dict[str, Any]: ...


def quality_case_service() -> QualityCasePort:
    raise RuntimeError("Quality cases are not wired")
