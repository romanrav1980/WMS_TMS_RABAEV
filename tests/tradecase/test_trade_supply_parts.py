"""C-0163 offline checks: SUPPLY composition in parts — contract, hashes, the hand-over flow through the existing intake and the kit.
Live READ ONLY proofs (native codes hash = sender rule; missing-parts query): reports/tradecase/2026-10-23/claude/C0163/candidate-live.json."""
import hashlib
import json
import pathlib
import re
import pytest
from pydantic import ValidationError
from app.modules.integrations.contracts_supply_parts import (TradeSupplyPart, TradeSupplyPartsEnd, assembled_event_id, codes_sha256, end_wire, part_wire)
from app.modules.integrations.contracts_tradecase import TradecaseError, TradeSupply
from app.modules.integrations.infrastructure import supply_parts as subject

ROOT = pathlib.Path(__file__).resolve().parents[2]
KIT = ROOT / "db/migrations/2026-10-23_trade_supply_parts"
HEADER = {"entity_type": "SUPPLY", "wms_article_id": "TC03089DDB36", "sap_order_id": "SO1", "sap_line_id": "1", "sku_id": "A", "owner_id": "SNS",
          "mrc": "200", "pallet_identifier": "PAL-1", "supplier_batch": "B1", "expiry_date": "2030-01-01", "composition_source": "SAP"}
CODES = [f"010460000000000121{n:04d}abc" for n in range(1, 8)]
SPLIT = {1: CODES[0:3], 2: CODES[3:5], 3: CODES[5:7]}


def part(no, event=None, codes=None, **kw):
    return TradeSupplyPart.model_validate({"schema_version": 1, "event_id": event or f"E.P{no}", "source_id": "TC03.SAP", "warehouse_id": 210564699,
                                          "document_id": "SUP.1", "version": 2, "transfer_id": "T1", "part_no": no, "part_count": 3,
                                          "occurred_at": "2026-10-23T10:00:00+00:00", "header": HEADER, "codes": [{"code": c} for c in (codes or SPLIT[no])], **kw})


def end(**kw):
    return TradeSupplyPartsEnd.model_validate({"schema_version": 1, "event_id": "E.END", "source_id": "TC03.SAP", "warehouse_id": 210564699, "document_id": "SUP.1",
                                               "version": 2, "transfer_id": "T1", "part_count": 3, "total_codes": 7, "codes_sha256": codes_sha256(CODES),
                                               "occurred_at": "2026-10-23T10:05:00+00:00", **kw})


def test_header_is_the_supply_without_codes_and_parts_are_numbered():
    assert set(part(1).header.model_dump()) == set(TradeSupply.model_fields) - {"codes"}
    for bad in (dict(part_no=4), dict(part_count=1001), dict(extra=1)):
        with pytest.raises(ValidationError):
            part(1, **bad)
    with pytest.raises(ValidationError):
        part(1, codes=["short"])  # the same code rule as a full SUPPLY
    with pytest.raises(ValidationError):
        end(total_codes=10001)


def test_hashes_bind_content_not_delivery_details():
    a, b = part_wire(part(2)), part_wire(part(2, event="E.OTHER"))
    assert a["part_hash"] == b["part_hash"] and a["header_hash"] == b["header_hash"]  # same content, other event: a repeat
    assert part_wire(part(2, codes=SPLIT[3]))["part_hash"] != a["part_hash"]  # same number, other codes: a conflict natively
    assert end_wire(end())["end_hash"] == end_wire(end(event_id="E.END2"))["end_hash"]
    assert assembled_event_id("TC03.SAP", 210564699, "T1") == assembled_event_id("TC03.SAP", 210564699, "T1") != assembled_event_id("TC03.SAP", 210564699, "T2")
    assert len(assembled_event_id("S" * 100, 1, "T" * 100)) <= 100


class Native:
    """Stands in for RRL_TRADE_SUPPLY_PARTS_API: records what the adapter sends and answers transfer states."""

    def __init__(self):
        self.parts, self.end, self.calls, self.status, self.delivered = {}, None, [], "OPEN", None

    def state(self, replayed=False):
        missing = [n for n in (1, 2, 3) if n not in self.parts]
        return {"warehouse_id": 210564699, "source_id": "TC03.SAP", "transfer_id": "T1", "document_id": "SUP.1", "version": 2, "part_count": 3,
                "missing_parts": missing, "end_received": self.end is not None, "status": self.status, "received_codes": sum(len(v) for v in self.parts.values()),
                **({"replayed": True} if replayed else {})}

    def call(self, name, args):
        self.calls.append(name)
        if name == "put_part":
            w = json.loads(args[2])
            self.parts.setdefault(w["part_no"], [c["code"] for c in w["codes"]])
        elif name == "put_end":
            self.end = json.loads(args[2])
        elif name == "assembled":
            codes = [{"system_code": "CRPT", "profile_code": "TOBACCO", "code": c} for n in sorted(self.parts) for c in self.parts[n]]
            return {"state": self.state(), "header": HEADER, "codes": codes, "end_occurred_at": "2026-10-23T10:05:00+00:00"}
        elif name == "mark_delivered":
            w = json.loads(args[2])
            if self.status != "COMPLETE":
                return self.state(True)
            self.status, self.delivered = w["outcome"], w
            return self.state()
        if name in ("put_part", "put_end") and len(self.parts) == 3 and self.end is not None and self.status == "OPEN":
            self.status = "COMPLETE"
        return self.state()


class Gateway:
    def __init__(self, native):
        self.native = native

    def transaction(self, name):
        native = self.native

        class Var:
            def __init__(self):
                self.value = None

            def setvalue(self, _, v):
                self.value = v

            def getvalue(self):
                return self.value

        class Cur:
            def var(self, kind):
                return Var()

            def execute(self, *a, **k):
                pass

            def callproc(self, proc, args):
                name = proc.split(".")[-1]
                values = [a.value if isinstance(a, Var) else a for a in args]
                args[-1].value = json.dumps(native.call(name, values))

        class Ctx:
            def __enter__(self):
                return Cur()

            def __exit__(self, *a):
                return False
        return Ctx()


class Seen(list):
    fail = None


@pytest.fixture
def received(monkeypatch):
    seen = Seen()

    class Docs:
        def __init__(self, gateway):
            pass

        def receive(self, envelope, actor):
            seen.append(envelope)
            if seen.fail:
                raise seen.fail
            return {"status": "ACCEPTED", "event_id": envelope.event_id}
    monkeypatch.setattr(subject, "OracleTradecaseDocuments", Docs)
    return seen


def test_order_2_end_1_hands_over_once_with_codes_in_part_order(received):
    native = Native(); svc = subject.OracleSupplyParts(Gateway(native))
    assert svc.put_part(part(2), "sap")["missing_parts"] == [1, 3] and received == []
    svc.put_part(part(3), "sap")
    early = svc.put_end(end(), "sap")
    assert early["status"] == "OPEN" and received == []  # END before the last part: nothing is accepted
    done = svc.put_part(part(1), "sap")
    assert done["status"] == "DELIVERED" and len(received) == 1
    env = received[0]
    assert env.event_id == assembled_event_id("TC03.SAP", 210564699, "T1") and env.document_id == "SUP.1" and env.version == 2
    assert [c.code for c in env.payload.codes] == CODES and env.payload.owner_id == "SNS"
    svc.put_part(part(1), "sap")  # a repeat after delivery hands nothing over again
    assert len(received) == 1


def test_unknown_outcome_keeps_the_transfer_and_the_same_event_is_repeated(received):
    native = Native(); svc = subject.OracleSupplyParts(Gateway(native))
    for n in (1, 2, 3):
        native.parts[n] = SPLIT[n]
    native.end, native.status = {"x": 1}, "COMPLETE"
    received.fail = TradecaseError("TRADECASE_RESULT_UNKNOWN", 503)
    with pytest.raises(TradecaseError):
        svc.deliver(210564699, "TC03.SAP", "T1", "sap")
    assert native.status == "COMPLETE" and "mark_delivered" not in native.calls
    received.fail = None
    assert svc.deliver(210564699, "TC03.SAP", "T1", "sap")["status"] == "DELIVERED"
    assert received[0].event_id == received[1].event_id  # recovery repeats the very same message


def test_business_rejection_is_recorded_not_retried_forever(received):
    native = Native(); svc = subject.OracleSupplyParts(Gateway(native))
    for n in (1, 2, 3):
        native.parts[n] = SPLIT[n]
    native.end, native.status = {"x": 1}, "COMPLETE"
    received.fail = TradecaseError("MASTER_MISSING:SKU:A", 409)
    r = svc.deliver(210564699, "TC03.SAP", "T1", "sap")
    assert r["status"] == "DELIVERY_REJECTED" and native.delivered["reason"] == "MASTER_MISSING:SKU:A"
    received.fail = None


def text(name):
    return (KIT / name).read_text(encoding="utf-8").replace("\r\n", "\n")


def test_native_rules():
    body = text("002_parts_api.sql")
    body = body[body.index("create or replace package body"):]
    put = body[body.index(" procedure put_part("):body.index(" procedure put_end(")]
    assert put.index("lock_site(") < put.index("require_owner(") < put.index("EVENT_ID=ev") < put.index("assert_current(") < put.index("for update")
    assert "fail('SUPPLY_PART_EVENT_CONFLICT')" in put and "fail('SUPPLY_PART_CONFLICT')" in put and "fail('SUPPLY_PART_HEADER_CONFLICT')" in put
    assert "if total+ncodes>10000 then fail('SUPPLY_PART_CODE_LIMIT')" in put
    ev = body[body.index(" procedure evaluate("):body.index(" procedure put_part(")]
    assert "n<t.PART_COUNT or t.END_EVENT_ID is null" in ev and "t.STATUS:='COMPLETE'" in ev and "CODES_HASH_MISMATCH" in ev and "TOTAL_MISMATCH" in ev
    assert "order by p.PART_NO,x.SEQ" in ev and "dbms_lob.writeappend(joined,1,chr(10))" in ev
    lock = body[body.index(" function lock_site("):body.index(" procedure require_owner(")]
    assert lock.index("lock table RRL_ACCESS_REV in share mode") < lock.index("assert_allowed") < lock.index("for update wait 5")
    assert "fail('SUPPLY_PART_VERSION_SUPERSEDED')" in body and "VERSION_NO>p_version" in body
    listing = body[body.index(" procedure transfers("):]
    assert listing.index("owner_allowed") < listing.index("fetch first 101")
    for stmt in re.findall(r"(?is)\b(?:select|insert|update)\b.*?;", body):
        assert not re.search(r"\b[a-z]\.get_(string|number|object|array)\(", stmt), stmt[:120]  # JSON object methods never inside SQL
    assert "RRL_TRADE_SUPPLY_PART_APPEND before update or delete" in text("001_schema.sql")
    assert "SUPPLY_PART_HISTORY_PRESENT" in text("rollback.sql")


def test_kit_and_live_proofs():
    m = json.loads(text("manifest.json"))
    assert m["status"] == "NOT_APPLIED" and m["applied_by_claude"] is False and m["shared_objects_changed"] == {}
    for v in m["unchanged_dependency_sha256"].values():
        assert v in text("000_preflight.sql") and v in text("verify.sql") and v in text("rollback_verify.sql")
    for v in m["after_sha256"].values():
        assert v in text("verify.sql")
    for name, sha in m["files_sha256"].items():
        assert hashlib.sha256((KIT / name).read_bytes()).hexdigest() == sha, name
    live = json.loads((ROOT / "reports/tradecase/2026-10-23/claude/C0163/candidate-live.json").read_text(encoding="utf-8"))
    assert live["hash_equal"] and live["missing_of_6_with_2_and_5"] == [1, 3, 4, 6]
