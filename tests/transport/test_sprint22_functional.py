"""
test_sprint22_functional.py — Functional tests for Sprint 22.

Sprint 22 scope:
  - GET /billing/companies  — returns list of strings from RRL_BILL_COMPANY
  - BillingOrder includes num_plat field in list and single-order responses
  - list_billing_orders SQL includes NUM_PLAT in GROUP BY (no Oracle errors)
  - get_billing_order SQL includes NUM_PLAT in GROUP BY (no Oracle errors)

Run:
    pytest tests/transport/test_sprint22_functional.py -v
"""

import pytest
import requests

BASE = "http://127.0.0.1:8088"
AUTH = ("admin", "admin123")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def get(path: str, **kwargs) -> requests.Response:
    return requests.get(f"{BASE}{path}", auth=AUTH, **kwargs)


def post(path: str, json=None) -> requests.Response:
    return requests.post(f"{BASE}{path}", auth=AUTH, json=json)


# ---------------------------------------------------------------------------
# GET /billing/companies
# ---------------------------------------------------------------------------

class TestBillingCompanies:

    def test_endpoint_returns_200(self):
        r = get("/api/admin/transport/billing/companies")
        assert r.status_code == 200

    def test_returns_list(self):
        r = get("/api/admin/transport/billing/companies")
        data = r.json()
        assert isinstance(data, list)

    def test_items_are_strings(self):
        r = get("/api/admin/transport/billing/companies")
        data = r.json()
        for item in data:
            assert isinstance(item, str), f"Expected str, got {type(item)}: {item}"

    def test_no_empty_strings(self):
        r = get("/api/admin/transport/billing/companies")
        data = r.json()
        for item in data:
            assert item.strip() != "", "Empty company name returned"

    def test_requires_auth(self):
        r = requests.get(f"{BASE}/api/admin/transport/billing/companies")
        assert r.status_code in (401, 403)


# ---------------------------------------------------------------------------
# BillingOrder schema — num_plat field
# ---------------------------------------------------------------------------

class TestBillingOrderNumPlat:

    def test_list_orders_includes_num_plat_key(self):
        r = get("/api/admin/transport/billing/orders")
        assert r.status_code == 200
        data = r.json()
        if data:
            order = data[0]
            assert "num_plat" in order, "num_plat field missing from list response"

    def test_list_orders_num_plat_is_string_or_null(self):
        r = get("/api/admin/transport/billing/orders")
        assert r.status_code == 200
        for order in r.json():
            val = order.get("num_plat")
            assert val is None or isinstance(val, str), \
                f"num_plat must be str|null, got {type(val)}"

    def test_single_order_includes_num_plat(self):
        r = get("/api/admin/transport/billing/orders")
        assert r.status_code == 200
        orders = r.json()
        if not orders:
            pytest.skip("No billing orders available")
        order_id = orders[0]["order_id"]
        r2 = get(f"/api/admin/transport/billing/orders/{order_id}")
        assert r2.status_code == 200
        data = r2.json()
        assert "num_plat" in data, "num_plat field missing from single-order response"

    def test_list_with_filter_includes_num_plat(self):
        r = get("/api/admin/transport/billing/orders", params={"closed": 0})
        assert r.status_code == 200
        for order in r.json():
            assert "num_plat" in order


# ---------------------------------------------------------------------------
# Schema validation — existing fields still present
# ---------------------------------------------------------------------------

class TestBillingOrderSchemaRegression:

    def test_list_has_all_required_fields(self):
        r = get("/api/admin/transport/billing/orders")
        assert r.status_code == 200
        for order in r.json():
            for field in ("order_id", "num", "company", "closed", "payed",
                          "task_count", "total_price", "date_from", "date_to"):
                assert field in order, f"Required field '{field}' missing"
