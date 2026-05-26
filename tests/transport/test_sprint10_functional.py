"""
test_sprint10_functional.py — Functional completeness tests for Sprint 10.

Sprint 10 scope: history analytics + demand forecast
  - GET /planner/history returns list with score, utilization, km fields
  - GET /planner/demand-forecast returns forecast_sts, confidence, samples
  - Analytics tab accessible via TransportPlannerPage

Run:
    pytest tests/transport/test_sprint10_functional.py -v
"""

from __future__ import annotations

import os
import pytest
import requests
from datetime import date, timedelta

BASE_URL = os.environ.get("TMS_API_BASE_URL", "http://127.0.0.1:8088")
AUTH = ("admin", "admin123")
TODAY = date.today().isoformat()
LAST_MONTH = (date.today() - timedelta(days=30)).isoformat()
TOMORROW = (date.today() + timedelta(days=1)).isoformat()


@pytest.fixture(scope="session")
def api():
    s = requests.Session()
    s.auth = AUTH
    s.headers.update({"Content-Type": "application/json"})
    return s


# ---------------------------------------------------------------------------
# GET /planner/history
# ---------------------------------------------------------------------------

class TestPlannerHistory:
    def test_history_returns_200(self, api):
        r = api.get(f"{BASE_URL}/api/admin/transport/planner/history",
                    params={"date_from": LAST_MONTH, "date_to": TODAY})
        assert r.status_code == 200, f"{r.status_code}: {r.text}"

    def test_history_is_list(self, api):
        r = api.get(f"{BASE_URL}/api/admin/transport/planner/history",
                    params={"date_from": LAST_MONTH, "date_to": TODAY})
        assert isinstance(r.json(), list)

    def test_history_item_fields(self, api):
        r = api.get(f"{BASE_URL}/api/admin/transport/planner/history",
                    params={"date_from": LAST_MONTH, "date_to": TODAY})
        data = r.json()
        if not data:
            pytest.skip("Нет истории планов за период")
        required = {"plan_id", "plan_date", "solver", "score", "routes",
                    "total_km", "fleet_utilization_pct", "tw_violations", "applied"}
        for item in data[:3]:
            missing = required - set(item.keys())
            assert not missing, f"Missing: {missing}"

    def test_history_applied_is_bool(self, api):
        r = api.get(f"{BASE_URL}/api/admin/transport/planner/history",
                    params={"date_from": LAST_MONTH, "date_to": TODAY})
        for item in r.json():
            assert isinstance(item["applied"], bool)

    def test_history_score_numeric(self, api):
        r = api.get(f"{BASE_URL}/api/admin/transport/planner/history",
                    params={"date_from": LAST_MONTH, "date_to": TODAY})
        for item in r.json():
            assert isinstance(item["score"], (int, float)), f"score not numeric: {item['score']}"

    def test_history_utilization_range(self, api):
        r = api.get(f"{BASE_URL}/api/admin/transport/planner/history",
                    params={"date_from": LAST_MONTH, "date_to": TODAY})
        for item in r.json():
            u = item["fleet_utilization_pct"]
            assert 0.0 <= u <= 100.0, f"utilization out of range: {u}"

    def test_history_narrow_date_range(self, api):
        r = api.get(f"{BASE_URL}/api/admin/transport/planner/history",
                    params={"date_from": TODAY, "date_to": TODAY})
        assert r.status_code == 200
        assert isinstance(r.json(), list)


# ---------------------------------------------------------------------------
# GET /planner/demand-forecast
# ---------------------------------------------------------------------------

class TestDemandForecast:
    def test_forecast_returns_200(self, api):
        r = api.get(f"{BASE_URL}/api/admin/transport/planner/demand-forecast",
                    params={"target_date": TOMORROW})
        assert r.status_code == 200, f"{r.status_code}: {r.text}"

    def test_forecast_required_fields(self, api):
        r = api.get(f"{BASE_URL}/api/admin/transport/planner/demand-forecast",
                    params={"target_date": TOMORROW})
        data = r.json()
        required = {"target_date", "day_of_week", "forecast_sts", "confidence", "samples"}
        missing = required - set(data.keys())
        assert not missing, f"Missing: {missing}"

    def test_forecast_sts_non_negative(self, api):
        r = api.get(f"{BASE_URL}/api/admin/transport/planner/demand-forecast",
                    params={"target_date": TOMORROW})
        assert r.json()["forecast_sts"] >= 0

    def test_forecast_confidence_valid(self, api):
        r = api.get(f"{BASE_URL}/api/admin/transport/planner/demand-forecast",
                    params={"target_date": TOMORROW})
        assert r.json()["confidence"] in ("high", "medium", "low", "none")

    def test_forecast_day_of_week_range(self, api):
        r = api.get(f"{BASE_URL}/api/admin/transport/planner/demand-forecast",
                    params={"target_date": TOMORROW})
        assert 0 <= r.json()["day_of_week"] <= 6

    def test_forecast_samples_non_negative(self, api):
        r = api.get(f"{BASE_URL}/api/admin/transport/planner/demand-forecast",
                    params={"target_date": TOMORROW})
        assert r.json()["samples"] >= 0

    def test_forecast_lookback_param(self, api):
        r = api.get(f"{BASE_URL}/api/admin/transport/planner/demand-forecast",
                    params={"target_date": TOMORROW, "lookback_weeks": "4"})
        assert r.status_code == 200

    def test_forecast_target_date_matches(self, api):
        r = api.get(f"{BASE_URL}/api/admin/transport/planner/demand-forecast",
                    params={"target_date": TOMORROW})
        assert r.json()["target_date"] == TOMORROW
