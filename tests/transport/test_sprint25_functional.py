"""
test_sprint25_functional.py — Functional tests for Sprint 25.

Sprint 25 scope:
  - UI button «Снять с биллинга» for detaching a trip from its billing order
  - DELETE /billing/orders/{order_id}/tasks/{tt_id} — existing endpoint
  - Regression: billing order endpoints still return correct structure

Run:
    pytest tests/transport/test_sprint25_functional.py -v
"""

import pytest
import requests

BASE = "http://127.0.0.1:8088"
AUTH = ("admin", "admin123")


def get(path: str, **kwargs) -> requests.Response:
    return requests.get(f"{BASE}{path}", auth=AUTH, **kwargs)


def post(path: str, json=None) -> requests.Response:
    return requests.post(f"{BASE}{path}", auth=AUTH, json=json)


def delete(path: str) -> requests.Response:
    return requests.delete(f"{BASE}{path}", auth=AUTH)


# ---------------------------------------------------------------------------
# Regression: billing order list structure
# ---------------------------------------------------------------------------

class TestBillingOrdersRegression:

    def test_orders_endpoint_reachable(self):
        r = get("/api/admin/transport/billing/orders")
        assert r.status_code in (200, 401, 403)

    def test_orders_list_is_array(self):
        r = get("/api/admin/transport/billing/orders")
        if r.status_code != 200:
            pytest.skip("No access or no data")
        assert isinstance(r.json(), list)

    def test_order_has_required_fields(self):
        r = get("/api/admin/transport/billing/orders")
        if r.status_code != 200:
            pytest.skip("No access")
        orders = r.json()
        if not orders:
            pytest.skip("No billing orders in DB")
        order = orders[0]
        for field in ("order_id", "closed", "payed"):
            assert field in order, f"Missing field: {field}"

    def test_order_has_num_plat(self):
        r = get("/api/admin/transport/billing/orders")
        if r.status_code != 200:
            pytest.skip("No access")
        orders = r.json()
        if not orders:
            pytest.skip("No billing orders in DB")
        assert "num_plat" in orders[0]


# ---------------------------------------------------------------------------
# DELETE /billing/orders/{id}/tasks/{tt_id} — detach endpoint
# ---------------------------------------------------------------------------

class TestDetachFromBilling:

    def _get_open_order_with_tasks(self):
        """Find an open (not closed, not payed) billing order that has tasks."""
        r = get("/api/admin/transport/billing/orders")
        if r.status_code != 200:
            return None, None
        for order in r.json():
            if order.get("closed") or order.get("payed"):
                continue
            oid = order["order_id"]
            rt = get(f"/api/admin/transport/billing/orders/{oid}/tasks")
            if rt.status_code == 200 and rt.json():
                return oid, rt.json()[0]["tt_id"]
        return None, None

    def test_detach_endpoint_exists(self):
        """DELETE /billing/orders/{id}/tasks/{tt_id} should not 404 on a valid call."""
        oid, tt_id = self._get_open_order_with_tasks()
        if not oid:
            pytest.skip("No open billing order with tasks found")
        r = delete(f"/api/admin/transport/billing/orders/{oid}/tasks/{tt_id}")
        assert r.status_code in (200, 204, 400, 422), \
            f"Unexpected status {r.status_code}: {r.text}"

    def test_detach_closed_order_rejected(self):
        """Cannot detach from a closed order — should return 4xx."""
        r = get("/api/admin/transport/billing/orders")
        if r.status_code != 200:
            pytest.skip("No access")
        closed = [o for o in r.json() if o.get("closed")]
        if not closed:
            pytest.skip("No closed billing orders")
        oid = closed[0]["order_id"]
        rt = get(f"/api/admin/transport/billing/orders/{oid}/tasks")
        if rt.status_code != 200 or not rt.json():
            pytest.skip("No tasks in closed order")
        tt_id = rt.json()[0]["tt_id"]
        r = delete(f"/api/admin/transport/billing/orders/{oid}/tasks/{tt_id}")
        assert r.status_code in (400, 409, 422), \
            f"Expected rejection for closed order, got {r.status_code}"

    def test_detach_payed_order_rejected(self):
        """Cannot detach from a payed order — should return 4xx."""
        r = get("/api/admin/transport/billing/orders")
        if r.status_code != 200:
            pytest.skip("No access")
        payed = [o for o in r.json() if o.get("payed")]
        if not payed:
            pytest.skip("No payed billing orders")
        oid = payed[0]["order_id"]
        rt = get(f"/api/admin/transport/billing/orders/{oid}/tasks")
        if rt.status_code != 200 or not rt.json():
            pytest.skip("No tasks in payed order")
        tt_id = rt.json()[0]["tt_id"]
        r = delete(f"/api/admin/transport/billing/orders/{oid}/tasks/{tt_id}")
        assert r.status_code in (400, 409, 422), \
            f"Expected rejection for payed order, got {r.status_code}"

    def test_detach_nonexistent_task_is_graceful(self):
        """Deleting a non-existent task should not crash the server."""
        r = get("/api/admin/transport/billing/orders")
        if r.status_code != 200:
            pytest.skip("No access")
        orders = r.json()
        if not orders:
            pytest.skip("No billing orders")
        oid = orders[0]["order_id"]
        r = delete(f"/api/admin/transport/billing/orders/{oid}/tasks/999999999")
        assert r.status_code in (200, 204, 400, 404, 422)


# ---------------------------------------------------------------------------
# Tasks endpoint structure (prerequisite for detach UI)
# ---------------------------------------------------------------------------

class TestBillingOrderTasks:

    def test_tasks_endpoint_returns_array(self):
        r = get("/api/admin/transport/billing/orders")
        if r.status_code != 200:
            pytest.skip("No access")
        orders = r.json()
        if not orders:
            pytest.skip("No orders")
        oid = orders[0]["order_id"]
        rt = get(f"/api/admin/transport/billing/orders/{oid}/tasks")
        assert rt.status_code in (200, 404)
        if rt.status_code == 200:
            assert isinstance(rt.json(), list)

    def test_tasks_have_tt_id(self):
        r = get("/api/admin/transport/billing/orders")
        if r.status_code != 200:
            pytest.skip("No access")
        orders = r.json()
        if not orders:
            pytest.skip("No orders")
        oid = orders[0]["order_id"]
        rt = get(f"/api/admin/transport/billing/orders/{oid}/tasks")
        if rt.status_code != 200:
            pytest.skip("Tasks endpoint missing")
        tasks = rt.json()
        if not tasks:
            pytest.skip("No tasks in first order")
        for t in tasks:
            assert "tt_id" in t, "task missing tt_id"
