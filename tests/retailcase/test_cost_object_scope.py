import pytest
from app.modules.finance.infrastructure import cost_read_scope
from app.modules.finance.contracts import LogisticsCostError


class Cursor:
    def __init__(self, warehouses, active=(0,), exists=(1,)):
        self.values = iter([active, exists, [(w,) for w in warehouses]])
        self.queries = []
    def execute(self, sql, **binds):
        self.queries.append((sql, binds))
        self.result = next(self.values)
    def fetchone(self): return self.result
    def fetchall(self): return self.result


def test_composite_cost_requires_every_warehouse_without_partial_result(monkeypatch):
    checked = []
    def require(cursor, ware, actor, permission):
        checked.append(ware)
        if ware == 20: raise LogisticsCostError("FORBIDDEN", "foreign", 403)
    monkeypatch.setattr(cost_read_scope, "require_warehouse", require)
    with pytest.raises(LogisticsCostError) as error:
        cost_read_scope.authorize_cost_object(Cursor([10, 20]), "INVOICE", 100, "viewer")
    assert error.value.status == 403 and checked == [10, 20]


def test_full_scope_uses_all_actual_sources(monkeypatch):
    checked = []
    monkeypatch.setattr(cost_read_scope, "require_warehouse", lambda cursor, ware, actor, permission: checked.append(ware))
    cursor = Cursor([10, 20])
    cost_read_scope.authorize_cost_object(cursor, "TRIP", 100, "viewer")
    assert checked == [10, 20]
    assert all(source in cursor.queries[-1][0] for source in ("RRL_SBORKA_PALLETS", "RRL_TT_HU_LOAD_FACT", "RRL_LOGISTICS_COST_RUN"))


@pytest.mark.parametrize("warehouses,legacy", [([None], 1), ([], 0), (list(range(201)), 1)])
def test_unknown_or_unattributable_or_unbounded_source_is_not_success(warehouses, legacy):
    with pytest.raises(LogisticsCostError):
        cost_read_scope.authorize_cost_object(Cursor(warehouses, active=(legacy,)), "INVOICE", 100, "viewer")
