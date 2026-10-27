"""C-0175 live check: order lines in pieces/blocks/boxes/kg normalized once at TRADECASE document intake. The CURRENT application code
runs in-process (FastAPI TestClient, ASGI) against real Oracle, because the shared API 8088 is restarted only by root; this is not a
served-8088 measurement. Own new warehouse and own ARTMAS article (box 12, block BLK 10, no KG coefficient); no stock is created.
--after-kit: the zero / missing-coefficient lines, TRIP refusal and binding skip that need db/migrations/2026-10-27_trade_order_units."""
from datetime import datetime, timedelta, timezone
from decimal import Decimal
import json
import os
from pathlib import Path
import re
import secrets
import sys
import time
from uuid import uuid4
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT), str(ROOT / "scripts"), str(ROOT / "api/wms_api_server"), str(Path(__file__).parent)]
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment()
from fastapi.testclient import TestClient
from app.main import app
from tools.mcp.tms_mcp_server import oracle_connection
from live_stock_acceptance import fields, ean

OUT = ROOT / "runtime/test-evidence/tradecase/2026-10-27/C0175"
AFTER_KIT = "--after-kit" in sys.argv
PASSWORD = re.search(r"PASS=(\S+?)[`,)\s]", (ROOT / "AGENTS.md").read_text(encoding="utf-8"))[1]
client = TestClient(app)
report = dict(status="FAIL", mode="ASGI in-process current code + real Oracle (not served 8088)", after_kit=AFTER_KIT, checks=[], calls=[])


def save():
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / ("order-units" + ("-after-kit" if AFTER_KIT else "") + ".json")).write_text(json.dumps(report, indent=1, ensure_ascii=False, default=str), encoding="utf-8")


def call(method, path, body=None, status=200, auth=None, raw=None, headers=None):
    start = time.perf_counter()
    r = client.request(method, path, json=body if raw is None else None, content=raw, headers=headers, auth=auth or ("admin", PASSWORD))
    value = r.json() if r.content else None
    report["calls"].append(dict(method=method, path=path, status=r.status_code, ms=round((time.perf_counter() - start) * 1000, 1), result=value))
    assert r.status_code == status, (r.status_code, value)
    return value


def db(sql, **binds):
    with oracle_connection() as c:
        q = c.cursor(); q.execute(sql, binds)
        return [tuple(x.read() if hasattr(x, "read") else x for x in row) for row in q.fetchall()]


def run():
    tag = uuid4().hex; ware = 210000000 + int(tag[:6], 16); article = "TC75" + tag[:8].upper(); t = "OU27." + tag[:8]
    assert db("""select (select count(*) from RRL_WARES where ID=:w)+(select count(*) from RRL_TRADE_SITE where WARE_ID=:w)
        +(select count(*) from RRL_ACCESS_OBJECT where KIND='WAREHOUSE' and OBJECT_ID=to_char(:w))+(select count(*) from RRL_ARTICULS where ACTICUL=:a) from dual""", w=ware, a=article)[0][0] == 0
    report.update(warehouse=ware, article=article, tag=t); save()
    # Own article through the existing ARTMAS writer: base EA, box 12, block BLK 10 (published to RRL_STOCK_UOM_CONVERSION).
    gtin = ean("291" + str(int(tag, 16)).zfill(10)[-10:])
    doc = ET.Element("ARTMAS10"); idoc = ET.SubElement(doc, "IDOC"); control = ET.SubElement(idoc, "EDI_DC40")
    fields(control, dict(MESTYP="ARTMAS", IDOCTYP="ARTMAS10", DOCNUM=str(2000000000000000 + int(tag[:12], 16)), SNDPRN="TC03.QA.SAP", CREDAT="20261027", CRETIM="100000"))
    for segment, values in [("E1BPE1MATHEAD", {}), ("E1BPE1MARART", dict(BASE_UOM="EA", EAN_UPC=gtin)), ("E1BPE1MAKTRT", dict(LANGU_ISO="EN", MATL_DESC="C-0175 QA " + tag[:8])),
                            ("E1BPE1MARMRT", dict(ALT_UNIT="EA", NUMERATOR=1, DENOMINATR=1, EAN_UPC=gtin)),
                            ("E1BPE1MARMRT", dict(ALT_UNIT="BOX", NUMERATOR=12, DENOMINATR=1, EAN_UPC=ean("292" + gtin[3:13]))),
                            ("E1BPE1MARMRT", dict(ALT_UNIT="BLK", NUMERATOR=10, DENOMINATR=1, EAN_UPC=ean("293" + gtin[3:13])))]:
        fields(ET.SubElement(idoc, segment), dict(MATERIAL=article, **values))
    call("POST", "/api/integrations/sap/artmas", raw=ET.tostring(doc, encoding="utf-8"), headers={"Content-Type": "application/xml"}, status=202)
    report["registry"] = [list(r) for r in db("select INPUT_UOM,NUMERATOR,DENOMINATOR,BASE_UOM,POLICY_VERSION from RRL_STOCK_UOM_CONVERSION where ARTICUL=:a order by INPUT_UOM", a=article)]
    with oracle_connection() as c:
        q = c.cursor(); q.callproc("RRL_STOCK_CONFIG_API.begin_change", ["admin", "warehouse_settings_edit"])
        try:
            q.execute("insert into RRL_WARES(ID,NAME,PREFIX)values(:w,:n,'OU')", w=ware, n="TRADECASE QA order units " + tag[:8])
            q.execute("update RRL_ARTICULS set COUNT_SHT_IN_KOR=12 where ACTICUL=:a", a=article); c.commit()
        finally:
            q.callproc("RRL_STOCK_CONFIG_API.end_change")
        q.execute("insert into RRL_ACCESS_OBJECT(KIND,OBJECT_ID,TITLE,ACTIVE,VERSION_NO)values('WAREHOUSE',:w,'C-0175 QA',1,1)", w=str(ware)); c.commit()
    save()
    now = datetime.now(timezone.utc)
    def send(kind, key, payload, version=1, event=None, status=200, auth=None):
        body = dict(schema_version=1, event_id=event or f"{t}.{kind}.{key}.{version}", source_id="TC03.SAP", warehouse_id=ware, document_id=key, version=version,
                    occurred_at=now.isoformat(), payload=dict(entity_type=kind, **payload))
        return call("POST", "/api/tradecase/messages", body, status=status, auth=auth), body
    call("PUT", f"/api/tradecase/warehouses/{ware}/site", dict(operation_id=t + ".site", expected_version=0, source_id="TC03.SAP", active_skm="TC03.SKM",
                                                                planning_source="SAP", enabled=True, reason="C-0175 order units"))
    send("OWNER", "SNS", dict(title="SNS"))
    sku = dict(title="C-0175 product", wms_article_id=article, units_per_box=12, permitted_mrc=["200"], processing_uom="BOX", processing_step="1", round_to_processing_unit=True)
    send("SKU", "A", sku)
    customer = call("POST", "/api/customers", dict(customer_code=t, customer_name="C-0175 store", customer_type="LEGAL_ENTITY"))["customer_id"]
    send("RECIPIENT", "C1", dict(title="Store", wms_customer_id=customer, target_owner_id="SNS", permitted_source_owners=["SNS"], buyout_mode="BEFORE_PICK",
                                 min_osg_days=0, lead_time_days=0, allow_broken_box=False))
    ship = (now + timedelta(days=1)).isoformat()
    def line(i, qty, uom):
        return dict(line_id=str(i), sku_id="A", source_owner_id="SNS", target_owner_id="SNS", mrc="200", quantity=qty, uom=uom, min_osg_days=0)
    def stored(key):
        value = db("select BODY_JSON from RRL_TRADE_DOCUMENT where WARE_ID=:w and ENTITY_TYPE='ORDER' and EXTERNAL_ID=:k", w=ware, k=key)[0][0]
        return value if isinstance(value, dict) else json.loads(value)
    # 1. Executable lines with rounding allowed: 25 EA -> 2 BOX (1 left), 5 BLK -> 4 BOX (2 left), 3 BOX exact.
    o2, o2_body = send("ORDER", "O2", dict(recipient_id="C1", planned_ship_at=ship, lines=[line(1, "25", "EA"), line(2, "5", "BLK"), line(3, "3", "BOX")]))
    body = stored("O2")
    got = [(x["quantity"], x["uom"], x["normalization"]["source_quantity"], x["normalization"]["source_uom"], x["normalization"]["base_difference"], x["normalization"]["status"], x["normalization"]["integration_error"]) for x in body["lines"]]
    report["o2"] = dict(result=o2, lines=got)
    assert got == [("2", "BOX", "25", "EA", "1", "ROUNDED_DOWN", False), ("4", "BOX", "5", "BLK", "2", "ROUNDED_DOWN", False), ("3", "BOX", "3", "BOX", "0", "EXACT", False)], got
    assert o2["loaded_with_integration_error"] is False and [x["status"] for x in o2["line_results"]] == ["ROUNDED_DOWN", "ROUNDED_DOWN", "EXACT"]
    report["checks"].append("25 EA -> 2 BOX (1 left), 5 BLK -> 4 BOX (2 left), 3 BOX exact; source and processed kept in the stored line")
    # 2. Rounding not allowed: 25 EA and 24 EA both load as 2 BOX with the integration error.
    sku2 = dict(sku, round_to_processing_unit=False); send("SKU", "A", sku2, 2)
    o3, _ = send("ORDER", "O3", dict(recipient_id="C1", planned_ship_at=ship, lines=[line(1, "25", "EA"), line(2, "24", "EA")]))
    got3 = [(x["quantity"], x["uom"], x["normalization"]["status"], x["normalization"]["error_code"]) for x in stored("O3")["lines"]]
    report["o3"] = dict(result=o3, lines=got3)
    assert got3 == [("2", "BOX", "ROUNDED_DOWN", "ORDER_UNIT_ROUNDING_NOT_ALLOWED"), ("2", "BOX", "CONVERTED", "ORDER_UNIT_ROUNDING_NOT_ALLOWED")] and o3["loaded_with_integration_error"] is True
    report["checks"].append("Rounding not allowed: 25 EA and 24 EA loaded as 2 BOX, each with ORDER_UNIT_ROUNDING_NOT_ALLOWED; message accepted, not rejected")
    # 3. Exact replay of O2 after the SKU setting changed: the stored result, no renormalization; changed payload: conflict.
    again = call("POST", "/api/tradecase/messages", o2_body)
    assert again.get("replayed") and again["line_results"] == o2["line_results"] and stored("O2") == body, again
    changed = dict(o2_body, payload=dict(o2_body["payload"], lines=[line(1, "26", "EA"), line(2, "5", "BLK"), line(3, "3", "BOX")]))
    report["changed_replay"] = call("POST", "/api/tradecase/messages", changed, status=409)
    report["checks"].append("Exact replay after the SKU setting changed returns the stored line results; changed payload under the same event: 409")
    # 4. Rights: an own actor without the document permission.
    actor, secret = "OU27" + uuid4().hex[:9], secrets.token_hex(16)
    with oracle_connection() as c:
        q = c.cursor(); q.execute("insert into RUSERS(ID,PASS,NAME,USER_GROUP,WARE_ID,DELETED,PRAVO_ADMIN_LOGIN)values(:a,:p,'C-0175 QA','TC03QA',:w,0,1)", a=actor, p=secret, w=ware); c.commit()
    report["denied"] = call("POST", "/api/tradecase/messages", dict(o2_body, event_id=t + ".denied"), status=403, auth=(actor, secret))
    with oracle_connection() as c:
        q = c.cursor(); q.execute("update RUSERS set DELETED=1 where ID=:a", a=actor); c.commit()
    report["checks"].append("Actor without the document right: 403")
    # 5. Zero and missing-coefficient lines.
    mixed = dict(recipient_id="C1", planned_ship_at=ship, lines=[line(1, "24", "BOX"), line(2, "11", "EA"), line(3, "2", "KG")])
    if not AFTER_KIT:
        report["o4_before_kit"] = send("ORDER", "O4", mixed, status=409)[0]
        assert "WHOLE_UNIT_REQUIRED" in json.dumps(report["o4_before_kit"]), report["o4_before_kit"]
        report["checks"].append("Before the native kit: an ORDER with a zero / no-coefficient line is refused whole (WHOLE_UNIT_REQUIRED) - the documented limitation")
    else:
        o4, _ = send("ORDER", "O4", mixed)
        got4 = [(x["quantity"], x["normalization"]["status"], x["normalization"]["executable"]) for x in stored("O4")["lines"]]
        assert got4 == [("24", "EXACT", True), ("0", "ZERO", False), ("0", "COEFFICIENT_MISSING", False)], got4
        report["o4"] = dict(result=o4, lines=got4)
        trip = dict(vehicle_id="OU27V", planning_source="SAP", planned_departure_at=ship, capacity_kg="1000", capacity_m3="10", orders=[dict(order_id="O4", line_id="2", quantity="1")])
        report["trip_refused"] = send("TRIP", "T1", trip, status=409)[0]
        assert "ORDER_LINE_NOT_EXECUTABLE" in json.dumps(report["trip_refused"])
        report["checks"].append("After the kit: zero and no-coefficient lines kept non-executable (quantity 0); TRIP assignment refused ORDER_LINE_NOT_EXECUTABLE")
    # 6. Downstream binding of the processed order to a native order (the existing EA/BOX check: BOX rows, registry BOX = 12).
    with oracle_connection() as c:
        q = c.cursor(); q.callproc("RRL_STOCK_METADATA_TX.begin_change", ["admin", "warehouse_settings_edit"])
        try:
            q.execute("select RRL_CUSTOMER_ORDER_SQ.nextval from dual"); order = q.fetchone()[0]
            q.execute("insert into RRL_CUSTOMER_ORDER(CUSTOMER_ORDER_ID,ORDER_NO,CUSTOMER_ID,WARE_ID,SHIPMENT_DATE,STATUS,SOURCE_SYSTEM,CREATED_BY)values(:o,:n,:c,:w,trunc(sysdate)+1,'OPEN','QA_TRADECASE_ONLY','admin')", o=order, n=t, c=customer, w=ware)
            rows = []
            for i, qty in ((1, 2), (2, 4), (3, 3)):
                q.execute("select RRL_CUSTOMER_ORDER_ROW_SQ.nextval from dual"); row = q.fetchone()[0]; rows.append(row)
                q.execute("insert into RRL_CUSTOMER_ORDER_ROW(CUSTOMER_ORDER_ROW_ID,CUSTOMER_ORDER_ID,LINE_NO,ARTICUL,PRODUCT_NAME,UNIT_CODE,ORDER_QTY,WARE_ID,STATUS,CREATED_BY)values(:r,:o,:l,:a,'C-0175','BOX',:q,:w,'OPEN','admin')",
                          r=row, o=order, l=i, a=article, q=qty, w=ware)
            c.commit()
        finally:
            q.callproc("RRL_STOCK_METADATA_TX.end_change")
    report["binding"] = call("POST", f"/api/tradecase/warehouses/{ware}/orders/O2/binding", dict(operation_id=t + ".bind", expected_order_version=1, customer_order_id=order,
                                                                                                lines=[dict(line_id=str(i), customer_order_row_id=r) for i, r in zip((1, 2, 3), rows)]))
    report["checks"].append("The processed O2 (2/4/3 BOX) binds to native BOX rows through the existing binding: no second recalculation downstream")
    report["status"] = "PASS"


if __name__ == "__main__":
    try:
        run()
    except Exception as exc:
        report["error"] = repr(exc)[:3000]; raise
    finally:
        save(); print(json.dumps({k: report.get(k) for k in ("status", "warehouse", "checks", "error")}, ensure_ascii=False)[:3000])
