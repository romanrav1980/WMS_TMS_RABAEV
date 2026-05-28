"""
transport_sprint8_load_test.py — Windows-safe Sprint 8 load gate.

Run:
    python tests/transport/transport_sprint8_load_test.py
"""
from __future__ import annotations

import os
import statistics
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests


BASE_URL = os.environ.get("TMS_API_BASE_URL", "http://127.0.0.1:8088")
AUTH = tuple(os.environ.get("TMS_AUTH", "admin:admin123").split(":", 1))
PLAN_DATE = os.environ.get("TMS_SPRINT8_DATE", "2026-05-25")


def _request(method: str, path: str, **kwargs) -> tuple[str, float, int, str]:
    started = time.perf_counter()
    try:
        response = requests.request(
            method,
            f"{BASE_URL}{path}",
            auth=AUTH,
            timeout=kwargs.pop("timeout", 90),
            **kwargs,
        )
        elapsed_ms = (time.perf_counter() - started) * 1000
        return path, elapsed_ms, response.status_code, response.text[:300]
    except Exception as exc:  # noqa: BLE001 - load gate reports failures, not stack traces.
        elapsed_ms = (time.perf_counter() - started) * 1000
        return path, elapsed_ms, 0, str(exc)


def _p95(values: list[float]) -> float:
    if not values:
        return 0.0
    if len(values) < 20:
        return max(values)
    return statistics.quantiles(values, n=100)[94]


def _run_parallel(name: str, calls: list[tuple[str, str, dict]], workers: int, nfr_ms: float) -> dict:
    durations: list[float] = []
    errors: list[str] = []
    with ThreadPoolExecutor(max_workers=workers) as pool:
        futures = [
            pool.submit(_request, method, path, **kwargs)
            for method, path, kwargs in calls
        ]
        for future in as_completed(futures):
            path, elapsed_ms, status, text = future.result()
            durations.append(elapsed_ms)
            if status not in (200, 422):
                errors.append(f"{path}: status={status} {text}")
    p95 = _p95(durations)
    return {
        "name": name,
        "count": len(durations),
        "errors": len(errors),
        "first_error": errors[0] if errors else None,
        "mean_ms": round(statistics.mean(durations), 1) if durations else 0,
        "p95_ms": round(p95, 1),
        "nfr_ms": nfr_ms,
        "nfr_ok": not errors and p95 <= nfr_ms,
    }


def main() -> None:
    headers = {"Content-Type": "application/json"}
    solve_body = {
        "plan_date": PLAN_DATE,
        "time_limit_s": 10,
        "source": "haversine",
        "solver": "savings",
    }

    # Matrix rebuild and solver are intentionally low-concurrency: these are heavy jobs.
    results = [
        _run_parallel(
            "GET /planner/metrics",
            [("GET", "/api/admin/transport/planner/metrics", {}) for _ in range(80)],
            workers=8,
            nfr_ms=500,
        ),
        _run_parallel(
            "POST /planner/solve",
            [
                ("POST", "/api/admin/transport/planner/solve", {"json": solve_body, "headers": headers, "timeout": 120})
                for _ in range(6)
            ],
            workers=2,
            nfr_ms=60_000,
        ),
        _run_parallel(
            "POST /distance-matrix/rebuild",
            [
                (
                    "POST",
                    "/api/admin/transport/distance-matrix/rebuild?source=haversine",
                    {"headers": headers, "timeout": 120},
                )
                for _ in range(2)
            ],
            workers=1,
            nfr_ms=30_000,
        ),
    ]

    print({item["name"]: item for item in results})
    failed = [item for item in results if not item["nfr_ok"]]
    if failed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
