"""C-0171 T08: the original physical top-up on ONE new isolated warehouse, pallet mode of the program (33 places: main 30 + top-up 3,
20 boxes of 10 units each per place). Main 600 BOX and top-up 60 BOX (of a need of 80, 20 stay uncovered) are moved only by the
existing native wave/warehouse tasks, bound to shipments and loaded. Real HTTP/Oracle; SAP/SKM messages, vehicle geometry and
measurements are synthetic. Resumable: every step is stored in the state file before the next one; a closed fixture is never rerun."""
from datetime import datetime, timedelta, timezone
import json
import os
from pathlib import Path
import re
import sys
import xml.etree.ElementTree as ET
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT), str(ROOT / "scripts"), str(Path(__file__).parent)]
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment()
import live_stock_acceptance
from live_stock_acceptance import setup, xml_call, fields, ean
from live_document_acceptance import http, expect, CALLS
from tools.mcp.tms_mcp_server import oracle_connection
from uuid import uuid4

OUT = ROOT / "runtime/test-evidence/tradecase/2026-10-26/T08"
STATE = OUT / "topup-physical-660.json"
PROTECTED = {225837931, 213059748, 225687965, 210564699}
PALLETS, UNITS = 33, 200  # 33 places of 20 boxes x 10 units
MAIN_PALLETS = 30
s: dict = {}


def save():
    OUT.mkdir(parents=True, exist_ok=True); STATE.write_text(json.dumps(s, indent=1, ensure_ascii=True, default=str), encoding="utf-8")


def step(key, method, path, body=None, status=200):
    """A step runs once; its request and response are kept, so a rerun continues instead of creating anything twice."""
    done = s.setdefault("steps", {})
    if key not in done:
        done[key] = dict(method=method, path=path, body=body, status=status, result=expect(status, http(method, path, body))); save()
    return done[key]["result"]


def db(sql, **binds):
    with oracle_connection() as conn:
        q = conn.cursor(); q.execute(sql, binds)
        return [tuple(x.read() if hasattr(x, "read") else x for x in row) for row in q.fetchall()]


def stock():
    return db("select nvl(sum(r.REMAIN),0),nvl(sum(r.HARD_RESERVED_BASE),0),count(distinct r.UID_POLETA) from RRL_REMAINS r join RRL_CELLS c on c.CELL=r.CELL where c.WARE_ID=:w and r.REMAIN>0", w=s["fixture"]["warehouse_id"])[0]


def plan_fixture():
    for _ in range(10):
        tag = uuid4().hex; ware = 210000000 + int(tag[:6], 16)
        if ware in PROTECTED:
            continue
        if db("""select (select count(*) from RRL_WARES where ID=:w)+(select count(*) from RRL_CELLS where WARE_ID=:w)+(select count(*) from RRL_TRADE_SITE where WARE_ID=:w)
            +(select count(*) from RRL_ACCESS_OBJECT where KIND='WAREHOUSE' and OBJECT_ID=to_char(:w))+(select count(*) from RUSERS where WARE_ID=:w) from dual""", w=ware)[0][0] == 0:
            return tag, ware
    raise RuntimeError("No absent warehouse id")


def tag():
    return "TP26." + s["fixture"]["tag"]


def send(key, kind, document, payload, version=1):
    f = s["fixture"]
    return step("msg_" + key, "POST", "/api/tradecase/messages", dict(schema_version=1, event_id=tag() + "." + key, source_id="TC03.SAP", warehouse_id=f["warehouse_id"],
        document_id=document, version=version, occurred_at=datetime.now(timezone.utc).isoformat(), payload=dict(entity_type=kind, **payload)))


def receive():
    """33 own pallets through the existing SAP supply order, UNIT receipt, putaway, SUPPLY bind and SKM verdict."""
    f = s["fixture"]; w = f["warehouse_id"]; base = f"/api/tradecase/warehouses/{w}"
    step("site", "PUT", base + "/site", dict(operation_id=tag() + ".site", expected_version=0, source_id="TC03.SAP", active_skm="TC03.SKM",
        planning_source="SAP", enabled=True, reason="C-0171 physical top-up isolated acceptance"))
    for owner in ("SNS", "BLC"):
        send("owner_" + owner, "OWNER", owner, dict(title=owner))
    send("sku", "SKU", "A", dict(title="Product A (program 21.10)", wms_article_id=f["article"], units_per_box=10, permitted_mrc=["200"]))
    for cell, zone in ((f["receive"], "RECEIVE"), (f["storage"], "STORAGE"), (f["pick"], "PICK")):
        body = dict(operation_id=tag() + ".cell." + cell, expected_version=0, zone_kind=zone, reason="C-0171 cell fixture")
        if zone == "PICK": body["owner_id"] = "SNS"
        step("cell_" + zone, "PUT", base + "/stock/cells/" + cell, body)
    # One storage place per pallet: the same own-warehouse cell DML as live_stock_acceptance.setup, then the trade STORAGE rule via the API.
    for n in range(2, PALLETS + 1):
        cell = f["storage"] + str(n).zfill(2)
        if not db("select count(*) from RRL_CELLS where CELL=:c", c=cell)[0][0]:
            with oracle_connection() as conn:
                q = conn.cursor(); q.callproc("RRL_STOCK_CONFIG_API.begin_change", ["admin", "warehouse_settings_edit"])
                try:
                    q.execute("insert into RRL_CELLS(CELL,WARE_ID,X,Y,Z,OTBOR,IS_SYSTEM,LIMIT_WEIGHT,LIMIT_HEIGHT)values(:c,:w,0,0,0,0,0,0,0)", c=cell, w=w)
                    q.execute("insert into RRL_STOCK_POLICY_GUARD(POLICY_KEY,LOCK_ID)select RRL_STOCK_LOCK_API.resource_key('CELL',:c),nvl(max(LOCK_ID),900000000)+1 from RRL_STOCK_POLICY_GUARD", c=cell)
                    conn.commit()
                finally:
                    q.callproc("RRL_STOCK_CONFIG_API.end_change")
        step("cell_STORAGE" + str(n).zfill(2), "PUT", base + "/stock/cells/" + cell, dict(operation_id=tag() + ".cell." + cell, expected_version=0, zone_kind="STORAGE", reason="C-0171 storage place"))
    if "order_import" not in s:
        supply = ET.Element("WarehouseSupplyOrder", version="1")
        fields(supply, dict(Sender="TC03.QA.SAP", MessageId=tag() + ".supply", OrderNumber="TP" + f["tag"][:8], Revision=1, WarehouseId=w, ReceiveCell=f["receive"], Supplier="C-0171 QA"))
        line = ET.SubElement(ET.SubElement(supply, "Lines"), "Line"); fields(line, dict(LineNumber="1", Material=f["article"]))
        ET.SubElement(line, "Quantity", unit="EA").text = str(PALLETS * UNITS)
        s["order_import"] = xml_call("/api/integrations/sap/supply-orders", supply, 202); save()
    pallets = s.setdefault("pallets", {})
    for n in range(1, PALLETS + 1):
        key = str(n).zfill(2)
        if pallets.get(key, {}).get("valid"):
            continue
        pallet = ean("6900" + key + "0" + str(int(f["tag"], 16)).zfill(10)[-10:])
        codes = [f["gtin"] + f["tag"][:2] + key + str(i).zfill(3) for i in range(1, UNITS + 1)]
        received = step("receipt_" + key, "POST", f"/api/receiving/supply-orders/{s['order_import']['order_id']}/pallets", dict(operation_id=tag() + ".receipt." + key,
            line_number="1", pallet_identifier=pallet, quantity=str(UNITS), supplier_batch="TP26", expiry_date="2030-01-01", gross_weight=str(UNITS),
            units=[dict(unit_id=str(i), quantity="1", codes=[dict(system_code="CRPT", profile_code="TOBACCO", code=c)]) for i, c in enumerate(codes, 1)]), status=201)
        send("supply_" + key, "SUPPLY", "SUPPLY" + key, dict(wms_article_id=f["article"], sap_order_id=s["order_import"]["order_id"], sap_line_id="1", sku_id="A", owner_id="SNS",
            mrc="200", pallet_identifier=pallet, supplier_batch="TP26", expiry_date="2030-01-01", composition_source="SAP", codes=[dict(system_code="CRPT", profile_code="TOBACCO", code=c) for c in codes]))
        step("bind_" + key, "POST", base + "/stock/bind", dict(operation_id=tag() + ".bind." + key, supply_id="SUPPLY" + key, expected_supply_version=1, scanned_pallet=pallet))
        target = db("select TO_CELL from RRL_WAREHOUSE_TASK where TASK_ID=:t", t=received["task_id"])[0][0]
        step("putaway_" + key, "POST", f"/api/receiving/putaway/{received['task_id']}/complete", dict(scanned_pallet=pallet, scanned_from_cell=f["receive"], scanned_to_cell=target))
        items = [dict(physical_unit_key=k, expected_attribute_version=v, verdict="VALID") for k, v in
                 db("select a.PHYSICAL_UNIT_KEY,a.VERSION_NO from RRL_TRADE_STOCK_ATTR a join RRL_WMS_RECEIPT_UNIT u on u.PHYSICAL_UNIT_KEY=a.PHYSICAL_UNIT_KEY where u.UID_PALLET=:p", p=pallet)]
        assert len(items) == UNITS, (key, len(items))
        step("valid_" + key, "POST", base + "/stock/mark-confirmations", dict(operation_id=tag() + ".valid." + key, skm_id="TC03.SKM", external_event_id=tag() + ".valid." + key,
            expected_site_version=1, occurred_at=datetime.now(timezone.utc).isoformat(), items=items))
        pallets[key] = dict(pallet=pallet, cell=target, valid=True); save()
    s["after_receipt"] = stock(); assert tuple(s["after_receipt"]) == (PALLETS * UNITS, 0, PALLETS), s["after_receipt"]
    s["phase"] = "RECEIVED"; save()


def native_order(key, units):
    """The same QA native order fixture DML as tests/tradecase/live_full_pallet.py (no stock, reservation or task rows)."""
    f = s["fixture"]
    if key not in s:
        with oracle_connection() as conn:
            q = conn.cursor(); q.callproc("RRL_STOCK_METADATA_TX.begin_change", ["admin", "warehouse_settings_edit"])
            try:
                q.execute("select RRL_CUSTOMER_ORDER_SQ.nextval,RRL_CUSTOMER_ORDER_ROW_SQ.nextval from dual"); order, row = q.fetchone()
                q.execute("insert into RRL_CUSTOMER_ORDER(CUSTOMER_ORDER_ID,ORDER_NO,CUSTOMER_ID,WARE_ID,SHIPMENT_DATE,STATUS,SOURCE_SYSTEM,CREATED_BY)values(:o,:n,:c,:w,trunc(sysdate)+1,'OPEN','QA_TRADECASE_ONLY','admin')",
                          o=order, n=tag() + "." + key, c=s["customer"], w=f["warehouse_id"])
                q.execute("insert into RRL_CUSTOMER_ORDER_ROW(CUSTOMER_ORDER_ROW_ID,CUSTOMER_ORDER_ID,LINE_NO,ARTICUL,PRODUCT_NAME,UNIT_CODE,ORDER_QTY,WARE_ID,STATUS,CREATED_BY)values(:r,:o,1,:a,'C-0171 product A','EA',:q,:w,'OPEN','admin')",
                          r=row, o=order, a=f["article"], q=units, w=f["warehouse_id"]); conn.commit()
            finally:
                q.callproc("RRL_STOCK_METADATA_TX.end_change")
        s[key] = dict(order=order, row=row); save()
    return s[key]


def wave(key, order):
    """Plan, wave, calculate, launch, staging and picking release through the existing native picking API; returns PICKING_MOVE tasks."""
    f = s["fixture"]; day = s["day"]
    plan = step(key + "_plan", "POST", "/api/picking/plans", dict(operation_id=tag() + "." + key + ".plan", customer_order_id=order))["pick_plan_id"]
    wid = step(key + "_wave", "POST", "/api/picking/waves", dict(wave_code=tag() + "." + key, wave_name="C-0171 " + key, ware_id=f["warehouse_id"],
        planned_start_at=day + "T08:00:00+03:00", planned_finish_at=day + "T10:00:00+03:00"))["pick_wave_id"]
    route = f"/api/picking/waves/{wid}"
    step(key + "_added", "POST", route + "/plans", dict(pick_plan_id=plan)); step(key + "_calculated", "POST", route + "/calculate", {})
    launched = step(key + "_launched", "POST", route + "/launch", dict(operation_id=tag() + "." + key + ".launch"))
    assert expect(200, http("POST", route + "/launch", dict(operation_id=tag() + "." + key + ".launch"))) == launched  # replay: no second reservation
    step(key + "_staging", "POST", route + "/staging/release", dict(to_cell=f["receive"]))
    step(key + "_release", "POST", route + "/release-picking", dict(operation_id=tag() + "." + key + ".release"))
    s[key + "_wave_id"] = wid; save()
    return db("select TASK_ID,UID_PALLET,FROM_CELL,TO_CELL,QTY from RRL_WAREHOUSE_TASK where TASK_SOURCE='WAVE' and SOURCE_DOC_ID=:w and TASK_TYPE='PICKING_MOVE' order by TASK_ID", w=wid)


def main_orders():
    """Recipient, main order 600 BOX, the 33-place vehicle (66 m3 / 6600 kg box mode), trip and need; main wave reserves 30 whole pallets."""
    f = s["fixture"]; w = f["warehouse_id"]; base = f"/api/tradecase/warehouses/{w}"
    assert s.get("phase") in ("RECEIVED", "MAIN_PLANNED"), s.get("phase")
    step("expedition", "PUT", base + "/stock/cells/" + f["receive"], dict(operation_id=tag() + ".expedition", expected_version=1, zone_kind="EXPEDITION", reason="C-0171 staging zone"))
    if "customer" not in s:
        s["customer"] = expect(200, http("POST", "/api/customers", dict(customer_code=tag(), customer_name="C-0171 store", customer_type="LEGAL_ENTITY")))["customer_id"]; save()
    s.setdefault("day", (datetime.now(ZoneInfo("Europe/Moscow")).date() + timedelta(days=1)).isoformat()); save()
    departure = s["day"] + "T12:00:00+03:00"
    send("recipient", "RECIPIENT", "C1", dict(title="C-0171 store", wms_customer_id=s["customer"], target_owner_id="SNS", permitted_source_owners=["SNS"],
        buyout_mode="BEFORE_PICK", min_osg_days=0, lead_time_days=0, allow_broken_box=False, allow_partial_ship=True))
    send("order_main", "ORDER", "O1", dict(recipient_id="C1", planned_ship_at=departure,
        lines=[dict(line_id="1", sku_id="A", source_owner_id="SNS", target_owner_id="SNS", mrc="200", quantity=str(MAIN_PALLETS * UNITS), uom="EA", min_osg_days=0)]))
    plate = "TP26V" + str(w)
    if "vehicle" not in s:
        s["vehicle"] = expect(201, http("POST", "/api/admin/transport/vehicles", dict(num_plat=plate, transtype_id="10", max_weight_kg=8000, max_pallets=33, sobstvennyy=True)))["id"]; save()
    profile = expect(200, http("GET", f"/api/admin/transport/vehicles/{s['vehicle']}/profile"))
    step("profile", "POST", "/api/admin/transport/vehicle-profiles", dict(operation_id=tag() + ".profile", vehicle_id=s["vehicle"], expected_source_hash=profile["base_hash"],
        expected_version=profile["version"], vehicle_size_class="QA_TOPUP", cargo_length_mm=13200, cargo_width_mm=2500, cargo_height_mm=2000, outer_height_mm=3000,
        outer_length_mm=14000, floor_variants=[dict(code="QA33", limits=[dict(pallet_type_id=1, max_places=33)])], reason="Synthetic program vehicle 33 places", evidence_reference="TEST_NOT_HARDWARE"))
    trip = dict(vehicle_id=plate, planning_source="SAP", planned_departure_at=departure, capacity_kg="6600", capacity_m3="66",
                orders=[dict(order_id="O1", line_id="1", quantity=str(MAIN_PALLETS * UNITS))])
    send("trip_1", "TRIP", "T1", trip); s["trip_v1"] = trip; save()
    now = datetime.now(timezone.utc)
    send("need", "NEED", "N1", dict(recipient_id="C1", sku_id="A", recipient_version=1, sku_version=1, snapshot_at=now.isoformat(), period_from=now.isoformat(),
        period_until=(now + timedelta(days=1)).isoformat(), uom="BOX", forecast_quantity="680", target_quantity="0", available_quantity="0", received_in_available=True,
        supplies=[dict(supply_id="MAIN", version=1, quantity="600", uom="BOX", status="PLANNED", confirmed=True, current_trip=True, expected_at=departure)]))
    main = native_order("native_main", MAIN_PALLETS * UNITS)
    step("binding_main", "POST", base + "/orders/O1/binding", dict(operation_id=tag() + ".bind.main", expected_order_version=1, customer_order_id=main["order"],
        lines=[dict(line_id="1", customer_order_row_id=main["row"])]))
    s["phase"] = "MAIN_PLANNED"; save()
    tasks = wave("main", main["order"])
    s["main_tasks"] = [list(t) for t in tasks]; s["after_main_wave"] = stock(); save()
    assert len(tasks) == MAIN_PALLETS and all(t[4] == UNITS for t in tasks), tasks
    assert tuple(s["after_main_wave"][:2]) == (PALLETS * UNITS, MAIN_PALLETS * UNITS), s["after_main_wave"]
    s["phase"] = "MAIN_WAVE"; save()


def topup():
    """Need 80 -> 60 fit (20 stay uncovered), approval race, confirm/replay, synthetic SAP order, updated trip; the wave takes the same holds."""
    from concurrent.futures import ThreadPoolExecutor
    f = s["fixture"]; w = f["warehouse_id"]; base = f"/api/tradecase/warehouses/{w}"; trip = base + "/trips/T1"
    assert s.get("phase") in ("MAIN_WAVE", "TOPUP_HELD", "TOPUP_ORDERED"), s.get("phase")
    if 'msg_need_horizon_identity' not in s.get('steps',{}):
        need=dict(s['steps']['msg_need']['body']['payload']);need.pop('entity_type',None)
        need.update(period_from=s['day']+'T00:00:00+03:00',period_until=s['day']+'T23:59:59+03:00')
        send('need_horizon_identity','NEED','N1.HORIZON',need,version=1)
    preview = step("topup_preview", "POST", trip + "/topup-preview", dict(need_ids=["N1.HORIZON"], max_age_minutes=1440))
    item = preview["items"][0]
    assert (item["proposed_boxes"], item["uncovered_boxes"], item["limited_by"], item["sender_stock_boxes"]) == (60, "20", "CAPACITY", 60), item
    body = dict(operation_id=tag() + ".save", need_ids=["N1.HORIZON"], max_age_minutes=1440)
    saved = step("topup_saved", "POST", trip + "/topup-proposals", body)
    proposal = saved["proposals"][0]; pid = proposal["proposal_id"]; s["proposal_id"] = pid; save()
    assert proposal["approved_boxes"] == 60, proposal
    assert expect(200, http("POST", trip + "/topup-proposals", body))["replayed"]  # same request: same proposal, nothing new
    step("topup_changed_body", "POST", trip + "/topup-proposals", dict(body, max_age_minutes=61), status=409)
    step("topup_adjust_over", "POST", trip + f"/topup-proposals/{pid}/decision", dict(operation_id=tag() + ".adjust.over", expected_version=proposal["version"], action="ADJUST", boxes=80), status=409)
    if "topup_race" not in s:  # two dispatchers decide the same version at once: exactly one decision is recorded
        bodies = [dict(operation_id=tag() + ".adjust." + n, expected_version=proposal["version"], action="ADJUST", boxes=60) for n in ("A", "B")]
        with ThreadPoolExecutor(max_workers=2) as pool:
            replies = list(pool.map(lambda b: http("POST", trip + f"/topup-proposals/{pid}/decision", b), bodies))
        s["topup_race"] = [dict(body=b, status=r[0], result=r[1]) for b, r in zip(bodies, replies)]; save()
    statuses = sorted(x["status"] for x in s["topup_race"]); assert statuses == [200, 409], s["topup_race"]
    decided = next(x["result"] for x in s["topup_race"] if x["status"] == 200)
    confirm = dict(operation_id=tag() + ".confirm", expected_version=decided["version"])
    confirmed = step("topup_confirmed", "POST", trip + f"/topup-proposals/{pid}/confirm", confirm)
    assert expect(200, http("POST", trip + f"/topup-proposals/{pid}/confirm", confirm)) == confirmed  # same operation: no second hold
    s["after_hold"] = stock(); save(); assert tuple(s["after_hold"][:2]) == (PALLETS * UNITS, PALLETS * UNITS), s["after_hold"]
    if "held_units" not in s:
        s["held_units"] = [list(r) for r in db("select u.UID_PALLET,u.PHYSICAL_UNIT_KEY,u.HARD_RESERVATION_ID from RRL_WMS_RECEIPT_UNIT u join RRL_TRADE_TOPUP_HOLD h on h.RESERVATION_ID=u.HARD_RESERVATION_ID where h.PROPOSAL_ID=:p order by u.PHYSICAL_UNIT_KEY", p=pid)]
        save()
    assert len(s["held_units"]) == 600 and len({r[1] for r in s["held_units"]}) == 600
    s["phase"] = "TOPUP_HELD"; save()
    accepted = step("topup_sap", "POST", trip + f"/topup-proposals/{pid}/sap-reply", dict(operation_id=tag() + ".sap", expected_version=confirmed["version"], source_id="TC03.SAP",
        event_id=tag() + ".SAP104", outcome="ACCEPTED", sap_order_id="O104"))
    send("order_topup", "ORDER", "O104", dict(order_kind="TOPUP", parent_trip_id="T1", recipient_id="C1", planned_ship_at=s["trip_v1"]["planned_departure_at"],
        lines=[dict(line_id="1", sku_id="A", source_owner_id="SNS", target_owner_id="SNS", mrc="200", quantity="600", uom="EA", min_osg_days=0)]))
    extra = native_order("native_topup", 600)
    step("binding_topup", "POST", base + "/orders/O104/binding", dict(operation_id=tag() + ".bind.topup", expected_order_version=1, customer_order_id=extra["order"],
        lines=[dict(line_id="1", customer_order_row_id=extra["row"])]))
    trip2 = dict(s["trip_v1"], orders=s["trip_v1"]["orders"] + [dict(order_id="O104", line_id="1", quantity="600")])
    send("trip_2", "TRIP", "T1", trip2, 2); s["trip_v2"] = trip2; s["phase"] = "TOPUP_ORDERED"; save()
    acknowledged=s['steps']['topup_sap']['body']['sap_order_id']
    if acknowledged != 'O104':
        # Preserve the accepted synthetic reply; correct the mismatched fixture documents explicitly.
        payload=dict(s['steps']['msg_order_topup']['body']['payload']);payload.pop('entity_type',None)
        send('order_topup_match','ORDER',acknowledged,payload)
        extra=native_order('native_topup_matched',600)
        step('binding_topup_match','POST',base+'/orders/'+acknowledged+'/binding',dict(operation_id=tag()+'.bind.topup.match',expected_order_version=1,customer_order_id=extra['order'],lines=[dict(line_id='1',customer_order_row_id=extra['row'])]))
        corrected=dict(s['trip_v1'],orders=s['trip_v1']['orders']+[dict(order_id=acknowledged,line_id='1',quantity='600')])
        send('trip_matched','TRIP','T1',corrected,version=3)
        send('order_topup_cancel_after_trip','ORDER','O104',dict(payload,cancelled=True),version=2)
    assert db("select RRL_TRADE_TOPUP_ADOPT.line_proposal(:r) from dual", r=extra["row"]) == [(pid,)]
    tasks = wave("topup", extra["order"])
    s["topup_tasks"] = [list(t) for t in tasks]; save()
    adopted = [list(r) for r in db("select u.UID_PALLET,u.PHYSICAL_UNIT_KEY,u.HARD_RESERVATION_ID from RRL_WMS_RECEIPT_UNIT u join RRL_TRADE_TOPUP_ADOPTION a on a.RESERVATION_ID=u.HARD_RESERVATION_ID where a.PROPOSAL_ID=:p order by u.PHYSICAL_UNIT_KEY", p=pid)]
    assert adopted == s["held_units"], "the wave must take the same held units"
    s["after_topup_wave"] = stock(); save(); assert tuple(s["after_topup_wave"][:2]) == (PALLETS * UNITS, PALLETS * UNITS), s["after_topup_wave"]
    assert len(tasks) == PALLETS - MAIN_PALLETS and all(t[4] == UNITS for t in tasks), tasks
    s["phase"] = "TOPUP_WAVE"; save()


def pick():
    """Each whole-pallet PICKING_MOVE task completes through the native task API (replay checked) and binds to its shipment."""
    from full_pallet_fixture import prepare_shipment
    f = s["fixture"]; w = f["warehouse_id"]
    assert s.get("phase") in ("TOPUP_WAVE", "PICKING"), s.get("phase")
    s["phase"] = "PICKING"; s["st_number"] = "TP." + str(w); save()
    for kind, tasks, order in (("main", s["main_tasks"], s["native_main"]["order"]), ("topup", s["topup_tasks"], s.get("native_topup_matched",s["native_topup"])["order"])):
        for tid, pallet, src, dst, qty in tasks:
            key = str(tid)
            body = dict(operation_id=tag() + ".move." + key, scanned_pallet=pallet, scanned_from_cell=src, scanned_to_cell=dst, fact_qty=str(qty))
            moved = step("move_" + key, "POST", f"/api/warehouse-tasks/{tid}/complete", body)
            if "move_replay_" + key not in s.get("steps", {}) and tid == tasks[0][0]:
                assert expect(200, http("POST", f"/api/warehouse-tasks/{tid}/complete", body)) == moved; s["steps"]["move_replay_" + key] = True; save()
            shipments = s.setdefault("shipments", {})
            if key not in shipments:
                shipments[key] = dict(prepare_shipment(dict(fixture=f, native_order=order, shipment_identifier="TP26.ST." + key, shipment_quantity=qty, st_number=s["st_number"])),
                                      kind=kind, pallet=pallet, cell=dst); save()
            path = f"/api/warehouse-tasks/{tid}/full-pallet-shipment"
            if "bind_ship_" + key not in s["steps"]:
                current = expect(200, http("GET", path))
                step("bind_ship_" + key, "POST", path, dict(operation_id=tag() + ".ship." + key, shipment_identifier=shipments[key]["shipment_identifier"],
                    scanned_pallet=current["pallet_identifier"], expected_stock_version=current["stock_version"]))
    s["after_pick"] = stock(); s["fulfillment"] = [list(r) for r in db("select f.CUSTOMER_ORDER_ID,f.STATUS,count(*),sum(f.FACT_QTY) from RRL_CUSTOMER_ORDER_FULFILLMENT f where f.CUSTOMER_ORDER_ID in(:a,:b) group by f.CUSTOMER_ORDER_ID,f.STATUS",
        a=s["native_main"]["order"], b=s.get("native_topup_matched",s["native_topup"])["order"])]; save()
    assert sorted((r[0], r[1], r[2], r[3]) for r in s["fulfillment"]) == sorted([(s["native_main"]["order"], "PICKED", MAIN_PALLETS, MAIN_PALLETS * UNITS), (s.get("native_topup_matched",s["native_topup"])["order"], "PICKED", PALLETS - MAIN_PALLETS, (PALLETS - MAIN_PALLETS) * UNITS)]), s["fulfillment"]
    s["phase"] = "PICKED"; save()


def load():
    """Native trip for the one ST, outgoing control of all 200 codes per pallet, LOAD of every pallet (replay of the first) and totals."""
    import subprocess
    f = s["fixture"]; w = f["warehouse_id"]
    assert s.get("phase") in ("PICKED", "LOADING"), s.get("phase")
    s["phase"] = "LOADING"; save()
    dock = "TP26D" + str(w)
    if not db("select count(*) from RRL_TT_DOCK where DOCK=:d", d=dock)[0][0]:
        with oracle_connection() as conn:  # the same own dock DML as prepare_transport_task.py, sized for 33 places
            q = conn.cursor(); q.callproc("RRL_STOCK_CONFIG_API.begin_change", ["admin", "warehouse_settings_edit"])
            try:
                q.execute("insert into RRL_TT_DOCK(DOCK,WARE_ID,ORD,COUNT_OF_PALLETS,DOCK_IS_BLOCKED)values(:d,:w,1,33,0)", d=dock, w=w); conn.commit()
            finally:
                q.callproc("RRL_STOCK_CONFIG_API.end_change")
    fixture = OUT / "topup-physical-transport.json"
    if not fixture.exists():
        fixture.write_text(json.dumps(dict(warehouse_id=w, case_id=w, st_number=s["st_number"], vehicle_id=s["vehicle"], vehicle_number="TP26V" + str(w), dock=dock,
                                           shipment_date=s["day"], http=[]), indent=1), encoding="utf-8")
    if "transport" not in s:
        run = subprocess.run([sys.executable, "tests/tradecase/prepare_transport_task.py"], cwd=ROOT, env=dict(os.environ, TRADECASE_TRANSPORT_FIXTURE=str(fixture)),
                             capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=120)
        assert run.returncode == 0, (run.stdout + run.stderr)[-2000:]
        s["transport"] = {k: v for k, v in json.loads(fixture.read_text(encoding="utf-8")).items() if k != "http"}; save()
    t = s["transport"]
    for key, ship in sorted(s["shipments"].items()):
        ident = ship["shipment_identifier"]
        n = next(k for k, p in s["pallets"].items() if p["pallet"] == ship["pallet"])
        scans = [dict(system_code="CRPT", profile_code="TOBACCO", code=f["gtin"] + f["tag"][:2] + n + str(i).zfill(3)) for i in range(1, UNITS + 1)]
        if "qc_" + key not in s["steps"]:
            quality = expect(200, http("GET", "/api/outgoing-quality/" + ident))
            step("qc_" + key, "POST", "/api/outgoing-quality/" + ident + "/scan", dict(operation_id=tag() + ".qc." + key, expected_composition_signature=quality["composition_signature"],
                error_count=0, scans=scans))
        if "load_" + key not in s["steps"]:
            preview = expect(200, http("GET", "/api/transport/loading/single-preview?shipment_identifier=" + ident))
            s.setdefault("load_bodies", {})[key] = dict(operation_id=tag() + ".load." + key, identifier=ident, expected_version=preview["expected_version"],
                expected_composition_signature=preview["composition_signature"], scan_container=ship["pallet"], scan_cell=preview["snapshot"]["cell"],
                transport_task_id=t["transport_task_id"], scan_vehicle=t["vehicle_number"], scan_dock=t["dock"],
                measurements=dict(origin="MANUAL_CONFIRMED", content_version=preview["expected_version"], gross_weight_kg="200", width_m="1.2", depth_m="0.8", height_m="2.5")); save()
        body = s["load_bodies"][key]
        loaded = step("load_" + key, "POST", "/api/transport/loading/confirm-single", body)
        if "load_replay" not in s:
            assert expect(200, http("POST", "/api/transport/loading/confirm-single", body)) == loaded  # same operation: one fact, one posting
            s["load_replay"] = key; save()
    s["after_load"] = stock()
    s["load_facts"] = [list(r) for r in db("select STATUS,count(*),sum(GROSS_WEIGHT_KG) from RRL_TT_HU_LOAD_FACT where TT_ID=:t group by STATUS", t=t["transport_task_id"])]
    s["loaded_units"] = db("select -sum(e.BASE_QTY) from RRL_EVENTS e where e.OPERATION_ID like :o", o=tag() + ".load.%")[0][0]; save()
    assert tuple(s["after_load"][:2]) == (0, 0) and s["load_facts"] == [["LOADED", PALLETS, PALLETS * UNITS]] and s["loaded_units"] == PALLETS * UNITS, (s["after_load"], s["load_facts"], s["loaded_units"])
    s["phase"] = "LOADED"; save()


def main():
    os.environ.setdefault("TRADECASE_ADMIN_USER", "admin")
    os.environ.setdefault("TRADECASE_ADMIN_PASSWORD", re.search(r"PASS=(\S+?)[`,)\s]", (ROOT / "AGENTS.md").read_text(encoding="utf-8"))[1])
    if STATE.exists():
        s.update(json.loads(STATE.read_text(encoding="utf-8")))  # resume the same fixture; never a second one
    assert s.get("phase") != "CLOSED", "Closed acceptance; no commands sent"
    try:
        if "fixture" not in s:
            assert not s.get("phase"), "Interrupted before the fixture was recorded; inspect the state first"
            t, ware = plan_fixture(); s.update(phase="PLANNED", planned={"tag": t[:8], "warehouse_id": ware}); save()
            original = live_stock_acceptance.uuid4
            live_stock_acceptance.uuid4 = lambda: type("Tag", (), {"hex": t})()
            try:
                f = setup()
            finally:
                live_stock_acceptance.uuid4 = original
            assert f["warehouse_id"] == ware
            s["fixture"] = {k: v for k, v in f.items() if k != "password"}; s["phase"] = "SETUP_DONE"; save()
            with oracle_connection() as conn:  # the program's box: 10 units, 0.40x0.50x0.50 m, 10 kg; 20 boxes (4 x 5 rows) per pallet place
                q = conn.cursor(); q.callproc("RRL_STOCK_CONFIG_API.begin_change", ["admin", "warehouse_settings_edit"])
                try:
                    q.execute("update RRL_ARTICULS set COUNT_SHT_IN_KOR=10,BRUTTO_WEIGHT_OF_KOR=10,DIMKOR_X=0.4,DIMKOR_Y=0.5,DIMKOR_Z=0.5,NORMA_UKLADKI=20,COUNT_IN_ROW=4,ROWS_IN_PAL=5 where ACTICUL=:a", a=f["article"])
                    assert q.rowcount == 1; conn.commit()
                finally:
                    q.callproc("RRL_STOCK_CONFIG_API.end_change")
            with oracle_connection() as conn:  # the setup identity is not used further
                q = conn.cursor(); q.execute("update RUSERS set DELETED=1 where ID=:a and USER_GROUP='TC03QA'", a=f["actor"])
                q.execute("update RRL_ACCESS_ASSIGNMENT set REVOKED_AT=systimestamp where ASSIGNMENT_ID=:a", a=f["role"]); conn.commit()
        stage = sys.argv[1] if len(sys.argv) > 1 else "receive"
        globals()[stage]()
        print(json.dumps({k: s.get(k) for k in ("phase", "fixture")}, default=str)[:600])
    except Exception as exc:
        s["error"] = str(exc)[:4000]; save(); raise
    finally:
        s.setdefault("http", []).extend(CALLS); save()


if __name__ == "__main__":
    main()
