"""Use the existing native current-source approval; never infer a legacy clock from a browser."""
from typing import Any
from .trip_time_approval import read_time_context
from .time_snapshot import original_operations


def current_timeline_clock(cursor: Any, trip: int, actor: str) -> dict[str, Any]:
    context = read_time_context(cursor, trip, actor)
    status = context["approval_status"]
    if status != "APPROVED":
        return {"status": status, "operations": {}, "time_zone": None, "version": context["version"]}
    approval = context["last_approval"]
    zone = approval.get("time_zone")
    if not isinstance(zone, str) or not zone:
        return {"status": "APPROVAL_ZONE_UNRESOLVED", "operations": {}, "time_zone": None, "version": context["version"]}
    operations = original_operations(cursor, trip, zone)
    return {"status": "APPROVED", "time_zone": zone, "version": context["version"],
            "operations": {int(row["operation_id"]): row for row in operations}}
