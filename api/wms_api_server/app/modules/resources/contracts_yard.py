"""TRADECASE yard visit commands: one versioned visit per trip, dock and vehicle occupied by at most one active visit."""
from datetime import datetime
from typing import Any, Literal, Protocol
from pydantic import AwareDatetime, BaseModel, ConfigDict, Field, model_validator

Operation = Field(min_length=8, max_length=100, pattern=r"^[A-Za-z0-9_.:-]+$")


class YardExpect(BaseModel):
    model_config = ConfigDict(extra="forbid")
    operation_id: str = Operation
    trip_id: str | None = Field(default=None, min_length=1, max_length=100)
    supply_ids: list[str] | None = Field(default=None, min_length=1, max_length=200)
    vehicle: str | None = Field(default=None, min_length=1, max_length=50)
    planned_arrival_at: AwareDatetime | None = None

    @model_validator(mode="after")
    def source(self) -> "YardExpect":
        if self.trip_id is not None:
            if self.supply_ids is not None or self.vehicle is not None:
                raise ValueError("Outbound visit uses its trip vehicle")
        elif self.supply_ids is None or self.vehicle is None or not self.vehicle.strip():
            raise ValueError("Inbound visit requires supplies and the vehicle number")
        if self.supply_ids is not None:
            if any(not s.strip() or len(s)>100 for s in self.supply_ids) or len(set(self.supply_ids))!=len(self.supply_ids):
                raise ValueError("Supply identifiers must be distinct and between 1 and 100 characters")
        return self


class YardTransition(BaseModel):
    model_config = ConfigDict(extra="forbid")
    operation_id: str = Operation
    expected_version: int = Field(strict=True, gt=0)
    action: Literal["ARRIVE", "ASSIGN_DOCK", "REASSIGN_DOCK", "START", "FINISH", "DEPART", "CANCEL"]
    dock: str | None = Field(default=None, min_length=1, max_length=50)
    reason: str | None = Field(default=None, min_length=3, max_length=500)

    @model_validator(mode="after")
    def arguments(self) -> "YardTransition":
        if (self.action in {"ASSIGN_DOCK", "REASSIGN_DOCK"}) != (self.dock is not None):
            raise ValueError("Only a dock assignment names a dock")
        if (self.action == "CANCEL") != (self.reason is not None):
            raise ValueError("Only a cancellation carries a reason")
        return self


class YardError(RuntimeError):
    def __init__(self, code: str, status: int) -> None:
        self.code, self.status = code, status
        super().__init__(code)


class YardPort(Protocol):
    def visits(self, ware: int, actor: str, active: bool) -> dict[str, Any]: ...
    def expect(self, ware: int, body: YardExpect, actor: str) -> dict[str, Any]: ...
    def transition(self, ware: int, visit: int, body: YardTransition, actor: str) -> dict[str, Any]: ...


def yard_service() -> YardPort:
    raise RuntimeError("Yard visits are not wired")


def wire(body: YardExpect | YardTransition, **extra: Any) -> dict[str, Any]:
    """Native command body; times as YYYY-MM-DDTHH:MM:SS+HH:MM (the format RRL_YARD_VISIT_API parses)."""
    data = body.model_dump(exclude_none=True)
    for key, value in list(data.items()):
        if isinstance(value, datetime):
            data[key] = value.replace(microsecond=0).isoformat()
    return {**data, **extra}
