"""
Windows-safe load check for TMS-2 Sprint 14 (plan-fact analytics).

Checks:
  GET /plan-fact (1 day)    p95 <= 500 ms
  GET /plan-fact (30 days)  p95 <= 2000 ms
  GET /vehicles/gantt      p95 <= 500 ms

Run:
    python tests/transport/transport_sprint14_load_test.py
"""

from __future__ import annotations

import concurrent.futures as cf
import os
import statistics
import sys
import time
from dataclasses import dataclass

import requests


BASE_URL = os.environ.get("TMS_API_BASE_URL", "http://127.0.0.1:8088")
AUTH = ("admin", "admin123")
PLAN_DATE = "2026-05-25"


@dataclass
class EndpointCase:
    name: str
    method: str
    path: str
    target_ms: float
    requests: int
    workers: int
    params: dict | None = None


def percentile(values: list[float], pct: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    index = min(len(ordered) - 1, int(round((pct / 100) * (len(ordered) - 1))))
    return ordered[index]


def request_once(case: EndpointCase) -> tuple[float, int, str]:
    started = time.perf_counter()
    try:
        response = requests.request(
            case.method,
            f"{BASE_URL}{case.path}",
            auth=AUTH,
            params=case.params,
            timeout=20,
        )
        elapsed_ms = (time.perf_counter() - started) * 1000
        return elapsed_ms, response.status_code, response.text[:240]
    except Exception as exc:  # noqa: BLE001 - load runner must report transport failures.
        elapsed_ms = (time.perf_counter() - started) * 1000
        return elapsed_ms, 0, repr(exc)


def run_case(case: EndpointCase) -> bool:
    with cf.ThreadPoolExecutor(max_workers=case.workers) as pool:
        results = list(pool.map(lambda _: request_once(case), range(case.requests)))

    latencies = [elapsed for elapsed, _, _ in results]
    failures = [(status, body) for _, status, body in results if status < 200 or status >= 300]
    p95 = percentile(latencies, 95)
    avg = statistics.mean(latencies) if latencies else 0.0

    print(
        f"{case.name}: requests={case.requests} workers={case.workers} "
        f"avg={avg:.1f}ms p95={p95:.1f}ms target={case.target_ms:.0f}ms "
        f"failures={len(failures)}"
    )
    if failures:
        print(f"  first failure: HTTP {failures[0][0]} {failures[0][1]}")
        return False
    if p95 > case.target_ms:
        print(f"  NFR FAIL: p95 {p95:.1f}ms > {case.target_ms:.0f}ms")
        return False
    return True


def main() -> int:
    cases = [
        EndpointCase(
            name="GET /plan-fact (1 day)",
            method="GET",
            path="/api/admin/transport/plan-fact",
            target_ms=500,
            requests=80,
            workers=10,
            params={"date_from": PLAN_DATE, "date_to": PLAN_DATE},
        ),
        EndpointCase(
            name="GET /plan-fact (30 days)",
            method="GET",
            path="/api/admin/transport/plan-fact",
            target_ms=2000,
            requests=60,
            workers=8,
            params={"date_from": "2026-05-01", "date_to": PLAN_DATE},
        ),
        EndpointCase(
            name="GET /vehicles/gantt",
            method="GET",
            path="/api/admin/transport/vehicles/gantt",
            target_ms=500,
            requests=50,
            workers=8,
            params={"gantt_date": PLAN_DATE},
        ),
    ]

    ok = True
    for case in cases:
        ok = run_case(case) and ok
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
