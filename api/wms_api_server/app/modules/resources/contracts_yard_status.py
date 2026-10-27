"""Commands and reads for the current blocked/reopened state of a yard dock."""
from typing import Any, Literal, Protocol
from pydantic import BaseModel, ConfigDict, Field, field_validator
from .contracts_yard import Operation, YardError


class YardDockStatusCommand(BaseModel):
    model_config = ConfigDict(extra="forbid")
    operation_id: str = Operation
    action: Literal["BLOCK", "UNBLOCK"]
    reason: str = Field(min_length=3, max_length=500)

    @field_validator("reason")
    @classmethod
    def nonblank_reason(cls, value: str) -> str:
        value = value.strip()
        if len(value) < 3:
            raise ValueError("A reason of at least three characters is required")
        return value


class YardDockStatusPort(Protocol):
    def docks(self, ware: int, actor: str) -> dict[str, Any]: ...
    def command(self, ware: int, dock: str, body: YardDockStatusCommand, actor: str) -> dict[str, Any]: ...


def yard_dock_status_service() -> YardDockStatusPort:
    raise RuntimeError("Yard dock status is not wired")
