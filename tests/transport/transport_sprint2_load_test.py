"""
Load test for TMS-2 Sprint 2 create-trip flow.

This is intentionally modest because it mutates Oracle state:
each worker repeatedly creates an empty trip and cancels it.
The ST assignment path is covered by functional tests to avoid
workers racing on the same free ST.

Run:
    python tests/transport/transport_sprint2_load_test.py --users=3 --duration=20
"""

from __future__ import annotations

import argparse
import statistics
import sys
import time
from concurrent.futures import ThreadPoolExecutor

import requests


AUTH = ("admin", "admin123")
DEFAULT_BASE_URL = "http://127.0.0.1:8088"
DEFAULT_STDATE = "2026-05-25"
NFR = {
    "GET /available-sts": 2500,
    "POST /tasks": 1500,
    "POST /tasks/{id}/cancel": 1500,
}


def p95(values: list[float]) -> float:
    ordered = sorted(values)
    return ordered[min(int(len(ordered) * 0.95), len(ordered) - 1)]


def timed(label: str, fn):
    started = time.perf_counter()
    response = fn()
    elapsed_ms = (time.perf_counter() - started) * 1000
    return label, response.status_code, elapsed_ms, response


def worker(base_url: str, stdate: str, deadline: float):
    session = requests.Session()
    session.auth = AUTH
    session.headers.update({"Content-Type": "application/json"})
    samples: dict[str, list[float]] = {}
    errors: dict[str, int] = {}
    while time.time() < deadline:
        label, status, ms, _ = timed(
            "GET /available-sts",
            lambda: session.get(
                f"{base_url}/api/admin/transport/available-sts",
                params={"stdate": stdate, "unassigned_only": "true"},
                timeout=30,
            ),
        )
        samples.setdefault(label, []).append(ms)
        if status != 200:
            errors[label] = errors.get(label, 0) + 1
            continue

        label, status, ms, response = timed(
            "POST /tasks",
            lambda: session.post(
                f"{base_url}/api/admin/transport/tasks",
                json={"transtype": "10", "shipment_date": stdate},
                timeout=30,
            ),
        )
        samples.setdefault(label, []).append(ms)
        if status != 200:
            errors[label] = errors.get(label, 0) + 1
            continue
        task_id = response.json()["task_id"]

        label, status, ms, _ = timed(
            "POST /tasks/{id}/cancel",
            lambda: session.post(f"{base_url}/api/admin/transport/tasks/{task_id}/cancel", timeout=30),
        )
        samples.setdefault(label, []).append(ms)
        if status != 200:
            errors[label] = errors.get(label, 0) + 1
    return samples, errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL)
    parser.add_argument("--stdate", default=DEFAULT_STDATE)
    parser.add_argument("--users", type=int, default=3)
    parser.add_argument("--duration", type=int, default=20)
    args = parser.parse_args()

    deadline = time.time() + args.duration
    merged: dict[str, list[float]] = {}
    errors: dict[str, int] = {}
    with ThreadPoolExecutor(max_workers=args.users) as pool:
        futures = [pool.submit(worker, args.base_url.rstrip("/"), args.stdate, deadline) for _ in range(args.users)]
        for future in futures:
            samples, worker_errors = future.result()
            for label, values in samples.items():
                merged.setdefault(label, []).extend(values)
            for label, count in worker_errors.items():
                errors[label] = errors.get(label, 0) + count

    report = {}
    ok = True
    for label, values in merged.items():
        value_p95 = p95(values)
        label_ok = value_p95 <= NFR[label] and errors.get(label, 0) == 0
        ok = ok and label_ok
        report[label] = {
            "count": len(values),
            "errors": errors.get(label, 0),
            "mean_ms": round(statistics.mean(values), 1),
            "p95_ms": round(value_p95, 1),
            "nfr_ms": NFR[label],
            "nfr_ok": label_ok,
        }
    print(report)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
