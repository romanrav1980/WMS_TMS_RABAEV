"""
Windows-safe load check for TMS-2 Sprint 11 (ARM/Gantt operations).

Checks the operational chain endpoints without Locust:
  POST  /tasks/{id}/plan-operations  p95 <= 500 ms
  GET   /tasks/{id}/operations       p95 <= 200 ms
  PATCH /operations/{op_id}/fact     p95 <= 300 ms
  GET   /vehicles/gantt              p95 <= 500 ms

Run:
    python tests/transport/transport_sprint11_load_test.py
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
    json_payload: dict | None = None
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
            json=case.json_payload,
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


def setup_task() -> tuple[int, list[int]]:
    response = requests.post(
        f"{BASE_URL}/api/admin/transport/tasks",
        auth=AUTH,
        json={"transtype": "Газель", "shipment_date": PLAN_DATE},
        timeout=20,
    )
    if response.status_code not in (200, 201):
        raise RuntimeError(f"task setup failed: HTTP {response.status_code} {response.text[:240]}")

    task_id = int(response.json()["task_id"])
    ops_response = requests.post(
        f"{BASE_URL}/api/admin/transport/tasks/{task_id}/plan-operations",
        auth=AUTH,
        timeout=20,
    )
    if ops_response.status_code != 200:
        raise RuntimeError(f"operation setup failed: HTTP {ops_response.status_code} {ops_response.text[:240]}")

    op_ids = [int(row["op_id"]) for row in ops_response.json()]
    if not op_ids:
        raise RuntimeError("operation setup returned an empty chain")
    return task_id, op_ids


def main() -> int:
    task_id, op_ids = setup_task()
    first_op_id = op_ids[0]
    cases = [
        EndpointCase(
            name="GET /tasks/{id}/operations",
            method="GET",
            path=f"/api/admin/transport/tasks/{task_id}/operations",
            target_ms=200,
            requests=70,
            workers=8,
        ),
        EndpointCase(
            name="PATCH /operations/{id}/fact",
            method="PATCH",
            path=f"/api/admin/transport/operations/{first_op_id}/fact",
            target_ms=300,
            requests=40,
            workers=4,
            json_payload={"fact_start": "2026-05-25 06:05", "fact_end": "2026-05-25 06:17"},
        ),
        EndpointCase(
            name="GET /vehicles/gantt",
            method="GET",
            path="/api/admin/transport/vehicles/gantt",
            target_ms=500,
            requests=60,
            workers=8,
            params={"gantt_date": PLAN_DATE},
        ),
        EndpointCase(
            name="POST /tasks/{id}/plan-operations",
            method="POST",
            path=f"/api/admin/transport/tasks/{task_id}/plan-operations",
            target_ms=500,
            requests=25,
            workers=3,
        ),
    ]

    ok = True
    for case in cases:
        ok = run_case(case) and ok
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
