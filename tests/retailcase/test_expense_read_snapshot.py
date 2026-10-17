from contextlib import contextmanager
from app.modules.finance.infrastructure import logistics_expenses, expense_register_read


def test_warehouse_admission_and_expense_rows_share_one_snapshot(monkeypatch):
    events = []
    class Cursor:
        def execute(self, sql):
            events.append(sql)
    cursor = Cursor()
    class Gateway:
        active = False
        @contextmanager
        def transaction(self, reason):
            assert not self.active
            self.active = True
            events.append("begin")
            try:
                yield cursor
            finally:
                self.active = False
                events.append("end")
    gateway = Gateway()
    def admit(current, ware, actor, permission):
        assert current is cursor and gateway.active
        assert (ware, actor, permission) == (10, "viewer", "transport_dispatch_view")
        events.append("authorized")
    def read(bound, ware, operation):
        assert bound.transaction_bound and gateway.active
        assert events[-1] == "authorized"
        assert (ware, operation) == (10, "EXACT.EXPENSE")
        events.append("rows")
        return [{"operation_id": operation}]
    monkeypatch.setattr(logistics_expenses, "require_warehouse", admit)
    monkeypatch.setattr(expense_register_read, "warehouse_expenses", read)
    assert logistics_expenses.LogisticsExpenses(gateway).pending(10, "viewer", "EXACT.EXPENSE") == [{"operation_id": "EXACT.EXPENSE"}]
    assert events == ["begin", "set transaction read only", "authorized", "rows", "end"]
