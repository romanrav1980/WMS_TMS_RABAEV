from datetime import date
from typing import Any, Protocol

class DriverWorkspacePort(Protocol):
    def trips(self, driver: int, day: date, actor: str) -> list[dict[str, Any]]: ...
    def details(self, driver: int, trip: int, kind: str, actor: str) -> list[dict[str, Any]]: ...
    def mark(self, driver: int, operation: int, action: str, actor: str) -> dict[str, Any]: ...

def driver_workspace_service() -> DriverWorkspacePort:
    raise RuntimeError("Driver workspace not wired")
