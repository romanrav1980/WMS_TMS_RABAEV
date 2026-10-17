"""Resume existing durable source intents after the original stock receipt commits."""
from collections.abc import Callable, Sequence
from typing import Any
from ..contracts_wave_launch import WaveLaunchContinuationError


def continue_launched_wave(post: Callable[[], Any], steps: Sequence[tuple[str, Callable[[], Any]]],
                           operation: str) -> dict[str, Any]:
    post()  # Its own uncertainty must remain an unconfirmed launch.
    for name, action in steps:
        try:
            action()
        except Exception as error:
            raise WaveLaunchContinuationError(operation, name) from error
    return {"operation_id": operation, "launch_outcome": "APPLIED", "continuation_state": "COMPLETE"}
