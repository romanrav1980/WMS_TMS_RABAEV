"""Read-only shared resource timeline; command owners remain unchanged."""
from datetime import datetime
from typing import Any, Protocol, Callable

TimelineClockReader = Callable[[Any, int, str], dict[str, Any]]


class TimelineError(RuntimeError):
    def __init__(self, code: str, status: int = 409) -> None:
        super().__init__(code)
        self.code = code
        self.status = status


class ResourceTimelinePort(Protocol):
    def read(self, warehouse: int, start: datetime, finish: datetime, actor: str) -> dict[str, Any]: ...


def resource_timeline_service() -> ResourceTimelinePort:
    raise RuntimeError("Resource timeline not composed")
