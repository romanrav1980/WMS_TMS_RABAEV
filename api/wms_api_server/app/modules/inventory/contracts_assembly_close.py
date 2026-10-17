"""Assigned assembly operator closes the existing CASE through its existing owner."""
from typing import Any, Protocol
from pydantic import BaseModel, ConfigDict, Field

class AssemblyCloseInput(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    operation_id: str = Field(min_length=1, max_length=100, pattern=r"^[A-Za-z0-9_.:-]+$")
    expected_content_version: int = Field(ge=0)

class AssemblyClosePort(Protocol):
    def close(self, session: str, body: AssemblyCloseInput, actor: str) -> dict[str, Any]: ...

def assembly_close_service() -> AssemblyClosePort:
    raise RuntimeError("Assembly close owner is not composed")
