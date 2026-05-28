"""
Load test for TMS-2 Sprint 3 routes view.

Run:
    python tests/transport/transport_sprint3_load_test.py --users=5 --duration=20
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
    "GET /tasks": 1800,
    "GET /tasks/{id}/sts": 1200,
}


def p95(values: list[float]) -> float:
    ordered = sorted(values)
    return ordered[min(int(len(ordered) * 0.95), len(ordered) - 1)]


def timed(fn):
    started = time.perf_counter()
    response = fn()
    return response, (time.perf_counter() - started) * 1000


def ensure_task(base_url: str, stdate: str) -> int:
    session = requests.Session()
    session.auth = AUTH
    session.headers.update({"Content-Type": "application/json"})
    created = session.post(
        f"{base_url}/api/admin/transport/tasks",
        json={"transtype": "10", "shipment_date": stdate},
        timeout=30,
    )
    created.raise_for_status()
    return int(created.json()["task_id"])


def worker(base_url: str, stdate: str, task_id: int, deadline: float):
    session = requests.Session()
    session.auth = AUTH
    samples: dict[str, list[float]] = {}
    errors: dict[str, int] = {}
    while time.time() < deadline:
        response, ms = timed(lambda: session.get(
            f"{base_url}/api/admin/transport/tasks",
            params={"shipment_date": stdate, "include_readiness": "true"},
            timeout=30,
        ))
        samples.setdefault("GET /tasks", []).append(ms)
        if response.status_code != 200:
            errors["GET /tasks"] = errors.get("GET /tasks", 0) + 1

        response, ms = timed(lambda: session.get(
            f"{base_url}/api/admin/transport/tasks/{task_id}/sts",
            timeout=30,
        ))
        samples.setdefault("GET /tasks/{id}/sts", []).append(ms)
        if response.status_code != 200:
            errors["GET /tasks/{id}/sts"] = errors.get("GET /tasks/{id}/sts", 0) + 1
    return samples, errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL)
    parser.add_argument("--stdate", default=DEFAULT_STDATE)
    parser.add_argument("--users", type=int, default=5)
    parser.add_argument("--duration", type=int, default=20)
    args = parser.parse_args()
    base_url = args.base_url.rstrip("/")
    task_id = ensure_task(base_url, args.stdate)
    try:
        deadline = time.time() + args.duration
        merged: dict[str, list[float]] = {}
        errors: dict[str, int] = {}
        with ThreadPoolExecutor(max_workers=args.users) as pool:
            futures = [pool.submit(worker, base_url, args.stdate, task_id, deadline) for _ in range(args.users)]
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
    finally:
        cleanup = requests.Session()
        cleanup.auth = AUTH
        cleanup.post(f"{base_url}/api/admin/transport/tasks/{task_id}/cancel", timeout=30)


if __name__ == "__main__":
    sys.exit(main())

