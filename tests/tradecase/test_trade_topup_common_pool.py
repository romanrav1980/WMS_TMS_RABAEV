"""C-0157 offline checks of the NOT_APPLIED candidate 'held top-up of a common-pool article' (no Oracle).
Live READ ONLY evidence that the changed functions behave like the live ones on ordinary inputs and zero a blocked top-up row:
reports/tradecase/2026-10-23/claude/C0157/candidate-logic-live.json."""
import hashlib
import json
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parents[2]
MIG = ROOT / "db/migrations/2026-10-23_trade_topup_common_pool"
PAIRS = {"RRL_STOCK_POOL_READ": ("before_rrl_stock_pool_read.sql", "001_pool_read.sql"),
         "RRL_STOCK_POOL_CMD": ("before_rrl_stock_pool_cmd.sql", "002_pool_cmd.sql"),
         "RRL_TRADE_TOPUP_ADOPT": ("before_rrl_trade_topup_adopt.sql", "003_topup_adopt.sql")}


def text(name):
    return (MIG / name).read_text(encoding="utf-8").replace("\r\n", "\n")


def body(name):
    s = text(name).strip("\n")
    return s[:s.rindex("\n/")][len("create or replace "):].rstrip("\n")


def added(name):
    before, after = PAIRS[name]
    b = text(before).splitlines()
    return [x for x in text(after).splitlines() if x not in b], [x for x in b if x not in text(after).splitlines()]


def code(lines):
    return [x for x in lines if x.strip() and not x.strip().startswith("--")]


def test_only_bodies_change_with_minimal_diffs():
    sizes = {name: tuple(len(code(part)) for part in added(name)) for name in PAIRS}
    assert sizes == {"RRL_STOCK_POOL_READ": (7, 1), "RRL_STOCK_POOL_CMD": (1, 0), "RRL_TRADE_TOPUP_ADOPT": (3, 4)}, sizes
    for before, after in PAIRS.values():
        assert text(after).startswith("create or replace package body") and text(before).startswith("create or replace package body")


def test_pool_snapshot_excludes_only_the_own_hold_and_blocks_cancelled_topups():
    new, _ = added("RRL_STOCK_POOL_READ")
    joined = "\n".join(new)
    assert "RRL_TRADE_TOPUP_ADOPT.line_proposal(o.CUSTOMER_ORDER_ROW_ID)" in joined
    assert "PROPOSAL_ID=tp and STATUS='ACTIVE'" in joined and "greatest(0,qty-held)" in joined and "if tp=-1 then" in joined
    after = body("001_pool_read.sql")
    line_fn = after[after.index("function line_snapshot_json"):after.index("function snapshot_json")]
    before = body("before_rrl_stock_pool_read.sql")
    assert line_fn == before[before.index("function line_snapshot_json"):before.index("function snapshot_json")]  # create_plan's demand unchanged
    assert after.index("tp:=RRL_TRADE_TOPUP_ADOPT") > after.index("function snapshot_json")


def test_wave_pool_skips_only_held_topup_rows_and_keeps_locks():
    after = body("002_pool_cmd.sql")
    fn = after[after.index("procedure compile_wave_pool"):after.index("procedure consume_wave_pool")]
    skip = fn.index("RRL_TRADE_TOPUP_ADOPT.line_proposal(demand.CUSTOMER_ORDER_ROW_ID),0)>0 then continue")
    assert fn.index("'SOFT.POOL:'") < skip and fn.index("'RRL_CUSTOMER_ORDER_ROW'") < skip < fn.index("WAVE_COMMON_POOL_ALLOCATION_REQUIRED")
    assert "consume_wave_pool" in after and body("before_rrl_stock_pool_cmd.sql").count("procedure") == after.count("procedure")


def test_topup_launch_refuses_a_leftover_pool_share_instead_of_all_pool_articles():
    new, gone = added("RRL_TRADE_TOPUP_ADOPT")
    assert any("TRADE_TOPUP_COMMON_POOL_UNSUPPORTED" in x for x in gone)
    assert "TRADE_TOPUP_COMMON_POOL_UNSUPPORTED" not in body("003_topup_adopt.sql")
    joined = "\n".join(new)
    assert "POOL_WARE_ID=r.WARE_ID and ARTICUL=r.ARTICUL and SOURCE_LINE_ID=r.ROW_ID" in joined and "TRADE_TOPUP_POOL_SHARE_RECALC_REQUIRED" in joined
    after = body("003_topup_adopt.sql")
    fn = after[after.index("procedure compile_wave("):after.index("function split_units")]
    assert fn.index("POOL_SHARE_RECALC_REQUIRED") < fn.index("row_key(p_resources,'RRL_TRADE_TOPUP_PROPOSAL'")  # still serialized with confirm/release


def test_no_private_helpers_or_json_methods_inside_new_sql_statements():
    for name in PAIRS:
        for stmt in re.findall(r"(?is)\bselect\b.*?;", "\n".join(added(name)[0])):
            assert "get_string" not in stmt and "json_object_t" not in stmt.lower() and "fail(" not in stmt


def test_kit_hashes_and_scripts():
    manifest = json.loads(text("manifest.json"))
    assert manifest["status"] in ("NOT_APPLIED", "APPLIED") and manifest["applied_by_claude"] is False and manifest["specs_changed"] == []  # root applied it 23.10
    for name, (before, after) in PAIRS.items():
        b, a = hashlib.sha256(body(before).encode()).hexdigest().upper(), hashlib.sha256(body(after).encode()).hexdigest().upper()
        assert manifest["before_sha256"][name + ":PACKAGE BODY"] == b and manifest["after_sha256"][name + ":PACKAGE BODY"] == a
        assert b in text("000_preflight.sql") and b in text("rollback_verify.sql") and a in text("verify.sql")
    apply = text("apply.sql")
    assert apply.index("000_preflight") < apply.index("001_pool_read") < apply.index("002_pool_cmd") < apply.index("003_topup_adopt") < apply.index("verify.sql")
    rollback = text("rollback.sql")
    assert all(f"@@{b}" in rollback for b, _ in PAIRS.values()) and rollback.index("@@before") < rollback.index("@@rollback_verify")
    for name, sha in manifest["files_sha256"].items():
        assert hashlib.sha256((MIG / name).read_bytes()).hexdigest() == sha, name


def test_live_evidence_is_recorded():
    live = json.loads((ROOT / "reports/tradecase/2026-10-23/claude/C0157/candidate-logic-live.json").read_text(encoding="utf-8"))
    assert all(w["pool_same"] and w["adopt_same"] for w in live["waves"].values()) and len(live["waves"]) >= 10
    snaps = live["snapshot"]
    assert all(s["before_equals_live"] for s in snaps.values())
    changed = [s for s in snaps.values() if not s["after_equals_before"]]
    assert changed and all(c["other_fields_equal"] and all(o["after"] == "0" for o in c["changed_orders"]) for c in changed)
