"""Isolated native/API deferred-intake proof; no physical inventory mutations."""
from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import sys
from uuid import uuid4

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
import live_document_acceptance as base
from tools.mcp.tms_mcp_server import oracle_connection
from api.wms_api_server.app.modules.integrations.contracts_tradecase import TradeEnvelope
from api.wms_api_server.app.modules.integrations.infrastructure.tradecase_documents import OracleTradecaseDocuments
from api.wms_api_server.app.transaction_gateway import TransactionGateway

OUT = ROOT / "runtime/test-evidence/tradecase/2026-10-21/T02"


def run(f):
    ware, actor, password = f["warehouse_id"], f["actor"], f["password"]
    path = f"/api/tradecase/warehouses/{ware}"
    http, expect = base.http, base.expect
    checks = []
    def env(key, payload, version=1):
        return dict(schema_version=1, event_id=uuid4().hex, source_id="SAP_QA", warehouse_id=ware,
                    document_id=key, version=version, occurred_at=datetime.now(timezone.utc).isoformat(), payload=payload)
    def send(body):
        return http("POST", "/api/tradecase/messages", body, actor, password)
    def retry(body):
        return http("POST", path+"/messages/"+body["event_id"]+"/retry", actor=actor, password=password)
    def query(sql, **binds):
        with oracle_connection() as conn:
            cur = conn.cursor();cur.execute(sql, binds);return cur.fetchall()
    setting = dict(operation_id="setup", expected_version=0, source_id="SAP_QA", active_skm="SAP_QA",
                   planning_source="SAP", enabled=True, reason="Isolated deferred metadata acceptance")
    expect(200, http("PUT", path+"/site", setting))
    line = dict(line_id="10", sku_id="A", source_owner_id="SNS", target_owner_id="BLC", mrc="200",
                quantity="20", uom="EA", min_osg_days=50)
    order = dict(entity_type="ORDER", recipient_id="C1", planned_ship_at="2026-10-22T12:00:00+03:00", lines=[line])
    original = env("O1", order)
    original["event_id"] = "TC21:pending/" + original["event_id"]
    first = expect(200, send(original));assert first["status"] == "WAITING"
    initial = expect(200, http("GET", path+"/messages/"+original["event_id"], actor=actor, password=password))
    assert initial["result"] == initial["current_result"] == first
    trip = env("R1", dict(entity_type="TRIP", vehicle_id="V1", planning_source="SAP",
               planned_departure_at="2026-10-22T12:00:00+03:00", capacity_kg="8000", capacity_m3="66",
               orders=[dict(order_id="O1", line_id="10", quantity="20")]), 2)
    assert expect(200, send(trip))["status"] == "WAITING"
    lower_trip = deepcopy(trip);lower_trip.update(event_id=uuid4().hex, version=1)
    assert expect(200, send(lower_trip))["status"] == "WAITING"
    assert expect(200, retry(original))["status"] == "WAITING"
    changed = deepcopy(original);changed["payload"]["lines"][0]["quantity"] = "30"
    assert "EVENT_CONTENT_CONFLICT" in expect(409, send(changed))["detail"]["code"]
    expect(403, http("POST", f"/api/tradecase/warehouses/{ware+1}/messages/{original['event_id']}/retry", actor=actor, password=password))
    checks.append("durable WAITING, exact replay, content conflict, warehouse denial")
    for key in ("SNS", "BLC"):
        expect(200, send(env(key, dict(entity_type="OWNER", title=key))))
    sku = dict(entity_type="SKU", title="Deferred A", units_per_box=10, permitted_mrc=["200"])
    expect(200, send(env("A", sku)))
    profile = dict(entity_type="RECIPIENT", title="C1", target_owner_id="BLC", permitted_source_owners=["SNS"],
                   buyout_mode="BEFORE_PICK", lead_time_days=0, min_osg_days=50)
    expect(200, send(env("C1", profile)))
    # Both native workers contend for the same site/queue row; only one applies and emits resolution.
    with ThreadPoolExecutor(max_workers=2) as pool:
        outcomes = list(pool.map(retry, [original, original]))
    results = [expect(200, item) for item in outcomes]
    assert results[0] == results[1] and results[0]["status"] == "ACCEPTED"
    again = expect(200, send(original));assert again == dict(first, replayed=True)
    assert expect(200, retry(trip))["status"] == "ACCEPTED"
    assert expect(409, retry(lower_trip))["detail"]["code"] == "STALE_VERSION"
    assert expect(200, http("GET", path+"/documents/TRIP/R1", actor=actor, password=password))["document_version"] == 2
    checks.append("late master arrival, dependent order/trip, two concurrent retries, immutable initial receipt")
    # A queue can now be rejected by ordinary current business rules, not silently forced through.
    bad = env("BAD", dict(order, lines=[dict(line, sku_id="LATE", mrc="201")]))
    assert expect(200, send(bad))["status"] == "WAITING"
    expect(200, send(env("LATE", sku)))
    assert expect(409, retry(bad))["detail"]["code"] == "MRC_NOT_PERMITTED"
    assert expect(409, retry(bad))["detail"]["code"] == "MRC_NOT_PERMITTED"
    rejected = expect(200, http("GET", path+"/messages/"+bad["event_id"], actor=actor, password=password))
    assert rejected["result"]["status"] == "WAITING" and rejected["current_result"]["status"] == "REJECTED"
    # Initial rejection is terminal; introducing the queue does not reopen old rejected receipts.
    rejected_direct = env("DIRECT.BAD", dict(order, lines=[dict(line, mrc="201")]))
    expect(409, send(rejected_direct));expect(404, retry(rejected_direct))
    checks.append("final rejection durable, original WAITING preserved, ordinary rejected receipt not reopened")
    # Queue and acknowledgement disappear together if the caller rolls back.
    rolled = env("ROLLBACK", dict(order, recipient_id="ABSENT"))
    with oracle_connection() as conn:
        result = OracleTradecaseDocuments(TransactionGateway(conn.cursor())).receive(TradeEnvelope.model_validate(rolled), actor)
        conn.rollback()
    assert query("select count(*) from RRL_TRADE_MESSAGE where WARE_ID=:w and EVENT_ID=:e", w=ware, e=rolled["event_id"])[0][0] == 0
    assert query("select count(*) from RRL_TRADE_DEFERRED where WARE_ID=:w and EVENT_ID=:e", w=ware, e=rolled["event_id"])[0][0] == 0
    assert query("select count(*) from RRL_EVENT_OUTBOX where EVENT_OUTBOX_ID=:i", i=result["outbox_id"])[0][0] == 0
    rolling_retry = env("ROLL.RETRY", dict(order, recipient_id="LATE.C"))
    expect(200, send(rolling_retry));expect(200, send(env("LATE.C", profile)))
    with oracle_connection() as conn:
        result = OracleTradecaseDocuments(TransactionGateway(conn.cursor())).retry(ware, rolling_retry["event_id"], actor)
        assert result["status"] == "ACCEPTED";conn.rollback()
    assert query("select count(*) from RRL_TRADE_DOCUMENT where WARE_ID=:w and EXTERNAL_ID='ROLL.RETRY'", w=ware)[0][0] == 0
    assert query("select STATE from RRL_TRADE_DEFERRED where WARE_ID=:w and EVENT_ID=:e", w=ware, e=rolling_retry["event_id"])[0][0] == "WAITING"
    assert query("select count(*) from RRL_EVENT_OUTBOX where EVENT_OUTBOX_ID=:i", i=result["outbox_id"])[0][0] == 0
    expect(200, retry(rolling_retry))
    checks.append("caller rollback of initial queue and final resolution includes metadata and outbox")
    # A late retry must not overwrite a newer accepted version of the same document.
    stale = env("VERSIONED", dict(order, recipient_id="VERSION.C"))
    expect(200, send(stale));expect(200, send(env("VERSION.C", profile)))
    expect(200, send(env("VERSIONED", dict(order, recipient_id="VERSION.C"), 2)))
    assert expect(409, retry(stale))["detail"]["code"] == "STALE_VERSION"
    # Financial-basis rights are re-evaluated even if a general importer has access to the queue.
    with oracle_connection() as conn:
        conn.cursor().execute("insert into RRL_ACCESS_ROLE_RIGHT(ROLE_ID,PERMISSION) values(:r,'tradecase_buyout_basis_import')", r=f["role"]);conn.commit()
    finance = env("FIN", dict(order, recipient_id="FIN.C", order_kind="BUYOUT", buyout_mode="BEFORE_PICK"))
    assert expect(200, send(finance))["status"] == "WAITING"
    with oracle_connection() as conn:
        conn.cursor().execute("delete from RRL_ACCESS_ROLE_RIGHT where ROLE_ID=:r and PERMISSION='tradecase_buyout_basis_import'", r=f["role"]);conn.commit()
    expect(403, retry(finance))
    checks.append("newer version protected; financial permission rechecked")
    page = expect(200, http("GET", path+"/messages?limit=100", actor=actor, password=password))
    current = next(x for x in page["items"] if x["event_id"] == original["event_id"])
    assert current["result"]["status"] == "WAITING" and current["current_result"]["status"] == "ACCEPTED"
    for _ in range(8):
        expect(200, http("GET", path+"/messages/"+original["event_id"], actor=actor, password=password))
    counts = query("select STATE,count(*) from RRL_TRADE_DEFERRED where WARE_ID=:w group by STATE", w=ware)
    with oracle_connection() as conn:
        cur = conn.cursor()
        cur.execute("select json_value(RESULT_JSON,'$.outbox_id' returning number) from RRL_TRADE_DEFERRED where WARE_ID=:w and STATE<>'WAITING'", w=ware)
        final_ids = [row[0] for row in cur]
        assert len(final_ids) == len(set(final_ids))
        for oid in final_ids:
            cur.execute("select count(*) from RRL_EVENT_OUTBOX where EVENT_OUTBOX_ID=:i", i=oid);assert cur.fetchone()[0] == 1
        cur.execute("update RRL_ACCESS_ASSIGNMENT set REVOKED_AT=systimestamp where ASSIGNMENT_ID=:r", r=f["role"]);conn.commit()
    expect(403, retry(original))
    assert query("select count(*) from RRL_PALLETS")[0][0] == f["physical_before"]
    assert query("select count(*) from user_objects where STATUS='INVALID'")[0][0] == 0
    checks.append("bounded current-state reads, unique resolution outboxes, revoked cached access denied, physical stock unchanged")
    return dict(checks=checks, queue_counts=counts, event_id=original["event_id"], warehouse_id=ware)


if __name__ == "__main__":
    os.environ.setdefault("TRADECASE_ADMIN_USER", "admin")
    os.environ.setdefault("TRADECASE_ADMIN_PASSWORD", re.search(r"PASS=(\S+?)[`,)\s]", (ROOT/"AGENTS.md").read_text(encoding="utf-8"))[1])
    OUT.mkdir(parents=True, exist_ok=True)
    f = base.make_fixture()
    safe = {k: v for k, v in f.items() if k != "password"}
    report = dict(status="FAIL", fixture=safe)
    try:
        report.update(run(f));report["status"] = "PASS"
    except Exception as exc:
        report["error"] = str(exc);raise
    finally:
        with oracle_connection() as conn:
            cur = conn.cursor()
            cur.execute("update RUSERS set DELETED=1 where ID=:a and USER_GROUP='TC19QA'", a=f["actor"])
            cur.execute("update RRL_ACCESS_ASSIGNMENT set REVOKED_AT=coalesce(REVOKED_AT,systimestamp) where ASSIGNMENT_ID=:r and USERNAME=:a", r=f["role"], a=f["actor"])
            cur.execute("select LOG_ID,ELAPSED_MS,OPERATION_KIND from RRL_SQL_SLOW_LOG where LOG_ID>:n order by LOG_ID fetch first 30 rows only", n=f["slow_marker"])
            report["slow_sql"] = [list(x) for x in cur];conn.commit()
        report["calls"] = base.CALLS
        (OUT/("deferred-"+str(f["warehouse_id"])+".json")).write_text(json.dumps(report, ensure_ascii=True, indent=2, default=str), encoding="utf-8")
    print(json.dumps({k: v for k, v in report.items() if k not in {"calls", "fixture"}}))
