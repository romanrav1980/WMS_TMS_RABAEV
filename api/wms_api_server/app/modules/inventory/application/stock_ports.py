"""Public application ports for stock operation visibility."""
from typing import Any, Protocol


class StockQueriesPort(Protocol):
    def status(self) -> dict[str, Any]: ...
    def operation(self, operation_id: str, actor: str) -> dict[str, Any]: ...
