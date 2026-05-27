"""
test_sprint12_functional.py — Functional completeness tests for Sprint 12.

Sprint 12 scope: Gantt diagram — backend validation
  - GET /vehicles/gantt returns vehicle list with operations
  - Operations have plan_start/plan_end in correct format
  - Vehicle fields: vehicle_id, vehicle_num, vehicle_type, operations

Run:
    pytest tests/transport/test_sprint12_functional.py -v
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


@pytest.fixture(scope="session")
def api():
    s = requests.Session()
    s.auth = AUTH
    s.headers.update({"Content-Type": "application/json"})
    return s


@pytest.fixture(scope="session")
def task_with_ops(api):
    """Создать рейс на завтра, запустить plan-operations, вернуть task_id."""
    r = api.post(f"{BASE_URL}/api/admin/transport/tasks", json={
        "transtype": "Газель", "shipment_date": TOMORROW,
    })
    if r.status_code not in (200, 201):
        pytest.skip(f"Не удалось создать рейс: {r.status_code}")
    tid = r.json()["task_id"]
    api.post(f"{BASE_URL}/api/admin/transport/tasks/{tid}/plan-operations")
    return tid


# ---------------------------------------------------------------------------
# GET /vehicles/gantt
# ---------------------------------------------------------------------------

class TestVehiclesGantt:
    def test_gantt_200(self, api):
        r = api.get(f"{BASE_URL}/api/admin/transport/vehicles/gantt",
                    params={"gantt_date": TOMORROW})
        assert r.status_code == 200, f"{r.status_code}: {r.text}"

    def test_gantt_is_list(self, api):
        r = api.get(f"{BASE_URL}/api/admin/transport/vehicles/gantt",
                    params={"gantt_date": TOMORROW})
        assert isinstance(r.json(), list)

    def test_gantt_today_returns_200(self, api):
        r = api.get(f"{BASE_URL}/api/admin/transport/vehicles/gantt",
                    params={"gantt_date": TODAY})
        assert r.status_code == 200

    def test_gantt_missing_date_422(self, api):
        r = api.get(f"{BASE_URL}/api/admin/transport/vehicles/gantt")
        assert r.status_code == 422

    def test_gantt_item_required_fields(self, api, task_with_ops):
        r = api.get(f"{BASE_URL}/api/admin/transport/vehicles/gantt",
                    params={"gantt_date": TOMORROW})
        data = r.json()
        if not data:
            pytest.skip("Нет машин на завтра")
        required = {"vehicle_id", "vehicle_num", "vehicle_type", "operations"}
        for item in data:
            missing = required - set(item.keys())
            assert not missing, f"Missing fields: {missing}"

    def test_gantt_operations_is_list(self, api, task_with_ops):
        r = api.get(f"{BASE_URL}/api/admin/transport/vehicles/gantt",
                    params={"gantt_date": TOMORROW})
        for item in r.json():
            assert isinstance(item["operations"], list), \
                f"operations not a list for {item['vehicle_num']}"

    def test_gantt_operation_fields(self, api, task_with_ops):
        r = api.get(f"{BASE_URL}/api/admin/transport/vehicles/gantt",
                    params={"gantt_date": TOMORROW})
        for item in r.json():
            for op in item["operations"]:
                required = {"op_id", "tt_id", "operation_code", "ord",
                            "duration_min", "plan_start", "plan_end"}
                missing = required - set(op.keys())
                assert not missing, f"Op missing fields: {missing}"

    def test_gantt_plan_start_format(self, api, task_with_ops):
        """plan_start должен быть в формате YYYY-MM-DD HH:MM."""
        import re
        r = api.get(f"{BASE_URL}/api/admin/transport/vehicles/gantt",
                    params={"gantt_date": TOMORROW})
        for item in r.json():
            for op in item["operations"]:
                if op["plan_start"]:
                    assert re.match(r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}", op["plan_start"]), \
                        f"Bad plan_start format: {op['plan_start']}"

    def test_gantt_chain_continuous(self, api, task_with_ops):
        """Конец каждой операции == начало следующей в цепочке."""
        r = api.get(f"{BASE_URL}/api/admin/transport/vehicles/gantt",
                    params={"gantt_date": TOMORROW})
        for item in r.json():
            ops = sorted(item["operations"], key=lambda o: o["ord"])
            for i in range(len(ops) - 1):
                if ops[i]["plan_end"] and ops[i + 1]["plan_start"]:
                    assert ops[i]["plan_end"] == ops[i + 1]["plan_start"], \
                        f"Gap between ops {ops[i]['operation_code']} and {ops[i+1]['operation_code']}"

    def test_gantt_12_ops_per_task(self, api, task_with_ops):
        """Каждый рейс должен иметь 12 операций."""
        r = api.get(f"{BASE_URL}/api/admin/transport/vehicles/gantt",
                    params={"gantt_date": TOMORROW})
        for item in r.json():
            assert len(item["operations"]) == 12, \
                f"{item['vehicle_num']}: expected 12 ops, got {len(item['operations'])}"

    def test_gantt_operation_codes(self, api, task_with_ops):
        """Коды операций из стандартного набора."""
        expected = {
            "DOCK_ASSIGN", "WAIT_LOAD", "LOADING", "CLOSE_GATE", "DOCUMENTS",
            "DEPART", "DRIVE", "UNLOAD", "LOAD_RETURNS", "DRIVE_BACK",
            "RETURN_HANDOVER", "CLEAN_RETURNS",
        }
        r = api.get(f"{BASE_URL}/api/admin/transport/vehicles/gantt",
                    params={"gantt_date": TOMORROW})
        for item in r.json():
            codes = {op["operation_code"] for op in item["operations"]}
            assert codes == expected, f"Unexpected codes for {item['vehicle_num']}: {codes}"

    def test_gantt_duration_non_negative(self, api, task_with_ops):
        r = api.get(f"{BASE_URL}/api/admin/transport/vehicles/gantt",
                    params={"gantt_date": TOMORROW})
        for item in r.json():
            for op in item["operations"]:
                assert op["duration_min"] >= 0
