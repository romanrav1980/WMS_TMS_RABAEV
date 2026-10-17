"""Explicit disposition of an empty ordinary CASE after accepted shortage."""
from typing import Any, Protocol
from pydantic import BaseModel, ConfigDict, Field, field_validator


class CaseEmptyInput(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    operation_id: str = Field(pattern=r"^[A-Za-z0-9_.:-]{1,100}$")
    expected_content_version: int = Field(ge=0)
    scan_container: str = Field(min_length=1, max_length=200)
    reason: str = Field(min_length=1, max_length=1000)

    @field_validator("scan_container", "reason")
    @classmethod
    def nonblank(cls, value: str) -> str:
        if not value.strip() or "\x00" in value:
            raise ValueError("Nonblank identifier/reason required")
        return value


class CaseEmptyPort(Protocol):
    def dispose(self, task: int, body: CaseEmptyInput, actor: str) -> dict[str, Any]: ...


def case_empty_service() -> CaseEmptyPort:
    raise RuntimeError("Empty CASE disposition owner is not composed")
