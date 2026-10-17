from typing import Any, Protocol


class CaseReadError(ValueError):
    def __init__(self, code: str, message: str, status: int = 403) -> None:
        super().__init__(message)
        self.code, self.status = code, status


class CaseReadPort(Protocol):
    def tasks(self, actor: str, resource: int | None, scope: str, status: str | None, limit: int, warehouse: int | None = None) -> list[dict[str, Any]]: ...
    def task(self, task: int, actor: str) -> dict[str, Any]: ...
    def shorts(self, actor: str, status: str | None, limit: int, warehouse: int | None = None) -> list[dict[str, Any]]: ...


def case_read_service() -> CaseReadPort:
    raise RuntimeError("CASE read service not wired")
