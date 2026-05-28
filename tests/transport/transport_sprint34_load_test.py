"""Safe load check for Sprint 34 cancel_task business logic.

The real endpoint is mutating and must not be hammered against dev Oracle.
This runner measures the service method with a mocked transaction and asserts
that the set-based unassign/delete path stays cheap under concurrent calls.
"""

from __future__ import annotations

import concurrent.futures as cf
import statistics
import sys
import time
from contextlib import contextmanager
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from api.wms_api_server.app.services.transport_service import TransportService


class FakeCursor:
    def __init__(self) -> None:
        self.calls = 0

    def execute(self, _sql: str, _params: dict) -> None:
        self.calls += 1

    def fetchone(self) -> tuple[None]:
        return (None,)


@contextmanager
def fake_transaction(cursor: FakeCursor):
    yield cursor


def percentile(values: list[float], pct: float) -> float:
    ordered = sorted(values)
    if not ordered:
        return 0.0
    return ordered[min(len(ordered) - 1, int(round((pct / 100) * (len(ordered) - 1))))]


def run_once(idx: int) -> float:
    svc = TransportService()
    cursor = FakeCursor()
    started = time.perf_counter()
    with (
        patch.object(svc.gateway, "transaction", return_value=fake_transaction(cursor)),
        patch("api.wms_api_server.app.services.transport_service._clear_available_sts_cache"),
        patch("api.wms_api_server.app.services.transport_service._clear_task_sts_cache"),
    ):
        svc.cancel_task(idx, "load-test")
    return (time.perf_counter() - started) * 1000


def main() -> int:
    with cf.ThreadPoolExecutor(max_workers=8) as pool:
        latencies = list(pool.map(run_once, range(1000, 1080)))
    avg = statistics.mean(latencies)
    p95 = percentile(latencies, 95)
    target = 20.0
    print(f"cancel_task mocked service path: avg={avg:.2f}ms p95={p95:.2f}ms target={target:.0f}ms")
    if p95 > target:
        print(f"NFR FAIL: p95 {p95:.2f}ms > {target:.0f}ms")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
