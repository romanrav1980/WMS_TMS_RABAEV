"""Trip-local diagnostics against revision-55 planning parameters, not legal admission."""
from datetime import datetime
from decimal import Decimal
from typing import Any

DRIVE_CODES = frozenset({"DRIVE", "DRIVE_TO_CLIENT", "DRIVE_BACK"})
CONTINUOUS_MIN = Decimal(120)
BREAK_MIN = Decimal(15)
TRIP_DRIVE_MIN = Decimal(540)


def evaluate_driver_rest(operations: list[dict[str, Any]]) -> dict[str, Any]:
    """Only explicit REST resets continuity; work and unknown gaps do not."""
    continuous = Decimal(0)
    total = Decimal(0)
    violations: list[dict[str, Any]] = []
    unknown: list[dict[str, Any]] = []
    previous_end: datetime | None = None
    for operation in operations:
        code = operation["operation_code"]
        a, b = operation["plan_start_at"], operation["plan_end_at"]
        key = operation["operation_id"]
        if a is None or b is None:
            unknown.append({"code": "DRIVER_INTERVAL_MISSING", "operation_id": key})
            continue
        start, end = datetime.fromisoformat(a), datetime.fromisoformat(b)
        if end < start:
            unknown.append({"code": "DRIVER_INTERVAL_INVALID", "operation_id": key})
            continue
        duration = Decimal(str((end - start).total_seconds())) / Decimal(60)
        if previous_end is not None and start != previous_end:
            unknown.append({"code": "DRIVER_CHAIN_GAP_OR_OVERLAP", "operation_id": key})
        previous_end = end
        if code in DRIVE_CODES:
            if duration <= 0:
                unknown.append({"code": "DRIVER_ROUTE_DURATION_UNKNOWN", "operation_id": key})
            total += duration
            continuous += duration
            if continuous > CONTINUOUS_MIN:
                violations.append({"code": "DRIVER_CONTINUOUS_DRIVE_LIMIT", "operation_id": key,
                                   "continuous_min": str(continuous),
                                   "excess_min": str(continuous - CONTINUOUS_MIN)})
        elif code == "REST":
            if duration >= BREAK_MIN:
                continuous = Decimal(0)
            else:
                violations.append({"code": "DRIVER_BREAK_TOO_SHORT", "operation_id": key,
                                   "duration_min": str(duration)})
        elif code == "DRIVER_CHANGE":
            unknown.append({"code": "DRIVER_CHANGE_BINDING_NOT_PROVEN", "operation_id": key})
    if total > TRIP_DRIVE_MIN:
        violations.append({"code": "DRIVER_TRIP_DRIVE_LIMIT", "drive_min": str(total),
                           "excess_min": str(total - TRIP_DRIVE_MIN)})
    return {"basis": "REVISION_55_PLANNING_PARAMETERS", "continuous_limit_min": str(CONTINUOUS_MIN),
            "minimum_break_min": str(BREAK_MIN), "trip_drive_limit_min": str(TRIP_DRIVE_MIN),
            "drive_min": str(total), "violations": violations, "unknown_intervals": unknown,
            "status": "VIOLATIONS" if violations else "INSUFFICIENT_EVIDENCE" if unknown or not operations else "NO_TRIP_LOCAL_VIOLATION",
            "coverage": "SINGLE_TRIP_PLANNED_OPERATIONS",
            "legal_compliance_verified": False, "driver_day_complete": False,
            "prior_duty_and_other_trips_verified": False, "operational_admission": False}
