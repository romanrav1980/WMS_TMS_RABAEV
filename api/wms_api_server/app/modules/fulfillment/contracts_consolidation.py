"""Expected fulfilment/ST membership, distinct from physical HU composition."""
from typing import Any, Protocol


class ConsolidationError(RuntimeError):
    def __init__(self, status: int, code: str, operation_id: str | None = None, uncertain: bool = False) -> None:
        super().__init__(code)
        self.status, self.code, self.operation_id, self.uncertain = status, code, operation_id, uncertain


class ConsolidationPort(Protocol):
    def page(self, warehouse_id: int, actor: str, after: str | None, limit: int, status: str) -> dict[str, Any]: ...
    def read(self, plan_id: str, actor: str) -> dict[str, Any]: ...
    def command(self, plan_id: str, body: dict[str, Any], actor: str) -> dict[str, Any]: ...


def consolidation_service() -> ConsolidationPort:
    raise RuntimeError("Consolidation service is not composed")
