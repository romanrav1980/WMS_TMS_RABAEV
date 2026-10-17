"""Only never-created session/step attempts may receive a durable abandonment."""
from typing import Any, Literal, Protocol
from pydantic import Field
from .contracts_assembly_scale import AssemblyInput, AssemblySessionOpen, AssemblyStepOpen

class AbandonSession(AssemblyInput):
    operation_id: str = Field(min_length=1,max_length=100,pattern=r"^[A-Za-z0-9_.:-]+$")
    kind: Literal["OPEN_SESSION"]
    reason: str = Field(min_length=8,max_length=500)
    original: AssemblySessionOpen

class AbandonStep(AssemblyInput):
    operation_id: str = Field(min_length=1,max_length=100,pattern=r"^[A-Za-z0-9_.:-]+$")
    kind: Literal["OPEN_STEP"]
    session_id: str = Field(min_length=1,max_length=100)
    reason: str = Field(min_length=8,max_length=500)
    original: AssemblyStepOpen

AbandonIntent = AbandonSession | AbandonStep

class AssemblyIntentPort(Protocol):
    def abandon(self, body: AbandonIntent, actor: str) -> dict[str, Any]: ...
    def read(self, identity: str, actor: str) -> dict[str, Any]: ...

def assembly_intent_service() -> AssemblyIntentPort:
    raise RuntimeError("Assembly intent owner is not composed")
