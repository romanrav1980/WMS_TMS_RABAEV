"""
transport_sprint7_load_test.py — Load tests for Sprint 7 planner map endpoints.

Run:
    python tests/transport/transport_sprint7_load_test.py --users=5 --duration=30
"""

from __future__ import annotations

import argparse
import statistics
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from typing import Any

import requests


DEFAULT_BASE_URL = "http://127.0.0.1:8088"
AUTH = ("admin", "admin123")
PLAN_DATE = "2026-05-25"
NFR = {
    "GET /planner/orders": 600,
    "GET /planner/orders type": 600,
    "GET /routing/status": 200,
}


def p95(values: list[float]) -> float:
    ordered = sorted(values)
    return ordered[min(int(len(ordered) * 0.95), len(ordered) - 1)]


class Client:
    def __init__(self, base_url: str) -> None:
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()
        self.session.auth = AUTH

    def get(self, path: str, **kwargs: Any) -> tuple[int, float]:
        started = time.perf_counter()
        response = self.session.get(f"{self.base_url}{path}", timeout=30, **kwargs)
        return response.status_code, (time.perf_counter() - started) * 1000


def worker(base_url: str, deadline: float):
    client = Client(base_url)
    samples: dict[str, list[float]] = {}
    errors: dict[str, int] = {}

    while time.time() < deadline:
        for label, path, params in [
            ("GET /planner/orders", "/api/admin/transport/planner/orders", {"date": PLAN_DATE}),
            ("GET /planner/orders type", "/api/admin/transport/planner/orders", {"date": PLAN_DATE, "transport_type": "10"}),
            ("GET /routing/status", "/api/admin/transport/routing/status", {}),
        ]:
            status, ms = client.get(path, params=params)
            samples.setdefault(label, []).append(ms)
            if status != 200:
                errors[label] = errors.get(label, 0) + 1
    return samples, errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL)
    parser.add_argument("--users", type=int, default=5)
    parser.add_argument("--duration", type=int, default=30)
    args = parser.parse_args()

    deadline = time.time() + args.duration
    merged: dict[str, list[float]] = {}
    errors: dict[str, int] = {}

    with ThreadPoolExecutor(max_workers=args.users) as pool:
        futures = [pool.submit(worker, args.base_url, deadline) for _ in range(args.users)]
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
