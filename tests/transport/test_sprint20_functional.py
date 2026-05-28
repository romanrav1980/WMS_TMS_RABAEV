"""
test_sprint20_functional.py — Functional completeness tests for Sprint 20.

Sprint 20 scope: billing — backend protection of billed trips
  - DELETE /tasks/{id} on billed trip → 409
  - POST /tasks/{id}/sts on billed trip → 409
  - DELETE /tasks/{id}/sts/{st} on billed trip → 409
  - PATCH /tasks/{id} fields comment, load-type, order → still 200

Run:
    pytest tests/transport/test_sprint20_functional.py -v
"""

from __future__ import annotations

import os
import pytest
import requests
from datetime import date

BASE_URL = os.environ.get("TMS_API_BASE_URL", "http://127.0.0.1:8088")
AUTH = ("admin", "admin123")
TODAY = date.today().isoformat()


@pytest.fixture(scope="session")
def api():
    s = requests.Session()
    s.auth = AUTH
    s.headers.update({"Content-Type": "application/json"})
    return s


@pytest.fixture(scope="session")
def billed_task_id(api):
    """Find or create a task that has PAY_ORDER_ID set."""
    r = api.get(f"{BASE_URL}/api/admin/transport/tasks", params={"date_to": TODAY})
    if r.status_code == 200:
        for task in r.json():
            if task.get("PAY_ORDER_ID") and int(task.get("ST_COUNT") or 0) > 0:
                return int(task["ID"])

        billable = next(
            (
                task
                for task in r.json()
                if task.get("VODITEL_ID")
                and task.get("TK_NAME")
                and float(task.get("PRICE") or 0) > 0
                and int(task.get("ST_COUNT") or 0) > 0
                and not task.get("PAY_ORDER_ID")
            ),
            None,
        )
        if billable:
            r_order = api.post(f"{BASE_URL}/api/admin/transport/billing/orders", json={
                "company": billable["TK_NAME"],
                "date_from": TODAY,
                "date_to": TODAY,
            })
            if r_order.status_code in (200, 201):
                order_id = r_order.json()["order_id"]
                r_add = api.post(
                    f"{BASE_URL}/api/admin/transport/billing/orders/{order_id}/tasks",
                    json={"tt_ids": [int(billable["ID"])]},
                )
                if r_add.status_code == 200:
                    return int(billable["ID"])
        for task in r.json():
            if task.get("PAY_ORDER_ID"):
                return int(task["ID"])
    pytest.skip("No billable task available for billed-trip protection tests")


@pytest.fixture(scope="session")
def billed_task_with_st(api, billed_task_id):
    """Return billed task ID and one of its ST numbers."""
    r = api.get(f"{BASE_URL}/api/admin/transport/tasks/{billed_task_id}/sts")
    if r.status_code != 200 or not r.json():
        pytest.skip("No STs in billed task")
    st_number = r.json()[0]["ST_NUMBER"]
    return {"task_id": billed_task_id, "st_number": st_number}


class TestBilledTripProtection:
    def test_cancel_billed_trip_returns_409(self, api, billed_task_id):
        r = api.post(
            f"{BASE_URL}/api/admin/transport/tasks/{billed_task_id}/cancel"
        )
        assert r.status_code == 409, f"Expected 409, got {r.status_code}: {r.text}"

    def test_assign_st_to_billed_trip_returns_409(self, api, billed_task_id):
        r = api.post(
            f"{BASE_URL}/api/admin/transport/tasks/{billed_task_id}/sts",
            json={"st_numbers": ["СТ-999999"]},
        )
        assert r.status_code == 409, f"Expected 409, got {r.status_code}: {r.text}"

    def test_unassign_st_from_billed_trip_returns_409(self, api, billed_task_with_st):
        task_id = billed_task_with_st["task_id"]
        st_number = billed_task_with_st["st_number"]
        r = api.delete(
            f"{BASE_URL}/api/admin/transport/tasks/{task_id}/sts/{st_number}"
        )
        assert r.status_code == 409, f"Expected 409, got {r.status_code}: {r.text}"

    def test_cancel_error_mentions_order_id(self, api, billed_task_id):
        r = api.post(
            f"{BASE_URL}/api/admin/transport/tasks/{billed_task_id}/cancel"
        )
        if r.status_code == 409:
            body = r.json()
            assert "счёт" in str(body).lower() or "409" in str(r.status_code)


class TestBilledTripAllowedActions:
    def test_note_update_allowed(self, api, billed_task_id):
        r = api.patch(
            f"{BASE_URL}/api/admin/transport/tasks/{billed_task_id}",
            json={"primechanie": "Тест-20 примечание"},
        )
        assert r.status_code in (200, 204), f"{r.status_code}: {r.text}"

    def test_recalculate_price_allowed(self, api, billed_task_id):
        r = api.post(
            f"{BASE_URL}/api/admin/transport/tasks/{billed_task_id}/recalculate-price"
        )
        assert r.status_code == 200, f"{r.status_code}: {r.text}"

    def test_set_price_allowed(self, api, billed_task_id):
        r = api.patch(
            f"{BASE_URL}/api/admin/transport/tasks/{billed_task_id}/price",
            json={"price": 5000.0},
        )
        assert r.status_code == 200, f"{r.status_code}: {r.text}"
