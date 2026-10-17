"""Public handoff contract; keep existing immutable legacy event serialization."""
from typing import Any
from pydantic import BaseModel, Field


class CasePickTransferRequest(BaseModel):
    to_resource_id: int = Field(ge=1)
    to_resource_session_id: int | None = Field(default=None,ge=1)
    to_equipment_id: int | None = Field(default=None,ge=1)
    reason: str | None = Field(default=None,max_length=1000)
    actor: str | None = Field(default=None,max_length=100)
    offline_event_id: str | None = Field(default=None,min_length=1,max_length=100)
    scan_container: str | None = Field(default=None,min_length=1,max_length=150)
    expected_content_version: int | None = Field(default=None,ge=0,strict=True)
    expected_assigned_to: str | None = Field(default=None,min_length=1,max_length=100)
    expected_from_session_id: int | None = Field(default=None,ge=1,strict=True)
    expected_assignment_version: int | None = Field(default=None,ge=0,strict=True)

    def model_dump(self, *args: Any, **kwargs: Any) -> dict[str, Any]:
        result = super().model_dump(*args, **kwargs)
        if self.expected_assignment_version is None:
            result.pop("expected_assignment_version", None)
        return result
