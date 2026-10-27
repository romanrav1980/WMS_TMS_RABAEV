"""C-0173 offline checks: the NOT_APPLIED kit that lets an order line bound to recipient version N use a later version only when the
accepted payloads differ in top-up settings alone, and the recorded behaviour of the live predicate versus the candidate."""
import hashlib
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[2]
KIT = ROOT / "db/migrations/2026-10-27_trade_recipient_version"
RUN = json.loads((ROOT / "tests/fixtures/tradecase_recipient_version_20261027.json").read_text(encoding="utf-8"))


def text(name):
    return (KIT / name).read_text(encoding="utf-8").replace("\r\n", "\n")


def source(name):
    return text(name)[len("create or replace "):].rsplit("\n/\n", 1)[0]


def test_kit_hashes_and_order():
    m = json.loads(text("manifest.json"))
    assert m["status"] == "NOT_APPLIED" and m["applied_by_claude"] is False
    assert hashlib.sha256(source("before_pick_context_body.sql").encode()).hexdigest().upper() == m["before_sha256"]["RRL_TRADE_PICK_CONTEXT:PACKAGE BODY"]
    assert hashlib.sha256(source("before_transport_core_body.sql").encode()).hexdigest().upper() == m["before_sha256"]["RRL_TRADE_TRANSPORT_CORE:PACKAGE BODY"]
    for name, key in (("001_function.sql", "RRL_TRADE_RECIPIENT_VERSION:FUNCTION"), ("002_pick_context_body.sql", "RRL_TRADE_PICK_CONTEXT:PACKAGE BODY"),
                      ("003_transport_core_body.sql", "RRL_TRADE_TRANSPORT_CORE:PACKAGE BODY")):
        assert hashlib.sha256(source(name).encode()).hexdigest().upper() == m["after_sha256"][key], name
    for name, sha in m["files_sha256"].items():
        assert hashlib.sha256((KIT / name).read_bytes()).hexdigest() == sha, name
    apply = text("apply.sql")
    assert apply.index("000_preflight") < apply.index("001_function") < apply.index("002_pick_context") < apply.index("003_transport_core") < apply.index("verify.sql")
    rollback = text("rollback.sql")
    assert rollback.index("AFTER_SOURCE_DRIFT_REFUSED") < rollback.index("@@before_pick_context_body.sql") < rollback.index("@@before_transport_core_body.sql") \
        < rollback.index("drop function RRL_TRADE_RECIPIENT_VERSION") < rollback.index("@@rollback_verify.sql")
    assert "FUNCTION_ALREADY_EXISTS" in text("000_preflight.sql")


def test_only_the_recipient_join_changes():
    before, after = source("before_pick_context_body.sql"), source("002_pick_context_body.sql")
    assert "RECIPIENT_VERSION=" not in after.replace("RRL_TRADE_RECIPIENT_VERSION(", "") and after.count("VERSION_NO=g_rver") == 2
    assert before.replace("l.RECIPIENT_VERSION", "") .count("SKU_VERSION") == after.count("SKU_VERSION")  # SKU, order and site checks unchanged
    t_before, t_after = source("before_transport_core_body.sql"), source("003_transport_core_body.sql")
    assert len(t_after.splitlines()) == len(t_before.splitlines()) and t_after.count("RRL_TRADE_RECIPIENT_VERSION(tl.WARE_ID,tl.RECIPIENT_ID,tl.RECIPIENT_VERSION)") == 1
    function = source("001_function.sql")
    assert function.index("if v_current=p_bound then return v_current;end if;") < function.index("from RRL_TRADE_MESSAGE")  # fast path first
    assert "'{\"topup_enabled\":null,\"topup_horizon_days\":null}'" in function  # merge patch removes exactly these two fields


def test_recorded_behaviour():
    by = {v["label"]: v for v in RUN["versions"]}
    assert all(v["live"] == "TRADE_ORDER_BINDING_STALE" for v in RUN["versions"] if v["recipient_version"] > 1)  # the blocker
    for label in ("v2 only topup_enabled", "v3 only top-up settings", "v8 back to v1 except top-up"):
        assert by[label]["candidate"] == by[label]["recipient_version"] and by[label]["candidate_context"] == "VALID"
    for label in ("v4 min_osg_days changed", "v5 owners changed", "v6 buyout changed", "v7 inactive"):
        assert by[label]["candidate"] is None and by[label]["candidate_context"] == "TRADE_ORDER_BINDING_STALE"
    assert RUN["v1_accepted_records"] == [2, 2] and RUN["missing_history"] is None
    assert RUN["c103"] == {"bound": 1, "live": "TRADE_ORDER_BINDING_STALE", "candidate": 4}
    assert RUN["parse"]["002_pick_context_body.sql"]["codes"] == [] and not RUN["parse"]["003_transport_core_body.sql"]["syntax_error"]
