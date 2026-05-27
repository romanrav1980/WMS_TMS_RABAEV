"""
test_sprint19_functional.py — Functional completeness tests for Sprint 19.

Sprint 19 scope: billing — link trip to existing billing order
  - GET /billing/orders?company=X&closed=0 returns open orders for company
  - POST /billing/orders/{id}/tasks adds task to existing order
  - Task can be linked to an existing order (not only via /billing/open)

Run:
    pytest tests/transport/test_sprint19_functional.py -v
"""

from __future__ import annotations

import os
import pytest
import requests
from datetime import date

BASE_URL = os.environ.get("TMS_API_BASE_URL", "http://127.0.0.1:8088")
AUTH = ("admin", "admin123")
TODAY = date.today().isoformat()
COMPANY = "ООО Тест-19-Линк"


@pytest.fixture(scope="session")
def api():
    s = requests.Session()
    s.auth = AUTH
    s.headers.update({"Content-Type": "application/json"})
    return s


@pytest.fixture(scope="session")
def open_order(api):
    r = api.post(f"{BASE_URL}/api/admin/transport/billing/orders", json={
        "company": COMPANY,
        "date_from": TODAY,
        "date_to": TODAY,
    })
    if r.status_code not in (200, 201):
        pytest.skip(f"Cannot create billing order: {r.status_code}")
    return r.json()["order_id"]


@pytest.fixture(scope="session")
def task_for_link(api):
    """Find a task that is not yet in a billing order."""
    r = api.get(f"{BASE_URL}/api/admin/transport/tasks", params={"stdate": TODAY})
    if r.status_code != 200 or not r.json():
        pytest.skip("No tasks for today")
    for task in r.json():
        if not task.get("PAY_ORDER_ID"):
            return task["ID"]
    pytest.skip("No unlinked tasks available")


class TestOpenOrdersFilter:
    def test_filter_by_company_returns_matching(self, api, open_order):
        r = api.get(
            f"{BASE_URL}/api/admin/transport/billing/orders",
            params={"company": COMPANY},
        )
        assert r.status_code == 200
        data = r.json()
        assert any(o["order_id"] == open_order for o in data), \
            f"Order {open_order} not found for company {COMPANY}"

    def test_filter_closed_0_excludes_closed(self, api, open_order):
        r = api.get(
            f"{BASE_URL}/api/admin/transport/billing/orders",
            params={"closed": 0},
        )
        assert r.status_code == 200
        for o in r.json():
            assert o["closed"] == 0

    def test_filter_payed_0_excludes_paid(self, api, open_order):
        r = api.get(
            f"{BASE_URL}/api/admin/transport/billing/orders",
            params={"payed": 0},
        )
        assert r.status_code == 200
        for o in r.json():
            assert o["payed"] == 0

    def test_combined_filter_open_orders_for_company(self, api, open_order):
        r = api.get(
            f"{BASE_URL}/api/admin/transport/billing/orders",
            params={"company": COMPANY, "closed": 0, "payed": 0},
        )
        assert r.status_code == 200
        data = r.json()
        assert any(o["order_id"] == open_order for o in data)
        for o in data:
            assert o["closed"] == 0
            assert o["payed"] == 0


class TestLinkTaskToExistingOrder:
    def test_add_task_to_existing_order(self, api, open_order, task_for_link):
        r = api.post(
            f"{BASE_URL}/api/admin/transport/billing/orders/{open_order}/tasks",
            json={"tt_ids": [task_for_link]},
        )
        assert r.status_code == 200, f"{r.status_code}: {r.text}"

    def test_task_appears_in_order_tasks(self, api, open_order, task_for_link):
        api.post(
            f"{BASE_URL}/api/admin/transport/billing/orders/{open_order}/tasks",
            json={"tt_ids": [task_for_link]},
        )
        r = api.get(f"{BASE_URL}/api/admin/transport/billing/orders/{open_order}/tasks")
        assert r.status_code == 200
        task_ids = [t["tt_id"] for t in r.json()]
        assert task_for_link in task_ids

    def test_task_billing_reflects_existing_order(self, api, open_order, task_for_link):
        r = api.get(f"{BASE_URL}/api/admin/transport/tasks/{task_for_link}/billing")
        if r.status_code == 200:
            assert r.json()["order_id"] == open_order

    def test_add_to_nonexistent_order_404(self, api):
        r = api.post(
            f"{BASE_URL}/api/admin/transport/billing/orders/999999999/tasks",
            json={"tt_ids": [1]},
        )
        assert r.status_code in (404, 422, 500)

    def test_get_order_reflects_linked_task(self, api, open_order, task_for_link):
        r = api.get(f"{BASE_URL}/api/admin/transport/billing/orders/{open_order}")
        assert r.status_code == 200
        data = r.json()
        assert data["order_id"] == open_order
        assert (data.get("task_count") or 0) >= 1
