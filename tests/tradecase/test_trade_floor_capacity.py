"""C-0178 T08: without confirmed pallet places or stacking the top-up is refused; nothing fits by volume, nothing is saved or held."""
from decimal import Decimal
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "api/wms_api_server"))
from app.modules.integrations.contracts_trade_topup import TopupPreview, TopupSave
from app.modules.integrations.contracts_trade_transport import TradeTransportError
from app.modules.integrations.infrastructure import trade_capacity, trade_topup, trade_topup_proposals as proposals

PACKAGE = dict(sku_id="A", sku_version=1, units_per_box=10, weight=Decimal("10"), volume=Decimal(".1"),
               dimensions=(Decimal(".4"), Decimal(".5"), Decimal(".5")), article="A")


class Cursor:
    def __init__(self, status="TARE_TYPE_UNCONFIRMED"):
        self.status, self.calls = status, []

    def execute(self, sql, *args, **binds):
        self.calls.append(("execute", sql))

    def fetchone(self):
        return (1,)

    def callfunc(self, name, kind, args):
        self.calls.append(("callfunc", name, list(args)))
        if name == "RRL_VEHICLE_PROFILE_API.check_floor_capacity":
            return json.dumps(dict(status=self.status, basis="EXPLICIT_FLOOR_VARIANTS", operational_admission=False))
        return "BASIS"

    def callproc(self, name, args):
        self.calls.append(("callproc", name))

    def var(self, kind):
        class Var:
            value = None
            def setvalue(self, i, v): self.value = v
            def getvalue(self): return self.value
        return Var()


class Gateway:
    def __init__(self, cursor):
        self.cursor = cursor

    def transaction(self, name):
        cursor = self.cursor

        class Scope:
            def __enter__(self): return cursor
            def __exit__(self, *exc): return False
        return Scope()


def context(max_weight="1000", max_volume="10", planned=()):
    return dict(trip=dict(planned_departure_at="2099-01-01T08:00:00+00:00"), version=3, planned=list(planned), orders=[], packages={"A": PACKAGE},
                profile=dict(version=1, base_hash="H"), dimensions=(Decimal("2.4"), Decimal("1.6"), Decimal("2.4")), started=False, loaded=None,
                max_weight=Decimal(max_weight), max_volume=Decimal(max_volume), vehicle=10059)


@pytest.mark.parametrize("status", ["TARE_TYPE_UNCONFIRMED", "NOT_CONFIGURED"])
def test_existing_profile_check_is_asked_with_type_unconfirmed_places_and_refuses(status):
    cursor = Cursor(status)
    floor = trade_capacity.floor_admission(cursor, 10059)
    assert ("callfunc", "RRL_VEHICLE_PROFILE_API.check_floor_capacity", [10059, "[]", 1]) in cursor.calls
    assert floor == dict(floor_places_checked=False, stacking_rules_checked=False, floor_profile_status=status,
                         blocking_reason="TOPUP_PALLET_PLACE_MAPPING_REQUIRED")


@pytest.mark.parametrize("limits,requested", [(("1000", "10"), 1), (("10", ".1"), 1), (("10", ".1"), 5), (("0", "0"), 1)])
def test_preview_never_fits_by_weight_or_volume_at_any_boundary(monkeypatch, limits, requested):
    monkeypatch.setattr(trade_capacity, "capacity_context", lambda *a: context(*limits))
    result = trade_capacity.capacity_preview(Gateway(Cursor()), 1, "T1", "A", requested, "u")
    assert result["blocking_reason"] == "TOPUP_PALLET_PLACE_MAPPING_REQUIRED"
    assert result["maximum_boxes"] is result["fitting_boxes"] is result["remaining_boxes"] is None
    assert result["floor_places_checked"] is False and result["stacking_rules_checked"] is False and result["approval_available"] is False
    assert result["box_limit_weight"] == int(Decimal(limits[0]) // 10)  # the accepted weight/volume ceiling is still shown, unchanged


def test_unproved_mixed_layout_keeps_its_own_reason(monkeypatch):
    other = dict(PACKAGE, sku_id="B", dimensions=(Decimal(".3"), Decimal(".5"), Decimal(".5")), boxes=Decimal(1))
    monkeypatch.setattr(trade_capacity, "capacity_context", lambda *a: context(planned=[other]))
    assert trade_capacity.capacity_preview(Gateway(Cursor()), 1, "T1", "A", 1, "u")["blocking_reason"] == "MIXED_PACKAGE_LAYOUT_REQUIRED"


def _allocate_until_floor(monkeypatch):
    monkeypatch.setattr(trade_topup, "capacity_context", lambda *a: context())
    monkeypatch.setattr(trade_topup, "_confirmed", lambda *a: [])
    need = dict(topup_enabled=True, forecast_kind="MOVEMENT", topup_horizon_days=3, recipient_id="R", sku_id="A", expired=False,
                period_from="2098-12-31T00:00:00+00:00", period_until="2099-01-03T00:00:00+00:00")
    monkeypatch.setattr(trade_topup, "need_snapshot", lambda *a: need)
    monkeypatch.setattr(trade_topup, "_uncovered_confirmations", lambda *a: Decimal(0))
    monkeypatch.setattr(trade_topup, "_item", lambda *a: dict(proposed_boxes=3))


def test_topup_preview_is_refused_after_the_existing_gates(monkeypatch):
    _allocate_until_floor(monkeypatch)
    with pytest.raises(TradeTransportError) as refused:
        trade_topup.topup_preview(Gateway(Cursor()), 1, "T1", TopupPreview(need_ids=["N1"], max_age_minutes=60), "u")
    assert (refused.value.code, refused.value.status) == ("TOPUP_PALLET_PLACE_MAPPING_REQUIRED", 409)


def test_blocked_calculation_is_never_saved_and_holds_nothing(monkeypatch):
    _allocate_until_floor(monkeypatch)
    cursor = Cursor()
    with pytest.raises(TradeTransportError) as refused:
        proposals.OracleTopupProposals(Gateway(cursor)).save(1, "T1", TopupSave(operation_id="op", need_ids=["N1"], max_age_minutes=60), "u")
    assert refused.value.code == "TOPUP_PALLET_PLACE_MAPPING_REQUIRED"
    called = [c[1] for c in cursor.calls if c[0] in ("callproc", "callfunc")]
    assert "RRL_TRADE_TOPUP_API.save" not in called and not any("HOLD" in str(c) or "insert" in str(c).lower() for c in cursor.calls)
