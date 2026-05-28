"""
Load test for TMS-2 Sprint 1 /available-sts.

Run:
    python tests/transport/transport_sprint1_load_test.py --users=5 --duration=20
"""

from __future__ import annotations

import argparse
import statistics
import time
from concurrent.futures import ThreadPoolExecutor
from typing import Any

import requests


AUTH = ("admin", "admin123")
DEFAULT_BASE_URL = "http://127.0.0.1:8088"
DEFAULT_STDATE = "2026-05-25"
NFR_P95_MS = 2500


def percentile(values: list[float], pct: float) -> float:
    ordered = sorted(values)
    idx = min(int(len(ordered) * pct), len(ordered) - 1)
    return ordered[idx]


def one_request(session: requests.Session, base_url: str, stdate: str, iteration: int) -> tuple[bool, float, int]:
    params: dict[str, Any] = {"stdate": stdate, "unassigned_only": "true"}
    if iteration % 4 == 1:
        params["transport_type"] = "10"
    elif iteration % 4 == 2:
        params["addr_mask"] = "Перм"
    elif iteration % 4 == 3:
        params["max_weight_kg"] = "999999"
    started = time.perf_counter()
    response = session.get(f"{base_url.rstrip('/')}/api/admin/transport/available-sts", params=params, timeout=30)
    elapsed_ms = (time.perf_counter() - started) * 1000
    return response.status_code == 200, elapsed_ms, response.status_code


def worker(base_url: str, stdate: str, deadline: float, worker_id: int) -> tuple[list[float], list[int]]:
    session = requests.Session()
    session.auth = AUTH
    latencies: list[float] = []
    errors: list[int] = []
    iteration = worker_id
    while time.time() < deadline:
        ok, elapsed_ms, status = one_request(session, base_url, stdate, iteration)
        latencies.append(elapsed_ms)
        if not ok:
            errors.append(status)
        iteration += 1
    return latencies, errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL)
    parser.add_argument("--stdate", default=DEFAULT_STDATE)
    parser.add_argument("--users", type=int, default=5)
    parser.add_argument("--duration", type=int, default=20)
    args = parser.parse_args()

    deadline = time.time() + args.duration
    latencies: list[float] = []
    errors: list[int] = []

    with ThreadPoolExecutor(max_workers=args.users) as pool:
        futures = [pool.submit(worker, args.base_url, args.stdate, deadline, i) for i in range(args.users)]
        for future in futures:
            worker_latencies, worker_errors = future.result()
            latencies.extend(worker_latencies)
            errors.extend(worker_errors)

    if not latencies:
        print("No samples collected")
        return 2

    p95 = percentile(latencies, 0.95)
    report = {
        "samples": len(latencies),
        "errors": len(errors),
        "mean_ms": round(statistics.mean(latencies), 1),
        "p95_ms": round(p95, 1),
        "p99_ms": round(percentile(latencies, 0.99), 1),
        "nfr_p95_ms": NFR_P95_MS,
        "nfr_ok": p95 <= NFR_P95_MS and not errors,
    }
    print(report)
    return 0 if report["nfr_ok"] else 1


if __name__ == "__main__":
    import sys

    sys.exit(main())
