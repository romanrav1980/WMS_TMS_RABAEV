"""Extra stop outside the main route (TRADECASE program, section 12): native evaluation, dispatcher decision and per-trip new-point ban."""
from typing import Any, Literal, Protocol
from pydantic import BaseModel, ConfigDict, Field, model_validator

Zone = Literal["UTC", "Europe/Moscow", "Asia/Tbilisi"]


class ExtraStopCommand(BaseModel):
    model_config = ConfigDict(extra="forbid")
    operation_id: str = Field(min_length=8, max_length=100, pattern=r"^[A-Za-z0-9_.:-]+$")
    action: Literal["APPROVE", "DECLINE", "SET_POLICY"]
    reason: str = Field(min_length=3, max_length=500)
    address: str | None = Field(default=None, min_length=1, max_length=255)
    zone: Zone = "UTC"
    expected_version: int | None = Field(default=None, strict=True, ge=0)
    source_hash: str | None = Field(default=None, pattern=r"^[a-f0-9]{64}$")
    position: int | None = Field(default=None, strict=True, ge=0, le=200)
    new_stops_forbidden: bool | None = None
    expected_policy_version: int | None = Field(default=None, strict=True, ge=0)

    @model_validator(mode="after")
    def arguments(self) -> "ExtraStopCommand":
        decision = (self.address, self.expected_version, self.source_hash)
        if self.action == "SET_POLICY":
            ok = self.new_stops_forbidden is not None and self.expected_policy_version is not None and all(v is None for v in (*decision, self.position))
        else:
            ok = all(v is not None for v in decision) and self.new_stops_forbidden is None and self.expected_policy_version is None \
                and (self.action == "APPROVE") == (self.position is not None)
        if not ok:
            raise ValueError("SET_POLICY names the ban and its version; APPROVE/DECLINE name the address and the route version (APPROVE: position)")
        return self


class ExtraStopError(RuntimeError):
    def __init__(self, code: str, status: int) -> None:
        self.code, self.status = code, status
        super().__init__(code)


class ExtraStopPort(Protocol):
    def evaluate(self, trip: int, address: str, zone: str, actor: str) -> dict[str, Any]: ...
    def decisions(self, trip: int, actor: str) -> dict[str, Any]: ...
    def command(self, trip: int, body: ExtraStopCommand, actor: str) -> dict[str, Any]: ...


def extra_stop_service() -> ExtraStopPort:
    raise RuntimeError("Extra stop decisions are not wired")
