"""Adapters for existing launch projections and immutable canonical source commands."""
import json
from time import monotonic
from typing import Any, Callable
from ...inventory.public import StockCommand, StockPosting
from .wave_continuation import WaveContinuation


def launch_steps(gateway: Any, wave: int, actor: str,
                 projection_factory: Callable[[Any], Any]) -> dict[str, Callable[[], Any]]:
    from ....services.case_pick_service import CasePickService
    service = projection_factory(gateway)
    return {
        "SETTINGS": lambda: service._enrich_replenishment_settings(wave, actor),
        "DEFICIT": lambda: service._refresh_replenishment_deficit(wave, actor),
        "PICK_FACE_CAPACITY": lambda: service._hold_replenishment_rows_without_pick_face_capacity(wave, actor),
        "RELEASE_QUEUE": lambda: service._release_next_replenishment_queue(wave, actor, include_minimax=False),
        "WAREHOUSE_TASKS": lambda: service._sync_replenishment_warehouse_tasks(wave, actor),
        "CASE_TASKS": lambda: CasePickService(gateway).ensure_wave_case_pick_tasks(wave, actor),
    }


def post_frozen_sources(repository: WaveContinuation) -> None:
    deadline = monotonic() + 30
    for source in repository.sources():
        # An already confirmed decision is finished, even if it was made by an older actor.
        if source["state"] == "APPLIED":
            continue
        if source["state"] is not None:
            raise ValueError("WAVE_SOURCE_INTENT_STATE_UNRESOLVED")
        if monotonic() >= deadline:
            raise TimeoutError("WAVE_CONTINUATION_REQUEST_BUDGET")
        data = json.loads(source["body"])
        command = StockCommand(operation_id=data["operation_id"], command_type=data["command_type"],
                               actor=data["actor"], lines=(), source=data["source"],
                               units=tuple(data["units"]), metadata=data["metadata"])
        if command.canonical_json() != source["body"]:
            raise ValueError("WAVE_SOURCE_EXISTING_CANONICAL_BODY_REQUIRED")
        StockPosting().post(command)


