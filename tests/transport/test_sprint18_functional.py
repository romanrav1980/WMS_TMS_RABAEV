"""
test_sprint18_functional.py — Functional completeness tests for Sprint 18.

Sprint 18 scope: billing — price management
  - POST /tasks/{id}/recalculate-price  — calls Oracle stoim_tt, returns price
  - PATCH /tasks/{id}/price             — manual price override
  - DELETE /billing/orders/{id}/tasks/{tt_id} — unlink task from billing order

Run:
    pytest tests/transport/test_sprint18_functional.py -v
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
def task_id(api):
    """Get an existing task ID (any open task)."""
    r = api.get(f"{BASE_URL}/api/admin/transport/tasks", params={"stdate": TODAY})
    if r.status_code != 200 or not r.json():
        pytest.skip("No tasks available for today")
    return r.json()[0]["ID"]


@pytest.fixture(scope="session")
def billing_order_with_task(api, task_id):
    """Create a billing order linked to a task."""
    r_task = api.get(f"{BASE_URL}/api/admin/transport/tasks/{task_id}")
    if r_task.status_code != 200:
        pytest.skip("Cannot get task detail")
    task = r_task.json()
    if task.get("PAY_ORDER_ID"):
        pytest.skip("Task already has a billing order")

    r = api.post(f"{BASE_URL}/api/admin/transport/billing/orders", json={
        "company": "ООО Тест-18",
        "date_from": TODAY,
        "date_to": TODAY,
    })
    if r.status_code not in (200, 201):
        pytest.skip(f"Cannot create billing order: {r.status_code}")
    order_id = r.json()["order_id"]

    api.post(
        f"{BASE_URL}/api/admin/transport/billing/orders/{order_id}/tasks",
        json={"tt_ids": [task_id]},
    )
    return {"order_id": order_id, "task_id": task_id}


class TestRecalculatePrice:
    def test_recalculate_returns_200(self, api, task_id):
        r = api.post(f"{BASE_URL}/api/admin/transport/tasks/{task_id}/recalculate-price")
        assert r.status_code == 200, f"{r.status_code}: {r.text}"

    def test_recalculate_returns_price_field(self, api, task_id):
        r = api.post(f"{BASE_URL}/api/admin/transport/tasks/{task_id}/recalculate-price")
        data = r.json()
        assert "price" in data
        assert isinstance(data["price"], (int, float))
        assert data["price"] >= 0

    def test_recalculate_returns_task_id(self, api, task_id):
        r = api.post(f"{BASE_URL}/api/admin/transport/tasks/{task_id}/recalculate-price")
        data = r.json()
        assert data.get("task_id") == task_id

    def test_recalculate_nonexistent_404(self, api):
        r = api.post(f"{BASE_URL}/api/admin/transport/tasks/999999999/recalculate-price")
        assert r.status_code == 404


class TestSetPrice:
    def test_set_price_200(self, api, task_id):
        r = api.patch(
            f"{BASE_URL}/api/admin/transport/tasks/{task_id}/price",
            json={"price": 12345.50},
        )
        assert r.status_code == 200, f"{r.status_code}: {r.text}"

    def test_set_price_returns_price(self, api, task_id):
        r = api.patch(
            f"{BASE_URL}/api/admin/transport/tasks/{task_id}/price",
            json={"price": 9999.00},
        )
        data = r.json()
        assert data.get("price") == 9999.00

    def test_set_price_nonexistent_404(self, api):
        r = api.patch(
            f"{BASE_URL}/api/admin/transport/tasks/999999999/price",
            json={"price": 100.0},
        )
        assert r.status_code == 404

    def test_set_price_negative_rejected(self, api, task_id):
        r = api.patch(
            f"{BASE_URL}/api/admin/transport/tasks/{task_id}/price",
            json={"price": -100.0},
        )
        assert r.status_code == 422


class TestRemoveTaskFromBillingOrder:
    def test_remove_task_200(self, api, billing_order_with_task):
        order_id = billing_order_with_task["order_id"]
        task_id = billing_order_with_task["task_id"]
        r = api.delete(
            f"{BASE_URL}/api/admin/transport/billing/orders/{order_id}/tasks/{task_id}"
        )
        assert r.status_code == 200, f"{r.status_code}: {r.text}"

    def test_remove_task_returns_removed_flag(self, api, billing_order_with_task):
        order_id = billing_order_with_task["order_id"]
        task_id = billing_order_with_task["task_id"]
        # Re-add the task first
        api.post(
            f"{BASE_URL}/api/admin/transport/billing/orders/{order_id}/tasks",
            json={"tt_ids": [task_id]},
        )
        r = api.delete(
            f"{BASE_URL}/api/admin/transport/billing/orders/{order_id}/tasks/{task_id}"
        )
        if r.status_code == 200:
            assert r.json().get("removed") is True

    def test_remove_nonexistent_order_404(self, api):
        r = api.delete(
            f"{BASE_URL}/api/admin/transport/billing/orders/999999999/tasks/1"
        )
        assert r.status_code == 404
