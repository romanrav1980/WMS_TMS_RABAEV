"""Separate terminal proof for never-recorded CASE/TASK resource commands."""
from typing import Any, Literal, Protocol, Self
from pydantic import BaseModel, ConfigDict, Field, model_validator
from .contracts_case_resource import CaseResourceAck, CaseResourceCommand
from .contracts_task_resource import TaskResourceAck, TaskResourceCommand

Domain = Literal["CASE", "TASK"]


class ResourceIntentError(Exception):
    def __init__(self, code: str, status: int = 503, operation_id: str | None = None) -> None:
        super().__init__(code)
        self.code, self.status, self.operation_id = code, status, operation_id


class ResourceIntentAbandon(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    operation_id: str = Field(pattern=r"^[A-Za-z0-9_.:-]{1,100}$")
    domain: Domain
    task_id: int = Field(gt=0)
    reason: str = Field(min_length=8, max_length=500)
    original_wire: str = Field(min_length=1, max_length=16384)

    @model_validator(mode="after")
    def original_command(self) -> Self:
        if len(self.reason.strip()) < 8 or len(self.original_wire.encode("utf-8")) > 16384:
            raise ValueError("Explicit reason and bounded original command required")
        model = CaseResourceCommand if self.domain == "CASE" else TaskResourceCommand
        original = model.model_validate_json(self.original_wire)
        if self.operation_id == original.operation_id:
            raise ValueError("Control operation must differ from original operation")
        return self


class ResourceIntentQuery(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    domain: Domain
    task_id: int = Field(gt=0)
    original_operation_id: str = Field(pattern=r"^[A-Za-z0-9_.:-]{1,100}$")
    action: Literal["CLAIM", "ASSIGN", "START"]
    target: str = Field(min_length=1, max_length=100)
    original_request_sha256: str = Field(pattern=r"^[A-F0-9]{64}$")

    @model_validator(mode="after")
    def domain_action(self) -> Self:
        if self.action == ("ASSIGN" if self.domain == "CASE" else "CLAIM"):
            raise ValueError("Action belongs to another domain")
        return self


class ResourceIntentAbandoned(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    operation_id: str
    status: Literal["ABANDONED"]
    domain: Domain
    task_id: int = Field(gt=0)
    actor: str
    action: Literal["CLAIM", "ASSIGN", "START"]
    target: str
    original_operation_id: str
    original_wire: str
    original_request_sha256: str = Field(pattern=r"^[A-F0-9]{64}$")
    control_request_sha256: str = Field(pattern=r"^[A-F0-9]{64}$")
    original_expected_assignment_version: int = Field(ge=0)
    assignment_version_at_abandon: int = Field(ge=0)
    outcome_confirmed: bool
    stock_posted: bool

    @model_validator(mode="after")
    def terminal_metadata_only(self) -> Self:
        if not self.outcome_confirmed or self.stock_posted:
            raise ValueError("Abandonment must confirm no stock posting")
        if self.domain == "CASE" and (self.action == "ASSIGN" or self.target != self.actor):
            raise ValueError("CASE intent must belong to original actor")
        return self


class ResourceIntentResolution(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    status: Literal["RECORDED", "ABANDONED"]
    domain: Domain
    task_id: int
    actor: str
    original_operation_id: str
    original_request_sha256: str
    original_receipt: CaseResourceAck | TaskResourceAck | None
    abandonment: ResourceIntentAbandoned | None

    @model_validator(mode="after")
    def exclusive_proof(self) -> Self:
        if (self.status == "RECORDED") != (self.original_receipt is not None):
            raise ValueError("Recorded resolution requires original receipt")
        if (self.status == "ABANDONED") != (self.abandonment is not None):
            raise ValueError("Abandoned resolution requires native tombstone")
        return self


class ResourceIntentPort(Protocol):
    def abandon(self, body: ResourceIntentAbandon, actor: str) -> dict[str, Any]: ...
    def resolution(self, query: ResourceIntentQuery, actor: str) -> dict[str, Any]: ...
    def receipt(self, operation: str, actor: str) -> dict[str, Any]: ...


def resource_intent_service() -> ResourceIntentPort:
    raise RuntimeError("Resource metadata intent recovery is not wired")
