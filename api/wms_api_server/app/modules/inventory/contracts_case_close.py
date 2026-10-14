from pydantic import BaseModel, ConfigDict, Field


class CaseCarrierCloseRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    operation_id: str | None = Field(default=None, min_length=1, max_length=100)
    expected_content_version: int | None = Field(default=None, strict=True, ge=0)
    resource_id: int | None = None
    resource_session_id: int | None = None
    equipment_id: int | None = None
    actor: str | None = None
    reason: str | None = Field(default=None, max_length=1000)
