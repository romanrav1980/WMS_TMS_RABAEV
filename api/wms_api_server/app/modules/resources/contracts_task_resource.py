"""Explicit ordinary warehouse-task metadata intents; native Oracle owns authority."""
from typing import Any, Literal, Protocol, Self
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class TaskResourceError(Exception):
    def __init__(self, code: str, status: int = 503, operation_id: str | None = None) -> None:
        super().__init__(code)
        self.code, self.status, self.operation_id = code, status, operation_id


class TaskResourceCommand(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    operation_id: str = Field(min_length=1, max_length=100, pattern=r"^[A-Za-z0-9_.:-]+$")
    action: Literal["ASSIGN", "START"]
    target: str = Field(min_length=1, max_length=100)
    expected_assignment_version: int = Field(ge=0)
    expected_task_signature: str = Field(pattern=r"^[A-Fa-f0-9]{64}$")
    resource_session_id: int = Field(gt=0)
    resource_id: int | None = Field(default=None, gt=0)
    equipment_id: int | None = Field(default=None, gt=0)


class TaskResourceState(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    task_id: int = Field(gt=0)
    status: str
    assignment_version: int = Field(ge=0)
    task_signature: str = Field(pattern=r"^[A-Fa-f0-9]{64}$")
    assigned_to: str | None
    resource_id: int | None = Field(ge=1)
    resource_session_id: int | None = Field(ge=1)
    equipment_id: int | None = Field(ge=1)
    started_at_instant: str | None
    started_shift_time_zone: str | None

    @field_validator("started_at_instant")
    @classmethod
    def original_instant_is_aware(cls, value: str | None) -> str | None:
        if value is not None and datetime.fromisoformat(value.replace("Z", "+00:00")).utcoffset() is None:
            raise ValueError("Original server instant must include an offset")
        return value


class TaskResourceAck(TaskResourceState):
    operation_id: str
    action: Literal["ASSIGN", "START"]
    actor: str
    target: str
    outcome: Literal["APPLIED", "REJECTED"]
    error_code: str | None
    outcome_confirmed: bool
    stock_posted: bool
    changed: bool
    request_sha256: str = Field(pattern=r"^[A-F0-9]{64}$")
    may_create_corrected_operation: bool

    @model_validator(mode="after")
    def confirmed_metadata_only(self) -> Self:
        rejected = self.outcome == "REJECTED"
        if not self.outcome_confirmed or self.stock_posted:
            raise ValueError("Warehouse resource command must confirm metadata only")
        if rejected and (self.changed or not self.error_code):
            raise ValueError("Rejected command cannot change the task")
        if self.may_create_corrected_operation != rejected or (not rejected and self.error_code is not None):
            raise ValueError("Inconsistent terminal receipt")
        return self


class TaskResourcePort(Protocol):
    def context(self, task: int, actor: str, target: str) -> dict[str, Any]: ...
    def command(self, task: int, body: TaskResourceCommand, actor: str) -> dict[str, Any]: ...
    def receipt(self, operation: str, actor: str) -> dict[str, Any]: ...


def task_resource_service() -> TaskResourcePort:
    raise RuntimeError("Warehouse resource commands are not wired")
