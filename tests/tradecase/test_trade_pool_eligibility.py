"""C-0160 offline checks: trade allocation by physical classes, the trusted-plan hints and the NOT_APPLIED native kit.
Live READ ONLY evidence (candidate executed unchanged as anonymous blocks): reports/tradecase/2026-10-23/claude/C0160/candidate-live.json."""
import hashlib
import json
import pathlib
from decimal import Decimal as D
import pytest
from app.modules.inventory.domain.pool_allocation import TradeDemand, allocate_trade_pool
from app.modules.inventory.infrastructure import pool_plan

ROOT = pathlib.Path(__file__).resolve().parents[2]
KIT = ROOT / "db/migrations/2026-10-23_trade_pool_eligibility"
SNS, BLC, SNS_OLD = "SNS|A|200|2030-01-01", "BLC|A|250|2030-01-01", "SNS|A|200|2029-01-01"


def test_two_owners_or_mrc_of_one_sku_never_share_a_source():
    r = allocate_trade_pool((TradeDemand(1, D(20), 0, (SNS,)), TradeDemand(2, D(15), 1, (BLC,))), {SNS: D(250), BLC: D(10)}, D(1))
    assert r.quantities == {1: D(20), 2: D(10)} and r.sources == {1: {SNS: D(20)}, 2: {BLC: D(10)}}


def test_same_terms_share_proportionally_like_the_existing_pool():
    r = allocate_trade_pool((TradeDemand(1, D(30), 0, (SNS,)), TradeDemand(2, D(10), 1, (SNS,))), {SNS: D(20)}, D(1))
    assert r.quantities == {1: D(15), 2: D(5)} and sum(r.sources[1].values()) + sum(r.sources[2].values()) == D(20)


def test_overlapping_terms_dispatch_order_and_fefo_never_exceed_a_class():
    # row 1 accepts both expiries, row 2 (higher OSG) only the later one: dispatch order first, FEFO inside the row.
    r = allocate_trade_pool((TradeDemand(1, D(10), 0, (SNS, SNS_OLD)), TradeDemand(2, D(10), 1, (SNS,))), {SNS: D(8), SNS_OLD: D(6)}, D(1))
    assert r.sources[1] == {SNS_OLD: D(6), SNS: D(4)} and r.sources[2] == {SNS: D(4)}
    used = {}
    for split in r.sources.values():
        for k, v in split.items():
            used[k] = used.get(k, 0) + v
    assert used[SNS] <= 8 and used[SNS_OLD] <= 6


def test_whole_steps_shortage_and_rows_without_classes():
    r = allocate_trade_pool((TradeDemand(1, D(7), 0, (SNS,)), TradeDemand(2, D(5), 1, ())), {SNS: D(5)}, D(2))
    assert r.quantities == {1: D(4), 2: D(0)} and r.sources == {1: {SNS: D(4)}}
    with pytest.raises(ValueError):
        allocate_trade_pool((TradeDemand(1, D(1), 0, (SNS,)), TradeDemand(1, D(1), 0, (SNS,))), {SNS: D(5)}, D(1))


class Cur:
    def __init__(self, snapshot):
        self.snapshot = snapshot

    def execute(self, sql, params):
        assert "RRL_STOCK_POOL_READ.snapshot_json" in sql

    def fetchone(self):
        return (json.dumps(self.snapshot),)


def test_plan_hints_name_the_classes_and_skip_rows_with_a_reason():
    snap = {"from_stock": 1, "trade": 1, "available": "260", "step": "1", "classes": [{"key": SNS, "owner": "SNS", "free": "250"}, {"key": BLC, "owner": "BLC", "free": "10"}],
            "orders": [{"line_id": 3690, "quantity": "20", "dispatch_order": 0, "classes": [SNS]},
                       {"line_id": 3692, "quantity": "10", "dispatch_order": 1, "classes": [], "pool_reason": "TRADE_ORDER_BINDING_STALE"},
                       {"line_id": 3693, "quantity": "15", "dispatch_order": 2, "classes": [BLC]}]}
    h = pool_plan.plan_pool(Cur(snap), {"source": {"warehouse": 210564699, "article": "TC"}})
    assert h["allocations"] == {"3690": "20", "3692": "0", "3693": "10"} and h["sources"] == {"3690": {SNS: "20"}, "3693": {BLC: "10"}}
    assert h["algorithm"] == "PROPORTIONAL_WHOLE_STEP_V1" and json.loads(h["snapshot"]) == snap


def test_non_trade_plan_is_unchanged():
    snap = {"from_stock": 1, "available": "10", "step": "1", "orders": [{"line_id": 1, "quantity": "6", "dispatch_order": 0}, {"line_id": 2, "quantity": "6", "dispatch_order": 1}]}
    h = pool_plan.plan_pool(Cur(snap), {"source": {"warehouse": 1, "article": "X"}})
    assert "sources" not in h and h["allocations"] == {"1": "5", "2": "5"}


def text(name):
    return (KIT / name).read_text(encoding="utf-8").replace("\r\n", "\n")


def test_context_keeps_reason_and_adds_reader_independent_compatibility():
    spec, body = text("001_ctx_spec.sql"), text("002_ctx_body.sql")
    assert "package RRL_STOCK_POOL_READ)as" in spec and "function compatible(p_row number,p_uid varchar2,p_cell varchar2,p_ware number)return varchar2;" in spec
    assert "begin return check_source(p_uid,p_cell,p_ware,p_purpose,true);end;" in body  # the guard for every existing caller keeps owner access
    assert "if p_access and RRL_TRADE_STOCK_GUARD.owner_allowed" in body and "check_source(p_uid,p_cell,p_ware,'ALLOCATE',false);restore;return v;" in body
    assert "exception when others then restore;raise;" in body
    before = text("before_ctx_body.sql").splitlines()
    assert len([x for x in text("002_ctx_body.sql").splitlines() if x not in before]) <= 12


def test_snapshot_trade_only_and_command_proves_and_checks_rights():
    read = text("003_pool_read.sql")
    assert "if trade=1 and note='TRADE_ORDER_BINDING_REQUIRED'then note:=null;end if;" in read  # only the last, per-row step is deferred
    assert "if trade=1 and enabled=1 and x.get_string('quantity')<>'0'then" in read and "POOL_TRADE_MATRIX_BOUND_2000" in read
    assert "if trade=1 then j.put('trade',1);j.put('classes',classes);end if;" in read and "j.put('trade',trade)" not in read
    cmd = text("004_pool_cmd.sql")
    compile_ = cmd[cmd.index(" procedure compile_command("):cmd.index(" procedure execute_command(")]
    execute = cmd[cmd.index(" procedure execute_command("):]
    assert "prove_trade(s,h,step)" in compile_ and compile_.index("POOL_OVERALLOCATED") < compile_.index("prove_trade(s,h,step)")
    assert execute.index("locked pool snapshot") < execute.index("RRL_TRADE_STOCK_GUARD.assert_owner(p_actor,ware,c.get_string('owner'),1)") < execute.index("update RRL_STOCK_RESERVATION")
    for code in ("POOL_TRADE_SOURCES_REQUIRED", "POOL_TRADE_LINE_NOT_ALLOCATABLE", "POOL_TRADE_SOURCE_INCOMPATIBLE", "POOL_TRADE_SOURCE_SPLIT_INVALID", "POOL_TRADE_CLASS_OVERALLOCATED"):
        assert code in cmd


def test_kit_hashes_scripts_and_live_evidence():
    m = json.loads(text("manifest.json"))
    assert m["status"] == "NOT_APPLIED" and m["applied_by_claude"] is False
    for v in m["before_sha256"].values():
        assert v in text("000_preflight.sql") and v in text("rollback_verify.sql")
    for v in m["after_sha256"].values():
        assert v in text("verify.sql")
    for name, sha in m["files_sha256"].items():
        assert hashlib.sha256((KIT / name).read_bytes()).hexdigest() == sha, name
    apply = text("apply.sql")
    assert apply.index("001_ctx_spec") < apply.index("002_ctx_body") < apply.index("003_pool_read") < apply.index("004_pool_cmd") < apply.index("recompile") < apply.index("verify.sql")
    live = json.loads((ROOT / "reports/tradecase/2026-10-23/claude/C0160/candidate-live.json").read_text(encoding="utf-8"))
    assert all(v["same_as_before"] for k, v in live["snapshots"].items() if not k.startswith("210564699"))
    trade = live["snapshots"]["210564699:TC03089DDB36"]
    assert trade["forced_classes"] and all(o["pool_reason"] for o in trade["forced_orders"] if o["quantity"] != "0" and not o["classes"])
    assert live["prove"]["accepted"] == "ACCEPTED" and sum(v != "ACCEPTED" for v in live["prove"].values()) == 5
