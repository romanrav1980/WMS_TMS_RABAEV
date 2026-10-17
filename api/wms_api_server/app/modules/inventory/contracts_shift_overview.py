"""One bounded read snapshot for wave preparation and execution facts."""
from typing import Any, Protocol


class ShiftOverviewError(RuntimeError):
    def __init__(self, code: str, status: int = 403) -> None:
        super().__init__(code)
        self.code, self.status = code, status


class ShiftOverviewPort(Protocol):
    def read(self, actor: str, warehouse: int, waves: list[int]) -> dict[str, Any]: ...


def shift_overview_service() -> ShiftOverviewPort:
    raise RuntimeError("Shift overview not composed")
