"""Exact planned driving intersections; no fabricated complete employment history."""
from datetime import datetime
from decimal import Decimal
from typing import Any
from .driver_rest import DRIVE_CODES, TRIP_DRIVE_MIN, evaluate_driver_rest


def planned_day_drive(operations: list[dict[str, Any]], start_at: str, end_at: str) -> dict[str, Any]:
    begin, finish = datetime.fromisoformat(start_at), datetime.fromisoformat(end_at)
    total = Decimal(0)
    unknown: list[int] = []
    for op in operations:
        if op["operation_code"] not in DRIVE_CODES:
            continue
        a, b = op["plan_start_at"], op["plan_end_at"]
        if a is None or b is None:
            unknown.append(op["operation_id"])
            continue
        start, end = datetime.fromisoformat(a), datetime.fromisoformat(b)
        if end <= start:
            unknown.append(op["operation_id"])
            continue
        seconds = (min(end, finish) - max(start, begin)).total_seconds()
        if seconds > 0:
            total += Decimal(str(seconds)) / Decimal(60)
    return {"drive_min": str(total), "unknown_drive_operation_ids": unknown,
            "planning_limit_min": str(TRIP_DRIVE_MIN),
            "limit_exceeded": total > TRIP_DRIVE_MIN,
            "excess_min": str(max(total - TRIP_DRIVE_MIN, Decimal(0)))}

def planned_day_continuity(operations: list[dict[str, Any]], start_at: str, end_at: str) -> dict[str, Any]:
    """Continue across trip boundaries; midnight and other work are not rest."""
    begin, finish = datetime.fromisoformat(start_at), datetime.fromisoformat(end_at)
    seen: set[int] = set()
    chain: list[dict[str, Any]] = []
    intersecting: set[int] = set()
    for operation in operations:
        key = operation["operation_id"]
        if key in seen:
            continue
        seen.add(key)
        a, b = operation["plan_start_at"], operation["plan_end_at"]
        if a is None or b is None:
            chain.append(operation)
            intersecting.add(key)
            continue
        start, end = datetime.fromisoformat(a), datetime.fromisoformat(b)
        if start >= finish:
            continue
        if end > begin or end <= start:
            intersecting.add(key)
        chain.append({**operation, "plan_end_at": min(end, finish).isoformat()})
    chain.sort(key=lambda op: (op["plan_start_at"] is None,
        datetime.fromisoformat(op["plan_start_at"]).timestamp() if op["plan_start_at"] else 0,
        op["operation_id"]))
    measured = evaluate_driver_rest(chain)
    violations = [item for item in measured["violations"]
        if item["code"] != "DRIVER_TRIP_DRIVE_LIMIT" and item.get("operation_id") in intersecting]
    return {"coverage": "RECORDED_APPROVED_CROSS_TRIP_CHAIN",
        "initial_continuity_verified": False, "legal_compliance_verified": False,
        "continuous_limit_min": measured["continuous_limit_min"],
        "minimum_break_min": measured["minimum_break_min"],
        "violations": violations, "unknown_intervals": measured["unknown_intervals"],
        "status": "VIOLATIONS" if violations else
            "INSUFFICIENT_EVIDENCE" if measured["unknown_intervals"] or not chain else "NO_OBSERVED_CHAIN_VIOLATION"}
