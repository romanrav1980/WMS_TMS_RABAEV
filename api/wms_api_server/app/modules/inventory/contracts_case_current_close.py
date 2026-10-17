"""Current actor closes an ordinary assigned CASE through the existing close journal."""
from typing import Any, Protocol
from pydantic import BaseModel, ConfigDict, Field


class CaseCurrentCloseInput(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    operation_id: str = Field(pattern=r"^[A-Za-z0-9_.:-]{1,100}$")
    expected_content_version: int = Field(ge=0)


class CaseCurrentClosePort(Protocol):
    def close(self, task: int, body: CaseCurrentCloseInput, actor: str) -> dict[str, Any]: ...


def case_current_close_service() -> CaseCurrentClosePort:
    raise RuntimeError("Current CASE close owner is not composed")
