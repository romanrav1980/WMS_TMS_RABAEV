"""One extra own unit: role-only quarantine, release of good stock, then posted QA disposal."""
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import secrets
import sys
from uuid import uuid4
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT), str(ROOT / "scripts"), str(ROOT / "tests/tradecase")]
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment()
from tools.mcp.tms_mcp_server import oracle_connection
from live_stock_acceptance import fields, xml_call
from live_document_acceptance import http, expect, CALLS

OUT = ROOT / "runtime/test-evidence/tradecase/2026-10-23/T11"
FILE = OUT / "quality-release-scope.json"
state = json.loads(FILE.read_text(encoding="utf-8")) if FILE.exists() else dict(status="RUNNING", checks=[])
f = json.loads(OUT.joinpath("quality-posting-live.json").read_text(encoding="utf-8"))["fixture"]
BASE = f"/api/tradecase/warehouses/{f['warehouse_id']}"
UID, PREFIX = "Q23.GOOD." + f["tag"], "Q23.GOOD." + f["tag"]
ACTOR, PASSWORD = "QG23" + uuid4().hex[:10], secrets.token_hex(24)
os.environ["TRADECASE_ADMIN_USER"], os.environ["TRADECASE_ADMIN_PASSWORD"] = "admin", "admin123"


def save():
    FILE.write_text(json.dumps(state, indent=2, default=str), encoding="utf-8")


def step(key, path, body, status=200, worker=False):
    if key not in state:
        state[key] = expect(status, http("POST", path, body, ACTOR if worker else "admin", PASSWORD if worker else "admin123")); save()
    return state[key]


def receipt():
    if "supply" not in state:
        doc = ET.Element("WarehouseSupplyOrder", version="1")
        fields(doc, dict(Sender="TC03.QA.SAP", MessageId=PREFIX, OrderNumber=PREFIX, Revision=1, WarehouseId=f["warehouse_id"], ReceiveCell=f["receive"], Supplier="Own release QA"))
        line = ET.SubElement(ET.SubElement(doc, "Lines"), "Line"); fields(line, dict(LineNumber="1", Material=f["article"]))
        ET.SubElement(line, "Quantity", unit="EA").text = "1"
        state["supply"] = xml_call("/api/integrations/sap/supply-orders", doc, 202); save()
    code = dict(system_code="CRPT", profile_code="TOBACCO", code=f["gtin"] + f["tag"][:3] + "9003")
    r = step("receipt", f"/api/receiving/supply-orders/{state['supply']['order_id']}/pallets", dict(operation_id=PREFIX + ".receive", line_number="1", pallet_identifier=UID, quantity="1", supplier_batch=PREFIX, expiry_date="2030-01-01", gross_weight="1", units=[dict(unit_id="3", quantity="1", codes=[code])]), status=201)
    step("attributes", "/api/tradecase/messages", dict(schema_version=1, event_id=PREFIX + ".attributes", source_id="TC03.SAP", warehouse_id=f["warehouse_id"], document_id="GOODSUPPLY", version=1, occurred_at=datetime.now(timezone.utc).isoformat(), payload=dict(entity_type="SUPPLY", wms_article_id=f["article"], sap_order_id=state["supply"]["order_id"], sap_line_id="1", sku_id="A", owner_id="SNS", mrc="200", pallet_identifier=UID, supplier_batch=PREFIX, expiry_date="2030-01-01", composition_source="SAP", codes=[code])))
    step("bound", BASE + "/stock/bind", dict(operation_id=PREFIX + ".bind", supply_id="GOODSUPPLY", expected_supply_version=1, scanned_pallet=UID))
    step("putaway", f"/api/receiving/putaway/{r['task_id']}/complete", dict(scanned_pallet=UID, scanned_from_cell=f["receive"], scanned_to_cell=r["putaway_cell"]))


def worker():
    with oracle_connection() as c:
        q = c.cursor(); q.execute("insert into RUSERS(ID,PASS,NAME,USER_GROUP,WARE_ID,DELETED,PRAVO_ADMIN_LOGIN)values(:a,:p,'Role-only quarantine QA','TC03QA',:w,0,1)", a=ACTOR, p=PASSWORD, w=f["warehouse_id"])
        q.execute("insert into RRL_ACCESS_ROLE(ROLE_ID,TITLE,ACTIVE,VERSION_NO)values(:a,'Role-only quarantine QA',1,1)", a=ACTOR)
        for permission in ("tradecase_view", "quarantine_move", "internal_move", "tradecase_quality_control", "tradecase_quality_approve", "tradecase_quality_post"):
            q.execute("insert into RRL_ACCESS_ROLE_RIGHT(ROLE_ID,PERMISSION)values(:a,:p)", a=ACTOR, p=permission)
        q.execute("insert into RRL_ACCESS_ASSIGNMENT(ASSIGNMENT_ID,USERNAME,ROLE_ID,SCOPE_KIND,SCOPE_ID,MEMBERSHIP,VALID_FROM,VALID_UNTIL,ASSIGNED_BY,REASON,VERSION_NO)values(:a,:a,:a,'WAREHOUSE',:w,'CURRENT',systimestamp-interval '1'minute,systimestamp+interval '1'hour,'admin','Role-only quarantine QA',1)", a=ACTOR, w=str(f["warehouse_id"]))
        q.execute("select RRL_HAS_WRIGHT(:a,'QUARANTINE_MOVE'),RRL_HAS_WRIGHT(:a,'INTERNAL_MOVE')from dual", a=ACTOR); assert q.fetchone() == (0, 0)
        c.commit()
    return expect(200, http("PUT", BASE + "/stock/owner-grants", dict(operation_id=ACTOR + ".grant", expected_version=0, username=ACTOR, owner_id="SNS", can_view=True, can_operate=True, reason="Own release scope QA"), "admin", "admin123"))["version"]


def run():
    path = BASE + "/exceptions"; reason = "Own release scope QA"
    def move(key, cell):
        return step(key, path + "/quarantine-moves", dict(operation_id=ACTOR + "." + key, pallet_uid=UID, target_cell=cell, reason=reason), worker=True)
    def case(key, action, **values):
        return step(key, path + "/cases", dict(operation_id=ACTOR + "." + key, action=action, **values), worker=True)
    move("quarantine", "Q23." + f["tag"])
    opened = case("good_open", "OPEN", pallet_uid=UID, reason=reason)
    released = case("good_release", "DECIDE", case_id=opened["case_id"], expected_version=opened["version"], decision="RELEASED", note=reason)
    assert released["state"] == "RELEASED"
    move("released_move", f["storage"])
    state["checks"] = ["Role-only worker with zero legacy move rights moves the whole pallet into quarantine", "Scoped controller releases a good pallet and worker moves it back"]
    move("cleanup_quarantine", "Q23." + f["tag"])
    opened = case("cleanup_open", "OPEN", pallet_uid=UID, reason="Dispose own synthetic QA unit")
    defect = case("cleanup_defect", "DECIDE", case_id=opened["case_id"], expected_version=opened["version"], decision="DEFECT", note=reason)
    approved = case("cleanup_approve", "APPROVE", case_id=opened["case_id"], expected_version=defect["version"], note=reason)
    body = dict(operation_id=ACTOR + ".writeoff", case_id=opened["case_id"], expected_version=approved["version"])
    posted = step("cleanup_post", path + "/write-offs", body, worker=True)
    assert expect(200, http("POST", path + "/write-offs", body, ACTOR, PASSWORD)) == posted
    state["checks"].append("Role-only posted write-off and same-actor exact replay; own extra unit consumed")
    with oracle_connection() as c:
        q = c.cursor(); q.execute("select nvl(sum(REMAIN),0),nvl(sum(HARD_RESERVED_BASE),0)from RRL_REMAINS where UID_POLETA=:u", u=UID); assert q.fetchone() == (0, 0)
    state.update(status="PASS"); state.pop("error", None)


if __name__ == "__main__":
    grant_version = None
    try:
        receipt(); grant_version = worker(); run()
    except Exception as exc:
        state.update(status="FAIL", error=str(exc)); raise
    finally:
        if grant_version is not None:
            expect(200, http("PUT", BASE + "/stock/owner-grants", dict(operation_id=ACTOR + ".revoke", expected_version=grant_version, username=ACTOR, owner_id="SNS", can_view=False, can_operate=False, reason="Own QA completed or failed"), "admin", "admin123"))
        with oracle_connection() as c:
            q = c.cursor(); q.execute("update RUSERS set DELETED=1 where ID=:a", a=ACTOR)
            q.execute("update RRL_ACCESS_ASSIGNMENT set REVOKED_AT=systimestamp where ASSIGNMENT_ID=:a", a=ACTOR); c.commit()
        state.update(qa_retired=True, last_actor=ACTOR, pallet_uid=UID)
        state["http"] = state.get("http", []) + CALLS; save()
    print(json.dumps(dict(status=state["status"], checks=len(state["checks"]), evidence=str(FILE))))
