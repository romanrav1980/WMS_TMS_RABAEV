"""Isolated marked receipt -> quarantine -> quality decision -> real write-off over HTTP."""
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import sys
from uuid import uuid4
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT), str(ROOT / "scripts"), str(ROOT / "tests/tradecase")]
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment()
from live_stock_acceptance import setup, fields, xml_call
from live_document_acceptance import http, expect, CALLS
from tools.mcp.tms_mcp_server import oracle_connection

OUT = ROOT / "runtime/test-evidence/tradecase/2026-10-23/T11"
OUT.mkdir(parents=True, exist_ok=True)
FILE = OUT / "quality-posting-live.json"
state = json.loads(FILE.read_text(encoding="utf-8")) if FILE.exists() else dict(status="RUNNING", checks=[])
os.environ["TRADECASE_ADMIN_USER"], os.environ["TRADECASE_ADMIN_PASSWORD"] = "admin", "admin123"


def save():
    FILE.write_text(json.dumps(state, indent=2, default=str), encoding="utf-8")


def step(key, path, body, method="POST", status=200):
    if key not in state:
        state[key] = expect(status, http(method, path, body)); save()
    return state[key]


def prepare():
    if "fixture" not in state:
        f = setup(); state["fixture"] = {k: v for k, v in f.items() if k != "password"}; save()
    f = state["fixture"]; w, tag = f["warehouse_id"], f["tag"]; base = f"/api/tradecase/warehouses/{w}"
    step("site", base + "/site", dict(operation_id="Q23.site." + tag, expected_version=0, source_id="TC03.SAP", active_skm="TC03.SKM", planning_source="SAP", enabled=True, reason="Isolated quality acceptance"), "PUT")
    def send(key, payload):
        return step(key, "/api/tradecase/messages", dict(schema_version=1, event_id="Q23." + tag + key, source_id="TC03.SAP", warehouse_id=w, document_id=key, version=1, occurred_at=datetime.now(timezone.utc).isoformat(), payload=payload))
    send("SNS", dict(entity_type="OWNER", title="SNS"))
    send("A", dict(entity_type="SKU", title="Quality acceptance units", wms_article_id=f["article"], units_per_box=10, permitted_mrc=["200"]))
    for cell, zone in [(f["receive"], "RECEIVE"), (f["storage"], "STORAGE"), (f["pick"], "PICK")]:
        body = dict(operation_id="Q23.cell." + cell, expected_version=0, zone_kind=zone, reason="Isolated quality cell")
        if zone == "PICK": body["owner_id"] = "SNS"
        step("cell." + cell, base + "/stock/cells/" + cell, body, "PUT")
    if "supply" not in state:
        supply = ET.Element("WarehouseSupplyOrder", version="1")
        fields(supply, dict(Sender="TC03.QA.SAP", MessageId="Q23.SUPPLY." + tag, OrderNumber="Q23." + tag, Revision=1, WarehouseId=w, ReceiveCell=f["receive"], Supplier="Own quality QA"))
        line = ET.SubElement(ET.SubElement(supply, "Lines"), "Line"); fields(line, dict(LineNumber="1", Material=f["article"]))
        ET.SubElement(line, "Quantity", unit="EA").text = "2"
        state["supply"] = xml_call("/api/integrations/sap/supply-orders", supply, 202); save()
    units = [dict(unit_id=str(i), quantity="1", codes=[dict(system_code="CRPT", profile_code="TOBACCO", code=f["gtin"] + tag[:3] + str(i).zfill(4))]) for i in [1, 2]]
    received = step("receipt", f"/api/receiving/supply-orders/{state['supply']['order_id']}/pallets", dict(operation_id="Q23.receive." + tag, line_number="1", pallet_identifier=f["pallet"], quantity="2", supplier_batch="Q23." + tag, expiry_date="2030-01-01", gross_weight="2", units=units), status=201)
    send("SUPPLY", dict(entity_type="SUPPLY", wms_article_id=f["article"], sap_order_id=state["supply"]["order_id"], sap_line_id="1", sku_id="A", owner_id="SNS", mrc="200", pallet_identifier=f["pallet"], supplier_batch="Q23." + tag, expiry_date="2030-01-01", composition_source="SAP", codes=[u["codes"][0] for u in units]))
    step("bind", base + "/stock/bind", dict(operation_id="Q23.bind." + tag, supply_id="SUPPLY", expected_supply_version=1, scanned_pallet=f["pallet"]))
    step("putaway", f"/api/receiving/putaway/{received['task_id']}/complete", dict(scanned_pallet=f["pallet"], scanned_from_cell=f["receive"], scanned_to_cell=received["putaway_cell"]))
    quarantine = "Q23." + tag
    if "quarantine_cell" not in state:
        with oracle_connection() as c:
            q = c.cursor(); q.callproc("RRL_STOCK_CONFIG_API.begin_change", ["admin", "warehouse_settings_edit"])
            try:
                q.execute("insert into RRL_CELLS(CELL,WARE_ID,X,Y,Z,OTBOR,IS_SYSTEM,LIMIT_WEIGHT,LIMIT_HEIGHT,BLOCKED_FOR_REMAINS)values(:c,:w,0,0,0,0,0,0,0,1)", c=quarantine, w=w)
                q.execute("insert into RRL_STOCK_POLICY_GUARD(POLICY_KEY,LOCK_ID)select RRL_STOCK_LOCK_API.resource_key('CELL',:c),nvl(max(LOCK_ID),900000000)+1 from RRL_STOCK_POLICY_GUARD", c=quarantine)
                q.callproc("RRL_STOCK_CONFIG_API.end_change"); c.commit()
            except BaseException:
                c.rollback(); q.callproc("RRL_STOCK_CONFIG_API.end_change"); raise
        state["quarantine_cell"] = quarantine; save()
    step("cell.Q", base + "/stock/cells/" + quarantine, dict(operation_id="Q23.policy." + tag, expected_version=0, zone_kind="STORAGE", reason="Quarantine location metadata"), "PUT")
    return f, base + "/exceptions"


def run(f, path):
    tag = f["tag"]; reason = "Own quality acceptance"
    move = dict(operation_id="Q23.move." + tag, pallet_uid=f["pallet"], target_cell=state["quarantine_cell"], reason=reason)
    step("quarantine", path + "/quarantine-moves", move)
    opened = step("open", path + "/cases", dict(operation_id="Q23.open." + tag, action="OPEN", pallet_uid=f["pallet"], reason=reason))
    assert expect(200, http("POST", path + "/cases", dict(operation_id="Q23.open." + tag, action="OPEN", pallet_uid=f["pallet"], reason=reason)))["case_id"] == opened["case_id"]
    state["blocked_release"] = expect(409, http("POST", path + "/quarantine-moves", dict(move, operation_id="Q23.blocked." + tag, target_cell=f["storage"]))); save()
    defect = step("defect", path + "/cases", dict(operation_id="Q23.defect." + tag, action="DECIDE", case_id=opened["case_id"], expected_version=opened["version"], decision="DEFECT", note=reason))
    approved = step("approved", path + "/cases", dict(operation_id="Q23.approve." + tag, action="APPROVE", case_id=opened["case_id"], expected_version=defect["version"], note=reason))
    assert approved["state"] == "WAITING_POSTING"
    body = dict(operation_id="Q23.post." + tag, case_id=opened["case_id"], expected_version=approved["version"])
    posted = step("posted", path + "/write-offs", body)
    assert expect(200, http("POST", path + "/write-offs", body)) == posted
    detail = expect(200, http("GET", path + "/cases/" + str(opened["case_id"]))); assert detail["state"] == "POSTED"
    with oracle_connection() as c:
        q = c.cursor(); q.execute("select nvl(sum(REMAIN),0),nvl(sum(HARD_RESERVED_BASE),0)from RRL_REMAINS where UID_POLETA=:u", u=f["pallet"]); assert q.fetchone() == (0, 0)
        q.execute("select STOCK_STATUS,count(*)from RRL_WMS_RECEIPT_UNIT where CURRENT_UID=:u group by STOCK_STATUS", u=f["pallet"]); state["units_after"] = [list(r) for r in q]
        assert state["units_after"] == [["ISSUED", 2]]
        q.execute("select count(*)from RRL_SAP_RECEIPT_OUTBOX where EVENT_TYPE='TRADE_QUALITY_WRITTEN_OFF'and json_value(PAYLOAD_JSON,'$.operation_id')=:op", op=body["operation_id"]); assert q.fetchone() == (1,)
        q.execute("select HOLD_STATUS from RRL_QUALITY_HOLD where QUALITY_HOLD_ID=:h", h=opened["quality_hold_id"]); state["hold_after"] = q.fetchone()[0]; assert state["hold_after"] != "ACTIVE"
        q.execute("select count(*)from USER_OBJECTS where STATUS='INVALID'"); assert q.fetchone() == (0,)
    state["detail_after"] = detail
    state["checks"] = ["Actual marked receipt2 and native putaway/quarantine", "Controller decision and approval do not write stock off", "Active case refuses release", "Native write-off consumes2 exact units and releases hold", "One outgoing document and exact replay"]
    state["status"] = "PASS"; state.pop("error", None)


if __name__ == "__main__":
    try:
        f, path = prepare(); run(f, path)
    except Exception as exc:
        state.update(status="FAIL", error=str(exc)); raise
    finally:
        if "fixture" in state:
            f = state["fixture"]
            with oracle_connection() as c:
                q = c.cursor(); q.execute("update RUSERS set DELETED=1 where ID=:a and USER_GROUP='TC03QA'", a=f["actor"])
                q.execute("update RRL_ACCESS_ASSIGNMENT set REVOKED_AT=coalesce(REVOKED_AT,systimestamp)where ASSIGNMENT_ID=:a", a=f["role"]); c.commit()
                q.execute("select LOG_ID,ELAPSED_MS,OPERATION_KIND from RRL_SQL_SLOW_LOG where LOG_ID>:m order by ELAPSED_MS desc fetch first 8 rows only", m=f["slow_marker"])
                state["slow_sql"] = [list(r) for r in q]
            state["qa_retired"] = True
        state["http"] = state.get("http", []) + CALLS; save()
    print(json.dumps(dict(status=state["status"], checks=len(state["checks"]), evidence=str(FILE))))
