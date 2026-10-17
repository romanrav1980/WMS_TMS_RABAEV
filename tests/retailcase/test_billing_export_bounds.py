"""Workbook bounds reject overflow instead of publishing a partial financial document."""
from contextlib import contextmanager

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from api.wms_api_server.app.modules.finance.contracts_billing_export import BillingExportError
from api.wms_api_server.app.modules.finance.infrastructure.billing_export_reads import (
    billing_order_export_rows, billing_registry_export_rows,
)
from api.wms_api_server.app.auth import AdminUser, get_current_admin
from api.wms_api_server.app.routers.transport import router


class Cursor:
    def __init__(self, batches):
        self.batches, self.rows, self.description, self.statements = iter(batches), [], [], []
    def execute(self, sql, params=None, **kwargs):
        self.statements.append((sql, params or kwargs))
        if sql == "set transaction read only":
            return
        self.rows = next(self.batches)
        self.description = [(key,) for key in self.rows[0]] if self.rows else []
    def fetchall(self):
        return [tuple(row.values()) for row in self.rows]


class Gateway:
    def __init__(self, batches):
        self.cursor = Cursor(batches)
    @contextmanager
    def transaction(self, label):
        yield self.cursor


@pytest.fixture
def workbook_scope(monkeypatch):
    """These tests isolate workbook bounds; admission is tested in scope cases."""
    from api.wms_api_server.app.modules.finance.infrastructure import billing_export_reads
    monkeypatch.setattr(billing_export_reads, "authorize_billing_export", lambda cursor, ids, actor: None)


def test_empty_registry_and_missing_order_have_different_outcomes(workbook_scope):
    assert billing_registry_export_rows(Gateway([[]]), None, None, None, None, None, "bounds-test") == []
    with pytest.raises(BillingExportError) as error:
        billing_order_export_rows(Gateway([[]]), 12, "bounds-test")
    assert error.value.status == 404


def test_single_order_exact_total_and_task_boundary(workbook_scope):
    rows = [dict(tt_id=i, transport="T", status="Ready", price="1.25", shipment_date="2026-10-15") for i in range(5000)]
    order, tasks = billing_order_export_rows(Gateway([[dict(order_id=12)], rows]), 12, "bounds-test")
    assert len(tasks) == 5000 and order["total_price"] == 6250 and order["task_count"] == 5000
    with pytest.raises(BillingExportError, match="5000"):
        billing_order_export_rows(Gateway([[dict(order_id=12)], rows + [rows[0]]]), 12, "bounds-test")


def test_registry_selected_orders_keep_complete_monetary_aggregates(workbook_scope):
    headers = [dict(order_id=i) for i in range(2000)]
    totals = [dict(order_id=0, task_count=100000, total_price="123456789.25")]
    rows = billing_registry_export_rows(Gateway([headers, totals]), None, None, None, None, None, "bounds-test")
    assert len(rows) == 2000 and rows[0]["task_count"] == 100000
    assert rows[0]["total_price"] == 123456789.25 and rows[-1]["total_price"] == 0
    with pytest.raises(BillingExportError, match="2000"):
        billing_registry_export_rows(Gateway([headers + [dict(order_id=2000)]]), None, None, None, None, None, "bounds-test")


@pytest.mark.parametrize("path", ["/billing/orders/export.xlsx", "/billing/orders/12/export.xlsx"])
def test_export_requires_authoritative_scope_before_build(monkeypatch, path):
    from api.wms_api_server.app.routers import transport
    class Service:
        def export_billing_registry_xlsx(self, *args):
            assert args[-1] == "no-grant"
            raise BillingExportError("BILLING_EXPORT_FORBIDDEN", "Denied", 403)
        def export_billing_order_xlsx(self, *args):
            assert args[-1] == "no-grant"
            raise BillingExportError("BILLING_EXPORT_FORBIDDEN", "Denied", 403)
    monkeypatch.setattr(transport, "TransportService", Service)
    app = FastAPI()
    app.include_router(router)
    app.dependency_overrides[get_current_admin] = lambda: AdminUser("no-grant", "No grant", "NONE", set())
    with TestClient(app) as client:
        response = client.get("/api/admin/transport" + path)
    assert response.status_code == 403


@pytest.mark.parametrize("path,code", [("/billing/orders/export.xlsx", "BILLING_EXPORT_ORDER_BOUND_2000"),
                                      ("/billing/orders/12/export.xlsx", "BILLING_EXPORT_TASK_BOUND_5000")])
def test_overflow_is_explicit_409_without_workbook(monkeypatch, path, code):
    from api.wms_api_server.app.routers import transport
    class Service:
        def export_billing_registry_xlsx(self, *args):
            raise BillingExportError(code, "Уточните фильтры")
        def export_billing_order_xlsx(self, *args):
            raise BillingExportError(code, "Разделите счёт")
    monkeypatch.setattr(transport, "TransportService", Service)
    app = FastAPI()
    app.include_router(router)
    app.dependency_overrides[get_current_admin] = lambda: AdminUser("viewer", "Viewer", "NONE", {"transport_dispatch_view"})
    with TestClient(app) as client:
        response = client.get("/api/admin/transport" + path)
    assert response.status_code == 409 and response.json()["detail"]["code"] == code
    assert "content-disposition" not in response.headers
