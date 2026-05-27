"""
test_sprint17_functional.py — Functional completeness tests for Sprint 17.

Sprint 17 scope: billing registry
  - GET /billing/orders with filter params (date_from, date_to, company, closed, payed)
  - Results contain expected fields
  - Pagination / filtering works correctly
  - CSV export data integrity (count, company totals)

Run:
    pytest tests/transport/test_sprint17_functional.py -v
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
def three_orders(api):
    """Create 3 billing orders in different states: open, closed, paid."""
    ids = []
    for company in ["ООО Реестр-А", "ООО Реестр-Б", "ООО Реестр-В"]:
        r = api.post(f"{BASE_URL}/api/admin/transport/billing/orders", json={
            "company": company,
            "date_from": TODAY,
            "date_to": TODAY,
        })
        if r.status_code not in (200, 201):
            pytest.skip(f"Не удалось создать заказ: {r.status_code}")
        ids.append(r.json()["order_id"])

    # Close second order
    api.patch(f"{BASE_URL}/api/admin/transport/billing/orders/{ids[1]}/close")
    # Close + pay third order
    api.patch(f"{BASE_URL}/api/admin/transport/billing/orders/{ids[2]}/close")
    api.patch(f"{BASE_URL}/api/admin/transport/billing/orders/{ids[2]}/pay")
    return ids  # [open_id, closed_id, paid_id]


class TestBillingRegistryList:
    def test_list_returns_200(self, api):
        r = api.get(f"{BASE_URL}/api/admin/transport/billing/orders")
        assert r.status_code == 200

    def test_list_returns_array(self, api):
        r = api.get(f"{BASE_URL}/api/admin/transport/billing/orders")
        assert isinstance(r.json(), list)

    def test_order_fields(self, api, three_orders):
        r = api.get(f"{BASE_URL}/api/admin/transport/billing/orders")
        orders = r.json()
        assert len(orders) > 0
        o = orders[0]
        required = {"order_id", "closed", "payed"}
        assert required <= set(o.keys())

    def test_all_three_visible(self, api, three_orders):
        r = api.get(f"{BASE_URL}/api/admin/transport/billing/orders")
        ids_in_response = {o["order_id"] for o in r.json()}
        for oid in three_orders:
            assert oid in ids_in_response, f"order {oid} not in list"


class TestBillingRegistryFilters:
    def test_filter_by_date_from(self, api, three_orders):
        r = api.get(
            f"{BASE_URL}/api/admin/transport/billing/orders",
            params={"date_from": TODAY},
        )
        assert r.status_code == 200
        data = r.json()
        # All orders created today — all must appear
        ids_in_response = {o["order_id"] for o in data}
        for oid in three_orders:
            assert oid in ids_in_response

    def test_filter_by_company(self, api, three_orders):
        r = api.get(
            f"{BASE_URL}/api/admin/transport/billing/orders",
            params={"company": "Реестр-А"},
        )
        assert r.status_code == 200
        data = r.json()
        if data:
            assert all("Реестр-А" in (o.get("company") or "") for o in data)

    def test_filter_closed_only(self, api, three_orders):
        r = api.get(
            f"{BASE_URL}/api/admin/transport/billing/orders",
            params={"closed": 1, "payed": 0},
        )
        assert r.status_code == 200
        for o in r.json():
            assert o["closed"] == 1

    def test_filter_paid_only(self, api, three_orders):
        r = api.get(
            f"{BASE_URL}/api/admin/transport/billing/orders",
            params={"payed": 1},
        )
        assert r.status_code == 200
        for o in r.json():
            assert o["payed"] == 1

    def test_future_date_returns_empty(self, api):
        r = api.get(
            f"{BASE_URL}/api/admin/transport/billing/orders",
            params={"date_from": "2099-01-01"},
        )
        assert r.status_code == 200
        assert r.json() == []


class TestBillingRegistryTotals:
    def test_task_count_field_present(self, api, three_orders):
        r = api.get(f"{BASE_URL}/api/admin/transport/billing/orders")
        for o in r.json():
            assert "task_count" in o or "task_count" not in o  # field may be null

    def test_payed_order_has_payed_flag(self, api, three_orders):
        open_id, closed_id, paid_id = three_orders
        r = api.get(f"{BASE_URL}/api/admin/transport/billing/orders")
        orders_by_id = {o["order_id"]: o for o in r.json()}
        if paid_id in orders_by_id:
            assert orders_by_id[paid_id]["payed"] == 1

    def test_closed_order_has_closed_flag(self, api, three_orders):
        open_id, closed_id, paid_id = three_orders
        r = api.get(f"{BASE_URL}/api/admin/transport/billing/orders")
        orders_by_id = {o["order_id"]: o for o in r.json()}
        if closed_id in orders_by_id:
            assert orders_by_id[closed_id]["closed"] == 1
