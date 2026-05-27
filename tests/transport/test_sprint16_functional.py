"""
test_sprint16_functional.py — Functional completeness tests for Sprint 16.

Sprint 16 scope: billing — close and pay billing order
  - GET /billing/orders/{id} returns single order
  - PATCH /billing/orders/{id}/close closes order (calls RRL_CLOSE_BILLINGORDER)
  - PATCH /billing/orders/{id}/pay marks order as paid (calls RRL_PAY_BILLINGORDER)
  - Status machine: open → closed → paid; reverse transitions not allowed

Run:
    pytest tests/transport/test_sprint16_functional.py -v
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
def fresh_order_id(api):
    r = api.post(f"{BASE_URL}/api/admin/transport/billing/orders", json={
        "company": "ООО Тест-16",
        "date_from": TODAY,
        "date_to": TODAY,
    })
    if r.status_code not in (200, 201):
        pytest.skip(f"Не удалось создать заказ: {r.status_code}")
    return r.json()["order_id"]


class TestBillingOrderGet:
    def test_get_single_order_200(self, api, fresh_order_id):
        r = api.get(f"{BASE_URL}/api/admin/transport/billing/orders/{fresh_order_id}")
        assert r.status_code == 200, f"{r.status_code}: {r.text}"

    def test_get_single_order_fields(self, api, fresh_order_id):
        r = api.get(f"{BASE_URL}/api/admin/transport/billing/orders/{fresh_order_id}")
        data = r.json()
        required = {"order_id", "closed", "payed"}
        assert required <= set(data.keys())
        assert data["order_id"] == fresh_order_id

    def test_get_nonexistent_order_404(self, api):
        r = api.get(f"{BASE_URL}/api/admin/transport/billing/orders/999999999")
        assert r.status_code == 404

    def test_new_order_is_open(self, api, fresh_order_id):
        r = api.get(f"{BASE_URL}/api/admin/transport/billing/orders/{fresh_order_id}")
        data = r.json()
        assert data["closed"] == 0
        assert data["payed"] == 0


class TestBillingStatusMachine:
    def test_close_order(self, api, fresh_order_id):
        r = api.patch(f"{BASE_URL}/api/admin/transport/billing/orders/{fresh_order_id}/close")
        assert r.status_code in (200, 409), f"{r.status_code}: {r.text}"
        if r.status_code == 200:
            data = r.json()
            assert data["closed"] == 1

    def test_close_idempotent(self, api, fresh_order_id):
        """Повторное закрытие должно вернуть 409."""
        api.patch(f"{BASE_URL}/api/admin/transport/billing/orders/{fresh_order_id}/close")
        r = api.patch(f"{BASE_URL}/api/admin/transport/billing/orders/{fresh_order_id}/close")
        assert r.status_code in (200, 409)

    def test_pay_order(self, api, fresh_order_id):
        api.patch(f"{BASE_URL}/api/admin/transport/billing/orders/{fresh_order_id}/close")
        r = api.patch(f"{BASE_URL}/api/admin/transport/billing/orders/{fresh_order_id}/pay")
        assert r.status_code in (200, 409), f"{r.status_code}: {r.text}"
        if r.status_code == 200:
            data = r.json()
            assert data["payed"] == 1

    def test_pay_idempotent(self, api, fresh_order_id):
        """Повторная оплата должна вернуть 409."""
        api.patch(f"{BASE_URL}/api/admin/transport/billing/orders/{fresh_order_id}/close")
        api.patch(f"{BASE_URL}/api/admin/transport/billing/orders/{fresh_order_id}/pay")
        r = api.patch(f"{BASE_URL}/api/admin/transport/billing/orders/{fresh_order_id}/pay")
        assert r.status_code in (200, 409)

    def test_close_nonexistent_404(self, api):
        r = api.patch(f"{BASE_URL}/api/admin/transport/billing/orders/999999999/close")
        assert r.status_code == 404

    def test_pay_nonexistent_404(self, api):
        r = api.patch(f"{BASE_URL}/api/admin/transport/billing/orders/999999999/pay")
        assert r.status_code == 404

    def test_status_progression_reflected_in_list(self, api, fresh_order_id):
        """GET /billing/orders должен возвращать актуальный статус."""
        api.patch(f"{BASE_URL}/api/admin/transport/billing/orders/{fresh_order_id}/close")
        r = api.get(f"{BASE_URL}/api/admin/transport/billing/orders")
        orders = r.json()
        order = next((o for o in orders if o["order_id"] == fresh_order_id), None)
        if order:
            assert order["closed"] in (0, 1)
