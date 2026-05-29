"""
Final sprint acceptance for the daily transport planning example.

The gate is intentionally narrow: one dated daily request set is optimized into
routes, route capacity and time-window data are visible in the plan, and the
Dobrotseny seed fleet can cover four dispatch slots in the day.
"""

from __future__ import annotations

from collections import Counter
import os

import requests


BASE_URL = os.environ.get("TMS_API_BASE_URL", "http://127.0.0.1:8088").rstrip("/")
AUTH = ("admin", "admin123")
PLAN_DATE = os.environ.get("TMS_FINAL_PLAN_DATE", "2026-05-24")
SEED_VEHICLE_IDS = set(range(9201, 9216))
DISPATCH_SLOTS = ("06:00", "10:00", "14:00", "18:00")


def _session() -> requests.Session:
    s = requests.Session()
    s.auth = AUTH
    s.headers.update({"Content-Type": "application/json"})
    return s


def _get_json(session: requests.Session, path: str, **params):
    response = session.get(f"{BASE_URL}{path}", params=params, timeout=60)
    assert response.status_code == 200, f"{path} failed: {response.status_code} {response.text}"
    return response.json()


def test_daily_order_set_exists_and_has_real_load():
    session = _session()
    sts = _get_json(
        session,
        "/api/admin/transport/available-sts",
        stdate=PLAN_DATE,
        unassigned_only="true",
    )
    assert len(sts) >= 300, f"Expected a full daily request set, got {len(sts)} ST"
    assert sum(int(row.get("PALLETS_COUNT") or 0) for row in sts) > 0


def test_seed_fleet_can_cover_four_dispatch_slots_with_availability_forecast():
    session = _session()
    sts = _get_json(
        session,
        "/api/admin/transport/available-sts",
        stdate=PLAN_DATE,
        unassigned_only="true",
    )
    daily_pallets = sum(int(row.get("PALLETS_COUNT") or 0) for row in sts)

    vehicles = _get_json(session, "/api/admin/transport/vehicles")
    seed_vehicles = [v for v in vehicles if int(v.get("ID") or 0) in SEED_VEHICLE_IDS]
    found_ids = {int(v.get("ID") or 0) for v in seed_vehicles}
    missing = sorted(SEED_VEHICLE_IDS - found_ids)
    assert not missing, f"Missing Dobrotseny seed vehicles: {missing}"
    assert all(int(v.get("PALLETS") or 0) > 0 for v in seed_vehicles)

    four_trip_capacity = sum(int(v.get("PALLETS") or 0) * 4 for v in seed_vehicles)
    assert four_trip_capacity >= daily_pallets, (
        f"4 trips per seed vehicle capacity {four_trip_capacity} pallets "
        f"is below daily demand {daily_pallets}"
    )

    for slot in DISPATCH_SLOTS:
        available = _get_json(
            session,
            "/api/admin/transport/vehicles/available",
            shipment_time=f"{PLAN_DATE} {slot}",
            pallets=1,
        )
        by_id = {int(v.get("vehicle_id") or 0): v for v in available}
        blocked = [
            vehicle_id
            for vehicle_id in sorted(SEED_VEHICLE_IDS)
            if by_id.get(vehicle_id, {}).get("status") == "red"
        ]
        assert not blocked, f"Seed vehicles unavailable/red at {slot}: {blocked}"


def test_daily_vrp_plan_uses_capacity_time_windows_and_current_fleet():
    session = _session()
    routing = _get_json(session, "/api/admin/transport/routing/status")
    assert routing["active_provider"] in ("osrm", "valhalla", "haversine")
    assert routing["haversine_available"] is True

    response = session.post(
        f"{BASE_URL}/api/admin/transport/planner/solve",
        json={
            "plan_date": PLAN_DATE,
            "time_limit_s": 15,
            "source": "auto",
            "solver": "savings",
        },
        timeout=120,
    )
    assert response.status_code == 200, f"Planner solve failed: {response.status_code} {response.text}"
    plan = response.json()
    assert plan["routes"], "Daily plan must produce at least one route"
    assert plan["unassigned_sts"] == [], f"All daily STs must be assigned: {plan['unassigned_sts'][:10]}"

    route_counts = Counter()
    saw_time_window = False
    for route in plan["routes"]:
        route_counts[route["vehicle_num"]] += 1
        assert route["total_pallets"] <= route["max_pallets"], (
            f"Route for {route['vehicle_num']} exceeds capacity: "
            f"{route['total_pallets']} > {route['max_pallets']}"
        )
        for stop in route["stops"]:
            assert "tw_from" in stop and "tw_to" in stop
            assert 0 <= int(stop["tw_from"]) <= int(stop["tw_to"]) <= 1440
            if int(stop["tw_from"]) != 0 or int(stop["tw_to"]) != 1080:
                saw_time_window = True
    assert saw_time_window, "VRP plan did not expose any non-default store time window"
    assert max(route_counts.values()) <= 4, f"One vehicle received more than 4 routes: {route_counts}"
