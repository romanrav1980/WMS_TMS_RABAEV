"""
Windows-safe load check for TMS-2 Sprint 16 (billing status lifecycle).

Checks:
  GET   /billing/orders/{id}        p95 <= 300 ms
  PATCH /billing/orders/{id}/close  p95 <= 500 ms
  PATCH /billing/orders/{id}/pay    p95 <= 500 ms

Run:
    python tests/transport/transport_sprint16_load_test.py
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
    ok_statuses: set[int] | None = None


def percentile(values: list[float], pct: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    index = min(len(ordered) - 1, int(round((pct / 100) * (len(ordered) - 1))))
    return ordered[index]


def request_once(case: EndpointCase) -> tuple[float, int, str]:
    started = time.perf_counter()
    try:
        response = requests.request(case.method, f"{BASE_URL}{case.path}", auth=AUTH, timeout=20)
        elapsed_ms = (time.perf_counter() - started) * 1000
        return elapsed_ms, response.status_code, response.text[:240]
    except Exception as exc:  # noqa: BLE001 - load runner must report transport failures.
        elapsed_ms = (time.perf_counter() - started) * 1000
        return elapsed_ms, 0, repr(exc)


def run_case(case: EndpointCase) -> bool:
    with cf.ThreadPoolExecutor(max_workers=case.workers) as pool:
        results = list(pool.map(lambda _: request_once(case), range(case.requests)))

    latencies = [elapsed for elapsed, _, _ in results]
    ok_statuses = case.ok_statuses or set(range(200, 300))
    failures = [(status, body) for _, status, body in results if status not in ok_statuses]
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


def create_order(company: str) -> int:
    response = requests.post(
        f"{BASE_URL}/api/admin/transport/billing/orders",
        auth=AUTH,
        json={"company": company, "date_from": PLAN_DATE, "date_to": PLAN_DATE},
        timeout=20,
    )
    if response.status_code not in (200, 201):
        raise RuntimeError(f"order setup failed: HTTP {response.status_code} {response.text[:240]}")
    return int(response.json()["order_id"])


def main() -> int:
    read_order_id = create_order("ООО Нагрузка-16-GET")
    close_order_id = create_order("ООО Нагрузка-16-CLOSE")
    pay_order_id = create_order("ООО Нагрузка-16-PAY")

    close_response = requests.patch(
        f"{BASE_URL}/api/admin/transport/billing/orders/{pay_order_id}/close",
        auth=AUTH,
        timeout=20,
    )
    if close_response.status_code not in (200, 409):
        raise RuntimeError(f"pay setup close failed: HTTP {close_response.status_code} {close_response.text[:240]}")

    cases = [
        EndpointCase(
            name="GET /billing/orders/{id}",
            method="GET",
            path=f"/api/admin/transport/billing/orders/{read_order_id}",
            target_ms=300,
            requests=70,
            workers=8,
        ),
        EndpointCase(
            name="PATCH /billing/orders/{id}/close",
            method="PATCH",
            path=f"/api/admin/transport/billing/orders/{close_order_id}/close",
            target_ms=500,
            requests=20,
            workers=2,
            ok_statuses={200, 409},
        ),
        EndpointCase(
            name="PATCH /billing/orders/{id}/pay",
            method="PATCH",
            path=f"/api/admin/transport/billing/orders/{pay_order_id}/pay",
            target_ms=500,
            requests=20,
            workers=2,
            ok_statuses={200, 409},
        ),
    ]

    ok = True
    for case in cases:
        ok = run_case(case) and ok
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
