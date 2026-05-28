"""Windows-safe load check for Sprint 36 (bulk ST removal endpoints)."""

from __future__ import annotations

import concurrent.futures as cf
import os
import statistics
import sys
import time
from dataclasses import dataclass
from urllib.parse import quote

import requests

BASE_URL = os.environ.get("TMS_API_BASE_URL", "http://127.0.0.1:8088")
AUTH = ("admin", "admin123")
TASK_ID = 999999
ST_NUMBERS = [f"BULK-TEST-{i:03d}" for i in range(1, 6)]


@dataclass
class EndpointCase:
    name: str
    method: str
    path: str
    target_ms: float
    requests: int
    workers: int
    ok_statuses: tuple[int, ...] = (200,)


def percentile(values: list[float], pct: float) -> float:
    ordered = sorted(values)
    if not ordered:
        return 0.0
    return ordered[min(len(ordered) - 1, int(round((pct / 100) * (len(ordered) - 1))))]


def request_once(case: EndpointCase) -> tuple[float, int, str]:
    started = time.perf_counter()
    try:
        response = requests.request(case.method, f"{BASE_URL}{case.path}", auth=AUTH, timeout=20)
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


def bulk_burst() -> tuple[float, bool]:
    started = time.perf_counter()
    with cf.ThreadPoolExecutor(max_workers=5) as pool:
        results = list(pool.map(
            lambda st: request_once(EndpointCase(
                "DELETE bulk item",
                "DELETE",
                f"/api/admin/transport/tasks/{TASK_ID}/sts/{quote(st)}",
                800,
                1,
                1,
                (404,),
            )),
            ST_NUMBERS,
        ))
    elapsed = (time.perf_counter() - started) * 1000
    ok = all(status == 404 for _, status, _ in results)
    return elapsed, ok


def run_bulk_case() -> bool:
    results = [bulk_burst() for _ in range(20)]
    latencies = [elapsed for elapsed, _ in results]
    failures = [r for r in results if not r[1]]
    p95 = percentile(latencies, 95)
    avg = statistics.mean(latencies) if latencies else 0.0
    target = 800.0
    print(f"DELETE bulk burst x5: avg={avg:.1f}ms p95={p95:.1f}ms target={target:.0f}ms failures={len(failures)}")
    return not failures and p95 <= target


def main() -> int:
    cases = [
        EndpointCase(
            "DELETE /tasks/{id}/sts/{st}",
            "DELETE",
            f"/api/admin/transport/tasks/{TASK_ID}/sts/{quote(ST_NUMBERS[0])}",
            300,
            30,
            5,
            (404,),
        ),
        EndpointCase(
            "GET /tasks/{id}/sts",
            "GET",
            f"/api/admin/transport/tasks/{TASK_ID}/sts",
            200,
            30,
            5,
            (200,),
        ),
    ]
    for case in cases:
        request_once(case)
    ok = True
    for case in cases:
        ok = run_case(case) and ok
    ok = run_bulk_case() and ok
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
