"""Windows-safe load check for Sprint 40 (day summary source endpoint).

The day summary is computed client-side from the already-loaded tasks list,
so this runner measures the task list endpoint and one adjacent read endpoint.
It does not mutate Oracle data.
"""

from __future__ import annotations

import concurrent.futures as cf
import statistics
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlencode

import requests

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from support.project_config import local_config  # noqa: E402

BASE_URL = local_config().api_base_url
AUTH = ("admin", "admin123")
PLAN_DATE = "2026-05-25"


@dataclass
class EndpointCase:
    name: str
    path: str
    target_ms: float
    requests: int
    workers: int
    ok_statuses: tuple[int, ...] = (200,)


def qs(**params: object) -> str:
    return urlencode({k: v for k, v in params.items() if v is not None})


def percentile(values: list[float], pct: float) -> float:
    ordered = sorted(values)
    if not ordered:
        return 0.0
    return ordered[min(len(ordered) - 1, int(round((pct / 100) * (len(ordered) - 1))))]


def request_once(case: EndpointCase) -> tuple[float, int, str]:
    started = time.perf_counter()
    try:
        response = requests.get(f"{BASE_URL}{case.path}", auth=AUTH, timeout=20)
        return (time.perf_counter() - started) * 1000, response.status_code, response.text[:160]
    except Exception as exc:  # noqa: BLE001
        return (time.perf_counter() - started) * 1000, 0, repr(exc)


def run_case(case: EndpointCase) -> bool:
    with cf.ThreadPoolExecutor(max_workers=case.workers) as pool:
        results = list(pool.map(lambda _: request_once(case), range(case.requests)))
    latencies = [elapsed for elapsed, _, _ in results]
    failures = [(status, body) for _, status, body in results if status not in case.ok_statuses]
    p95 = percentile(latencies, 95)
    avg = statistics.mean(latencies) if latencies else 0.0
    print(f"{case.name}: avg={avg:.1f}ms p95={p95:.1f}ms target={case.target_ms:.0f}ms failures={len(failures)}")
    if failures:
        print(f"  first failure: HTTP {failures[0][0]} {failures[0][1]}")
        return False
    if p95 > case.target_ms:
        print(f"  NFR FAIL: p95 {p95:.1f}ms > {case.target_ms:.0f}ms")
        return False
    return True


def main() -> int:
    cases = [
        EndpointCase("GET /tasks day summary source", f"/api/admin/transport/tasks?{qs(shipment_date=PLAN_DATE)}", 800, 40, 5),
        EndpointCase("GET /tasks all statuses", f"/api/admin/transport/tasks?{qs(shipment_date=PLAN_DATE, unassigned_only='false')}", 800, 40, 5),
        EndpointCase("GET /available-sts adjacent", f"/api/admin/transport/available-sts?{qs(stdate=PLAN_DATE)}", 400, 30, 5),
    ]
    for case in cases:
        request_once(case)
    ok = True
    for case in cases:
        ok = run_case(case) and ok
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
