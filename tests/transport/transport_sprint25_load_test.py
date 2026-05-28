"""Windows-safe load check for Sprint 25 (detach from billing)."""

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


@dataclass
class EndpointCase:
    name: str
    method: str
    path: str
    target_ms: float
    requests: int
    workers: int


def percentile(values: list[float], pct: float) -> float:
    ordered = sorted(values)
    if not ordered:
        return 0.0
    return ordered[min(len(ordered) - 1, int(round((pct / 100) * (len(ordered) - 1))))]


def request_once(case: EndpointCase) -> tuple[float, int, str]:
    started = time.perf_counter()
    try:
        response = requests.request(case.method, f"{BASE_URL}{case.path}", auth=AUTH, timeout=20)
        return (time.perf_counter() - started) * 1000, response.status_code, response.text[:240]
    except Exception as exc:  # noqa: BLE001
        return (time.perf_counter() - started) * 1000, 0, repr(exc)


def run_case(case: EndpointCase) -> bool:
    with cf.ThreadPoolExecutor(max_workers=case.workers) as pool:
        results = list(pool.map(lambda _: request_once(case), range(case.requests)))
    latencies = [elapsed for elapsed, _, _ in results]
    failures = [(status, body) for _, status, body in results if status != 200]
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


def sample_order_id() -> int:
    response = requests.get(f"{BASE_URL}/api/admin/transport/billing/orders", auth=AUTH, timeout=20)
    if response.status_code != 200:
        raise RuntimeError(f"billing list failed: HTTP {response.status_code} {response.text[:240]}")
    orders = response.json()
    if not orders:
        raise RuntimeError("No billing order available for Sprint 25 load gate")
    return int(orders[0]["order_id"])


def main() -> int:
    order_id = sample_order_id()
    for path in (
        "/api/admin/transport/billing/orders",
        f"/api/admin/transport/billing/orders/{order_id}/tasks",
        "/api/admin/transport/billing/companies",
    ):
        requests.get(f"{BASE_URL}{path}", auth=AUTH, timeout=20)
    cases = [
        EndpointCase("GET /billing/orders", "GET", "/api/admin/transport/billing/orders", 300, 50, 6),
        EndpointCase("GET /billing/orders/{id}/tasks", "GET", f"/api/admin/transport/billing/orders/{order_id}/tasks", 300, 50, 6),
        EndpointCase("GET /billing/companies", "GET", "/api/admin/transport/billing/companies", 200, 40, 5),
    ]
    ok = True
    for case in cases:
        ok = run_case(case) and ok
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
