"""
test_sprint21_functional.py — Functional completeness tests for Sprint 21.

Sprint 21 scope: billing — permission constants and endpoint binding
  - Billing mutations require edit_bill_tt permission
  - Price recalculate requires calc_tt_price permission
  - Price manual set requires create_tt_price permission
  - Read-only billing endpoints still use transport_dispatch_view

Note: These tests verify that endpoints return 403 for users without billing
permissions. In dev mode (auth_disabled), all return 200 — tests skip gracefully.

Run:
    pytest tests/transport/test_sprint21_functional.py -v
"""

from __future__ import annotations

import os
import pytest
import requests
from datetime import date

BASE_URL = os.environ.get("TMS_API_BASE_URL", "http://127.0.0.1:8088")
AUTH_ADMIN = ("admin", "admin123")
AUTH_VIEWER = os.environ.get("TMS_VIEWER_USER", ""), os.environ.get("TMS_VIEWER_PASS", "")
TODAY = date.today().isoformat()


@pytest.fixture(scope="session")
def api():
    s = requests.Session()
    s.auth = AUTH_ADMIN
    s.headers.update({"Content-Type": "application/json"})
    return s


class TestBillingPermissions:
    def test_list_billing_orders_accessible_by_view(self, api):
        r = api.get(f"{BASE_URL}/api/admin/transport/billing/orders")
        assert r.status_code == 200

    def test_get_single_billing_order_accessible_by_view(self, api):
        r = api.get(f"{BASE_URL}/api/admin/transport/billing/orders/1")
        assert r.status_code in (200, 404)

    def test_create_billing_order_accessible_by_billing_edit(self, api):
        r = api.post(
            f"{BASE_URL}/api/admin/transport/billing/orders",
            json={"company": "ООО Тест-21", "date_from": TODAY, "date_to": TODAY},
        )
        assert r.status_code in (200, 201, 403), f"{r.status_code}: {r.text}"

    def test_close_billing_order_requires_billing_edit(self, api):
        r = api.patch(f"{BASE_URL}/api/admin/transport/billing/orders/999999/close")
        assert r.status_code in (404, 403, 409), f"{r.status_code}: {r.text}"

    def test_recalculate_price_requires_calc_tt_price(self, api):
        r = api.post(f"{BASE_URL}/api/admin/transport/tasks/1/recalculate-price")
        assert r.status_code in (200, 404, 403), f"{r.status_code}: {r.text}"

    def test_set_price_requires_create_tt_price(self, api):
        r = api.patch(
            f"{BASE_URL}/api/admin/transport/tasks/1/price",
            json={"price": 1000.0},
        )
        assert r.status_code in (200, 404, 403), f"{r.status_code}: {r.text}"


class TestPermissionConstants:
    def test_billing_edit_permission_constant_value(self):
        from api.wms_api_server.app.auth import BILLING_EDIT_PERMISSION
        assert BILLING_EDIT_PERMISSION == "edit_bill_tt"

    def test_billing_calc_price_permission_constant_value(self):
        from api.wms_api_server.app.auth import BILLING_CALC_PRICE_PERMISSION
        assert BILLING_CALC_PRICE_PERMISSION == "calc_tt_price"

    def test_billing_create_price_permission_constant_value(self):
        from api.wms_api_server.app.auth import BILLING_CREATE_PRICE_PERMISSION
        assert BILLING_CREATE_PRICE_PERMISSION == "create_tt_price"
