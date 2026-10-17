"""Fresh read series with optional server-directed change gate, no spread classifier."""
import asyncio
from collections.abc import Callable
from datetime import datetime
from decimal import Decimal
import time
from ..contracts_scale_opc import OpcWeightObservation, OpcWeightReader
from ..contracts_scales import ScaleGatewayError


async def collect_opc_window(reader: OpcWeightReader, renew: Callable[[], None], timeout: float = 10,
                             before: Decimal | None = None, min_change: Decimal | None = None
                             ) -> tuple[list[OpcWeightObservation], list[int]]:
    if not 2.5 <= timeout <= 30:
        raise ValueError("OPC_WINDOW_TIMEOUT_INVALID")
    if before is not None and (not before.is_finite() or min_change is None or not min_change.is_finite() or min_change <= 0):
        raise ValueError("OPC_SERVER_CHANGE_THRESHOLD_REQUIRED")
    deadline = time.monotonic()+timeout
    observations: list[OpcWeightObservation] = []
    offsets: list[int] = []
    start = 0.0
    while time.monotonic() < deadline:
        renew()
        observation = await reader.read()
        renew()
        stamp = time.monotonic()
        unchanged = before is not None and abs(observation.gross-before) < min_change
        if not observation.stable or observation.gross <= 0 or unchanged:
            observations.clear()
            offsets.clear()
        else:
            if observations:
                previous = observations[-1]
                old = datetime.fromisoformat(previous.evidence["values"]["current_weight"]["server_timestamp"])
                current = datetime.fromisoformat(observation.evidence["values"]["current_weight"]["server_timestamp"])
                if current <= old or observation.observed_at < previous.observed_at:
                    raise ScaleGatewayError("OPC_OBSERVATION_TIME_NOT_ADVANCING")
            else:
                start = stamp
            observations.append(observation)
            offsets.append(round((stamp-start)*1000))
            if len(observations) >= 5 and offsets[-1] >= 2000:
                if len(observations) > 25 or offsets[-1] > 10000:
                    raise ScaleGatewayError("OPC_WINDOW_BOUND_EXCEEDED")
                return observations, offsets
        await asyncio.sleep(.5)
    raise ScaleGatewayError("OPC_STABLE_WINDOW_TIMEOUT", True)
