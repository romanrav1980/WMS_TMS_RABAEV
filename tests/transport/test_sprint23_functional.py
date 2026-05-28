"""
test_sprint23_functional.py — Functional tests for Sprint 23.

Sprint 23 scope:
  - GET /billing/orders/{id}/tasks — list of trips in a billing order
  - Response fields: tt_id, transport, status, price, shipment_date
  - Returns 200 and empty list for valid order with no tasks
  - Returns 404 for unknown order

Run:
    pytest tests/transport/test_sprint23_functional.py -v
"""

import pytest
import requests

from tests.transport.config import API_BASE as BASE, API_AUTH as AUTH


def get(path: str, **kwargs) -> requests.Response:
    return requests.get(f"{BASE}{path}", auth=AUTH, **kwargs)


def post(path: str, json=None) -> requests.Response:
    return requests.post(f"{BASE}{path}", auth=AUTH, json=json)


def first_order_id() -> int | None:
    r = get("/api/admin/transport/billing/orders")
    if r.status_code != 200:
        return None
    orders = r.json()
    return orders[0]["order_id"] if orders else None


# ---------------------------------------------------------------------------
# GET /billing/orders/{id}/tasks
# ---------------------------------------------------------------------------

class TestBillingOrderTasks:

    def test_returns_200_for_valid_order(self):
        oid = first_order_id()
        if oid is None:
            pytest.skip("No billing orders available")
        r = get(f"/api/admin/transport/billing/orders/{oid}/tasks")
        assert r.status_code == 200

    def test_returns_list(self):
        oid = first_order_id()
        if oid is None:
            pytest.skip("No billing orders available")
        r = get(f"/api/admin/transport/billing/orders/{oid}/tasks")
        assert isinstance(r.json(), list)

    def test_task_has_required_fields(self):
        oid = first_order_id()
        if oid is None:
            pytest.skip("No billing orders available")
        r = get(f"/api/admin/transport/billing/orders/{oid}/tasks")
        tasks = r.json()
        for t in tasks:
            for field in ("tt_id", "transport", "status", "price", "shipment_date"):
                assert field in t, f"Field '{field}' missing from task response"

    def test_tt_id_is_integer(self):
        oid = first_order_id()
        if oid is None:
            pytest.skip("No billing orders available")
        r = get(f"/api/admin/transport/billing/orders/{oid}/tasks")
        for t in r.json():
            assert isinstance(t["tt_id"], int)

    def test_price_is_number(self):
        oid = first_order_id()
        if oid is None:
            pytest.skip("No billing orders available")
        r = get(f"/api/admin/transport/billing/orders/{oid}/tasks")
        for t in r.json():
            assert isinstance(t["price"], (int, float))

    def test_404_for_nonexistent_order(self):
        r = get("/api/admin/transport/billing/orders/999999999/tasks")
        assert r.status_code == 404

    def test_requires_auth(self):
        oid = first_order_id()
        if oid is None:
            pytest.skip("No billing orders available")
        r = requests.get(f"{BASE}/api/admin/transport/billing/orders/{oid}/tasks")
        assert r.status_code in (401, 403)


# ---------------------------------------------------------------------------
# Task list consistency with order header
# ---------------------------------------------------------------------------

class TestBillingOrderConsistency:

    def test_task_count_matches_header(self):
        """task_count in order header should match actual tasks returned."""
        r = get("/api/admin/transport/billing/orders")
        assert r.status_code == 200
        orders = r.json()
        if not orders:
            pytest.skip("No billing orders available")
        # Check first order with at least 1 task
        for order in orders:
            if (order.get("task_count") or 0) > 0:
                r2 = get(f"/api/admin/transport/billing/orders/{order['order_id']}/tasks")
                assert r2.status_code == 200
                tasks = r2.json()
                assert len(tasks) == order["task_count"], \
                    f"Header task_count={order['task_count']} but got {len(tasks)} tasks"
                break

    def test_total_price_matches_sum(self):
        """total_price in header should equal sum of task prices."""
        r = get("/api/admin/transport/billing/orders")
        if r.status_code != 200:
            pytest.skip("Cannot fetch orders")
        for order in r.json():
            if (order.get("task_count") or 0) > 0:
                r2 = get(f"/api/admin/transport/billing/orders/{order['order_id']}/tasks")
                tasks = r2.json()
                if tasks:
                    total = sum(t["price"] for t in tasks)
                    assert abs(total - (order.get("total_price") or 0)) < 0.01, \
                        f"total_price mismatch: header={order['total_price']}, sum={total}"
                    break
