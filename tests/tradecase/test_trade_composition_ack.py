"""C-0164 offline checks: assembled order composition and separate SAP/SKM business acknowledgments — contract, adapter, routes, native
rules and the kit. Live READ ONLY proofs: reports/tradecase/2026-10-23/claude/C0164/{candidate-live.json, parse-check.json}."""
import hashlib
import json
import pathlib
import re
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from pydantic import ValidationError
from app.modules.integrations.api.composition_ack_routes import router
from app.modules.integrations.contracts_composition_ack import CompositionAck, CompositionReport, ack_wire, composition_ack_service
from app.modules.integrations.infrastructure import composition_ack as subject
from app.modules.platform.public import get_current_user

ROOT = pathlib.Path(__file__).resolve().parents[2]
KIT = ROOT / "db/migrations/2026-10-23_trade_composition_ack_v2"
SIG = "a" * 64


def ack(**kw):
    return CompositionAck.model_validate({"schema_version": 1, "warehouse_id": 210564699, "system_code": "SAP", "sender_id": "TC03.SAP", "event_id": "E1",
                                          "order_id": "O/1", "composition_no": 1, "signature": SIG, "outcome": "ACCEPTED",
                                          "occurred_at": "2026-10-23T10:00:00+00:00", **kw})


def test_ack_contract_and_hash():
    assert ack().reason is None and ack(system_code="SKM", sender_id="TC03.SKM").system_code == "SKM"
    for bad in (dict(outcome="REJECTED"), dict(system_code="EDO"), dict(signature="x"), dict(composition_no=0), dict(extra=1), dict(outcome="DELIVERED")):
        with pytest.raises(ValidationError):
            ack(**bad)
    assert ack(outcome="REJECTED", reason="NO_SUCH_ORDER").reason == "NO_SUCH_ORDER"
    a, b = ack_wire(ack()), ack_wire(ack())
    assert a["payload_hash"] == b["payload_hash"]  # the same answer repeated: the same bytes
    assert ack_wire(ack(outcome="REJECTED", reason="X"))["payload_hash"] != a["payload_hash"]  # changed body under one event: a conflict natively


class Gateway:
    def __init__(self):
        self.calls, self.statements = [], []

    def transaction(self, name):
        outer = self

        class Var:
            value = None

            def setvalue(self, _, v):
                self.value = v

            def getvalue(self):
                return self.value

        class Cur:
            def var(self, kind):
                return Var()

            def execute(self, sql, *a, **k):
                outer.statements.append(sql)

            def callproc(self, proc, args):
                outer.calls.append((proc, [a.value if isinstance(a, Var) else a for a in args[:-1]]))
                args[-1].value = json.dumps({"status": "WAITING"})

        class Ctx:
            def __enter__(self):
                return Cur()

            def __exit__(self, *a):
                return False
        return Ctx()


def test_adapter_calls_one_native_procedure_each():
    g = Gateway(); svc = subject.OracleCompositionAck(g)
    svc.report(CompositionReport(warehouse_id=210564699, order_id="O1"), "op")
    svc.acknowledge(ack(), "sap")
    svc.orders(210564699, 50, "viewer")
    assert [c[0] for c in g.calls] == ["RRL_TRADE_COMPOSITION_API.report", "RRL_TRADE_COMPOSITION_API.acknowledge", "RRL_TRADE_COMPOSITION_API.orders"]
    assert json.loads(g.calls[0][1][2]) == {"warehouse_id": 210564699, "order_id": "O1"}
    assert json.loads(g.calls[1][1][2])["payload_hash"] == ack_wire(ack())["payload_hash"]
    assert g.statements == ["set transaction read only"]
    assert g.calls[2][1] == [210564699, "viewer", 50]


def test_routes():
    calls = []

    class Service:
        def report(self, body, actor):
            calls.append(("report", body.order_id, actor)); return {"status": "WAITING"}

        def acknowledge(self, body, actor):
            calls.append(("ack", body.system_code, body.order_id, actor)); return {"status": "CONFIRMED"}

        def orders(self, warehouse, limit, actor):
            calls.append(("orders", warehouse, limit, actor)); return {"items": [], "has_more": False}
    app = FastAPI(); app.include_router(router)
    app.dependency_overrides[get_current_user] = lambda: type("U", (), {"username": "op"})()
    app.dependency_overrides[composition_ack_service] = Service
    c = TestClient(app)
    assert c.post("/api/tradecase/order-compositions/report", json={"warehouse_id": 210564699, "order_id": "O/1"}).status_code == 200
    body = ack().model_dump(mode="json")
    assert c.post("/api/tradecase/order-compositions/acknowledgments", json=body).status_code == 200
    assert c.post("/api/tradecase/order-compositions/acknowledgments", json={**body, "outcome": "REJECTED"}).status_code == 422
    assert c.get("/api/tradecase/warehouses/210564699/order-compositions?limit=20").status_code == 200
    assert c.get("/api/tradecase/warehouses/210564699/order-compositions?limit=101").status_code == 422
    assert calls == [("report", "O/1", "op"), ("ack", "SAP", "O/1", "op"), ("orders", 210564699, 20, "op")]


def text(name):
    return (KIT / name).read_text(encoding="utf-8").replace("\r\n", "\n")


def body():
    s = text("002_composition_api.sql")
    return s[s.index("create or replace package body"):]


def part(name, nxt):
    b = body()
    return b[b.index(f" procedure {name}(") if f" procedure {name}(" in b else b.index(f" function {name}("):b.index(nxt)]


def test_composition_is_the_existing_fulfillment_fact():
    c = part("compose", " -- Stored snapshot + live reconciliation")
    assert "from RRL_CUSTOMER_ORDER_FULFILLMENT where CUSTOMER_ORDER_ID=p_order" in c
    line = c[c.index("line('F|'"):c.index("if p_items then")]
    for field in ("FULFILLMENT_ID", "CARRIER", "PICKED_CASE_TASK_ID", "PICKED_CONTENT_VERSION", "PICKED_WAREHOUSE_TASK_ID", "PICKED_STOCK_VERSION", "FACT_UOM",
                  "sha(r.FACT_COMPOSITION_JSON)"):
        assert field in line
    assert "STATUS" not in line  # shipping after the report keeps the signature; a re-pick (new version) changes it
    assert "r.STATUS not in('PICKED','SHIPPED')or(r.PICKED_CASE_TASK_ID is null and r.PICKED_WAREHOUSE_TASK_ID is null)then n_open:=n_open+1" in c
    assert "closed:=case when n_all>0 and n_open=0 then 1 else 0 end" in c  # no fulfillment is not an assembly
    assert "RRL_WMS_HU_LINK" not in c  # no second versioning of HU membership
    assert "fail('TRADE_COMPOSITION_UNIT_BOUND')" in c and "fail('TRADE_COMPOSITION_FULFILLMENT_BOUND')" in c


def test_report_rules():
    r = part("report", " procedure acknowledge(")
    order = ["lock_site(p_ware,p_actor,'tradecase_order_bind')", "require_owners(p_actor,p_ware,l.CUSTOMER_ORDER_ID,1)", "compose(l.CUSTOMER_ORDER_ID,true",
             "fail('TRADE_COMPOSITION_ASSEMBLY_OPEN')", "c.SIGNATURE=sig and c.ORDER_VERSION=l.DOCUMENT_VERSION and c.SOURCE_ID=site.SOURCE_ID",
             "set STATE='SUPERSEDED'", "insert into RRL_TRADE_ORDER_COMPOSITION", "RRL_TRACEABILITY_API.enqueue_event('TRADECASE_COMPOSITION_REPORTED'"]
    assert [r.index(x) for x in order] == sorted(r.index(x) for x in order)  # closure before any report; a repeat queues nothing
    assert "p_result:=card(c,l,site,true).to_clob;return;" in r
    assert "skm_need:=case when codes>0 then 'WAITING' else 'NOT_REQUIRED' end" in r and "fail('TRADE_COMPOSITION_SKM_NOT_CONFIGURED')" in r
    assert "WMS_INTERNAL_COMPOSITION_V1" in r


def test_acknowledge_rules():
    a = part("acknowledge", " procedure orders(")
    order = ["lock_site(p_ware,p_actor,'tradecase_import')", "require_owners(p_actor,p_ware,l.CUSTOMER_ORDER_ID,1)", "prior_ack.PAYLOAD_HASH<>ph",
             "fail('TRADE_COMPOSITION_ACK_STALE')", "fail('TRADE_COMPOSITION_SIGNATURE_MISMATCH')", "sender<>c.SOURCE_ID or sender<>site.SOURCE_ID",
             "fail('TRADE_COMPOSITION_SKM_NOT_EXPECTED')", "fail('TRADE_COMPOSITION_SKM_CHANGED')", "fail('TRADE_COMPOSITION_PHYSICAL_CHANGED')",
             "fail('TRADE_COMPOSITION_ACK_FINAL')", "insert into RRL_TRADE_COMPOSITION_ACK"]
    assert [a.index(x) for x in order] == sorted(a.index(x) for x in order)
    sap = a[a.index("set SAP_STATUS=outcome"):a.index("else", a.index("set SAP_STATUS=outcome"))]
    skm = a[a.index("set SKM_STATUS=outcome"):a.index("end if;", a.index("set SKM_STATUS=outcome"))]
    assert "SKM_" not in sap and "SAP_" not in skm  # one system's result never writes the other's
    assert "r.put('business_replayed',true)" in a and "r.put('stock_changed',false)" in a


def test_no_stock_write_and_reads():
    b = body()
    writes = set(re.findall(r"(?i)\b(?:insert\s+into|update|delete\s+from)\s+(RRL_\w+)", b))
    assert writes == {"RRL_TRADE_ORDER_COMPOSITION", "RRL_TRADE_COMPOSITION_ACK"}
    for stmt in re.findall(r"(?is)\b(?:select|insert|update)\b.*?;", b):
        assert not re.search(r"\b[a-z]\.get_(string|number|object|array)\(", stmt), stmt[:120]  # JSON object methods never inside SQL
    o = part("orders", "\nend;\n/")
    assert o.index("owner_allowed(p_actor,p_ware,ol.SOURCE_OWNER_ID,0)") < o.index("fetch first 101") and "'tradecase_view'" in o
    card = part("card", " procedure report(")
    for why in ("ASSEMBLY_REOPENED", "COMPOSITION_CHANGED", "ORDER_VERSION_CHANGED", "SOURCE_CHANGED", "SKM_CHANGED", "NOT_REPORTED", "ASSEMBLY_OPEN"):
        assert why in card
    s = text("001_schema.sql")
    assert "RRL_TRADE_COMP_ACK_APPEND before update or delete" in s and "COMPOSITION_SNAPSHOT_FROZEN" in s and "RRL_TRADE_ORDER_COMP_CUR_UK" in s
    assert "COMPOSITION_HISTORY_PRESENT" in text("rollback.sql")


def test_kit_and_live_proofs():
    m = json.loads(text("manifest.json"))
    assert m["status"] == "NOT_APPLIED" and m["applied_by_claude"] is False and m["shared_objects_changed"] == {}
    for v in m["unchanged_dependency_sha256"].values():
        assert v in text("000_preflight.sql") and v in text("verify.sql") and v in text("rollback_verify.sql")
    for v in m["after_sha256"].values():
        assert v in text("verify.sql")
    for name, sha in m["files_sha256"].items():
        assert hashlib.sha256((KIT / name).read_bytes()).hexdigest() == sha, name
    reports = ROOT / "reports/tradecase/2026-10-23/claude/C0164"
    live = json.loads((reports / "candidate-live.json").read_text(encoding="utf-8"))
    assert live["all_equal"] and any(o["has_full_pallet"] for o in live["orders"]) and any(not o["has_full_pallet"] for o in live["orders"])
    parse = json.loads((reports / "parse-check.json").read_text(encoding="utf-8"))
    assert not parse["syntax_error"] and set(parse["codes"]) <= {"ORA-06550", "ORA-00942", "PLS-00201", "PLS-00320"}
