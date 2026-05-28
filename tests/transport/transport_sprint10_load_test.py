"""Windows-safe load gate for Sprint 10 analytics endpoints."""
from __future__ import annotations

import os
import statistics
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests

BASE_URL = os.environ.get("TMS_API_BASE_URL", "http://127.0.0.1:8088")
AUTH = tuple(os.environ.get("TMS_AUTH", "admin:admin123").split(":", 1))


def call(path: str) -> tuple[float, int, str]:
    started = time.perf_counter()
    try:
        response = requests.get(f"{BASE_URL}{path}", auth=AUTH, timeout=30)
        return (time.perf_counter() - started) * 1000, response.status_code, response.text[:200]
    except Exception as exc:  # noqa: BLE001
        return (time.perf_counter() - started) * 1000, 0, str(exc)


def p95(values: list[float]) -> float:
    if not values:
        return 0.0
    if len(values) < 20:
        return max(values)
    return statistics.quantiles(values, n=100)[94]


def run_group(name: str, path: str, count: int, workers: int, nfr_ms: float) -> dict:
    durations: list[float] = []
    errors: list[str] = []
    with ThreadPoolExecutor(max_workers=workers) as pool:
        futures = [pool.submit(call, path) for _ in range(count)]
        for future in as_completed(futures):
            elapsed_ms, status, text = future.result()
            durations.append(elapsed_ms)
            if status != 200:
                errors.append(f"status={status} {text}")
    value = p95(durations)
    return {
        "name": name,
        "count": count,
        "errors": len(errors),
        "first_error": errors[0] if errors else None,
        "mean_ms": round(statistics.mean(durations), 1) if durations else 0,
        "p95_ms": round(value, 1),
        "nfr_ms": nfr_ms,
        "nfr_ok": not errors and value <= nfr_ms,
    }


def main() -> None:
    results = [
        run_group(
            "GET /planner/history",
            "/api/admin/transport/planner/history?date_from=2026-05-01&date_to=2026-05-28",
            count=80,
            workers=8,
            nfr_ms=800,
        ),
        run_group(
            "GET /planner/demand-forecast",
            "/api/admin/transport/planner/demand-forecast?target_date=2026-05-25&lookback_weeks=8",
            count=80,
            workers=8,
            nfr_ms=800,
        ),
    ]
    print({item["name"]: item for item in results})
    if any(not item["nfr_ok"] for item in results):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
