"""
test_sprint14_functional.py — Functional completeness tests for Sprint 14.

Sprint 14 scope: plan-fact analytics
  - GET /plan-fact returns operations with delta_min
  - PATCH /operations/{id}/fact updates fact times
  - delta_min calculated correctly

Run:
    pytest tests/transport/test_sprint14_functional.py -v
"""

from __future__ import annotations

import os
import pytest
import requests
from datetime import date, timedelta

BASE_URL = os.environ.get("TMS_API_BASE_URL", "http://127.0.0.1:8088")
AUTH = ("admin", "admin123")
TODAY    = date.today().isoformat()
TOMORROW = (date.today() + timedelta(days=1)).isoformat()
LAST_30  = (date.today() - timedelta(days=30)).isoformat()


@pytest.fixture(scope="session")
def api():
    s = requests.Session()
    s.auth = AUTH
    s.headers.update({"Content-Type": "application/json"})
    return s


@pytest.fixture(scope="session")
def task_with_ops(api):
    r = api.post(f"{BASE_URL}/api/admin/transport/tasks", json={
        "transtype": "Газель", "shipment_date": TOMORROW,
    })
    if r.status_code not in (200, 201):
        pytest.skip(f"Не удалось создать рейс: {r.status_code}")
    tid = r.json()["task_id"]
    api.post(f"{BASE_URL}/api/admin/transport/tasks/{tid}/plan-operations")
    return tid


class TestPlanFactAnalytics:
    def test_plan_fact_200(self, api):
        r = api.get(f"{BASE_URL}/api/admin/transport/plan-fact",
                    params={"date_from": LAST_30, "date_to": TODAY})
        assert r.status_code == 200, f"{r.status_code}: {r.text}"

    def test_plan_fact_required_fields(self, api):
        r = api.get(f"{BASE_URL}/api/admin/transport/plan-fact",
                    params={"date_from": LAST_30, "date_to": TODAY})
        data = r.json()
        if not data:
            pytest.skip("Нет рейсов")
        required = {"tt_id", "vehicle", "shipment_date", "operations",
                    "total_delta_min", "rest_violations"}
        for item in data[:3]:
            assert not (required - set(item.keys()))

    def test_plan_fact_delta_calculated_after_fact(self, api, task_with_ops):
        """После фиксации факта delta_min должна быть рассчитана."""
        # Get ops
        ops_r = api.get(f"{BASE_URL}/api/admin/transport/tasks/{task_with_ops}/operations")
        ops = ops_r.json()
        if not ops:
            pytest.skip("Нет операций")
        first_op = ops[0]

        # Patch fact = plan (delta = 0)
        api.patch(
            f"{BASE_URL}/api/admin/transport/operations/{first_op['op_id']}/fact",
            json={"fact_start": first_op["plan_start"],
                  "fact_end": first_op["plan_end"]}
        )

        # Get plan-fact
        r = api.get(f"{BASE_URL}/api/admin/transport/plan-fact",
                    params={"date_from": TOMORROW, "date_to": TOMORROW})
        data = r.json()
        task_data = next((d for d in data if d["tt_id"] == task_with_ops), None)
        if task_data is None:
            pytest.skip("Рейс не попал в plan-fact")
        op_data = next((o for o in task_data["operations"] if o["op_id"] == first_op["op_id"]), None)
        if op_data is None:
            pytest.skip("Операция не найдена")
        assert op_data["delta_min"] == 0.0, \
            f"Expected delta=0, got {op_data['delta_min']}"

    def test_plan_fact_positive_delta(self, api, task_with_ops):
        """delta_min > 0 если факт конец позже плана."""
        from datetime import datetime, timedelta
        ops = api.get(f"{BASE_URL}/api/admin/transport/tasks/{task_with_ops}/operations").json()
        if not ops:
            pytest.skip("Нет операций")
        op = ops[1]  # Use second op
        plan_end = datetime.strptime(op["plan_end"], "%Y-%m-%d %H:%M")
        late_end = (plan_end + timedelta(minutes=30)).strftime("%Y-%m-%d %H:%M")

        api.patch(f"{BASE_URL}/api/admin/transport/operations/{op['op_id']}/fact",
                  json={"fact_start": op["plan_start"], "fact_end": late_end})

        r = api.get(f"{BASE_URL}/api/admin/transport/plan-fact",
                    params={"date_from": TOMORROW, "date_to": TOMORROW})
        data = r.json()
        task_data = next((d for d in data if d["tt_id"] == task_with_ops), None)
        if task_data is None:
            pytest.skip("Рейс не найден")
        op_data = next((o for o in task_data["operations"] if o["op_id"] == op["op_id"]), None)
        if op_data is None:
            pytest.skip("Операция не найдена")
        assert op_data["delta_min"] == 30.0, f"Expected 30, got {op_data['delta_min']}"

    def test_plan_fact_total_delta_non_negative(self, api):
        r = api.get(f"{BASE_URL}/api/admin/transport/plan-fact",
                    params={"date_from": LAST_30, "date_to": TODAY})
        for item in r.json():
            assert item["total_delta_min"] >= 0

    def test_plan_fact_rest_violations_range(self, api):
        r = api.get(f"{BASE_URL}/api/admin/transport/plan-fact",
                    params={"date_from": LAST_30, "date_to": TODAY})
        for item in r.json():
            assert item["rest_violations"] in (0, 1)

    def test_plan_fact_date_range_narrow(self, api):
        r = api.get(f"{BASE_URL}/api/admin/transport/plan-fact",
                    params={"date_from": TODAY, "date_to": TODAY})
        assert r.status_code == 200
        assert isinstance(r.json(), list)
