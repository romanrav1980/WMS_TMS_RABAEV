"""C-0145 offline checks of the trip coverage read model with a scripted cursor (no Oracle)."""
import json
import oracledb
import pytest
from app.modules.integrations.contracts_trade_transport import TradeTransportError
from app.modules.integrations.infrastructure import trade_route

DOCS = {
    ("TRIP", "R1"): {"planned_departure_at": "2026-11-01T10:00:00+03:00", "orders": [
        {"order_id": "O1", "line_id": "1", "quantity": 4}, {"order_id": "O1", "line_id": "2", "quantity": 7},
        {"order_id": "O2", "line_id": "1", "quantity": 5}, {"order_id": "O3", "line_id": "1", "quantity": 9}]},
    ("ORDER", "O1"): {"recipient_id": "R", "lines": [{"line_id": "1", "sku_id": "A", "source_owner_id": "SNS", "mrc": 200, "uom": "BOX"},
                                                    {"line_id": "2", "sku_id": "A", "source_owner_id": "SNS", "mrc": 200, "uom": "EA"}]},
    ("ORDER", "O2"): {"recipient_id": "R", "lines": [{"line_id": "1", "sku_id": "A", "source_owner_id": "HIDDEN", "mrc": 200, "uom": "EA"}]},
    ("ORDER", "O3"): {"recipient_id": "R", "cancelled": True, "lines": [{"line_id": "1", "sku_id": "A", "source_owner_id": "SNS", "mrc": 200, "uom": "EA"}]},
    ("SKU", "A"): {"units_per_box": 10},
}
SNAP = {3001: {"requested_base_quantity": "40", "hard_quantity": "30", "picked_quantity": "10", "quantity": "0"}}


class Cursor:
    def __init__(self, linked: bool = True, unattributed: int = 0):
        self.linked, self.unattributed, self.rows, self.sql = linked, unattributed, [], []

    def execute(self, sql: str, **kw):
        self.sql.append(sql)
        s = " ".join(sql.split())
        if s.startswith("set transaction"): self.rows = []
        elif "RRL_ACCESS_API.allowed" in s: self.rows = [(1,)]
        elif "from RRL_TRADE_DOCUMENT" in s:
            body = DOCS.get((kw["k"], kw["id"])); self.rows = [] if body is None else [(json.dumps(body), 3)]
        elif "from RRL_TRADE_TRIP_LINK" in s: self.rows = [(33660, 1)] if self.linked else []
        elif "owner_allowed" in s: self.rows = [(0 if kw["o"] == "HIDDEN" else 1,)]
        elif "from RRL_TRADE_ORDER_LINK" in s:
            self.rows = {("O1", "1"): [(3001, 3)], ("O1", "2"): [(3002, 3)], ("O3", "1"): []}.get((kw["o"], kw["line"]), [])
        elif "UNATTRIBUTED_LOADS" in s: self.rows = [(self.unattributed,)]
        elif "from RRL_TT_HU_LOAD_FACT" in s: self.rows = [(3001, "DEPARTED", 0, 6), (3001, "DEPARTED", 1, 2), (3001, "LOADED", 0, 2), (3001, "UNLOADED", 0, 5)]
        else: raise AssertionError(s)

    def fetchone(self):
        return self.rows[0] if self.rows else None

    def __iter__(self):
        return iter(self.rows)

    def callfunc(self, name, kind, args):
        assert name == "RRL_STOCK_POOL_READ.line_snapshot_json"
        if args[0] not in SNAP:
            err = oracledb.DatabaseError(); err.args = (type("E", (), {"code": 20868, "__str__": lambda self: "ORA-20868: POOL_LINE_OR_UOM_NOT_FOUND"})(),)
            raise err
        return json.dumps(SNAP[args[0]])


class Gateway:
    def __init__(self, cursor):
        self.cursor = cursor

    def transaction(self, name):
        cursor = self.cursor

        class Ctx:
            def __enter__(self): return cursor
            def __exit__(self, *a): return False
        return Ctx()


def test_lines_with_sources_unknown_and_hidden_owner():
    cur = Cursor()
    r = trade_route.trip_coverage(Gateway(cur), 7, "R1", "u")
    assert "set transaction read only" in cur.sql[0]
    by = {(x["order_id"], x["line_id"]): x for x in r["lines"]}
    assert set(by) == {("O1", "1"), ("O1", "2"), ("O3", "1")}  # HIDDEN owner line is absent, not counted
    assert r["owner_scope_filtered"] is True and r["unattributed_loads"] is None  # no unattributed count may leak the hidden part
    one = by[("O1", "1")]
    assert one["ordered_base"] == "40" and one["reserved_base"] == "30" and one["picked_base"] == "10"
    assert one["departed_base"] == "8" and one["loaded_base"] == "2" and one["released_base"] == "2"  # UNLOADED is not shipped
    two = by[("O1", "2")]
    assert two["native_error"] == "POOL_LINE_OR_UOM_NOT_FOUND" and two["reserved_base"] is None  # unknown, not zero
    three = by[("O3", "1")]
    assert three["order_cancelled"] is True and three["native_row_id"] is None and three["picked_base"] is None and three["loaded_base"] is None


def test_unbound_trip_has_unknown_loading():
    r = trade_route.trip_coverage(Gateway(Cursor(linked=False)), 7, "R1", "u")
    assert r["native_task_id"] is None and all(x["loaded_base"] is None and x["departed_base"] is None for x in r["lines"])


def test_trip_missing_is_404_and_denied_access_is_403():
    cur = Cursor(); DOCS_BACKUP = DOCS.pop(("TRIP", "R1"))
    try:
        with pytest.raises(TradeTransportError) as missing:
            trade_route.trip_coverage(Gateway(cur), 7, "R1", "u")
        assert missing.value.status == 404
    finally:
        DOCS[("TRIP", "R1")] = DOCS_BACKUP
    denied = Cursor(); denied.execute = (lambda orig: (lambda sql, **kw: (orig(sql, **kw), setattr(denied, "rows", [(0,)]) if "allowed" in sql else None)))(denied.execute)
    with pytest.raises(TradeTransportError) as forbidden:
        trade_route.trip_coverage(Gateway(denied), 7, "R1", "u")
    assert forbidden.value.status == 403


def test_unmapped_frozen_place_does_not_turn_unknown_delivery_into_zero():
    r=trade_route.trip_coverage(Gateway(Cursor(unattributed=1)),7,"R1","u")
    assert r["load_coverage_complete"] is False
    assert all(x["loaded_base"] is None and x["departed_base"] is None for x in r["lines"])
    assert r["unattributed_loads"] is None  # hidden-owner quantities remain undisclosed
