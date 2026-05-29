"""
Wave 3 Business Factor Trace load gate.

This runner measures the business-process endpoints used by the daily
planner, and validates that responses still carry the factor evidence under
load.  It is intentionally no-mutation.

Run:
    python tests/transport/transport_wave3_business_factor_load_test.py
"""

from __future__ import annotations

import concurrent.futures as cf
import os
import statistics
import time
from dataclasses import dataclass

import requests


BASE_URL = os.environ.get("TMS_API_BASE_URL", "http://127.0.0.1:8088").rstrip("/")
AUTH = tuple(os.environ.get("TMS_AUTH", "admin:admin123").split(":", 1))
PLAN_DATE = os.environ.get("TMS_WAVE3_PLAN_DATE", "2026-05-24")
AVAILABLE_STS_CONTRACT = {"ST_NUMBER", "ADDR", "RAION", "PALLETS_COUNT", "WEIGHT_KG", "WARE_ID", "VERIFY_PERC"}
PLANNER_ORDERS_CONTRACT = {
    "ST_NUMBER",
    "LAT",
    "LON",
    "PALLETS_COUNT",
    "WEIGHT_KG",
    "WARE_ID",
    "TRANSPORT_TYPE",
    "TIME_FROM",
    "TIME_TO",
    "UNLOAD_NORM_MIN",
    "VERIFY_PERC",
    "TW_STRICT",
}
VRP_STOP_CONTRACT = {"st_number", "lat", "lon", "pallets", "weight_kg", "ware_id", "tw_from", "tw_to", "unload_norm_min"}


@dataclass(frozen=True)
class Case:
    name: str
    method: str
    path: str
    requests: int
    workers: int
    target_p95_ms: float
    json_body: dict | None = None


def _request(case: Case) -> tuple[float, int, str]:
    started = time.perf_counter()
    try:
        response = requests.request(
            case.method,
            f"{BASE_URL}{case.path}",
            auth=AUTH,
            json=case.json_body,
            timeout=120,
        )
        elapsed_ms = (time.perf_counter() - started) * 1000
        return elapsed_ms, response.status_code, response.text
    except Exception as exc:  # noqa: BLE001
        elapsed_ms = (time.perf_counter() - started) * 1000
        return elapsed_ms, 0, repr(exc)


def _p95(values: list[float]) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    return ordered[min(len(ordered) - 1, int(round(0.95 * (len(ordered) - 1))))]


def _assert_business_payload(case: Case, body: str) -> None:
    data = requests.models.complexjson.loads(body)
    if "available-sts" in case.path:
        assert isinstance(data, list) and data, "available-sts returned empty data"
        for row in data[:20]:
            missing = AVAILABLE_STS_CONTRACT - set(row)
            assert not missing, f"available-sts contract violation under load: missing {missing}"
        assert len({int(row.get("PALLETS_COUNT") or 0) for row in data[:80]}) >= 2, (
            "available-sts PALLETS_COUNT is default-locked under load"
        )
        assert any(float(row.get("WEIGHT_KG") or 0) > 0 for row in data[:80]), (
            "available-sts WEIGHT_KG is zero under load"
        )
    elif "planner/orders" in case.path:
        assert isinstance(data, list) and data, "planner/orders returned empty data"
        for row in data[:20]:
            missing = PLANNER_ORDERS_CONTRACT - set(row)
            assert not missing, f"planner/orders contract violation under load: missing {missing}"
        assert len({int(row.get("PALLETS_COUNT") or 0) for row in data[:80]}) >= 2, (
            "planner/orders PALLETS_COUNT is default-locked under load"
        )
        assert any(float(row.get("WEIGHT_KG") or 0) > 0 for row in data[:80]), (
            "planner/orders WEIGHT_KG is zero under load"
        )
    elif "vehicles/available" in case.path:
        assert isinstance(data, list) and data, "vehicles/available returned empty data"
        row = data[0]
        required = {"vehicle_id", "status"}
        missing = required - set(row)
        assert not missing, f"vehicles/available misses forecast fields: {missing}"
    elif "routing/status" in case.path:
        assert data.get("active_provider") in ("osrm", "valhalla", "haversine")
        assert data.get("haversine_available") is True
    elif "planner/solve" in case.path:
        assert data.get("routes"), "planner/solve returned no routes"
        stops = [stop for route in data["routes"] for stop in route.get("stops", [])]
        assert stops, "planner/solve returned routes without stops"
        for stop in stops[:50]:
            missing = VRP_STOP_CONTRACT - set(stop)
            assert not missing, f"planner/solve stop contract violation under load: missing {missing}"
            assert 0 <= int(stop["tw_from"]) <= int(stop["tw_to"]) <= 1440
        assert any(int(stop.get("tw_from") or 0) != 0 or int(stop.get("tw_to") or 1080) != 1080 for stop in stops), (
            "planner/solve TW values are all default under load"
        )


def _run_case(case: Case) -> bool:
    durations: list[float] = []
    errors: list[str] = []
    with cf.ThreadPoolExecutor(max_workers=case.workers) as pool:
        futures = [pool.submit(_request, case) for _ in range(case.requests)]
        for future in cf.as_completed(futures):
            elapsed_ms, status, body = future.result()
            durations.append(elapsed_ms)
            if status != 200:
                errors.append(f"HTTP {status}: {body}")
                continue
            try:
                _assert_business_payload(case, body)
            except Exception as exc:  # noqa: BLE001
                errors.append(str(exc))

    avg = statistics.mean(durations) if durations else 0.0
    p95 = _p95(durations)
    print(
        f"{case.name}: count={len(durations)} avg={avg:.1f}ms "
        f"p95={p95:.1f}ms target={case.target_p95_ms:.0f}ms errors={len(errors)}"
    )
    if errors:
        print(f"  first error: {errors[0]}")
    if p95 > case.target_p95_ms:
        print(f"  NFR FAIL: p95 {p95:.1f}ms > {case.target_p95_ms:.0f}ms")
    return not errors and p95 <= case.target_p95_ms


def main() -> int:
    solve_body = {
        "plan_date": PLAN_DATE,
        "time_limit_s": 15,
        "source": "auto",
        "solver": "savings",
    }
    cases = [
        Case(
            "Wave3 GET available STs with data contract",
            "GET",
            f"/api/admin/transport/available-sts?stdate={PLAN_DATE}&unassigned_only=true",
            requests=24,
            workers=4,
            target_p95_ms=900,
        ),
        Case(
            "Wave3 GET planner orders with factor contract",
            "GET",
            f"/api/admin/transport/planner/orders?date={PLAN_DATE}",
            requests=24,
            workers=4,
            target_p95_ms=900,
        ),
        Case(
            "Wave3 GET vehicle availability forecast",
            "GET",
            f"/api/admin/transport/vehicles/available?shipment_time={PLAN_DATE}%2006:00&pallets=1",
            requests=24,
            workers=4,
            target_p95_ms=700,
        ),
        Case(
            "Wave3 GET routing provider status",
            "GET",
            "/api/admin/transport/routing/status",
            requests=8,
            workers=2,
            target_p95_ms=6_000,
        ),
        Case(
            "Wave3 POST planner solve with factor contract",
            "POST",
            "/api/admin/transport/planner/solve",
            requests=4,
            workers=2,
            target_p95_ms=60_000,
            json_body=solve_body,
        ),
    ]

    ok = True
    for case in cases:
        _request(case)
        ok = _run_case(case) and ok
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
