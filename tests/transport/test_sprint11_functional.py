"""
test_sprint11_functional.py — Functional completeness tests for Sprint 11.

Sprint 11 scope: ARM operations model
  - POST /tasks/{id}/plan-operations  → creates 12-step chain
  - GET  /tasks/{id}/operations       → returns chain with plan times
  - PATCH /operations/{op_id}/fact    → records fact_start / fact_end
  - GET /vehicles/gantt?date=         → Gantt data for all vehicles

Run:
    pytest tests/transport/test_sprint11_functional.py -v
"""

from __future__ import annotations

import os
import pytest
import requests
from datetime import date, timedelta

BASE_URL = os.environ.get("TMS_API_BASE_URL", "http://127.0.0.1:8088")
AUTH = ("admin", "admin123")
TODAY = date.today().isoformat()
TOMORROW = (date.today() + timedelta(days=1)).isoformat()

EXPECTED_OPERATIONS = [
    "DOCK_ASSIGN", "WAIT_LOAD", "LOADING", "CLOSE_GATE", "DOCUMENTS",
    "DEPART", "DRIVE", "UNLOAD", "LOAD_RETURNS", "DRIVE_BACK",
    "RETURN_HANDOVER", "CLEAN_RETURNS",
]


@pytest.fixture(scope="session")
def api():
    s = requests.Session()
    s.auth = AUTH
    s.headers.update({"Content-Type": "application/json"})
    return s


@pytest.fixture(scope="session")
def task_id(api):
    """Создаём тестовый рейс для проверки операций."""
    r = api.post(f"{BASE_URL}/api/admin/transport/tasks", json={
        "transtype": "Газель",
        "shipment_date": TOMORROW,
    })
    if r.status_code not in (200, 201):
        pytest.skip(f"Не удалось создать рейс: {r.status_code} {r.text}")
    return r.json()["task_id"]


# ---------------------------------------------------------------------------
# POST /tasks/{id}/plan-operations
# ---------------------------------------------------------------------------

class TestPlanOperations:
    def test_plan_operations_returns_200(self, api, task_id):
        r = api.post(f"{BASE_URL}/api/admin/transport/tasks/{task_id}/plan-operations")
        assert r.status_code == 200, f"{r.status_code}: {r.text}"

    def test_plan_operations_returns_list(self, api, task_id):
        r = api.post(f"{BASE_URL}/api/admin/transport/tasks/{task_id}/plan-operations")
        assert isinstance(r.json(), list)

    def test_plan_operations_12_steps(self, api, task_id):
        r = api.post(f"{BASE_URL}/api/admin/transport/tasks/{task_id}/plan-operations")
        assert len(r.json()) == 12, f"Expected 12 operations, got {len(r.json())}"

    def test_plan_operations_codes_match(self, api, task_id):
        r = api.post(f"{BASE_URL}/api/admin/transport/tasks/{task_id}/plan-operations")
        codes = [op["operation_code"] for op in r.json()]
        assert codes == EXPECTED_OPERATIONS, f"Unexpected codes: {codes}"

    def test_plan_operations_ord_sequential(self, api, task_id):
        r = api.post(f"{BASE_URL}/api/admin/transport/tasks/{task_id}/plan-operations")
        ords = [op["ord"] for op in r.json()]
        assert ords == list(range(1, 13)), f"Unexpected ords: {ords}"

    def test_plan_operations_plan_start_not_null(self, api, task_id):
        r = api.post(f"{BASE_URL}/api/admin/transport/tasks/{task_id}/plan-operations")
        for op in r.json():
            assert op["plan_start"] is not None, f"plan_start is null for {op['operation_code']}"

    def test_plan_operations_plan_end_after_start(self, api, task_id):
        from datetime import datetime
        r = api.post(f"{BASE_URL}/api/admin/transport/tasks/{task_id}/plan-operations")
        for op in r.json():
            ps = datetime.strptime(op["plan_start"], "%Y-%m-%d %H:%M")
            pe = datetime.strptime(op["plan_end"], "%Y-%m-%d %H:%M")
            assert pe >= ps, f"plan_end < plan_start for {op['operation_code']}"

    def test_plan_operations_chain_continuous(self, api, task_id):
        """Конец каждой операции == начало следующей."""
        r = api.post(f"{BASE_URL}/api/admin/transport/tasks/{task_id}/plan-operations")
        ops = r.json()
        for i in range(len(ops) - 1):
            assert ops[i]["plan_end"] == ops[i + 1]["plan_start"], (
                f"Gap between {ops[i]['operation_code']} and {ops[i+1]['operation_code']}"
            )

    def test_plan_operations_duration_non_negative(self, api, task_id):
        r = api.post(f"{BASE_URL}/api/admin/transport/tasks/{task_id}/plan-operations")
        for op in r.json():
            assert op["duration_min"] >= 0


# ---------------------------------------------------------------------------
# GET /tasks/{id}/operations
# ---------------------------------------------------------------------------

class TestGetOperations:
    def test_get_operations_200(self, api, task_id):
        # Убедиться что операции существуют
        api.post(f"{BASE_URL}/api/admin/transport/tasks/{task_id}/plan-operations")
        r = api.get(f"{BASE_URL}/api/admin/transport/tasks/{task_id}/operations")
        assert r.status_code == 200

    def test_get_operations_fields(self, api, task_id):
        r = api.get(f"{BASE_URL}/api/admin/transport/tasks/{task_id}/operations")
        data = r.json()
        if not data:
            pytest.skip("Нет операций")
        required = {"op_id", "tt_id", "operation_code", "ord", "duration_min",
                    "plan_start", "plan_end", "fact_start", "fact_end", "delta_min"}
        for op in data:
            missing = required - set(op.keys())
            assert not missing, f"Missing fields: {missing}"

    def test_get_operations_tt_id_matches(self, api, task_id):
        r = api.get(f"{BASE_URL}/api/admin/transport/tasks/{task_id}/operations")
        for op in r.json():
            assert op["tt_id"] == task_id


# ---------------------------------------------------------------------------
# PATCH /operations/{op_id}/fact
# ---------------------------------------------------------------------------

class TestUpdateFact:
    @pytest.fixture
    def op_id(self, api, task_id):
        api.post(f"{BASE_URL}/api/admin/transport/tasks/{task_id}/plan-operations")
        ops = api.get(f"{BASE_URL}/api/admin/transport/tasks/{task_id}/operations").json()
        if not ops:
            pytest.skip("Нет операций")
        return ops[0]["op_id"]

    def test_patch_fact_200(self, api, op_id):
        r = api.patch(
            f"{BASE_URL}/api/admin/transport/operations/{op_id}/fact",
            json={"fact_start": "2026-05-27 06:05"},
        )
        assert r.status_code == 200, f"{r.status_code}: {r.text}"

    def test_patch_fact_updated_flag(self, api, op_id):
        r = api.patch(
            f"{BASE_URL}/api/admin/transport/operations/{op_id}/fact",
            json={"fact_start": "2026-05-27 06:05", "fact_end": "2026-05-27 06:22"},
        )
        assert r.json().get("updated") is True

    def test_patch_fact_persisted(self, api, task_id, op_id):
        api.patch(
            f"{BASE_URL}/api/admin/transport/operations/{op_id}/fact",
            json={"fact_start": "2026-05-27 06:10"},
        )
        ops = api.get(f"{BASE_URL}/api/admin/transport/tasks/{task_id}/operations").json()
        matched = next((o for o in ops if o["op_id"] == op_id), None)
        assert matched is not None
        assert matched["fact_start"] == "2026-05-27 06:10"

    def test_patch_fact_empty_body_400(self, api, op_id):
        r = api.patch(
            f"{BASE_URL}/api/admin/transport/operations/{op_id}/fact",
            json={},
        )
        assert r.status_code == 400


# ---------------------------------------------------------------------------
# GET /vehicles/gantt
# ---------------------------------------------------------------------------

class TestVehiclesGantt:
    def test_gantt_200(self, api):
        r = api.get(
            f"{BASE_URL}/api/admin/transport/vehicles/gantt",
            params={"gantt_date": TOMORROW},
        )
        assert r.status_code == 200, f"{r.status_code}: {r.text}"

    def test_gantt_is_list(self, api):
        r = api.get(
            f"{BASE_URL}/api/admin/transport/vehicles/gantt",
            params={"gantt_date": TOMORROW},
        )
        assert isinstance(r.json(), list)

    def test_gantt_item_fields(self, api):
        r = api.get(
            f"{BASE_URL}/api/admin/transport/vehicles/gantt",
            params={"gantt_date": TOMORROW},
        )
        data = r.json()
        if not data:
            pytest.skip("Нет рейсов на дату")
        required = {"vehicle_id", "vehicle_num", "vehicle_type", "operations"}
        for item in data:
            missing = required - set(item.keys())
            assert not missing

    def test_gantt_operations_is_list(self, api):
        r = api.get(
            f"{BASE_URL}/api/admin/transport/vehicles/gantt",
            params={"gantt_date": TOMORROW},
        )
        for item in r.json():
            assert isinstance(item["operations"], list)
