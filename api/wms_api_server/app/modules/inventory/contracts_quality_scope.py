"""Addressed QC configuration; stock posting remains Oracle's responsibility."""
from typing import Any, Protocol

class QualityScopeError(RuntimeError):
    def __init__(self, message: str, status: int = 409) -> None:
        super().__init__(message)
        self.status = status

class QualityScopePort(Protocol):
    def read(self, warehouse: int, actor: str, address: str, category: str) -> dict[str, Any]: ...
    def save(self, warehouse: int, actor: str, body: dict[str, Any]) -> dict[str, Any]: ...

def quality_scope_service() -> QualityScopePort:
    raise RuntimeError("Quality scope service not wired")
