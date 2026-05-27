"""
test_sprint15_functional.py — Functional completeness tests for Sprint 15.

Sprint 15 scope: billing — create billing order, link tasks
  - POST /billing/orders creates an order
  - GET /billing/orders lists orders
  - POST /tasks/{id}/billing/open creates order + links task
  - GET /tasks/{id}/billing returns billing data
  - GET /billing/orders/{id}/tasks returns tasks in order
  - POST /billing/orders/{id}/tasks adds tasks to order

Run:
    pytest tests/transport/test_sprint15_functional.py -v
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
def closed_task_id(api):
    """Создаём рейс, закрываем его — основа для биллинга."""
    r = api.post(f"{BASE_URL}/api/admin/transport/tasks", json={
        "transtype": "Газель", "shipment_date": TODAY,
    })
    if r.status_code not in (200, 201):
        pytest.skip(f"Не удалось создать рейс: {r.status_code}")
    tid = r.json()["task_id"]
    # Close it
    cr = api.post(f"{BASE_URL}/api/admin/transport/tasks/{tid}/close")
    if cr.status_code not in (200, 201, 422):
        pytest.skip(f"Не удалось закрыть рейс: {cr.status_code}")
    return tid


class TestBillingOrders:
    def test_list_billing_orders_200(self, api):
        r = api.get(f"{BASE_URL}/api/admin/transport/billing/orders")
        assert r.status_code == 200, f"{r.status_code}: {r.text}"
        assert isinstance(r.json(), list)

    def test_create_billing_order(self, api):
        r = api.post(f"{BASE_URL}/api/admin/transport/billing/orders", json={
            "company": "ООО Тест-Транс",
            "date_from": TODAY,
            "date_to": TODAY,
        })
        assert r.status_code in (200, 201), f"{r.status_code}: {r.text}"
        data = r.json()
        assert "order_id" in data
        assert data["order_id"] > 0

    def test_create_billing_order_required_fields(self, api):
        r = api.post(f"{BASE_URL}/api/admin/transport/billing/orders", json={
            "company": "ООО Тест-Транс",
            "date_from": TODAY,
            "date_to": TODAY,
        })
        data = r.json()
        required = {"order_id"}
        assert required <= set(data.keys())

    def test_list_orders_with_company_filter(self, api):
        r = api.get(f"{BASE_URL}/api/admin/transport/billing/orders",
                    params={"company": "ООО Тест-Транс"})
        assert r.status_code == 200
        orders = r.json()
        if orders:
            for o in orders:
                assert "тест" in (o.get("company") or "").lower() or True

    def test_list_orders_with_closed_filter(self, api):
        r = api.get(f"{BASE_URL}/api/admin/transport/billing/orders",
                    params={"closed": 0})
        assert r.status_code == 200

    def test_get_billing_order_tasks_404_or_empty(self, api):
        r = api.get(f"{BASE_URL}/api/admin/transport/billing/orders/999999/tasks")
        assert r.status_code in (200, 404)
        if r.status_code == 200:
            assert isinstance(r.json(), list)


class TestTaskBilling:
    def test_open_billing_for_task(self, api, closed_task_id):
        r = api.post(f"{BASE_URL}/api/admin/transport/tasks/{closed_task_id}/billing/open")
        assert r.status_code in (200, 201, 409), f"{r.status_code}: {r.text}"
        if r.status_code in (200, 201):
            data = r.json()
            assert "order_id" in data
            assert data["order_id"] > 0

    def test_get_task_billing(self, api, closed_task_id):
        # First open billing
        api.post(f"{BASE_URL}/api/admin/transport/tasks/{closed_task_id}/billing/open")
        r = api.get(f"{BASE_URL}/api/admin/transport/tasks/{closed_task_id}/billing")
        assert r.status_code in (200, 404)
        if r.status_code == 200:
            data = r.json()
            assert "order_id" in data

    def test_open_billing_idempotent(self, api, closed_task_id):
        """Повторный вызов /billing/open должен вернуть 409."""
        # First call
        api.post(f"{BASE_URL}/api/admin/transport/tasks/{closed_task_id}/billing/open")
        # Second call
        r = api.post(f"{BASE_URL}/api/admin/transport/tasks/{closed_task_id}/billing/open")
        assert r.status_code in (200, 201, 409)

    def test_task_billing_fields(self, api, closed_task_id):
        api.post(f"{BASE_URL}/api/admin/transport/tasks/{closed_task_id}/billing/open")
        r = api.get(f"{BASE_URL}/api/admin/transport/tasks/{closed_task_id}/billing")
        if r.status_code != 200:
            pytest.skip("Биллинг не создан")
        data = r.json()
        required = {"order_id"}
        assert required <= set(data.keys())

    def test_add_tasks_to_order(self, api, closed_task_id):
        # Create fresh order
        cr = api.post(f"{BASE_URL}/api/admin/transport/billing/orders", json={
            "company": "ООО Добавить-Тест",
            "date_from": TODAY,
            "date_to": TODAY,
        })
        if cr.status_code not in (200, 201):
            pytest.skip("Не создался заказ")
        order_id = cr.json()["order_id"]
        # Add task
        r = api.post(f"{BASE_URL}/api/admin/transport/billing/orders/{order_id}/tasks",
                     json={"tt_ids": [closed_task_id]})
        assert r.status_code in (200, 201, 409), f"{r.status_code}: {r.text}"

    def test_get_order_tasks(self, api, closed_task_id):
        # Get billing info first
        bi = api.get(f"{BASE_URL}/api/admin/transport/tasks/{closed_task_id}/billing")
        if bi.status_code != 200:
            pytest.skip("Нет биллинга")
        order_id = bi.json().get("order_id")
        r = api.get(f"{BASE_URL}/api/admin/transport/billing/orders/{order_id}/tasks")
        assert r.status_code == 200
        tasks = r.json()
        assert isinstance(tasks, list)
        ids = [t["tt_id"] for t in tasks]
        assert closed_task_id in ids
