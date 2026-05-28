"""Windows-safe load gate for Sprint 9 cluster/templates endpoints."""
from __future__ import annotations

import os
import statistics
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests

BASE_URL = os.environ.get("TMS_API_BASE_URL", "http://127.0.0.1:8088")
AUTH = tuple(os.environ.get("TMS_AUTH", "admin:admin123").split(":", 1))
PLAN_DATE = os.environ.get("TMS_SPRINT9_DATE", "2026-05-25")


def call(method: str, path: str, **kwargs) -> tuple[float, int, str]:
    started = time.perf_counter()
    try:
        response = requests.request(method, f"{BASE_URL}{path}", auth=AUTH, timeout=90, **kwargs)
        return (time.perf_counter() - started) * 1000, response.status_code, response.text[:200]
    except Exception as exc:  # noqa: BLE001
        return (time.perf_counter() - started) * 1000, 0, str(exc)


def p95(values: list[float]) -> float:
    if not values:
        return 0.0
    if len(values) < 20:
        return max(values)
    return statistics.quantiles(values, n=100)[94]


def run_group(name: str, calls: list[tuple[str, str, dict]], workers: int, nfr_ms: float) -> dict:
    durations: list[float] = []
    errors: list[str] = []
    with ThreadPoolExecutor(max_workers=workers) as pool:
        futures = [pool.submit(call, method, path, **kwargs) for method, path, kwargs in calls]
        for future in as_completed(futures):
            elapsed_ms, status, text = future.result()
            durations.append(elapsed_ms)
            if status not in (200, 422):
                errors.append(f"status={status} {text}")
    value = p95(durations)
    return {
        "name": name,
        "count": len(durations),
        "errors": len(errors),
        "first_error": errors[0] if errors else None,
        "mean_ms": round(statistics.mean(durations), 1) if durations else 0,
        "p95_ms": round(value, 1),
        "nfr_ms": nfr_ms,
        "nfr_ok": not errors and value <= nfr_ms,
    }


def main() -> None:
    headers = {"Content-Type": "application/json"}
    solve_body = {
        "plan_date": PLAN_DATE,
        "solver": "cluster",
        "time_limit_s": 10,
        "source": "haversine",
    }
    results = [
        run_group(
            "POST /planner/solve cluster",
            [("POST", "/api/admin/transport/planner/solve", {"json": solve_body, "headers": headers}) for _ in range(6)],
            workers=2,
            nfr_ms=60_000,
        ),
        run_group(
            "GET /planner/templates",
            [
                ("GET", f"/api/admin/transport/planner/templates?plan_date={PLAN_DATE}&min_jaccard=0.1", {})
                for _ in range(60)
            ],
            workers=8,
            nfr_ms=800,
        ),
        run_group(
            "GET /planner/orders",
            [("GET", f"/api/admin/transport/planner/orders?date={PLAN_DATE}", {}) for _ in range(60)],
            workers=8,
            nfr_ms=600,
        ),
    ]
    print({item["name"]: item for item in results})
    if any(not item["nfr_ok"] for item in results):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
