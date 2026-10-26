"""C-0170 live (root runs it AFTER applying db/migrations/2026-10-23_trade_short_guard): a picking shortage on trade stock through the
existing writers only. NEW isolated warehouse (same guard as live_factory_hierarchy), two own lots of 10 SNS units; an order of 10 is
replenished from lot A into the pick cell, CASE picker reports the whole shortage, an independent approver decides RESTORE, the linked
inventory task counts lot A to 0 (the only loss posting), lot B replenishes, READY re-reserves lot B under the same order row, the picker
picks lot B. The line is partly picked first (4 of 10, a carrier lot of the CASE) and 6 are reported short. Plus owner revoke -> replay 403 -> restore -> same receipt, and changed-body 409. Resumable: phases are saved in the state
file and repeated steps return the stored result. NOT executed by Claude (native candidate not applied when written)."""
from datetime import datetime, timezone, timedelta
import json
import os
from pathlib import Path
import re
import secrets
import sys
from uuid import uuid4
import xml.etree.ElementTree as ET
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT), str(ROOT / 'scripts'), str(Path(__file__).parent)]
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment()
import live_stock_acceptance
from live_stock_acceptance import setup, xml_call, fields, ean
from live_document_acceptance import http, expect, CALLS
from tools.mcp.tms_mcp_server import oracle_connection

OUT = ROOT / "runtime/test-evidence/tradecase/2026-10-26/T11"
STATE = OUT / "trade-pick-shortage-state.json"
PROTECTED = {225837931, 213059748, 225687965, 210564699}
s: dict = {}


def save():
    OUT.mkdir(parents=True, exist_ok=True); STATE.write_text(json.dumps(s, indent=2, ensure_ascii=True, default=str), encoding="utf-8")


def step(key, method, path, body=None, actor=None, password=None, status=200):
    """A step runs once; its response is kept, so a rerun after a failure continues instead of creating anything twice."""
    if key not in s:
        s[key] = expect(status, http(method, path, body, actor, password)); save()
    return s[key]


def db(sql, **binds):
    with oracle_connection() as conn:
        q = conn.cursor(); q.execute(sql, **binds)
        return [tuple(v.read() if hasattr(v,'read') else v for v in row)for row in q.fetchall()]


def plan_fixture():
    for _ in range(10):
        tag = uuid4().hex; ware = 210000000 + int(tag[:6], 16)
        if ware in PROTECTED:
            continue
        if db("""select (select count(*) from RRL_WARES where ID=:w)+(select count(*) from RRL_CELLS where WARE_ID=:w)+(select count(*) from RRL_TRADE_SITE where WARE_ID=:w)
            +(select count(*) from RRL_ACCESS_OBJECT where KIND='WAREHOUSE' and OBJECT_ID=to_char(:w))+(select count(*) from RUSERS where WARE_ID=:w) from dual""", w=ware)[0][0] == 0:
            return tag, ware
    raise RuntimeError("No absent warehouse id")


def actor(key, permissions, ware):
    """An own short-lived test identity with a warehouse-scoped role (never a reused or retired actor)."""
    if key not in s:
        name, password = "TS23" + uuid4().hex[:9], secrets.token_hex(24)
        with oracle_connection() as conn:
            q = conn.cursor()
            q.execute("insert into RUSERS(ID,PASS,NAME,USER_GROUP,WARE_ID,DELETED,PRAVO_ADMIN_LOGIN)values(:a,:p,'Trade shortage QA','TC03QA',:w,0,1)", a=name, p=password, w=ware)
            q.execute("insert into RRL_ACCESS_ROLE(ROLE_ID,TITLE,ACTIVE,VERSION_NO)values(:a,'Trade shortage QA',1,1)", a=name)
            for permission in permissions:
                q.execute("insert into RRL_ACCESS_ROLE_RIGHT(ROLE_ID,PERMISSION)values(:a,:p)", a=name, p=permission)
            q.execute("""insert into RRL_ACCESS_ASSIGNMENT(ASSIGNMENT_ID,USERNAME,ROLE_ID,SCOPE_KIND,SCOPE_ID,MEMBERSHIP,VALID_FROM,VALID_UNTIL,ASSIGNED_BY,REASON,VERSION_NO)
                values(:a,:a,:a,'WAREHOUSE',:w,'CURRENT',systimestamp-interval '1'minute,systimestamp+interval '6'hour,'admin','Trade picking shortage acceptance',1)""", a=name, w=str(ware))
            conn.commit()
        s[key] = {"username": name, "password": password}; save()
    return s[key]["username"], s[key]["password"]


def prepare():
    f = s["fixture"]; w = f["warehouse_id"]; tag = "TS23." + f["tag"]; base = f"/api/tradecase/warehouses/{w}"
    def send(key, kind, payload):
        return step(key, "POST", "/api/tradecase/messages", dict(schema_version=1, event_id=tag + "." + key, source_id="TC03.SAP", warehouse_id=w,
            document_id=tag + "." + key, version=1, occurred_at=datetime.now(timezone.utc).isoformat(), payload=dict(entity_type=kind, **payload)))
    step("site", "PUT", base + "/site", dict(operation_id=tag + ".site", expected_version=0, source_id="TC03.SAP", active_skm="TC03.SKM",
        planning_source="SAP", enabled=True, reason="Trade picking shortage isolated acceptance"))
    for owner in ("SNS", "BLC"):
        send("owner_" + owner, "OWNER", dict(title=owner))
    send("sku", "SKU", dict(title="Shortage QA", wms_article_id=f["article"], units_per_box=10, permitted_mrc=["200"]))
    for cell, zone in ((f["receive"], "RECEIVE"), (f["storage"], "STORAGE"), (f["pick"], "PICK")):
        body = dict(operation_id=tag + ".cell." + cell, expected_version=0, zone_kind=zone, reason="Trade shortage cell fixture")
        if zone == "PICK": body["owner_id"] = tag + ".owner_SNS"
        step("cell_" + zone, "PUT", base + "/stock/cells/" + cell, body)
    # Separate storage slots: the second lot must not occupy the first pallet's slot.
    second_storage = f['storage'] + 'B'
    if not db('select count(*)from RRL_CELLS where CELL=:c',c=second_storage)[0][0]:
        with oracle_connection() as conn:
            q=conn.cursor();q.callproc('RRL_STOCK_CONFIG_API.begin_change',['admin','warehouse_settings_edit'])
            try:
                q.execute('insert into RRL_CELLS(CELL,WARE_ID,X,Y,Z,OTBOR,IS_SYSTEM,LIMIT_WEIGHT,LIMIT_HEIGHT)values(:c,:w,0,0,0,0,0,0,0)',c=second_storage,w=w)
                q.execute("insert into RRL_STOCK_POLICY_GUARD(POLICY_KEY,LOCK_ID)select RRL_STOCK_LOCK_API.resource_key('CELL',:c),nvl(max(LOCK_ID),900000000)+1 from RRL_STOCK_POLICY_GUARD",c=second_storage)
                conn.commit()
            finally:q.callproc('RRL_STOCK_CONFIG_API.end_change')
    step('second_storage','PUT',base+'/stock/cells/'+second_storage,dict(operation_id=tag+'.second.storage',expected_version=0,zone_kind='STORAGE',reason='Second isolated shortage lot'))
    # Two own lots of 10 units each through the existing supply receipt (UNIT scans), putaway to storage, SUPPLY bind to SNS/200.
    if "order_import" not in s:
        supply = ET.Element("WarehouseSupplyOrder", version="1")
        fields(supply, dict(Sender="TC03.QA.SAP", MessageId=tag + ".supply", OrderNumber="TS" + f["tag"][:8], Revision=1, WarehouseId=w, ReceiveCell=f["receive"], Supplier="Shortage QA"))
        line = ET.SubElement(ET.SubElement(supply, "Lines"), "Line"); fields(line, dict(LineNumber="1", Material=f["article"]))
        ET.SubElement(line, "Quantity", unit="EA").text = "20"
        s["order_import"] = xml_call("/api/integrations/sap/supply-orders", supply, 202); save()
    lots = s.setdefault("lots", {})
    for lot, pallet in (("A", f["pallet"]), ("B", ean("690000001" + str(int(f["tag"], 16)).zfill(8)[-8:]))):
        codes = [f["gtin"] + f["tag"][:2] + lot + str(i).zfill(4) for i in range(1, 11)]
        received = step("receipt_" + lot, "POST", f"/api/receiving/supply-orders/{s['order_import']['order_id']}/pallets", dict(operation_id=tag + ".receipt." + lot,
            line_number="1", pallet_identifier=pallet, quantity="10", supplier_batch="TS." + lot, expiry_date="2030-01-01", gross_weight="10",
            units=[dict(unit_id=str(i), quantity="1", codes=[dict(system_code="CRPT", profile_code="TOBACCO", code=c)]) for i, c in enumerate(codes, 1)]), status=201)
        target = db("select TO_CELL from RRL_WAREHOUSE_TASK where TASK_ID=:t", t=received["task_id"])[0][0]
        send("supply_" + lot, "SUPPLY", dict(wms_article_id=f["article"], sap_order_id=s["order_import"]["order_id"], sap_line_id="1", sku_id=tag + ".sku", owner_id=tag + ".owner_SNS",
            mrc="200", pallet_identifier=pallet, supplier_batch="TS." + lot, expiry_date="2030-01-01", composition_source="SAP", codes=[dict(system_code="CRPT", profile_code="TOBACCO", code=c) for c in codes]))
        step("bind_" + lot, "POST", base + "/stock/bind", dict(operation_id=tag + ".bind." + lot, supply_id=tag + ".supply_" + lot, expected_supply_version=1, scanned_pallet=pallet))
        step("putaway_" + lot, "POST", f"/api/receiving/putaway/{received['task_id']}/complete", dict(scanned_pallet=pallet, scanned_from_cell=f["receive"], scanned_to_cell=target))
        units = db('select a.PHYSICAL_UNIT_KEY,a.VERSION_NO from RRL_TRADE_STOCK_ATTR a join RRL_WMS_RECEIPT_UNIT u on u.PHYSICAL_UNIT_KEY=a.PHYSICAL_UNIT_KEY where u.UID_PALLET=:p',p=pallet)
        assert len(units)==10
        step('valid_'+lot,'POST',base+'/stock/mark-confirmations',dict(operation_id=tag+'.valid.'+lot,skm_id='TC03.SKM',external_event_id=tag+'.valid.'+lot,expected_site_version=1,occurred_at=datetime.now(timezone.utc).isoformat(),items=[dict(physical_unit_key=k,expected_attribute_version=v,verdict='VALID')for k,v in units]))
        lots[lot] = {"pallet": pallet, "codes": codes}; save()
    # Customer, route, pick face, recipient/order, native order and binding, plan, wave, replenishment, release (the factory CASE pattern).
    if "customer" not in s:
        s["customer"] = expect(200, http("POST", "/api/customers", dict(customer_code=tag, customer_name="Shortage QA", customer_type="LEGAL_ENTITY")))["customer_id"]; save()
    route = step("route", "POST", "/api/picking/routes", dict(route_code=tag, route_name="Shortage QA", ware_id=w))["pick_route_id"]
    rc = step("route_cell", "POST", "/api/picking/route-cells", dict(pick_route_id=route, cell_code=f["pick"], pick_sequence=1))["pick_route_cell_id"]
    face = step("face", "POST", "/api/picking/pick-faces", dict(ware_id=w, cell_code=f["pick"], pick_face_code=tag, pick_route_id=route, pick_route_cell_id=rc,
        pick_sequence=1, min_case_qty=0, max_case_qty=10, replenishment_trigger_qty=1))["pick_face_id"]
    step("face_article", "POST", f"/api/picking/pick-faces/{face}/articuls", dict(articul=f["article"], priority="1", min_qty="0", max_qty="10",
        replenishment_method="IMMEDIATE", replenishment_qty_mode="FILL_TO_VOLUME", use_articul_replenish_rule=0, boxes_per_layer="5", boxes_per_pallet="25", box_volume_m3="0.01"))
    send("recipient", "RECIPIENT", dict(title="Shortage QA", wms_customer_id=s["customer"], target_owner_id=tag + ".owner_SNS", permitted_source_owners=[tag + ".owner_SNS"],
        buyout_mode="BEFORE_PICK", min_osg_days=0, lead_time_days=0, allow_broken_box=True, allow_partial_pick=True, allow_partial_ship=True))
    # An order for a whole source pallet is correctly FULL_PALLET, not CASE.
    # Retire that initial preparation once and retain it as failed-path evidence.
    if 'wave' in s and 'case8_preparation' not in s:
        step('cancel_full_pallet_wave','POST',f"/api/picking/waves/{s['wave']['pick_wave_id']}/cancel",dict(operation_id=tag+'.cancel.fullpallet',reason='CASE shortage requires an order smaller than one source pallet'))
        keys=('order','native_order','native_row','binding','plan','plan_after_marks','cancel_unavailable_plan','wave','wave_plan','wave_calc','wave_launch','release')
        s['initial_full_pallet_preparation']={k:s.pop(k)for k in keys if k in s}
        s['case8_preparation']=True;save()
    planned_day = (datetime.now(ZoneInfo('Europe/Moscow')).date() + timedelta(days=1)).isoformat()
    send("case_order8", "ORDER", dict(recipient_id=tag + ".recipient", planned_ship_at=planned_day + "T12:00:00+03:00",
        lines=[dict(line_id="1", sku_id=tag + ".sku", source_owner_id=tag + ".owner_SNS", target_owner_id=tag + ".owner_SNS", mrc="200", quantity="8", uom="EA", min_osg_days=0)]))
    if "native_order" not in s:  # the same native order fixture DML as tests/tradecase/live_factory_case.py
        with oracle_connection() as conn:
            q = conn.cursor(); q.callproc("RRL_STOCK_METADATA_TX.begin_change", ["admin", "warehouse_settings_edit"])
            try:
                q.execute("select RRL_CUSTOMER_ORDER_SQ.nextval,RRL_CUSTOMER_ORDER_ROW_SQ.nextval from dual"); order, row = q.fetchone()
                q.execute("insert into RRL_CUSTOMER_ORDER(CUSTOMER_ORDER_ID,ORDER_NO,CUSTOMER_ID,WARE_ID,SHIPMENT_DATE,STATUS,SOURCE_SYSTEM,CREATED_BY)values(:o,:code,:c,:w,trunc(sysdate)+1,'OPEN','QA_TRADECASE_ONLY','admin')", o=order, code=tag + ".case8", c=s["customer"], w=w)
                q.execute("insert into RRL_CUSTOMER_ORDER_ROW(CUSTOMER_ORDER_ROW_ID,CUSTOMER_ORDER_ID,LINE_NO,ARTICUL,PRODUCT_NAME,UNIT_CODE,ORDER_QTY,WARE_ID,STATUS,CREATED_BY)values(:r,:o,1,:a,'Shortage QA','EA',8,:w,'OPEN','admin')", r=row, o=order, a=f["article"], w=w)
                conn.commit()
            finally:
                q.callproc("RRL_STOCK_METADATA_TX.end_change")
        s.update(native_order=order, native_row=row); save()
    step("binding", "POST", base + "/orders/" + tag + ".case_order8/binding", dict(operation_id=tag + ".case8.bindorder", expected_order_version=1,
        customer_order_id=s["native_order"], lines=[dict(line_id="1", customer_order_row_id=s["native_row"])]))
    plan = step("plan", "POST", "/api/picking/plans", dict(operation_id=tag + ".case8.plan", customer_order_id=s["native_order"]))["pick_plan_id"]
    if db('select STATUS from RRL_PICK_PLAN where PICK_PLAN_ID=:p',p=plan)==[('NO_STOCK',)]:
        step('cancel_unavailable_plan','POST',f'/api/picking/plans/{plan}/cancel',{})
        plan = step('plan_after_marks','POST','/api/picking/plans',dict(operation_id=tag+'.plan.after.marks',customer_order_id=s['native_order']))['pick_plan_id']
    wave = step("wave", "POST", "/api/picking/waves", dict(wave_code=tag + ".case8", wave_name="Shortage QA", ware_id=w,
        planned_start_at=planned_day + "T08:00:00+03:00", planned_finish_at=planned_day + "T09:00:00+03:00"))["pick_wave_id"]
    for key, suffix, body in (("wave_plan", "/plans", dict(pick_plan_id=plan)), ("wave_calc", "/calculate", {}), ("wave_launch", "/launch", dict(operation_id=tag + ".case8.launch"))):
        step(key, "POST", f"/api/picking/waves/{wave}{suffix}", body)
    for tid, pallet, src, dst, qty in db("select TASK_ID,UID_PALLET,FROM_CELL,TO_CELL,QTY from RRL_WAREHOUSE_TASK where TASK_SOURCE='WAVE'and SOURCE_DOC_ID=:w and TASK_TYPE='REPLENISHMENT'", w=wave):
        step("wave_repl_" + str(tid), "POST", f"/api/warehouse-tasks/{tid}/complete", dict(operation_id=tag + ".repl." + str(tid), scanned_pallet=pallet,
            scanned_from_cell=src, scanned_to_cell=dst, fact_qty=str(qty)))
        s["picked_lot_pallet"] = pallet; save()
    step("release", "POST", f"/api/picking/waves/{wave}/release-picking", dict(operation_id=tag + ".case8.release"))
    rows = db("select CASE_PICK_TASK_ID,CASE_PICK_LINE_ID,PICK_TASK_ID from RRL_CASE_PICK_LINE where PICK_WAVE_ID=:w", w=wave)
    assert len(rows) == 1, rows; s["case"], s["line"], s["pick_task"] = rows[0]; s["phase"] = "PREPARED"; save()


def picker_session():
    f = s["fixture"]; w = f["warehouse_id"]; tag = "TS23." + f["tag"]; base = f"/api/tradecase/warehouses/{w}"
    picker, password = actor("picker", ["case_pick_execute", "case_pick_view"], w)
    cell = "CPT_" + str(w)
    if not db("select count(*) from RRL_CELLS where CELL=:c", c=cell)[0][0]:
        with oracle_connection() as conn:
            q = conn.cursor(); q.callproc("RRL_STOCK_CONFIG_API.begin_change", ["admin", "warehouse_settings_edit"])
            try:
                q.execute("insert into RRL_CELLS(CELL,WARE_ID,X,Y,Z,OTBOR,IS_SYSTEM,LIMIT_WEIGHT,LIMIT_HEIGHT)values(:c,:w,0,0,0,0,1,0,0)", c=cell, w=w)
                q.execute("insert into RRL_STOCK_POLICY_GUARD(POLICY_KEY,LOCK_ID)select RRL_STOCK_LOCK_API.resource_key('CELL',:c),nvl(max(LOCK_ID),900000000)+1 from RRL_STOCK_POLICY_GUARD", c=cell); conn.commit()
            finally:
                q.callproc("RRL_STOCK_CONFIG_API.end_change")
    step("cpt_policy", "PUT", base + "/stock/cells/" + cell, dict(operation_id=tag + ".cpt", expected_version=0, zone_kind="SORT", reason="Shortage CASE transit cell"))
    step("picker_owner", "PUT", base + "/stock/owner-grants", dict(operation_id=tag + ".picker.owner", expected_version=0, username=picker, owner_id=tag + ".owner_SNS",
        can_view=True, can_operate=True, reason="Trade shortage picker owner scope"))
    day = datetime.now(ZoneInfo("Europe/Moscow")).date().isoformat()
    shift = step("shift", "POST", "/api/resources/shifts", dict(shift_code=tag, shift_date=day, start_at=day + "T00:00:00+03:00", finish_at=day + "T23:59:59+03:00", ware_id=w, status="OPEN"))["id"]
    resource = step("resource", "POST", "/api/resources", dict(resource_code=tag, resource_name="Shortage QA", resource_type="CASE_PICKER", resource_class="PERSON", user_id=picker, ware_id=w))["id"]
    step("qualification", "PUT", f"/api/resources/{resource}/qualifications", dict(task_type="CASE_PICK", active=True))
    session = step("session", "POST", "/api/resources/sessions/login", dict(shift_id=shift, resource_id=resource, operator_user_id=picker, terminal_id="QA_NOT_HARDWARE"))["id"]
    step("tare_count", "POST", "/api/inventory/tare/count", dict(operation_id=tag + ".tare.count", owner_ware_id=w, pallet_type_id=1, condition="GOOD", observed_quantity="1",
        expected_version=0, reason="Synthetic fixture, not physical tare survey", decision_reference="TEST_FIXTURE_NOT_HARDWARE:" + tag))
    step("tare_book", "POST", "/api/inventory/tare/book", dict(operation_id=tag + ".tare.book", place_kind="CASE", place_id=str(s["case"]), expected_warehouse_id=w, pallet_type_id=1))
    case = f"/api/case-pick/tasks/{s['case']}"
    for action in ("CLAIM", "START"):
        if action not in s:
            ctx = expect(200, http("GET", case + "/resource-context", None, picker, password))
            step(action, "POST", case + "/resource-commands", dict(operation_id=tag + "." + action, action=action, expected_assignment_version=ctx["assignment_version"],
                resource_session_id=session, resource_id=resource, reason="Trade shortage CASE"), picker, password)
    return picker, password, resource, session


def shortage():
    f = s["fixture"]; w = f["warehouse_id"]; tag = "TS23." + f["tag"]; base = f"/api/tradecase/warehouses/{w}"
    picker, password, resource, session = picker_session()
    case = f"/api/case-pick/tasks/{s['case']}"
    carrier = db("select SSCC from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=:t", t=s["case"])[0][0]
    def reserved_scans(limit):
        rows = db("""select c.RAW_CODE from RRL_WMS_RECEIPT_UNIT u join RRL_WMS_RECEIPT_CODE c on c.UID_PALLET=u.UID_PALLET and c.UNIT_ID=u.UNIT_ID
            join RRL_STOCK_RESERVATION r on r.RESERVATION_ID=u.HARD_RESERVATION_ID where r.SOURCE_DOC_TYPE='PICK_WAVE' and r.SOURCE_LINE_ID=:p
            and r.STATUS in('ACTIVE','ALLOCATED','PICKING') order by u.PHYSICAL_UNIT_KEY""", p=s["pick_task"])[:limit]
        return [dict(system_code="CRPT", profile_code="TOBACCO", code=(raw.read() if hasattr(raw, "read") else raw)) for (raw,) in rows]
    # 0. Partly picked first (4 of 10): the carrier lot of this CASE then holds picked trade goods, which the decision also locks.
    step("picked_part", "POST", case + f"/lines/{s['line']}/confirm", dict(operation_id=tag + ".pickpart", fact_qty="4", scan_cell=f["pick"], scan_product=f["article"],
        scan_container=carrier, resource_id=resource, resource_session_id=session, unit_scans=reserved_scans(4)), picker, password)
    # 1. The picker reports the remaining 6 short: no quantity or owner change yet.
    step("short", "POST", case + f"/lines/{s['line']}/short", dict(picked_qty="4", short_qty="4", reason_text="Cell short at pick (isolated QA)",
        offline_event_id=tag + ".short", resource_id=resource, resource_session_id=session), picker, password)
    short_id = db("select CASE_PICK_SHORT_ID from RRL_CASE_PICK_SHORT where CASE_PICK_LINE_ID=:l", l=s["line"])[0][0]; s["short_id"] = short_id; save()
    s["after_report"] = [list(r) for r in db("select r.UID_POLETA,r.CELL,r.REMAIN,r.HARD_RESERVED_BASE from RRL_REMAINS r join RRL_CELLS c on c.CELL=r.CELL where c.WARE_ID=:w and r.REMAIN>0 order by 1,2", w=w)]; save()
    # 2. The reporter may not approve; an independent scoped approver with the owner right decides RESTORE.
    status, result = http("POST", f"/api/case-pick/shorts/{short_id}/approve", dict(decision="RESTORE", reason_text="self", operation_id=tag + ".selfapprove"), picker, password)
    assert status in (403, 409), (status, result); s["self_approve"] = [status, result]
    approver, apw = actor("approver", ["case_pick_short_approve", "case_pick_view"], w)
    step("approver_owner", "PUT", base + "/stock/owner-grants", dict(operation_id=tag + ".approver.owner", expected_version=0, username=approver, owner_id=tag + ".owner_SNS",
        can_view=True, can_operate=True, reason="Trade shortage approver owner scope"))
    restore = dict(decision="RESTORE", reason_text="Check the cell and replenish", operation_id=tag + ".restore")
    step("restore", "POST", f"/api/case-pick/shorts/{short_id}/approve", restore, approver, apw)
    assert s["restore"]["recovery_state"] == "WAIT_INVENTORY", s["restore"]
    # 3. Owner revoke -> replay 403 (checked before the cached receipt) -> restore -> the same receipt; changed body under the id -> 409.
    if "revoke_checked" not in s:
        expect(200, http("PUT", base + "/stock/owner-grants", dict(operation_id=tag + ".approver.revoke", expected_version=1, username=approver, owner_id=tag + ".owner_SNS",
            can_view=False, can_operate=False, reason="Revoke for replay check")))
        status, result = http("POST", f"/api/case-pick/shorts/{short_id}/approve", restore, approver, apw); assert status == 403, (status, result)
        expect(200, http("PUT", base + "/stock/owner-grants", dict(operation_id=tag + ".approver.restore", expected_version=2, username=approver, owner_id=tag + ".owner_SNS",
            can_view=True, can_operate=True, reason="Restore after replay check")))
        assert expect(200, http("POST", f"/api/case-pick/shorts/{short_id}/approve", restore, approver, apw)) == s["restore"]
        status, result = http("POST", f"/api/case-pick/shorts/{short_id}/approve", dict(restore, reason_text="changed"), approver, apw); assert status == 409, (status, result)
        s["revoke_checked"] = True; save()
    # 4. The linked inventory task counts the problem cell: lot A to 0 — this confirmed count is the only loss posting.
    task_id = s["restore"]["inventory_task_id"]
    step("inv_claim", "POST", f"/api/inventory/tasks/{task_id}/claim", {})
    revision = step("revision", "POST", "/api/inventory/stock-posting/inventory/revisions", dict(warehouse_id=w))["revision_id"]
    lot_a = s.get("picked_lot_pallet") or s["lots"]["A"]["pallet"]
    version = db("select STOCK_VERSION from RRL_REMAINS where UID_POLETA=:u and CELL=:c", u=lot_a, c=f["pick"])[0][0]
    if 'expected_count_loss' not in s:
        s['expected_count_loss']=int(db('select REMAIN from RRL_REMAINS where UID_POLETA=:u and CELL=:c',u=lot_a,c=f['pick'])[0][0]);save()
    count = step("count", "POST", "/api/inventory/stock-posting/inventory/counts", dict(operation_id=tag + ".count", revision_id=revision, inventory_task_id=task_id,
        reason="ISOLATED QA: cell confirmed empty", counts=[dict(uid=lot_a, cell=f["pick"], article=f["article"], unit="EA", quantity="0", expected_stock_version=version, scans=[])]))
    assert count["recovery_state"] == "WAIT_REPLENISHMENT", count
    # 5. Replenishment from the other own lot through the existing warehouse task (trade guard checks REPLENISH compatibility).
    for tid, pallet, src, dst, qty in db("""select wh.TASK_ID,wh.UID_PALLET,wh.FROM_CELL,wh.TO_CELL,wh.QTY from RRL_WAREHOUSE_TASK wh
        where wh.TASK_SOURCE='WAVE' and wh.SOURCE_TASK_ID=:r and wh.TASK_TYPE='REPLENISHMENT' and wh.STATUS not in('DONE','CANCELLED')""", r=count["replenish_task_id"]):
        step("short_repl_" + str(tid), "POST", f"/api/warehouse-tasks/{tid}/complete", dict(operation_id=tag + ".shortrepl." + str(tid), scanned_pallet=pallet,
            scanned_from_cell=src, scanned_to_cell=dst, fact_qty=str(qty)))
    # 6. READY re-reserves the replenished lot under the same order row; the picker then picks those units.
    recovery = db('select RECOVERY_STATE from RRL_CASE_PICK_SHORT where CASE_PICK_SHORT_ID=:i',i=short_id)[0][0]
    assert recovery == 'READY', recovery
    s['ready_observed'] = dict(source='NATIVE_AFTER_REPLENISHMENT_READ_ONLY',recovery_state=recovery);save()
    scans = reserved_scans(100)
    assert len(scans) == 4, len(scans)  # exactly the remaining 6 of lot B are now reserved under the same order row
    step("picked", "POST", case + f"/lines/{s['line']}/confirm", dict(operation_id=tag + ".pick", fact_qty="4", scan_cell=f["pick"], scan_product=f["article"],
        scan_container=carrier, resource_id=resource, resource_session_id=session, unit_scans=scans), picker, password)
    s["final"] = {"remains": [list(r) for r in db("select r.UID_POLETA,r.CELL,r.REMAIN,r.HARD_RESERVED_BASE from RRL_REMAINS r join RRL_CELLS c on c.CELL=r.CELL where c.WARE_ID=:w and r.REMAIN>0 order by 1,2", w=w)],
                  "loss_rows": db("select count(*) from RRL_INVENTORY_LOSS_UNIT where UID_PALLET=:u", u=lot_a)[0][0],
                  "short": [list(r) for r in db("select STATUS,RECOVERY_STATE from RRL_CASE_PICK_SHORT where CASE_PICK_SHORT_ID=:i", i=short_id)],
                  "invalid": db("select count(*) from user_objects where STATUS='INVALID'")[0][0]}
    assert s['final']['loss_rows'] == s['expected_count_loss'], s['final']
    assert s['final']['invalid'] == 0, s['final']
    totals = db('select sum(r.REMAIN),sum(r.HARD_RESERVED_BASE)from RRL_REMAINS r join RRL_CELLS c on c.CELL=r.CELL where c.WARE_ID=:w',w=w)[0]
    assert totals == (20-s['expected_count_loss'], 0), totals
    s['final']['totals'] = list(totals)
    s["phase"] = "RECOVERED"; save()


if __name__ == "__main__":
    os.environ.setdefault("TRADECASE_ADMIN_USER", "admin")
    os.environ.setdefault("TRADECASE_ADMIN_PASSWORD", re.search(r"PASS=(\S+?)[`,)\s]", (ROOT / "AGENTS.md").read_text(encoding="utf-8"))[1])
    if STATE.exists():
        s.update(json.loads(STATE.read_text(encoding="utf-8")))  # resume the same fixture; never a second one
    try:
        if s.get('phase') in ('PLANNED', 'CLEANED'):
            raise RuntimeError('Do not rerun incomplete setup or closed fixture; inspect saved state first')
        if "fixture" not in s:
            assert db("select count(*) from user_source where name='RRL_TRADE_STOCK_GUARD' and type='PACKAGE BODY' and text like '%C-0170%'")[0][0] > 0, "apply the C-0170 kit first"
            tag, ware = plan_fixture(); s.update(phase="PLANNED", fixture={"tag": tag[:8], "warehouse_id": ware}); save()
            original = live_stock_acceptance.uuid4
            live_stock_acceptance.uuid4 = lambda: type("Tag", (), {"hex": tag})()
            try:
                f = setup()
            finally:
                live_stock_acceptance.uuid4 = original
            assert f["warehouse_id"] == ware
            s["fixture"] = {k: v for k, v in f.items() if k != "password"}; s["phase"] = "SETUP_DONE"; save()
        if s.get("phase") in ("SETUP_DONE",):
            prepare()
        if s.get("phase") == "PREPARED":
            shortage()
        assert s.get('phase') == 'RECOVERED', s.get('phase')
        print(json.dumps({k: s.get(k) for k in ("phase", "fixture", "short_id", "final")}, default=str))
    except Exception as exc:
        s["error"] = str(exc); save(); raise
    finally:
        s.setdefault("http", []).extend(CALLS); save()
    # Cleanup (return of goods, retirement of actors, tare) follows the established root retirement procedure and is not automated here.
