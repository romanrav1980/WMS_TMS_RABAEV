"""Resume only unfinished launch steps; never reinterpret an applied source decision."""
import logging
from typing import Any, Callable
from fastapi import HTTPException
from ...inventory.public import StockPostingError

_LOG = logging.getLogger(__name__)
STEPS = ("SETTINGS", "DEFICIT", "RESERVE_SOURCES", "PICK_FACE_CAPACITY",
         "RELEASE_QUEUE", "WAREHOUSE_TASKS", "CASE_TASKS")


def run_wave_launch(wave: int, operation: str, actor: str,
                    post_launch: Callable[[], Any], repository: Any,
                    actions: Callable[..., Any], post_sources: Callable[..., Any]) -> dict[str, Any]:
    post_launch()
    for number, name in enumerate(STEPS, 1):
        try:
            with repository.step(number) as (bound, run):
                if not run:
                    continue
                if name == "RESERVE_SOURCES":
                    repository.freeze_sources(bound)
                else:
                    actions(bound, wave, actor)[name]()
                    repository.finish(bound)
            if name == "RESERVE_SOURCES":
                # The metadata transaction committed before StockPosting's strict begin_plan.
                post_sources(repository)
                with repository.step(number) as (bound, run):
                    if run:
                        repository.finish(bound)
        except Exception as error:
            state = "UNCONFIRMED"
            try:
                repository.fail(number, failure_code(error))
                state = "FAILED"
            except Exception:
                _LOG.exception("Could not confirm wave continuation failure receipt")
            raise HTTPException(503, detail={"code": "WAVE_LAUNCHED_CONTINUATION_UNCONFIRMED",
                "operation_id": operation, "launch_outcome": "APPLIED", "continuation_state": state,
                "continuation_step": name, "outcome_confirmed": False, "read_before_retry": True,
                "retry_same_operation_id": True,
                "receipt_url": f"/api/picking/waves/{wave}/launch-receipts/{operation}"}) from error
    return {"operation_id": operation, "launch_outcome": "APPLIED", "continuation_state": "COMPLETE"}


def failure_code(error: Exception) -> str:
    if isinstance(error, StockPostingError):
        return error.code
    if isinstance(error, HTTPException) and isinstance(error.detail, dict):
        return str(error.detail.get("code", "CONTINUATION_STEP_FAILED"))[:100]
    return "CONTINUATION_STEP_FAILED"
