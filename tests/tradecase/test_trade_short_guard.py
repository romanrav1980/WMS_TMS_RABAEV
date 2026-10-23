"""C-0170 offline checks: the NOT_APPLIED guard branch admitting CASE_SHORT_APPROVE on trade stock only for what its own plan locks,
the guarded rollback, the LIVE READ ONLY evidence (current refusal, existing current-owner check before the cached receipt), the approval
UI wording and the root live runner guards."""
import hashlib
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[2]
KIT = ROOT / "db/migrations/2026-10-23_trade_short_guard_v2"  # the published first kit is DO NOT APPLY
REPORT = ROOT / "reports/tradecase/2026-10-23/claude/C0170"


def text(path):
    return path.read_text(encoding="utf-8").replace("\r\n", "\n")


def branch():
    body = text(KIT / "001_guard_body.sql")
    return body[body.index("elsif command_kind='CASE_SHORT_APPROVE' then"):body.index("elsif command_kind not in('SAP_RECEIPT'")]


def test_branch_binds_to_the_operation_plan():
    b = branch()
    order = ["from RRL_CASE_PICK_SHORT s", "where s.CASE_PICK_SHORT_ID=v_short and ct.WARE_ID=w.WARE_ID",
             "select RESOLVED_PLAN_JSON into v_plan from RRL_STOCK_OPERATION where OPERATION_ID=v_op and COMMAND_TYPE='CASE_SHORT_APPROVE'and STATE='IN_FLIGHT'",
             "if v_decision='READY'then"]
    assert [b.index(x) for x in order] == sorted(b.index(x) for x in order)
    ready = b[b.index("if v_decision='READY'then"):b.index("     else\n")]
    assert "'$.domain.chunks[*]'" in ready and "reason(p_uid,v_cell,w.WARE_ID,'PICK')" in ready  # planned chunk, line's own cell, trade rules
    assert "from RRL_REMAINS" not in ready  # no arbitrary source row by UID
    other = b[b.index("     else\n"):]
    assert "'$.domain.reservations[*]'" in other and "'$.domain.carrier[*]'" in other
    assert "join RRL_CASE_CARRIER_LOT c on c.LOT_UID=x.U and c.CASE_PICK_TASK_ID=v_case" in other  # picked goods only of the same CASE
    assert b.count("fail('TRADE_SHORT_BINDING_REQUIRED')") == 3 and "exception when no_data_found then RRL_TRADE_PICK_CONTEXT.clear_line" in b


def test_kit_hashes_and_guarded_rollback():
    m = json.loads(text(KIT / "manifest.json"))
    assert m["status"] == "NOT_APPLIED" and m["before_sha256"]["RRL_TRADE_STOCK_GUARD:PACKAGE BODY"] == "7D6E1781DB7F46AC66105865B83D583C2FF35A9A905C1D8B91C97421CF0A68EE"
    stored = text(KIT / "before_guard_body.sql")[len("create or replace "):].rsplit("\n/\n", 1)[0]
    assert hashlib.sha256(stored.encode()).hexdigest().upper() == m["before_sha256"]["RRL_TRADE_STOCK_GUARD:PACKAGE BODY"]
    after = text(KIT / "001_guard_body.sql")[len("create or replace "):].rsplit("\n/\n", 1)[0]
    assert hashlib.sha256(after.encode()).hexdigest().upper() == m["after_sha256"]["RRL_TRADE_STOCK_GUARD:PACKAGE BODY"]
    for dep in ("RRL_CASE_TASK_ACCESS:PACKAGE BODY", "RRL_TRADE_CASE_ACCESS:PACKAGE BODY", "RRL_STOCK_CASE_SHORT_CMD:PACKAGE BODY"):
        assert dep in m["unchanged_dependency_sha256"]
    assert "НЕ ПРИМЕНЯТЬ" in text(ROOT / "db/migrations/2026-10-23_trade_short_guard/README.md")  # v1 stays as published
    assert m["migration_id"] == "2026-10-23-trade-short-guard-v2"
    rb = text(KIT / "rollback.sql")
    assert rb.index("AFTER_SOURCE_DRIFT_REFUSED") < rb.index("TRADE_SHORT_HISTORY_PRESENT") < rb.index("@@before_guard_body.sql")
    assert "always safe" not in rb
    for name, sha in m["files_sha256"].items():
        assert hashlib.sha256((KIT / name).read_bytes()).hexdigest() == sha, name


def test_live_read_only_evidence():
    probe = json.loads(text(REPORT / "guard-probe.json"))
    outcomes = {(p["command_type"], p["decision"]): p["outcome"] for p in probe["probes"]}
    assert all("TRADE_ORDER_BINDING_REQUIRED" in outcomes[("CASE_SHORT_APPROVE", d)] for d in ("RESTORE", "ACCEPT_SHORT", "READY"))
    assert outcomes[("INVENTORY_COUNT", None)] == "ALLOWED"
    owner = json.loads(text(REPORT / "owner-probe.json"))
    denied = [p for p in owner["probes"] if p["actor"] != "admin"]
    assert denied and all("TRADE_OWNER_ACCESS_DENIED" in p["outcome"] for p in denied)  # current owner already checked before the cache
    assert not json.loads(text(REPORT / "parse-check-v2.json"))["syntax_error"]
    dry = json.loads(text(REPORT / "rollback-guard-dry.json"))
    assert "AFTER_SOURCE_DRIFT_REFUSED" in dry["after_drift"] and dry["history"].startswith("PASSED")


def test_ui_and_runner():
    js = text(ROOT / "wiki-raw/wms_admin_ui_reference/case-pick-management.js")
    assert "TRADE_SHORT_BINDING_REQUIRED" in js and "TRADE_OWNER_ACCESS_DENIED" in js and "shortDecisionText(String(error.message || error))" in js
    assert js.index("localStorage.setItem(key, JSON.stringify(body));") < js.index("throw new Error(shortDecisionText") < js.index("localStorage.removeItem(key);\n  await loadCaseData();")
    for help_id in ("case.short.restore", "case.short.accept", "case.short.weight"):
        assert f'data-help-id="{help_id}"' in js
    runner = text(ROOT / "tests/tradecase/live_trade_pick_shortage.py")
    assert "apply the C-0170 kit first" in runner and "225837931" in runner and "trade-pick-shortage-state.json" in runner
    assert runner.index('"revoke_checked" not in s') < runner.index('step("count"')
