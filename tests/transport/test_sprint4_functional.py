"""
test_sprint4_functional.py — Functional completeness tests for Sprint 4.

Sprint 4 scope: full trip lifecycle
  - Add STs to existing trip
  - Remove ST from trip
  - Edit trip attributes: transport, driver, dock, time, date, transtype, note
  - Close trip with can_print check (422 on failure)
  - Cancel trip

Run against API at http://127.0.0.1:8088 with seed «Добра Цен» applied.

Usage:
    pip install pytest requests
    pytest tests/transport/test_sprint4_functional.py -v
    pytest tests/transport/test_sprint4_functional.py -v --base-url=http://myserver:8088
"""

from __future__ import annotations

import os
import pytest
import requests
from datetime import date, timedelta


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

BASE_URL = os.environ.get("TMS_API_BASE_URL", "http://127.0.0.1:8088")
AUTH = ("admin", "admin123")
TODAY = date.today().isoformat()
TOMORROW = (date.today() + timedelta(days=1)).isoformat()


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="session")
def api():
    """HTTP session with Basic auth."""
    s = requests.Session()
    s.auth = AUTH
    s.headers.update({"Content-Type": "application/json"})
    return s


@pytest.fixture(scope="session")
def base_url():
    return BASE_URL


@pytest.fixture
def fresh_task(api, base_url):
    """Create a task for the test and delete it afterwards."""
    r = api.post(f"{base_url}/api/admin/transport/tasks",
                 json={"transtype": "10", "shipment_date": TOMORROW})
    r.raise_for_status()
    task_id = r.json()["task_id"]
    yield task_id
    # cleanup — cancel task
    api.post(f"{base_url}/api/admin/transport/tasks/{task_id}/cancel")


# ---------------------------------------------------------------------------
# AT-D-06 / AT-D-08: list tasks endpoint
# ---------------------------------------------------------------------------

class TestListTasks:
    def test_returns_list(self, api, base_url):
        r = api.get(f"{base_url}/api/admin/transport/tasks",
                    params={"shipment_date": TODAY, "include_readiness": "true"})
        assert r.status_code == 200
        data = r.json()
        assert isinstance(data, list)

    def test_filter_by_date_returns_only_that_date(self, api, base_url):
        r = api.get(f"{base_url}/api/admin/transport/tasks",
                    params={"shipment_date": "2099-01-01"})
        assert r.status_code == 200
        data = r.json()
        assert all(row["SHIPMENT_DATE"].startswith("2099-01-01") for row in data)

    def test_filter_no_payments(self, api, base_url):
        r = api.get(f"{base_url}/api/admin/transport/tasks",
                    params={"no_payments_only": "true"})
        assert r.status_code == 200
        data = r.json()
        assert all(not row.get("PAY_ORDER_ID") for row in data)

    def test_readiness_fields_present(self, api, base_url):
        r = api.get(f"{base_url}/api/admin/transport/tasks",
                    params={"shipment_date": TOMORROW, "include_readiness": "true"})
        assert r.status_code == 200
        data = r.json()
        if data:
            assert "READY_PERC" in data[0]
            assert "UNREADY_COUNT" in data[0]


# ---------------------------------------------------------------------------
# AT-D-06: create task
# ---------------------------------------------------------------------------

class TestCreateTask:
    def test_create_returns_task_id(self, api, base_url):
        r = api.post(f"{base_url}/api/admin/transport/tasks",
                     json={"transtype": "10", "shipment_date": TOMORROW})
        assert r.status_code == 200
        body = r.json()
        assert "task_id" in body
        task_id = body["task_id"]
        assert isinstance(task_id, int) and task_id > 0
        # cleanup
        api.post(f"{base_url}/api/admin/transport/tasks/{task_id}/cancel")

    def test_create_missing_shipment_date_returns_422(self, api, base_url):
        r = api.post(f"{base_url}/api/admin/transport/tasks",
                     json={"transtype": "10"})
        assert r.status_code == 422

    def test_get_created_task(self, api, base_url, fresh_task):
        r = api.get(f"{base_url}/api/admin/transport/tasks/{fresh_task}")
        assert r.status_code == 200
        body = r.json()
        assert body["ID"] == fresh_task


# ---------------------------------------------------------------------------
# Sprint 4: edit trip attributes (PATCH /tasks/{id})
# ---------------------------------------------------------------------------

class TestUpdateTask:
    def test_patch_transport(self, api, base_url, fresh_task):
        r = api.patch(f"{base_url}/api/admin/transport/tasks/{fresh_task}",
                      json={"transport": "Т368ХН"})
        assert r.status_code == 200
        task = api.get(f"{base_url}/api/admin/transport/tasks/{fresh_task}").json()
        assert task["TRANSPORT"] == "Т368ХН"

    def test_patch_dock(self, api, base_url, fresh_task):
        r = api.patch(f"{base_url}/api/admin/transport/tasks/{fresh_task}",
                      json={"dock": "Д3"})
        assert r.status_code == 200
        task = api.get(f"{base_url}/api/admin/transport/tasks/{fresh_task}").json()
        assert task["DOCK"] == "Д3"

    def test_patch_shipment_date(self, api, base_url, fresh_task):
        new_date = (date.today() + timedelta(days=5)).isoformat()
        r = api.patch(f"{base_url}/api/admin/transport/tasks/{fresh_task}",
                      json={"shipment_date": new_date})
        assert r.status_code == 200
        task = api.get(f"{base_url}/api/admin/transport/tasks/{fresh_task}").json()
        assert task["SHIPMENT_DATE"].startswith(new_date)

    def test_patch_transtype(self, api, base_url, fresh_task):
        r = api.patch(f"{base_url}/api/admin/transport/tasks/{fresh_task}",
                      json={"transtype": "15"})
        assert r.status_code == 200
        task = api.get(f"{base_url}/api/admin/transport/tasks/{fresh_task}").json()
        assert task["TRANSTYPE"] == "15"

    def test_patch_primechanie(self, api, base_url, fresh_task):
        r = api.patch(f"{base_url}/api/admin/transport/tasks/{fresh_task}",
                      json={"primechanie": "Тест Sprint 4"})
        assert r.status_code == 200
        task = api.get(f"{base_url}/api/admin/transport/tasks/{fresh_task}").json()
        assert task["PRIMECHANIE"] == "Тест Sprint 4"

    def test_patch_shipment_time(self, api, base_url, fresh_task):
        r = api.patch(f"{base_url}/api/admin/transport/tasks/{fresh_task}",
                      json={"shipment_time": "08:30"})
        assert r.status_code == 200

    def test_patch_empty_body_no_op(self, api, base_url, fresh_task):
        r = api.patch(f"{base_url}/api/admin/transport/tasks/{fresh_task}", json={})
        assert r.status_code == 200


# ---------------------------------------------------------------------------
# AT-D-09/10: assign / unassign STs
# ---------------------------------------------------------------------------

class TestAssignUnassign:
    def test_available_sts_returns_list(self, api, base_url):
        r = api.get(f"{base_url}/api/admin/transport/available-sts",
                    params={"stdate": TOMORROW, "unassigned_only": "true"})
        assert r.status_code == 200
        data = r.json()
        assert isinstance(data, list)

    def test_assign_returns_assigned_count(self, api, base_url, fresh_task):
        # get any available ST
        r = api.get(f"{base_url}/api/admin/transport/available-sts",
                    params={"stdate": TOMORROW, "unassigned_only": "true"})
        sts = r.json()
        if not sts:
            pytest.skip("Нет свободных СТ на завтра для теста назначения")
        st_num = sts[0]["ST_NUMBER"]
        r2 = api.post(f"{base_url}/api/admin/transport/tasks/{fresh_task}/sts",
                      json={"st_numbers": [st_num]})
        assert r2.status_code == 200
        body = r2.json()
        assert body["assigned"] == 1

        # cleanup: unassign
        api.delete(f"{base_url}/api/admin/transport/tasks/{fresh_task}/sts/{st_num}")

    def test_unassign_returns_200(self, api, base_url, fresh_task):
        r = api.get(f"{base_url}/api/admin/transport/available-sts",
                    params={"stdate": TOMORROW, "unassigned_only": "true"})
        sts = r.json()
        if not sts:
            pytest.skip("Нет свободных СТ")
        st_num = sts[0]["ST_NUMBER"]
        api.post(f"{base_url}/api/admin/transport/tasks/{fresh_task}/sts",
                 json={"st_numbers": [st_num]})
        r2 = api.delete(
            f"{base_url}/api/admin/transport/tasks/{fresh_task}/sts/{st_num}")
        assert r2.status_code == 200
        body = r2.json()
        assert body["unassigned"] is True

    def test_get_task_sts_returns_list(self, api, base_url, fresh_task):
        r = api.get(f"{base_url}/api/admin/transport/tasks/{fresh_task}/sts")
        assert r.status_code == 200
        assert isinstance(r.json(), list)


# ---------------------------------------------------------------------------
# AT-D-10: set load type / order
# ---------------------------------------------------------------------------

class TestStAttributes:
    def test_set_load_type_г(self, api, base_url, fresh_task):
        r = api.get(f"{base_url}/api/admin/transport/available-sts",
                    params={"stdate": TOMORROW, "unassigned_only": "true"})
        sts = r.json()
        if not sts:
            pytest.skip("Нет свободных СТ")
        st_num = sts[0]["ST_NUMBER"]
        api.post(f"{base_url}/api/admin/transport/tasks/{fresh_task}/sts",
                 json={"st_numbers": [st_num]})
        r2 = api.patch(
            f"{base_url}/api/admin/transport/tasks/{fresh_task}/sts/{st_num}/load-type",
            json={"load_type": "Г"})
        assert r2.status_code == 200
        # verify via get_task_sts
        task_sts = api.get(f"{base_url}/api/admin/transport/tasks/{fresh_task}/sts").json()
        row = next((s for s in task_sts if s["ST_NUMBER"] == st_num), None)
        assert row is not None
        assert row["LOAD_TYPE"] == "Г"
        api.delete(f"{base_url}/api/admin/transport/tasks/{fresh_task}/sts/{st_num}")

    def test_set_load_type_invalid_returns_422(self, api, base_url, fresh_task):
        r = api.patch(
            f"{base_url}/api/admin/transport/tasks/{fresh_task}/sts/DUMMY/load-type",
            json={"load_type": "X"})
        assert r.status_code == 422


# ---------------------------------------------------------------------------
# AT-D-11: close trip with can_print check
# ---------------------------------------------------------------------------

class TestCloseTask:
    def test_close_empty_task_returns_422_or_404(self, api, base_url, fresh_task):
        """Empty task should fail can_print (422) or have no rows (404).
        Both are acceptable — what must NOT happen is silent success (200)."""
        r = api.post(f"{base_url}/api/admin/transport/tasks/{fresh_task}/close")
        assert r.status_code in (404, 422), (
            f"Expected 404 or 422 for empty task close, got {r.status_code}: {r.text}")

    def test_close_response_has_detail_on_422(self, api, base_url, fresh_task):
        r = api.post(f"{base_url}/api/admin/transport/tasks/{fresh_task}/close")
        if r.status_code == 422:
            body = r.json()
            assert "detail" in body
            assert len(body["detail"]) > 0


# ---------------------------------------------------------------------------
# AT-D-12: cancel task (расформировать)
# ---------------------------------------------------------------------------

class TestCancelTask:
    def test_cancel_sets_deleted(self, api, base_url):
        r = api.post(f"{base_url}/api/admin/transport/tasks",
                     json={"transtype": "10", "shipment_date": TOMORROW})
        r.raise_for_status()
        task_id = r.json()["task_id"]
        r2 = api.post(f"{base_url}/api/admin/transport/tasks/{task_id}/cancel")
        assert r2.status_code == 200
        body = r2.json()
        assert body.get("deleted") is True
        # Task should not appear in normal list anymore
        tasks = api.get(f"{base_url}/api/admin/transport/tasks",
                        params={"shipment_date": TOMORROW}).json()
        ids = [t["ID"] for t in tasks]
        assert task_id not in ids


# ---------------------------------------------------------------------------
# Reference data endpoints
# ---------------------------------------------------------------------------

class TestReferenceData:
    def test_vehicles_returns_list(self, api, base_url):
        r = api.get(f"{base_url}/api/admin/transport/vehicles")
        assert r.status_code == 200
        data = r.json()
        assert isinstance(data, list)
        if data:
            assert "NUM" in data[0]

    def test_drivers_returns_list(self, api, base_url):
        r = api.get(f"{base_url}/api/admin/transport/drivers")
        assert r.status_code == 200
        assert isinstance(r.json(), list)

    def test_types_returns_list(self, api, base_url):
        r = api.get(f"{base_url}/api/admin/transport/types")
        assert r.status_code == 200
        assert isinstance(r.json(), list)

    def test_clusters_returns_list(self, api, base_url):
        r = api.get(f"{base_url}/api/admin/transport/clusters",
                    params={"stdate": TOMORROW})
        assert r.status_code == 200
        assert isinstance(r.json(), list)
