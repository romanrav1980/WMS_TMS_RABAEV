"""C-0168 live (root runs it after the API loads the nested supplier composition): a NEW isolated warehouse via the existing setup(),
one factory pallet SSCC with BOX6 + BOX4 received by ONE SSCC scan through the existing receipt, bound to SNS/MRC/expiry, plus the
refusal set. Existing public APIs only; no synthetic inventory DML. Writes runtime/test-evidence/tradecase/2026-10-23/T03/factory-hierarchy-<ware>.json."""
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import sys
from uuid import uuid4
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT), str(Path(__file__).parent)]
from live_stock_acceptance import setup, xml_call, fields
from live_document_acceptance import http, expect, CALLS
from tools.mcp.tms_mcp_server import oracle_connection

OUT = ROOT / "runtime/test-evidence/tradecase/2026-10-23/T03"


def supply_xml(f, tag, codes, boxes, children, message):
    supply = ET.Element("WarehouseSupplyOrder", version="1")
    fields(supply, dict(Sender="TC03.QA.SAP", MessageId=message, OrderNumber="FH."+tag[:8], Revision=1, WarehouseId=f["warehouse_id"],
                        ReceiveCell=f["receive"], Supplier="Factory hierarchy fixture"))
    line = ET.SubElement(ET.SubElement(supply, "Lines"), "Line")
    fields(line, dict(LineNumber="1", Material=f["article"])); ET.SubElement(line, "Quantity", unit="EA").text = "10"
    aggs = ET.SubElement(supply, "Aggregations")
    for box_code, members in boxes:
        agg = ET.SubElement(aggs, "Aggregation")
        fields(agg, dict(LineNumber="1", System="CRPT", Profile="TOBACCO", Level="BOX", Code=box_code))
        units = ET.SubElement(agg, "Units")
        for i in members:
            fields(ET.SubElement(units, "Unit"), dict(UnitId=str(i), Quantity="1", Code=codes[i - 1]["code"]))
    for sscc, kids in children:
        agg = ET.SubElement(aggs, "Aggregation")
        fields(agg, dict(LineNumber="1", System="CRPT", Profile="TOBACCO", Level="PALLET", Code=sscc))
        holder = ET.SubElement(agg, "Children")
        for kid in kids:
            fields(ET.SubElement(holder, "Child"), dict(Code=kid))
    return supply


def run(f):
    w, tag = f["warehouse_id"], f["tag"]
    path = f"/api/tradecase/warehouses/{w}"; stock = path + "/stock"
    def send(document, payload):
        return expect(200, http("POST", "/api/tradecase/messages", dict(schema_version=1, event_id=uuid4().hex, source_id="TC03.SAP",
            warehouse_id=w, document_id=document, version=1, occurred_at=datetime.now(timezone.utc).isoformat(), payload=payload)))
    expect(200, http("PUT", f"/api/finished-goods/skus/{f['article']}/receiving-policy", dict(expected_version=1,
        marking_required=True, serialized_weight_boxes=False,
        profiles=[dict(system_code="CRPT", profile_code="TOBACCO", profile_version="TC03.FH", scan_mode="UNIT_OR_AGGREGATION")])))
    expect(200, http("PUT", path+"/site", dict(operation_id="FH.SITE."+tag, expected_version=0, source_id="TC03.SAP",
        active_skm="TC03.SKM", planning_source="SAP", enabled=True, reason="Factory hierarchy isolated receipt acceptance")))
    for owner in ("SNS", "BLC"):
        send(owner, dict(entity_type="OWNER", title=owner))
    send("A", dict(entity_type="SKU", title="Factory hierarchy A", wms_article_id=f["article"], units_per_box=10, permitted_mrc=["200"]))
    for cell, zone in ((f["receive"], "RECEIVE"), (f["storage"], "STORAGE"), (f["pick"], "PICK")):
        data = dict(operation_id="FH.CELL."+cell, expected_version=0, zone_kind=zone, reason="Factory hierarchy cell fixture")
        if zone == "PICK": data["owner_id"] = "SNS"
        expect(200, http("PUT", stock+"/cells/"+cell, data))
    codes = [dict(system_code="CRPT", profile_code="TOBACCO", code=f["gtin"]+tag[:3]+str(i).zfill(4)) for i in range(1, 11)]
    sscc, box1, box2 = f["pallet"], f["gtin"]+tag[:3]+"B001", f["gtin"]+tag[:3]+"B002"
    boxes = [(box1, range(1, 7)), (box2, range(7, 11))]
    failures = []
    # Wrong hierarchy is refused at import (box in two pallets) — nothing stored.
    try:
        xml_call("/api/integrations/sap/supply-orders", supply_xml(f, tag, codes, boxes, [(sscc, [box1, box2]), (sscc+"X", [box1])], "FH.BAD."+tag), 202)
        raise RuntimeError("a box in two pallets was accepted")
    except AssertionError:
        refused = CALLS[-1]
    assert refused["status"] in {400, 409, 422}, refused; failures.append(dict(case="box_in_two_pallets", status=refused["status"], result=refused["response"]))
    imported = xml_call("/api/integrations/sap/supply-orders", supply_xml(f, tag, codes, boxes, [(sscc, [box1, box2])], "FH.SUPPLY."+tag), 202)
    receipt_path = f"/api/receiving/supply-orders/{imported['order_id']}/pallets"
    pallet_scan = dict(system_code="CRPT", profile_code="TOBACCO", level="PALLET", code=sscc)
    body = dict(operation_id="FH.RECEIPT."+tag, line_number="1", pallet_identifier=sscc, quantity="10", supplier_batch="FH."+tag,
                expiry_date="2030-01-01", gross_weight="10", aggregations=[pallet_scan])
    for key, patch in [("unknown_sscc", dict(aggregations=[dict(pallet_scan, code="UNKNOWN.SSCC."+tag)])),
                       ("pallet_and_child_box", dict(aggregations=[pallet_scan, dict(pallet_scan, level="BOX", code=box1)])),
                       ("quantity", dict(quantity="9", gross_weight="9")),
                       ("one_box_only", dict(aggregations=[dict(pallet_scan, level="BOX", code=box1)]))]:
        status, result = http("POST", receipt_path, dict(body, operation_id=body["operation_id"]+"."+key, **patch))
        assert status in {409, 422}, (key, status, result); failures.append(dict(case=key, status=status, result=result))
    first = expect(201, http("POST", receipt_path, body))
    assert expect(201, http("POST", receipt_path, body)) == first  # exact replay: the same immutable receipt
    status, result = http("POST", receipt_path, dict(body, supplier_batch="FH.CHANGED."+tag))
    assert status == 409, (status, result); failures.append(dict(case="changed_replay", status=status, result=result))
    status, result = http("POST", receipt_path, dict(body, operation_id="FH.RECEIPT.AGAIN."+tag))
    assert status in {409, 422}, (status, result); failures.append(dict(case="second_receipt_same_sscc", status=status, result=result))
    send("SUPPLY", dict(entity_type="SUPPLY", wms_article_id=f["article"], sap_order_id=imported["order_id"], sap_line_id="1", sku_id="A",
        owner_id="SNS", mrc="200", pallet_identifier=sscc, supplier_batch="FH."+tag, expiry_date="2030-01-01", composition_source="SAP", codes=codes))
    bind_body = dict(operation_id="FH.BIND."+tag, supply_id="SUPPLY", expected_supply_version=1, scanned_pallet=sscc)
    status, result = http("POST", stock+"/bind", bind_body, f["actor"], f["password"])
    assert status == 403, (status, result); failures.append(dict(case="bind_without_owner_right", status=status, result=result))
    status, result = http("POST", f"/api/tradecase/warehouses/{w+1}/stock/bind", dict(bind_body, operation_id="FH.BIND.X."+tag))
    assert status in {403, 404, 409, 422}, (status, result); failures.append(dict(case="bind_other_warehouse", status=status, result=result))
    bind = expect(200, http("POST", stock+"/bind", bind_body))
    assert bind["bound_units"] == 10
    page = expect(200, http("GET", stock+"?pallet_identifier="+sscc+"&limit=100"))
    assert len(page["items"]) == 10 and all(x["owner_id"] == "SNS" and x["mrc"] == "200" and x["expiry_date"] == "2030-01-01" for x in page["items"])
    with oracle_connection() as conn:
        q = conn.cursor()
        q.execute("select count(*),sum(BASE_QTY)from RRL_WMS_RECEIPT_UNIT where CURRENT_UID=:p", p=sscc); units = q.fetchone(); assert units == (10, 10)
        q.execute("select AGG_LEVEL,count(*)from RRL_SAP_TRACE_AGG where ORDER_ID=:o group by AGG_LEVEL order by 1", o=imported["order_id"])
        stored = q.fetchall(); assert stored == [("BOX", 2), ("PALLET", 1)]
        q.execute("select AGG_LEVEL from RRL_WMS_RECEIPT_AGG where UID_PALLET=:p", p=sscc); assert q.fetchall() == [("PALLET",)]
        q.execute("select count(*)from RRL_STOCK_OPERATION where OPERATION_ID=:o and STATE='APPLIED'", o=body["operation_id"]); assert q.fetchone()[0] == 1
        q.execute("select count(*)from RRL_WMS_RECEIPT_CODE c join RRL_WMS_RECEIPT_UNIT u on u.UID_PALLET=c.UID_PALLET and u.UNIT_ID=c.UNIT_ID where u.CURRENT_UID=:p", p=sscc)
        assert q.fetchone()[0] == 10
        q.execute("select count(*)from user_objects where STATUS='INVALID'"); assert q.fetchone()[0] == 0
    return dict(status="PASS", warehouse_id=w, sscc=sscc, boxes=[box1, box2], supply_order=imported["order_id"], receipt=first,
                units=list(units), stored_nodes=stored, failures=failures,
                checks=["one SSCC scan receives BOX6+BOX4 = 10 units through the existing receipt", "each node stored with its expanded composition",
                        "wrong hierarchy, unknown SSCC, pallet+child box, wrong quantity, single box, changed replay and second receipt refused",
                        "exact replay returns the same receipt; one APPLIED operation", "bind keeps SNS/MRC 200/expiry; owner right and warehouse enforced"],
                limits=["Synthetic supplier XML through the existing gateway, not an external DESADV/API adapter or provider response",
                        "Regulatory confirmation of the boxes by the SKM is not part of this receipt"])


PROTECTED = {225837931}
STATE = OUT / "factory-hierarchy-state.json"


def save_state(state):
    STATE.write_text(json.dumps(state, indent=2, ensure_ascii=True, default=str), encoding="utf-8")


def plan_fixture():
    """Pick a tag whose warehouse id (the same formula as setup) is absent from every warehouse-keyed table checked here."""
    for _ in range(10):
        tag = uuid4().hex
        ware = 210000000 + int(tag[:6], 16)
        if ware in PROTECTED:
            continue
        with oracle_connection() as conn:
            q = conn.cursor()
            q.execute("""select (select count(*) from RRL_WARES where ID=:w)+(select count(*) from RRL_CELLS where WARE_ID=:w)
                +(select count(*) from RRL_TRADE_SITE where WARE_ID=:w)+(select count(*) from RRL_ACCESS_OBJECT where KIND='WAREHOUSE' and OBJECT_ID=to_char(:w))
                +(select count(*) from RUSERS where ID=:a or WARE_ID=:w) from dual""", w=ware, a="TC03"+tag[:8])
            if q.fetchone()[0] == 0:
                return tag, ware
    raise RuntimeError("No absent warehouse id found in 10 attempts")


if __name__ == "__main__":
    os.environ.setdefault("TRADECASE_ADMIN_USER", "admin")
    os.environ.setdefault("TRADECASE_ADMIN_PASSWORD", re.search(r"PASS=(\S+?)[`,)\s]", (ROOT/"AGENTS.md").read_text(encoding="utf-8"))[1])
    OUT.mkdir(parents=True, exist_ok=True)
    if STATE.exists():  # one isolated fixture per state file: never a second one after an earlier pass or failure
        print(json.dumps({"status": "REFUSED", "reason": "previous run state exists; inspect/clean it and move the file deliberately",
                          "state": json.loads(STATE.read_text(encoding="utf-8"))}))
        sys.exit(2)
    import live_stock_acceptance
    tag, ware = plan_fixture()
    state = {"phase": "PLANNED", "tag": tag[:8], "warehouse_id": ware, "planned_at": datetime.now(timezone.utc).isoformat()}
    save_state(state)
    f = None; report = dict(status="FAIL"); cleanup_error = None
    try:
        original = live_stock_acceptance.uuid4
        live_stock_acceptance.uuid4 = lambda: type("Tag", (), {"hex": tag})()  # setup derives the warehouse from this exact tag
        try:
            f = setup()
        finally:
            live_stock_acceptance.uuid4 = original
        assert f["warehouse_id"] == ware and ware not in PROTECTED, (f["warehouse_id"], ware)
        state.update(phase="SETUP_DONE", actor=f["actor"], role=f["role"]); save_state(state)
        report.update(run(f))
        state.update(phase="RUN_DONE", run_status=report["status"]); save_state(state)
    except Exception as exc:
        report["error"] = str(exc); state.update(run_error=str(exc)); save_state(state); raise
    finally:
        if f:
            try:
                with oracle_connection() as conn:
                    q = conn.cursor()
                    q.execute("update RUSERS set DELETED=1 where ID=:a and USER_GROUP='TC03QA'", a=f["actor"])
                    q.execute("update RRL_ACCESS_ASSIGNMENT set REVOKED_AT=systimestamp where ASSIGNMENT_ID=:r", r=f["role"])
                    q.execute("select LOG_ID,ELAPSED_MS,OPERATION_KIND from RRL_SQL_SLOW_LOG where LOG_ID>:n order by LOG_ID fetch first 30 rows only", n=f["slow_marker"])
                    report["slow_sql"] = [list(x) for x in q]; conn.commit()
                state["phase"] = "CLEANED"
            except Exception as exc:  # a failed cleanup is a failed run, never hidden behind PASS
                cleanup_error = str(exc); report["status"] = "FAIL_CLEANUP"; report["cleanup_error"] = cleanup_error
                state.update(phase="CLEANUP_FAILED", cleanup_error=cleanup_error)
            report["fixture"] = {k: v for k, v in f.items() if k != "password"}
        save_state(state)
        report["http"] = CALLS; report["state"] = state
        (OUT/("factory-hierarchy-"+str(ware)+".json")).write_text(json.dumps(report, indent=2, ensure_ascii=True, default=str), encoding="utf-8")
        print(json.dumps({k: v for k, v in report.items() if k not in {"http", "fixture", "failures", "receipt"}}))
    if cleanup_error:
        sys.exit(3)
