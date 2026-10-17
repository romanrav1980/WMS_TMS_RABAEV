"""A workbook cannot expose partial totals or authorize in another snapshot."""
import pytest
from api.wms_api_server.app.modules.finance.infrastructure import billing_export_access as access
from api.wms_api_server.app.modules.finance.infrastructure.billing_export_reads import billing_order_export_rows
from api.wms_api_server.app.modules.finance.contracts import LogisticsCostError
from api.wms_api_server.app.modules.finance.contracts_billing_export import BillingExportError
from tests.retailcase.test_billing_export_bounds import Gateway


class ScopeCursor:
    def __init__(self, warehouses, empty=0):
        self.warehouses, self.empty, self.sql = warehouses, empty, []
    def execute(self, sql, **binds):
        self.sql.append(sql)
        self.last = sql
    def fetchone(self):
        return (self.empty,) if "select count(*) from json_table" in self.last else (0,)
    def fetchall(self):
        return [(w,) for w in self.warehouses]


def test_composite_export_requires_each_warehouse(monkeypatch):
    seen = []
    def require(cursor, warehouse, actor, permission):
        seen.append((warehouse, actor, permission))
        if warehouse == 2:
            raise LogisticsCostError("COST_WAREHOUSE_FORBIDDEN", "Denied", 403)
    monkeypatch.setattr(access, "require_warehouse", require)
    with pytest.raises(BillingExportError) as error:
        access.authorize_billing_export(ScopeCursor([1, 2]), [12], "viewer")
    assert error.value.status == 403
    assert [row[0] for row in seen] == [1, 2]


def test_unknown_invoice_is_not_hidden_by_an_authorized_invoice(monkeypatch):
    monkeypatch.setattr(access, "require_warehouse", lambda *args: None)
    with pytest.raises(BillingExportError, match="всех счетов") as error:
        access.authorize_billing_export(ScopeCursor([1], empty=1), [12, 13], "viewer")
    assert error.value.status == 403


def test_export_authorizes_before_amounts_in_same_read_snapshot(monkeypatch):
    from api.wms_api_server.app.modules.finance.infrastructure import billing_export_reads as reads
    gateway = Gateway([[dict(order_id=12)], [dict(tt_id=1, price="2.5")]])
    def authorize(cursor, ids, actor):
        assert cursor is gateway.cursor and ids == [12] and actor == "viewer"
        assert cursor.statements[0][0] == "set transaction read only"
        assert not any("nvl(TT.PRICE" in row[0] for row in cursor.statements)
    monkeypatch.setattr(reads, "authorize_billing_export", authorize)
    header, _ = billing_order_export_rows(gateway, 12, "viewer")
    assert header["total_price"] == 2.5
