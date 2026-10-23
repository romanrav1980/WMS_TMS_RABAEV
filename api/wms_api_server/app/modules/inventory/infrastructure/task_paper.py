"""Read the existing authoritative task snapshot and encode its version for a paper sheet."""
from datetime import datetime, timezone
from typing import Any
from ..contracts_task_read import TaskReadError
from ..domain.task_paper import task_barcode
from .task_scoped_view import scoped_task_detail


def task_paper_snapshot(gateway: Any, actor: str, task: int, expected_signature: str | None = None) -> dict:
    snapshot = scoped_task_detail(gateway, actor, task)
    signature = snapshot.get("task_signature")
    if expected_signature is not None and signature != expected_signature:
        raise TaskReadError("PAPER_TASK_CHANGED", 409)
    try:
        reference, svg = task_barcode(task, signature or "")
    except ValueError as error:
        raise TaskReadError("PAPER_TASK_SIGNATURE_UNAVAILABLE", 503) from error
    return {"task": snapshot, "reference": reference, "barcode_svg": svg,
            "prepared_at": datetime.now(timezone.utc).isoformat()}
