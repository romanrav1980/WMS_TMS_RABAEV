"""C-0146 offline checks: SAP top-up already inside the updated TRIP is not counted twice; adoption migration contract.

Native behaviour (planning/launch/relink) needs the applied migration and is accepted live by Codex; here only what is
provable without Oracle: Python accounting and the static shape of the candidate migration.
"""
import hashlib
import json
import pathlib
import re
from decimal import Decimal
from app.modules.integrations.infrastructure import trade_topup

M = pathlib.Path(__file__).resolve().parents[2] / "db" / "migrations" / "2026-10-22_trade_topup_wave_adoption"
ORDERS = {"MAIN": {"lines": [{"line_id": "1", "uom": "BOX"}]}, "SAP104": {"lines": [{"line_id": "1", "uom": "EA"}]}}


class Cur:
    def __init__(self, proposals):
        self.proposals, self.rows = proposals, []

    def execute(self, sql, **kw):
        assert "RRL_TRADE_TOPUP_PROPOSAL" in sql and "CONFIRMED" in sql
        self.rows = self.proposals

    def fetchall(self):
        return self.rows


def _patch(monkeypatch):
    monkeypatch.setattr(trade_topup, "_document", lambda cur, ware, kind, key: (ORDERS[key], 1))


def test_sap_order_inside_trip_occupies_no_extra_space(monkeypatch):
    _patch(monkeypatch)
    trip = {"orders": [{"order_id": "MAIN", "line_id": "1", "quantity": 600}, {"order_id": "SAP104", "line_id": "1", "quantity": 400}]}
    got = trade_topup._confirmed(Cur([("N1", "A", 40, "SAP104", 10)]), 1, "R1", trip)
    assert got == [dict(need_id="N1", sku_id="A", inside=Decimal(40), extra=Decimal(0))]


def test_confirmed_without_order_or_not_yet_in_trip_occupies_full_space(monkeypatch):
    _patch(monkeypatch)
    trip = {"orders": [{"order_id": "MAIN", "line_id": "1", "quantity": 600}]}
    got = trade_topup._confirmed(Cur([("N1", "A", 40, None, 10), ("N2", "B", 20, "SAP104", 10)]), 1, "R1", trip)
    assert [(g["inside"], g["extra"]) for g in got] == [(Decimal(0), Decimal(40)), (Decimal(0), Decimal(20))]


def test_partial_inclusion_counts_only_the_remainder(monkeypatch):
    _patch(monkeypatch)
    trip = {"orders": [{"order_id": "SAP104", "line_id": "1", "quantity": 150}]}  # 15 boxes of 40 already in the TRIP
    got = trade_topup._confirmed(Cur([("N1", "A", 40, "SAP104", 10)]), 1, "R1", trip)[0]
    assert (got["inside"], got["extra"]) == (Decimal(15), Decimal(25))


def _stored(ddl_text: str) -> str:
    t = ddl_text.replace("\r", "")
    assert t.startswith("create or replace ")
    return t[len("create or replace "):].rstrip()[:-1].rstrip("\n")


def test_manifest_hashes_match_before_and_patched_files():
    man = json.loads((M / "manifest.json").read_text(encoding="utf-8"))
    files = {"RRL_STOCK_RESERVE_CORE:PACKAGE": ("before_rrl_stock_reserve_core_spec.sql", "003_reserve_core.sql", 0),
             "RRL_STOCK_RESERVE_CORE:PACKAGE BODY": ("before_rrl_stock_reserve_core.sql", "003_reserve_core.sql", 1),
             "RRL_PICKING_API:PACKAGE BODY": ("before_rrl_picking_api.sql", "004_picking.sql", None),
             "RRL_STOCK_WAVE_LAUNCH_CMD:PACKAGE BODY": ("before_rrl_stock_wave_launch_cmd.sql", "005_wave_launch.sql", None),
             "RRL_TRADE_PICK_CONTEXT:PACKAGE BODY": ("before_rrl_trade_pick_context.sql", "006_pick_context.sql", None)}
    sha = lambda s: hashlib.sha256(s.encode()).hexdigest().upper()  # noqa: E731
    for key, (before, after, index) in files.items():
        assert sha(_stored((M / before).read_text(encoding="utf-8"))) == man["objects_before"][key], key
        raw = (M / after).read_text(encoding="utf-8").replace("\r", "")
        unit = raw if index is None else [b for b in raw.split("\n/\n") if b.strip()][index] + "\n/\n"
        assert sha(_stored(unit)) == man["objects_after"][key], key
    assert man["applied_by_claude"] is False


def test_patches_are_minimal_and_keep_the_ordinary_path():
    launch = (M / "005_wave_launch.sql").read_text(encoding="utf-8")
    # Ordinary orders still create their own HARD and units; held top-up rows take over instead.
    assert launch.count("RRL_STOCK_RESERVE_CORE.create_hard(") == 1 and "adopt_hold(v_topup" in launch
    assert "RRL_TRADE_TOPUP_ADOPT.compile_wave(v_wave,r)" in launch and "release_hard" not in launch
    picking = (M / "004_picking.sql").read_text(encoding="utf-8")
    assert "hold_free(v_topup,l.CUSTOMER_ORDER_ROW_ID" in picking and "TRADE_TOPUP_ADOPTION_CONDITIONS_NOT_MET" in picking
    core = (M / "003_reserve_core.sql").read_text(encoding="utf-8")
    assert "r.SOURCE_DOC_TYPE!='TRADE_TOPUP'" in core and "apply_delta" not in core.split("procedure relink_topup")[2].split(" end;")[0]
    gate = (M / "006_pick_context.sql").read_text(encoding="utf-8")
    assert "RRL_TRADE_TOPUP_ADOPT.gate(" in gate and "TRADE_TOPUP_HOLD_ADOPTION_REQUIRED" not in gate


def test_adoption_conditions_cover_both_sap_documents_and_cancelled_proposals():
    adopt = (M / "002_adopt.sql").read_text(encoding="utf-8")
    body = adopt.split("function line_proposal(p_row number)return number is", 1)[1].split(" function hold_rid", 1)[0]
    for needle in ("p.STATUS<>'SAP_ACCEPTED'then return -1", "ENTITY_TYPE='TRIP'", "'$.orders[*]'", "parent_trip_id", "order_kind",
                   "recipient_id", "ol.SKU_ID<>p.SKU_ID", "ol.MRC<>p.MRC", "SOURCE_OWNER_ID", "APPROVED_BOXES*p.UNITS_PER_BOX", "site_src"):
        assert needle in body, needle
    # Cancelled check precedes the hold count: a released proposal never falls back to free stock.
    assert body.index("SAP_ACCEPTED") < body.index("STATUS='ACTIVE'")
    assert "TOPUP_ADOPTION_ONLY_IN_WAVE_LAUNCH" in adopt


def test_apply_and_rollback_order():
    apply = (M / "apply.sql").read_text(encoding="utf-8")
    steps = re.findall(r"@@(\S+)", apply)
    assert steps[:2] == ["000_preflight.sql", "001_schema.sql"] and steps[-1] == "verify.sql"
    assert steps.index("002_adopt.sql") < steps.index("004_picking.sql") and steps.index("003_reserve_core.sql") < steps.index("005_wave_launch.sql")
    rollback = (M / "rollback.sql").read_text(encoding="utf-8")
    assert "ADOPTION_HISTORY_PRESENT" in rollback and rollback.index("ADOPTION_HISTORY_PRESENT") < rollback.index("@@before_")
    assert rollback.index("@@before_rrl_trade_pick_context.sql") < rollback.index("drop package RRL_TRADE_TOPUP_ADOPT")
