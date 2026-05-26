"""
test_sprint8_functional.py — Functional completeness tests for Sprint 8.

Sprint 8 scope: distance matrix + VRP optimizer
  - POST /distance-matrix/rebuild returns {pairs, source, addresses}
  - POST /planner/solve returns valid VrpPlan with routes + metrics
  - POST /planner/apply creates transport tasks
  - GET  /planner/metrics returns latest plan metrics

Run:
    pytest tests/transport/test_sprint8_functional.py -v
"""

from __future__ import annotations

import os
import pytest
import requests
from datetime import date, timedelta

BASE_URL = os.environ.get("TMS_API_BASE_URL", "http://127.0.0.1:8088")
AUTH = ("admin", "admin123")
TOMORROW = (date.today() + timedelta(days=1)).isoformat()


@pytest.fixture(scope="session")
def api():
    s = requests.Session()
    s.auth = AUTH
    s.headers.update({"Content-Type": "application/json"})
    return s


# ---------------------------------------------------------------------------
# POST /distance-matrix/rebuild
# ---------------------------------------------------------------------------

class TestDistanceMatrixRebuild:
    def test_rebuild_haversine_returns_200(self, api):
        r = api.post(f"{BASE_URL}/api/admin/transport/distance-matrix/rebuild",
                     params={"source": "haversine"})
        assert r.status_code == 200, f"Expected 200, got {r.status_code}: {r.text}"

    def test_rebuild_returns_required_fields(self, api):
        r = api.post(f"{BASE_URL}/api/admin/transport/distance-matrix/rebuild",
                     params={"source": "haversine"})
        data = r.json()
        assert "pairs" in data, "Missing 'pairs'"
        assert "source" in data, "Missing 'source'"
        assert "addresses" in data, "Missing 'addresses'"

    def test_source_is_haversine(self, api):
        r = api.post(f"{BASE_URL}/api/admin/transport/distance-matrix/rebuild",
                     params={"source": "haversine"})
        assert r.json()["source"] == "haversine"

    def test_pairs_equals_addresses_squared_minus_diagonal(self, api):
        r = api.post(f"{BASE_URL}/api/admin/transport/distance-matrix/rebuild",
                     params={"source": "haversine"})
        data = r.json()
        n = data["addresses"]
        expected_pairs = n * (n - 1) if n > 0 else 0
        assert data["pairs"] == expected_pairs, (
            f"Expected {expected_pairs} pairs for {n} addresses, got {data['pairs']}"
        )

    def test_auto_source_available(self, api):
        r = api.post(f"{BASE_URL}/api/admin/transport/distance-matrix/rebuild",
                     params={"source": "auto"})
        assert r.status_code == 200
        assert r.json()["source"] in ("haversine", "osrm", "valhalla")


# ---------------------------------------------------------------------------
# POST /planner/solve
# ---------------------------------------------------------------------------

class TestPlannerSolve:
    @pytest.fixture(scope="class")
    def plan(self, api):
        r = api.post(f"{BASE_URL}/api/admin/transport/planner/solve",
                     json={"plan_date": TOMORROW, "time_limit_s": 15, "source": "haversine"})
        if r.status_code == 422 and "Нет активных ТС" in r.text:
            pytest.skip("Нет активных ТС в тестовой БД")
        assert r.status_code == 200, f"Expected 200: {r.text}"
        return r.json()

    def test_solve_returns_200(self, api):
        r = api.post(f"{BASE_URL}/api/admin/transport/planner/solve",
                     json={"plan_date": TOMORROW, "time_limit_s": 10, "source": "haversine"})
        assert r.status_code in (200, 422), f"Unexpected status {r.status_code}: {r.text}"

    def test_plan_has_required_fields(self, plan):
        required = {"routes", "unassigned_sts", "total_km", "fleet_utilization_pct",
                    "tw_violations", "score", "solver_used", "solve_time_ms"}
        missing = required - set(plan.keys())
        assert not missing, f"Missing fields: {missing}"

    def test_routes_is_list(self, plan):
        assert isinstance(plan["routes"], list)

    def test_solver_used_known(self, plan):
        known = {"ortools-cvrptw", "clarke-wright", "none"}
        assert plan["solver_used"] in known, f"Unknown solver: {plan['solver_used']}"

    def test_total_km_non_negative(self, plan):
        assert plan["total_km"] >= 0

    def test_utilization_between_0_and_100(self, plan):
        assert 0.0 <= plan["fleet_utilization_pct"] <= 100.0

    def test_tw_violations_non_negative(self, plan):
        assert plan["tw_violations"] >= 0

    def test_route_items_have_required_fields(self, plan):
        if not plan["routes"]:
            pytest.skip("Нет маршрутов в плане")
        required = {"vehicle_id", "vehicle_num", "vehicle_type", "max_pallets",
                    "total_pallets", "total_km", "utilization_pct", "stops"}
        for route in plan["routes"]:
            missing = required - set(route.keys())
            assert not missing, f"Route missing fields: {missing}"

    def test_stops_have_required_fields(self, plan):
        if not plan["routes"]:
            pytest.skip("Нет маршрутов в плане")
        required = {"st_number", "addr", "lat", "lon", "pallets", "weight_kg", "ware_id"}
        for route in plan["routes"]:
            for stop in route["stops"][:3]:
                missing = required - set(stop.keys())
                assert not missing, f"Stop missing fields: {missing}"

    def test_plan_id_is_integer(self, plan):
        if plan.get("plan_id") is not None:
            assert isinstance(plan["plan_id"], int)

    def test_solve_time_reasonable(self, plan):
        assert plan["solve_time_ms"] < 120_000, f"Solve took too long: {plan['solve_time_ms']}ms"


# ---------------------------------------------------------------------------
# GET /planner/metrics
# ---------------------------------------------------------------------------

class TestPlannerMetrics:
    def test_metrics_returns_200(self, api):
        r = api.get(f"{BASE_URL}/api/admin/transport/planner/metrics")
        assert r.status_code == 200, f"Expected 200: {r.text}"

    def test_metrics_required_fields(self, api):
        r = api.get(f"{BASE_URL}/api/admin/transport/planner/metrics")
        data = r.json()
        required = {"routes", "total_km", "fleet_utilization_pct",
                    "tw_violations", "score", "solver_used", "applied"}
        missing = required - set(data.keys())
        assert not missing, f"Missing: {missing}"

    def test_applied_is_bool(self, api):
        r = api.get(f"{BASE_URL}/api/admin/transport/planner/metrics")
        assert isinstance(r.json()["applied"], bool)


# ---------------------------------------------------------------------------
# POST /planner/apply (smoke — only if plan exists)
# ---------------------------------------------------------------------------

class TestPlannerApply:
    def test_apply_without_plan_id_returns_422(self, api):
        r = api.post(f"{BASE_URL}/api/admin/transport/planner/apply",
                     json={"plan_id": 999999999, "shipment_date": TOMORROW})
        assert r.status_code in (404, 422), f"Expected 404/422 for unknown plan_id: {r.status_code}"

    def test_apply_full_flow(self, api):
        """Создаём план → применяем → проверяем tasks_created."""
        # Solve first
        solve_r = api.post(f"{BASE_URL}/api/admin/transport/planner/solve",
                           json={"plan_date": TOMORROW, "time_limit_s": 10, "source": "haversine"})
        if solve_r.status_code == 422:
            pytest.skip("Нет активных ТС / СТ")
        plan = solve_r.json()
        plan_id = plan.get("plan_id")
        if plan_id is None:
            pytest.skip("plan_id не возвращён (Oracle недоступна?)")

        apply_r = api.post(f"{BASE_URL}/api/admin/transport/planner/apply",
                           json={"plan_id": plan_id, "shipment_date": TOMORROW})
        assert apply_r.status_code == 200, f"Apply failed: {apply_r.text}"
        result = apply_r.json()
        assert "tasks_created" in result
        assert result["tasks_created"] >= 0
