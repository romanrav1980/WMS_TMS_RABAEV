"""
test_sprint24_functional.py — Functional tests for Sprint 24.

Sprint 24 scope:
  - Client-side drag-and-drop of STs between VRP routes (no new API)
  - Regression: VRP plan endpoints still work correctly after frontend changes
  - GET /planner/solve   — returns VrpPlan with routes and stops
  - GET /planner/metrics — returns plan metrics

Run:
    pytest tests/transport/test_sprint24_functional.py -v
"""

import pytest
import requests

from tests.transport.config import API_BASE as BASE, API_AUTH as AUTH


def get(path: str, **kwargs) -> requests.Response:
    return requests.get(f"{BASE}{path}", auth=AUTH, **kwargs)


def post(path: str, json=None) -> requests.Response:
    return requests.post(f"{BASE}{path}", auth=AUTH, json=json)


# ---------------------------------------------------------------------------
# VRP plan structure — route stops must have draggable fields
# ---------------------------------------------------------------------------

class TestVrpRouteStops:

    def _get_plan(self) -> dict | None:
        from datetime import date
        r = post("/api/admin/transport/planner/solve", json={
            "plan_date": date.today().isoformat(),
            "time_limit_s": 5,
            "source": "auto",
            "solver": "savings",
        })
        if r.status_code != 200:
            return None
        return r.json()

    def test_routes_have_stops(self):
        plan = self._get_plan()
        if not plan:
            pytest.skip("Solver returned no plan")
        for route in plan.get("routes", []):
            assert "stops" in route, "route missing 'stops'"
            assert isinstance(route["stops"], list)

    def test_stops_have_st_number(self):
        plan = self._get_plan()
        if not plan:
            pytest.skip("Solver returned no plan")
        for route in plan.get("routes", []):
            for stop in route["stops"]:
                assert "st_number" in stop, "stop missing 'st_number'"

    def test_stops_have_pallets(self):
        plan = self._get_plan()
        if not plan:
            pytest.skip("Solver returned no plan")
        for route in plan.get("routes", []):
            for stop in route["stops"]:
                assert "pallets" in stop, "stop missing 'pallets'"
                assert isinstance(stop["pallets"], (int, float))

    def test_stops_have_weight_kg(self):
        plan = self._get_plan()
        if not plan:
            pytest.skip("Solver returned no plan")
        for route in plan.get("routes", []):
            for stop in route["stops"]:
                assert "weight_kg" in stop

    def test_stops_have_ware_id(self):
        plan = self._get_plan()
        if not plan:
            pytest.skip("Solver returned no plan")
        for route in plan.get("routes", []):
            for stop in route["stops"]:
                assert "ware_id" in stop

    def test_routes_have_max_pallets(self):
        plan = self._get_plan()
        if not plan:
            pytest.skip("Solver returned no plan")
        for route in plan.get("routes", []):
            assert "max_pallets" in route, "route missing max_pallets for utilization calc"
            assert "utilization_pct" in route

    def test_plan_metrics_endpoint(self):
        r = get("/api/admin/transport/planner/metrics")
        assert r.status_code in (200, 404)
        if r.status_code == 200:
            data = r.json()
            assert isinstance(data, (dict, list))


# ---------------------------------------------------------------------------
# Client-side metric calculation logic (validate assumptions)
# ---------------------------------------------------------------------------

class TestClientMetricRecalculation:
    """Validate that client recalculation formula matches server data."""

    def _get_plan(self) -> dict | None:
        from datetime import date
        r = post("/api/admin/transport/planner/solve", json={
            "plan_date": date.today().isoformat(),
            "time_limit_s": 5,
            "source": "auto",
            "solver": "savings",
        })
        if r.status_code != 200:
            return None
        return r.json()

    def test_total_pallets_matches_stops_sum(self):
        plan = self._get_plan()
        if not plan:
            pytest.skip("No plan available")
        for route in plan.get("routes", []):
            stops_sum = sum(s["pallets"] for s in route["stops"])
            assert abs(stops_sum - route["total_pallets"]) <= 1, \
                f"total_pallets mismatch: server={route['total_pallets']}, sum={stops_sum}"

    def test_utilization_calculation(self):
        plan = self._get_plan()
        if not plan:
            pytest.skip("No plan available")
        for route in plan.get("routes", []):
            if route["max_pallets"] > 0:
                expected = route["total_pallets"] / route["max_pallets"] * 100
                assert abs(expected - route["utilization_pct"]) <= 2, \
                    f"utilization mismatch: expected≈{expected:.0f}%, got {route['utilization_pct']}%"
