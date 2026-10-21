"""Fresh TRADECASE receipt via one sender BOX scan; no synthetic inventory DML."""
from copy import deepcopy
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

OUT = ROOT / "runtime/test-evidence/tradecase/2026-10-21/T03"


def split_box(f, receipt, units, codes):
    """Exercise the existing physical coordinator, not a second BOX quantity ledger."""
    w, tag = f["warehouse_id"], f["tag"]
    base = f"/api/tradecase/warehouses/{w}/stock"
    expect(200, http("POST", f"/api/receiving/putaway/{receipt['task_id']}/complete", dict(
        scanned_pallet=f["pallet"], scanned_from_cell=f["receive"], scanned_to_cell=receipt["putaway_cell"])))
    expect(200, http("PUT", base+"/cells/"+f["receive"], dict(operation_id="BOX.SORT.CELL."+tag,
        expected_version=1, zone_kind="SORT", reason="Empty original receiving cell used for isolated split")))
    with oracle_connection() as conn:
        conn.cursor().execute("insert into RRL_ACCESS_ROLE_RIGHT(ROLE_ID,PERMISSION)values(:r,'tradecase_stock_sort')", r=f["role"])
        conn.commit()
    expect(200, http("PUT", base+"/owner-grants", dict(operation_id="BOX.SORT.GRANT."+tag, expected_version=0,
        username=f["actor"], owner_id="SNS", can_view=True, can_operate=True, reason="Factory box isolated owner scoped split")))
    body = dict(operation_id="BOX.SPLIT."+tag, source_pallet=f["pallet"], source_cell=receipt["putaway_cell"],
                target_cell=f["receive"], scans=codes[:3])
    expect(409, http("POST", base+"/sort", dict(body, operation_id=body["operation_id"]+".PENDING"), f["actor"], f["password"]))
    confirmation = dict(operation_id="BOX.MARK."+tag, skm_id="TC03.SKM", external_event_id="BOX.SKM."+tag,
        expected_site_version=1, occurred_at=datetime.now(timezone.utc).isoformat(),
        items=[dict(physical_unit_key=u["physical_unit_key"], expected_attribute_version=u["attribute_version"], verdict="VALID") for u in units])
    expect(200, http("POST", base+"/mark-confirmations", confirmation))
    result = expect(200, http("POST", base+"/sort", body, f["actor"], f["password"]))
    assert result["base_quantity"] == "3" and result["regulatory_composition_status"] == "PENDING"
    assert expect(200, http("POST", base+"/sort", body, f["actor"], f["password"])) == result
    changed = dict(body, scans=codes[:2]);expect(409, http("POST", base+"/sort", changed, f["actor"], f["password"]))
    with oracle_connection() as conn:
        q = conn.cursor()
        q.execute("select r.UID_POLETA,r.CELL,r.REMAIN,r.HARD_RESERVED_BASE from RRL_REMAINS r join RRL_CELLS c on c.CELL=r.CELL where c.WARE_ID=:w and r.REMAIN>0 order by r.REMAIN", w=w)
        stock = [list(x) for x in q];assert [x[2] for x in stock] == [3, 7]
        q.execute("select u.CURRENT_UID,count(*),sum(u.BASE_QTY),count(distinct a.OWNER_ID)from RRL_WMS_RECEIPT_UNIT u join RRL_TRADE_STOCK_ATTR a on a.PHYSICAL_UNIT_KEY=u.PHYSICAL_UNIT_KEY where a.CAPTURE_WARE_ID=:w group by u.CURRENT_UID order by count(*)", w=w)
        assert [tuple(x[1:]) for x in q] == [(3, 3, 1), (7, 7, 1)]
    expect(200, http("PUT", base+"/owner-grants", dict(operation_id="BOX.SORT.REVOKE."+tag, expected_version=1,
        username=f["actor"], owner_id="SNS", can_view=True, can_operate=False, reason="Verify owner scope on cached split result")))
    expect(403, http("POST", base+"/sort", body, f["actor"], f["password"]))
    return dict(status="PASS", stock=stock, result=result, checks=["PENDING codes block split", "synthetic SKM confirms ten",
        "three scanned pieces moved once, seven remain", "owner unchanged; exact replay; changed content/revoked owner rejected"],
        limits="Physical 3+7 are not two externally confirmed BOX aggregates; their composition response remains pending")


def run(f):
    w, tag = f["warehouse_id"], f["tag"]
    path = f"/api/tradecase/warehouses/{w}"
    stock = path + "/stock"
    def send(key, payload):
        return expect(200, http("POST", "/api/tradecase/messages", dict(schema_version=1, event_id=uuid4().hex,
            source_id="TC03.SAP", warehouse_id=w, document_id=key, version=1,
            occurred_at=datetime.now(timezone.utc).isoformat(), payload=payload)))
    expect(200, http("PUT", f"/api/finished-goods/skus/{f['article']}/receiving-policy", dict(expected_version=1,
        marking_required=True, serialized_weight_boxes=False,
        profiles=[dict(system_code="CRPT", profile_code="TOBACCO", profile_version="TC03.BOX", scan_mode="BOX")])))
    expect(200, http("PUT", path+"/site", dict(operation_id="BOX.SITE."+tag, expected_version=0, source_id="TC03.SAP",
        active_skm="TC03.SKM", planning_source="SAP", enabled=True, reason="Factory box isolated receipt acceptance")))
    send("SNS", dict(entity_type="OWNER", title="SNS"))
    send("A", dict(entity_type="SKU", title="Factory box A", wms_article_id=f["article"], units_per_box=10, permitted_mrc=["200"]))
    for cell, zone in [(f["receive"], "RECEIVE"), (f["storage"], "STORAGE"), (f["pick"], "PICK")]:
        data = dict(operation_id="BOX.CELL."+cell, expected_version=0, zone_kind=zone, reason="Factory box cell fixture")
        if zone == "PICK":data["owner_id"] = "SNS"
        expect(200, http("PUT", stock+"/cells/"+cell, data))
    codes = [dict(system_code="CRPT", profile_code="TOBACCO", code=f["gtin"]+tag[:3]+str(i).zfill(4)) for i in range(1, 11)]
    box_code = f["gtin"]+tag[:3]+"B001"
    supply = ET.Element("WarehouseSupplyOrder", version="1")
    fields(supply, dict(Sender="TC03.QA.SAP", MessageId="BOX.SUPPLY."+tag, OrderNumber="BOX."+tag,
        Revision=1, WarehouseId=w, ReceiveCell=f["receive"], Supplier="Factory fixture"))
    line = ET.SubElement(ET.SubElement(supply, "Lines"), "Line")
    fields(line, dict(LineNumber="1", Material=f["article"]));ET.SubElement(line, "Quantity", unit="EA").text = "10"
    agg = ET.SubElement(ET.SubElement(supply, "Aggregations"), "Aggregation")
    fields(agg, dict(LineNumber="1", System="CRPT", Profile="TOBACCO", Level="BOX", Code=box_code))
    members = ET.SubElement(agg, "Units")
    for i, code in enumerate(codes, 1):
        fields(ET.SubElement(members, "Unit"), dict(UnitId=str(i), Quantity="1", Code=code["code"]))
    imported = xml_call("/api/integrations/sap/supply-orders", supply, 202)
    receipt_path = f"/api/receiving/supply-orders/{imported['order_id']}/pallets"
    body = dict(operation_id="BOX.RECEIPT."+tag, line_number="1", pallet_identifier=f["pallet"], quantity="10",
        supplier_batch="BOX."+tag, expiry_date="2030-01-01", gross_weight="10",
        aggregations=[dict(system_code="CRPT", profile_code="TOBACCO", level="BOX", code=box_code)])
    failures = []
    for key, patch in [
        ("unknown", dict(aggregations=[dict(body["aggregations"][0], code="UNKNOWN.BOX."+tag)])),
        ("quantity", dict(quantity="9")),
        ("duplicate", dict(aggregations=body["aggregations"]*2)),
        ("unit_scan", dict(aggregations=[], units=[dict(unit_id=str(i), quantity="1", codes=[code]) for i, code in enumerate(codes, 1)])),
    ]:
        value = dict(body, operation_id=body["operation_id"]+"."+key, **patch)
        status, result = http("POST", receipt_path, value)
        assert status in {409, 422}, (key, status, result)
        failures.append(dict(case=key, status=status, result=result))
    first = expect(201, http("POST", receipt_path, body))
    duplicate = expect(201, http("POST", receipt_path, body))
    assert duplicate == first  # Exact native receipt is immutable, including its original flag.
    send("SUPPLY", dict(entity_type="SUPPLY", wms_article_id=f["article"], sap_order_id=imported["order_id"],
        sap_line_id="1", sku_id="A", owner_id="SNS", mrc="200", pallet_identifier=f["pallet"],
        supplier_batch="BOX."+tag, expiry_date="2030-01-01", composition_source="SAP", codes=codes))
    bind = expect(200, http("POST", stock+"/bind", dict(operation_id="BOX.BIND."+tag, supply_id="SUPPLY",
        expected_supply_version=1, scanned_pallet=f["pallet"])))
    assert bind["bound_units"] == 10 and bind["mark_state"] == "PENDING"
    page = expect(200, http("GET", stock+"?pallet_identifier="+f["pallet"]+"&limit=100"))
    assert len(page["items"]) == 10 and all(x["base_quantity"] == "1" and x["owner_id"] == "SNS" for x in page["items"])
    with oracle_connection() as conn:
        q = conn.cursor()
        q.execute("select sum(REMAIN),sum(HARD_RESERVED_BASE)from RRL_REMAINS r join RRL_CELLS c on c.CELL=r.CELL where c.WARE_ID=:w", w=w)
        physical = list(q.fetchone());assert physical == [10, 0]
        q.execute("select count(*),sum(BASE_QTY)from RRL_WMS_RECEIPT_UNIT where CURRENT_UID=:p", p=f["pallet"])
        assert q.fetchone() == (10, 10)
        q.execute("select count(*)from RRL_STOCK_OPERATION where OPERATION_ID=:o and STATE='APPLIED'", o=body["operation_id"])
        assert q.fetchone()[0] == 1
        q.execute("select AGG_LEVEL from RRL_WMS_RECEIPT_AGG where UID_PALLET=:p", p=f["pallet"])
        assert q.fetchall() == [("BOX",)]
        q.execute("select count(*)from user_objects where STATUS='INVALID'");assert q.fetchone()[0] == 0
    split = split_box(f, first, page["items"], codes)
    return dict(status="PASS", warehouse_id=w, pallet=f["pallet"], article=f["article"], box_code=box_code, split=split,
        physical=physical, failures=failures, codes=codes, supply_order=imported["order_id"],
        checks=["one source BOX scan expands exactly ten pieces", "unknown/quantity/duplicate/unit-only scan rejected",
                "native receipt exact replay does not double units/tasks", "same ten legal attributes; pending regulatory confirmation"],
        limits=["Factory composition is synthetic XML, not an external provider response", "Nested pallet/box tree, FULL_PAL and outgoing reaggregation not tested; physical split is not regulatory BOX confirmation"])


if __name__ == "__main__":
    os.environ.setdefault("TRADECASE_ADMIN_USER", "admin")
    os.environ.setdefault("TRADECASE_ADMIN_PASSWORD", re.search(r"PASS=(\S+?)[`,)\s]", (ROOT/"AGENTS.md").read_text(encoding="utf-8"))[1])
    OUT.mkdir(parents=True, exist_ok=True)
    f = None;report = dict(status="FAIL")
    try:
        f = setup();report.update(run(f))
    except Exception as exc:
        report["error"] = str(exc);raise
    finally:
        if f:
            with oracle_connection() as conn:
                q = conn.cursor()
                q.execute("update RUSERS set DELETED=1 where ID=:a and USER_GROUP='TC03QA'", a=f["actor"])
                q.execute("update RRL_ACCESS_ASSIGNMENT set REVOKED_AT=systimestamp where ASSIGNMENT_ID=:r", r=f["role"])
                q.execute("select LOG_ID,ELAPSED_MS,OPERATION_KIND from RRL_SQL_SLOW_LOG where LOG_ID>:n order by LOG_ID fetch first 30 rows only", n=f["slow_marker"])
                report["slow_sql"] = [list(x) for x in q];conn.commit()
            report["fixture"] = {k: v for k, v in f.items() if k != "password"}
        report["http"] = CALLS
        (OUT/("factory-box-"+str(f["warehouse_id"] if f else uuid4().hex)+".json")).write_text(json.dumps(report, indent=2, ensure_ascii=True, default=str), encoding="utf-8")
    print(json.dumps({k: v for k, v in report.items() if k not in {"http", "fixture", "codes", "failures"}}))
