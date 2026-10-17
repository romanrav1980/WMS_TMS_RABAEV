from datetime import datetime
from typing import Any, Protocol


class PickerKpiError(Exception):
    def __init__(self, code: str, status: int = 409) -> None:
        super().__init__(code)
        self.code, self.status = code, status


class PickerKpiPort(Protocol):
    def window(self, warehouse: int, start: datetime, finish: datetime, actor: str,
               operator: str | None = None) -> dict[str, Any]: ...


class PickerKpiReadPort(Protocol):
    def snapshot(self, warehouse: int, start: datetime, finish: datetime, actor: str,
                 operator: str | None) -> dict[str, Any]: ...


def picker_kpi_service() -> PickerKpiPort:
    raise RuntimeError("Picker KPI service is not wired")
