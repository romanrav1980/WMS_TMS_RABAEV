"""Adapt the native approved schedule for existing diagnostics, never replace facts."""
from typing import Any


def planned_operations(context: dict[str, Any], original: list[dict[str, Any]]) -> list[dict[str, Any]]:
    if context.get("approval_status") != "APPROVED" or any(
        op.get("fact_start_at") or op.get("fact_end_at") for op in original
    ):
        return original
    approval = context.get("last_approval", {})
    segments = approval.get("route_schedule", {}).get("segments")
    if approval.get("source_contract_version") != 6 or not segments:
        return original
    return [{"operation_id": f"APPROVED:{approval['operation_id']}:{index}",
             "operation_code": segment["code"], "plan_start_at": segment["start_at"],
             "plan_end_at": segment["finish_at"], "fact_start_at": None, "fact_end_at": None,
             "schedule_basis": "NATIVE_APPROVED_ROUTE_V6"}
            for index, segment in enumerate(segments)]
