"""UTC interval interpretation without assumptions about local legacy clocks."""
from datetime import datetime, timezone
from typing import Any


def instant(value: str | None) -> datetime | None:
    if value is None:
        return None
    parsed = datetime.fromisoformat(value)
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError("Aware instant required")
    return parsed.astimezone(timezone.utc)


def overlaps(start: str | None, finish: str | None, view_start: datetime, view_finish: datetime) -> bool:
    begins, ends = instant(start), instant(finish)
    return begins is not None and begins < view_finish and (ends is None or ends > view_start)


def overlap_candidates(events: list[dict[str, Any]], bindings: list[dict[str, str]],
                       observed_at: datetime, view_finish: datetime) -> list[dict[str, Any]]:
    """Candidates for review, not a capacity rule. Attendance is not task consumption."""
    lookup = {event["event_id"]: event for event in events if event["kind"] != "ATTENDANCE"}
    lanes: dict[tuple[str, str], list[tuple[datetime, datetime, str]]] = {}
    for binding in bindings:
        event = lookup.get(binding["event_id"])
        if event is None:
            continue
        for phase in ("plan", "fact"):
            start, finish = instant(event.get(phase + "_start_at")), instant(event.get(phase + "_finish_at"))
            if start is None:
                continue
            if finish is None and phase == "fact":
                if event.get("status") in {"DONE", "CANCELLED", "SHIPPED", "READY_TO_SHIP", "CONTROLLED", "WAIT_CONTROL", "CONTROL_IN_PROGRESS", "PICKED", "CLOSED"}:
                    continue
                finish = min(observed_at, view_finish)
            if finish is not None and finish > start:
                lanes.setdefault((binding["resource_id"], phase), []).append((start, finish, event["event_id"]))
    result: list[dict[str, Any]] = []
    for (resource, phase), intervals in lanes.items():
        active: list[tuple[datetime, datetime, str]] = []
        for current in sorted(set(intervals)):
            active = [item for item in active if item[1] > current[0]]
            for previous in active:
                if previous[2] != current[2]:
                    result.append({"resource_id": resource, "phase": phase,
                                   "event_ids": [previous[2], current[2]], "status": "OVERLAP_REVIEW"})
                    if len(result) >= 200:
                        return result
            active.append(current)
    return result
