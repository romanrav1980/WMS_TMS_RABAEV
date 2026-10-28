"""C-0173: an order bound to recipient v1 stays usable when only top-up settings change.
The script creates isolated documents only. It calls the installed
RRL_TRADE_RECIPIENT_VERSION function read-only. The former strict predicate is
kept as a historical baseline; it is not presented as the current package."""
from datetime import datetime, timedelta, timezone
import json
import os
from pathlib import Path
import re
import sys
from uuid import uuid4

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT), str(ROOT / "scripts"), str(Path(__file__).parent)]
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment()
os.environ.setdefault("TRADECASE_ADMIN_USER", "admin")
os.environ.setdefault("TRADECASE_ADMIN_PASSWORD", re.search(r"PASS=(\S+?)[`,)\s]", (ROOT / "AGENTS.md").read_text(encoding="utf-8"))[1])
import oracledb
import live_stock_acceptance
from live_document_acceptance import http, expect, CALLS
from tools.mcp.tms_mcp_server import oracle_connection

OUT = ROOT / "runtime/test-evidence/tradecase/2026-10-27/C0173"
PROTECTED = {225837931, 213059748, 225687965, 210564699, 210069361, 223214750, 225290508}
report = dict(status="FAIL", checks=[], versions=[])


def save():
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "recipient-version.json").write_text(json.dumps(dict(report, http=CALLS), indent=1, ensure_ascii=False, default=str), encoding="utf-8")


def resolved_recipient_version(ware, recipient, bound):
    """Read the installed compatibility function; it performs no mutation."""
    with oracle_connection() as c:
        q = c.cursor(); q.execute("set transaction read only")
        q.execute("select RRL_TRADE_RECIPIENT_VERSION(:w,:c,:b) from dual", w=ware, c=recipient, b=bound)
        value = q.fetchone()[0]; c.rollback()
        return None if value is None else int(value)


PREDICATE = """select count(*) from RRL_TRADE_ORDER_LINE ln join RRL_TRADE_ORDER_LINK l on l.CUSTOMER_ORDER_ID=ln.CUSTOMER_ORDER_ID
 join RRL_TRADE_DOCUMENT d on d.WARE_ID=l.WARE_ID and d.ENTITY_TYPE='ORDER'and d.EXTERNAL_ID=l.EXTERNAL_ID and d.VERSION_NO=l.DOCUMENT_VERSION and d.STATUS='ACCEPTED'
 join RRL_TRADE_DOCUMENT r on r.WARE_ID=l.WARE_ID and r.ENTITY_TYPE='RECIPIENT'and r.EXTERNAL_ID=l.RECIPIENT_ID and r.VERSION_NO={version} and r.STATUS='ACCEPTED'
 join RRL_TRADE_DOCUMENT s on s.WARE_ID=l.WARE_ID and s.ENTITY_TYPE='SKU'and s.EXTERNAL_ID=ln.SKU_ID and s.VERSION_NO=ln.SKU_VERSION and s.STATUS='ACCEPTED'
 join RRL_TRADE_SITE ts on ts.WARE_ID=l.WARE_ID and ts.ENABLED=1
 where ln.CUSTOMER_ORDER_ROW_ID=:prow and json_value(r.BODY_JSON,'$.active')='true'and json_value(s.BODY_JSON,'$.active')='true'"""


def line_valid(row, version_sql, **binds):
    """Exact copy of the live enter_line recipient/order/SKU/site predicate (RRL_TRADE_PICK_CONTEXT is accessible only by its callers)."""
    with oracle_connection() as c:
        q = c.cursor(); q.execute("set transaction read only"); q.execute(PREDICATE.format(version=version_sql), prow=row, **binds)
        n = q.fetchone()[0]; c.rollback(); return n == 1


def legacy_strict_baseline(row, ware):
    return "VALID" if line_valid(row, "l.RECIPIENT_VERSION") else "TRADE_ORDER_BINDING_STALE"


def candidate_context(row, ware, recipient):
    version = resolved_recipient_version(ware, recipient, 1)
    return version, ("VALID" if version is not None and line_valid(row, ":v", v=version) else "TRADE_ORDER_BINDING_STALE")


def run():
    tag = uuid4().hex; ware = 210000000 + int(tag[:6], 16)
    with oracle_connection() as c:
        q = c.cursor(); q.execute("""select (select count(*) from RRL_WARES where ID=:w)+(select count(*) from RRL_CELLS where WARE_ID=:w)
            +(select count(*) from RRL_TRADE_SITE where WARE_ID=:w)+(select count(*) from RRL_ACCESS_OBJECT where KIND='WAREHOUSE' and OBJECT_ID=to_char(:w)) from dual""", w=ware)
        assert q.fetchone() == (0,) and ware not in PROTECTED, "warehouse must be absent before the first write"
    report.update(warehouse=ware, tag=tag[:8]); save()
    original = live_stock_acceptance.uuid4
    live_stock_acceptance.uuid4 = lambda: type("Tag", (), {"hex": tag})()
    try:
        f = live_stock_acceptance.setup()
    finally:
        live_stock_acceptance.uuid4 = original
    with oracle_connection() as c:  # the setup identity is not used
        q = c.cursor(); q.execute("update RUSERS set DELETED=1 where ID=:a and USER_GROUP='TC03QA'", a=f["actor"])
        q.execute("update RRL_ACCESS_ASSIGNMENT set REVOKED_AT=systimestamp where ASSIGNMENT_ID=:a", a=f["role"]); c.commit()
    report["fixture"] = {k: v for k, v in f.items() if k != "password"}; save()
    base = f"/api/tradecase/warehouses/{ware}"; t = "RV27." + tag[:8]; now = datetime.now(timezone.utc).isoformat()
    def send(kind, key, payload, version=1, event=""):
        return expect(200, http("POST", "/api/tradecase/messages", dict(schema_version=1, event_id=f"{t}.{kind}.{key}.{version}{event}", source_id="TC03.SAP", warehouse_id=ware,
                      document_id=key, version=version, occurred_at=now, payload=dict(entity_type=kind, **payload))))
    expect(200, http("PUT", base + "/site", dict(operation_id=t + ".site", expected_version=0, source_id="TC03.SAP", active_skm="TC03.SKM", planning_source="SAP", enabled=True, reason="C-0173 recipient version check")))
    send("OWNER", "SNS", dict(title="SNS"))
    send("SKU", "A", dict(title="Recipient version QA", wms_article_id=f["article"], units_per_box=10, permitted_mrc=["200"]))
    customer = expect(200, http("POST", "/api/customers", dict(customer_code=t, customer_name="C-0173 store", customer_type="LEGAL_ENTITY")))["customer_id"]
    recipient = dict(title="Store", wms_customer_id=customer, target_owner_id="SNS", permitted_source_owners=["SNS"], buyout_mode="BEFORE_PICK", min_osg_days=50,
                     lead_time_days=0, allow_broken_box=False, allow_partial_ship=True, topup_enabled=False, topup_horizon_days=3)
    send("RECIPIENT", "C1", recipient)
    ship = (datetime.now(timezone.utc) + timedelta(days=1)).isoformat()
    send("ORDER", "O1", dict(recipient_id="C1", planned_ship_at=ship, lines=[dict(line_id="1", sku_id="A", source_owner_id="SNS", target_owner_id="SNS", mrc="200", quantity="10", uom="EA", min_osg_days=50)]))
    with oracle_connection() as c:  # the same QA native order fixture DML as live_full_pallet.py (no stock rows)
        q = c.cursor(); q.callproc("RRL_STOCK_METADATA_TX.begin_change", ["admin", "warehouse_settings_edit"])
        try:
            q.execute("select RRL_CUSTOMER_ORDER_SQ.nextval,RRL_CUSTOMER_ORDER_ROW_SQ.nextval from dual"); order, row = q.fetchone()
            q.execute("insert into RRL_CUSTOMER_ORDER(CUSTOMER_ORDER_ID,ORDER_NO,CUSTOMER_ID,WARE_ID,SHIPMENT_DATE,STATUS,SOURCE_SYSTEM,CREATED_BY)values(:o,:n,:c,:w,trunc(sysdate)+1,'OPEN','QA_TRADECASE_ONLY','admin')", o=order, n=t, c=customer, w=ware)
            q.execute("insert into RRL_CUSTOMER_ORDER_ROW(CUSTOMER_ORDER_ROW_ID,CUSTOMER_ORDER_ID,LINE_NO,ARTICUL,PRODUCT_NAME,UNIT_CODE,ORDER_QTY,WARE_ID,STATUS,CREATED_BY)values(:r,:o,1,:a,'C-0173','EA',10,:w,'OPEN','admin')", r=row, o=order, a=f["article"], w=ware)
            c.commit()
        finally:
            q.callproc("RRL_STOCK_METADATA_TX.end_change")
    expect(200, http("POST", base + "/orders/O1/binding", dict(operation_id=t + ".bind", expected_order_version=1, customer_order_id=order, lines=[dict(line_id="1", customer_order_row_id=row)])))
    report.update(native_order=order, native_row=row); save()
    def observe(label, version, expect_candidate, expect_live_stale):
        strict, (cand, cand_context) = legacy_strict_baseline(row, ware), candidate_context(row, ware, "C1")
        report["versions"].append(dict(label=label, recipient_version=version, legacy_strict_baseline=strict, resolved_recipient_version=cand, resolved_context=cand_context)); save()
        assert cand == expect_candidate and (cand_context == "VALID") == (expect_candidate is not None), (label, cand, cand_context)
        assert (strict == "TRADE_ORDER_BINDING_STALE") == expect_live_stale, (label, strict)
    observe("v1 bound", 1, 1, False)
    # The same accepted snapshot of v1 resent under a new event id: one snapshot, not an ambiguous history.
    report["v1_resend"] = send("RECIPIENT", "C1", recipient, 1, ".resend")
    with oracle_connection() as c:
        q = c.cursor(); q.execute("set transaction read only")
        q.execute("select count(*),count(distinct EVENT_ID) from RRL_TRADE_MESSAGE where WARE_ID=:w and ENTITY_TYPE='RECIPIENT' and EXTERNAL_ID='C1' and VERSION_NO=1 and json_value(RESULT_JSON,'$.status')='ACCEPTED'", w=ware)
        report["v1_accepted_records"] = list(q.fetchone()); c.rollback()
    send("RECIPIENT", "C1", dict(recipient, topup_enabled=True), 2); observe("v2 only topup_enabled", 2, 2, True)
    send("RECIPIENT", "C1", dict(recipient, topup_enabled=True, topup_horizon_days=5), 3); observe("v3 only top-up settings", 3, 3, True)
    send("RECIPIENT", "C1", dict(recipient, topup_enabled=True, min_osg_days=60), 4); observe("v4 min_osg_days changed", 4, None, True)
    send("RECIPIENT", "C1", dict(recipient, topup_enabled=True, permitted_source_owners=["SNS", "BLC"]), 5); observe("v5 owners changed", 5, None, True)
    send("RECIPIENT", "C1", dict(recipient, topup_enabled=True, buyout_mode="IN_TRANSIT"), 6); observe("v6 buyout changed", 6, None, True)
    send("RECIPIENT", "C1", dict(recipient, active=False), 7); observe("v7 inactive", 7, None, True)
    send("RECIPIENT", "C1", dict(recipient, topup_enabled=True), 8); observe("v8 back to v1 except top-up", 8, 8, True)
    report["checks"].append("Legacy strict baseline rejects every later recipient version")
    report["checks"].append("Installed compatibility function accepts only top-up-only versions; OSG, owners, buyout and inactive remain stale")
    report["checks"].append(f"Bound v1 resent under a new event id: accepted records {report['v1_accepted_records']}; still compatible (same snapshot, not ambiguous)")
    # Missing history of the bound version: candidate refuses (a bound version that never had an accepted message).
    report["missing_history"] = resolved_recipient_version(ware, "C1", 99); assert report["missing_history"] is None
    report["c103"] = dict(bound=1, legacy_strict_baseline=None, resolved_recipient_version=resolved_recipient_version(210069361, "C103", 1))
    with oracle_connection() as c:
        q = c.cursor(); q.execute("set transaction read only")
        q.execute("select ol.CUSTOMER_ORDER_ROW_ID from RRL_TRADE_ORDER_LINK l join RRL_TRADE_ORDER_LINE ol on ol.CUSTOMER_ORDER_ID=l.CUSTOMER_ORDER_ID where l.WARE_ID=210069361 and l.EXTERNAL_ID='103' fetch first 1 rows only")
        c103_row = q.fetchone()[0]; c.rollback()
    report["c103"]["legacy_strict_baseline"] = legacy_strict_baseline(c103_row, 210069361)
    assert report["c103"]["resolved_recipient_version"] == 4 and report["c103"]["legacy_strict_baseline"] == "TRADE_ORDER_BINDING_STALE", report["c103"]
    report["checks"].append("READ ONLY 210069361/C103 bound v1: strict baseline is stale; installed function returns current v4")
    report["status"] = "PASS"


if __name__ == "__main__":
    try:
        run()
    except Exception as exc:
        report["error"] = repr(exc)[:2000]; raise
    finally:
        save(); print(json.dumps({k: report.get(k) for k in ("status", "warehouse", "versions", "c103", "error")}, ensure_ascii=False, default=str)[:3000])
