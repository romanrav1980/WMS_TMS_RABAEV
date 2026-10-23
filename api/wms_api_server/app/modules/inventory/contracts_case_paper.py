"""Paper sheet of an existing CASE pick task (C-0156, BP15): READ ONLY snapshot port; the access guard is wired by the composition."""
from typing import Any, Protocol


class CasePaperError(ValueError):
    def __init__(self, code: str, status: int) -> None:
        super().__init__(code)
        self.code, self.status = code, status


class CasePaperPort(Protocol):
    def snapshot(self, task: int, actor: str, line: int | None = None, expected_signature: str | None = None) -> dict[str, Any]: ...


def case_paper_service() -> CasePaperPort:
    raise RuntimeError("CASE paper service not wired")
