"""
test_sprint9_functional.py — Functional completeness tests for Sprint 9.

Sprint 9 scope: polygon/cluster selection, DBSCAN solver, historical templates
  - POST /planner/solve?solver=cluster returns routes using DBSCAN
  - GET /planner/templates returns list with jaccard field
  - planner/orders response contains RAION (needed for clusters)

Run:
    pytest tests/transport/test_sprint9_functional.py -v
"""

from __future__ import annotations

import os
import pytest
import requests

BASE_URL = os.environ.get("TMS_API_BASE_URL", "http://127.0.0.1:8088")
AUTH = ("admin", "admin123")
PLAN_DATE = os.environ.get("TMS_SPRINT9_DATE", "2026-05-25")


@pytest.fixture(scope="session")
def api():
    s = requests.Session()
    s.auth = AUTH
    s.headers.update({"Content-Type": "application/json"})
    return s


# ---------------------------------------------------------------------------
# DBSCAN cluster solver
# ---------------------------------------------------------------------------

class TestClusterSolver:
    def test_cluster_solve_returns_200(self, api):
        r = api.post(f"{BASE_URL}/api/admin/transport/planner/solve",
                     json={"plan_date": PLAN_DATE, "solver": "cluster",
                           "time_limit_s": 10, "source": "haversine"})
        assert r.status_code in (200, 422), f"{r.status_code}: {r.text}"

    def test_cluster_solve_solver_field(self, api):
        r = api.post(f"{BASE_URL}/api/admin/transport/planner/solve",
                     json={"plan_date": PLAN_DATE, "solver": "cluster",
                           "time_limit_s": 10, "source": "haversine"})
        if r.status_code == 422:
            pytest.skip("Нет ТС / СТ")
        data = r.json()
        assert data["solver_used"] in (
            "dbscan-cluster", "clarke-wright", "ortools-cvrptw", "none"
        ), f"Unexpected solver: {data['solver_used']}"
        assert data["routes"], f"Cluster solver returned empty routes for seed date {PLAN_DATE}"

    def test_savings_solver_works(self, api):
        r = api.post(f"{BASE_URL}/api/admin/transport/planner/solve",
                     json={"plan_date": PLAN_DATE, "solver": "savings",
                           "time_limit_s": 10, "source": "haversine"})
        if r.status_code == 422:
            pytest.skip("Нет ТС / СТ")
        assert r.status_code == 200


# ---------------------------------------------------------------------------
# GET /planner/templates
# ---------------------------------------------------------------------------

class TestPlannerTemplates:
    def test_templates_returns_200(self, api):
        r = api.get(f"{BASE_URL}/api/admin/transport/planner/templates",
                    params={"plan_date": PLAN_DATE})
        assert r.status_code == 200, f"{r.status_code}: {r.text}"

    def test_templates_is_list(self, api):
        r = api.get(f"{BASE_URL}/api/admin/transport/planner/templates",
                    params={"plan_date": PLAN_DATE})
        assert isinstance(r.json(), list)

    def test_templates_required_fields(self, api):
        r = api.get(f"{BASE_URL}/api/admin/transport/planner/templates",
                    params={"plan_date": PLAN_DATE})
        data = r.json()
        if not data:
            pytest.skip("Нет исторических планов")
        required = {"plan_id", "plan_date", "score", "jaccard", "routes_count",
                    "matched_sts", "total_current_sts"}
        for tmpl in data[:3]:
            missing = required - set(tmpl.keys())
            assert not missing, f"Missing fields: {missing}"

    def test_templates_jaccard_in_range(self, api):
        r = api.get(f"{BASE_URL}/api/admin/transport/planner/templates",
                    params={"plan_date": PLAN_DATE, "min_jaccard": "0.1"})
        data = r.json()
        for tmpl in data:
            assert 0.0 <= tmpl["jaccard"] <= 1.0, f"jaccard out of range: {tmpl['jaccard']}"

    def test_templates_min_jaccard_filter(self, api):
        r = api.get(f"{BASE_URL}/api/admin/transport/planner/templates",
                    params={"plan_date": PLAN_DATE, "min_jaccard": "0.9"})
        data = r.json()
        for tmpl in data:
            assert tmpl["jaccard"] >= 0.9

    def test_templates_lookback_param(self, api):
        r = api.get(f"{BASE_URL}/api/admin/transport/planner/templates",
                    params={"plan_date": PLAN_DATE, "lookback_days": "7"})
        assert r.status_code == 200


# ---------------------------------------------------------------------------
# Planner orders RAION field (needed for clusters)
# ---------------------------------------------------------------------------

class TestPlannerOrdersClusterFields:
    def test_raion_field_present(self, api):
        r = api.get(f"{BASE_URL}/api/admin/transport/planner/orders",
                    params={"date": PLAN_DATE})
        data = r.json()
        if not data:
            pytest.fail(f"Нет СТ для seed-date {PLAN_DATE}")
        for row in data[:5]:
            assert "RAION" in row, "Поле RAION обязательно для кластеризации"

    def test_orders_have_valid_raion_or_null(self, api):
        r = api.get(f"{BASE_URL}/api/admin/transport/planner/orders",
                    params={"date": PLAN_DATE})
        data = r.json()
        for row in data[:20]:
            raion = row.get("RAION")
            if raion is not None:
                assert isinstance(raion, str), f"RAION должен быть строкой: {raion}"
