"""Resumable CASE proof on the owned factory-BOX fixture; no stock seed DML."""
from datetime import datetime, timedelta, timezone
import json
import os
from pathlib import Path
import re
import secrets
import sys
from uuid import uuid4
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT), str(Path(__file__).parent)]
from live_document_acceptance import http, expect, CALLS
from tools.mcp.tms_mcp_server import oracle_connection

OUT = ROOT/"runtime/test-evidence/tradecase/2026-10-21/T06"
FILE = OUT/"factory-case.json"
s = json.loads(FILE.read_text()) if FILE.exists() else dict(warehouse_id=219023232, article="TC0389AF0087", pick="T3P89af0087", history=[])
tag = "FC21."+str(s["warehouse_id"])
w = s["warehouse_id"]
base = f"/api/tradecase/warehouses/{w}"


def save():
    OUT.mkdir(parents=True, exist_ok=True);FILE.write_text(json.dumps(s, indent=2, ensure_ascii=True, default=str), encoding="utf-8")


def verify_fixture():
    with oracle_connection() as conn:
        q=conn.cursor();q.execute("select user,sys_context('USERENV','SERVICE_NAME')from dual")
        assert q.fetchone()==("RABAEV","orcl")
        q.execute("select NAME from RRL_WARES where ID=:w",w=w)
        assert q.fetchone()==("TRADECASE QA 89af0087",)
        assert s["article"]=="TC0389AF0087" and s["pick"]=="T3P89af0087"


def step(key, path, body, method="POST", actor=None, password=None):
    if key not in s:
        s[key] = expect(200, http(method, path, body, actor, password));save()
    return s[key]


def prepare():
    if "customer" not in s:
        s["customer"] = expect(200, http("POST", "/api/customers", dict(customer_code=tag, customer_name="Factory CASE QA", customer_type="LEGAL_ENTITY")))["customer_id"];save()
    if "face" not in s:
        route = step("route", "/api/picking/routes", dict(route_code=tag, route_name="Factory CASE QA", ware_id=w))["pick_route_id"]
        rc = step("route_cell", "/api/picking/route-cells", dict(pick_route_id=route, cell_code=s["pick"], pick_sequence=1))["pick_route_cell_id"]
        s["face"] = step("face_created", "/api/picking/pick-faces", dict(ware_id=w, cell_code=s["pick"], pick_face_code=tag,
            pick_route_id=route, pick_route_cell_id=rc, pick_sequence=1, min_case_qty=0, max_case_qty=100, replenishment_trigger_qty=1))["pick_face_id"];save()
    step("face_article", f"/api/picking/pick-faces/{s['face']}/articuls", dict(articul=s["article"], priority="1", min_qty="0", max_qty="100",
        replenishment_method="IMMEDIATE", replenishment_qty_mode="FILL_TO_VOLUME", use_articul_replenish_rule=0, boxes_per_layer="5", boxes_per_pallet="25", box_volume_m3="0.01"))
    def send(key, kind, payload):
        return step(key, "/api/tradecase/messages", dict(schema_version=1, event_id=tag+"."+kind, source_id="TC03.SAP", warehouse_id=w,
            document_id=tag+"."+kind, version=1, occurred_at="2026-10-21T12:00:00+03:00", payload=dict(entity_type=kind, **payload)))
    send("recipient", "RECIPIENT", dict(title="Factory CASE QA", wms_customer_id=s["customer"], target_owner_id="SNS", permitted_source_owners=["SNS"],
        buyout_mode="BEFORE_PICK", min_osg_days=0, lead_time_days=0, allow_broken_box=True, allow_partial_pick=True, allow_partial_ship=True))
    send("order", "ORDER", dict(recipient_id=tag+".RECIPIENT", planned_ship_at="2026-10-22T12:00:00+03:00",
        lines=[dict(line_id="1", sku_id="A", source_owner_id="SNS", target_owner_id="SNS", mrc="200", quantity="2", uom="EA", min_osg_days=0)]))
    if "native_order" not in s:
        with oracle_connection() as conn:
            q=conn.cursor();q.callproc("RRL_STOCK_METADATA_TX.begin_change", ["admin", "warehouse_settings_edit"])
            try:
                q.execute("select RRL_CUSTOMER_ORDER_SQ.nextval,RRL_CUSTOMER_ORDER_ROW_SQ.nextval from dual");order,row=q.fetchone()
                q.execute("insert into RRL_CUSTOMER_ORDER(CUSTOMER_ORDER_ID,ORDER_NO,CUSTOMER_ID,WARE_ID,SHIPMENT_DATE,STATUS,SOURCE_SYSTEM,CREATED_BY)values(:o,:code,:c,:w,to_date('2026-10-22','YYYY-MM-DD'),'OPEN','QA_TRADECASE_ONLY','admin')", o=order,code=tag,c=s["customer"],w=w)
                q.execute("insert into RRL_CUSTOMER_ORDER_ROW(CUSTOMER_ORDER_ROW_ID,CUSTOMER_ORDER_ID,LINE_NO,ARTICUL,PRODUCT_NAME,UNIT_CODE,ORDER_QTY,WARE_ID,STATUS,CREATED_BY)values(:r,:o,1,:a,'Factory CASE QA','EA',2,:w,'OPEN','admin')", r=row,o=order,a=s["article"],w=w);conn.commit()
            finally:q.callproc("RRL_STOCK_METADATA_TX.end_change")
        s.update(native_order=order,native_row=row);save()
    step("binding", base+"/orders/"+tag+".ORDER/binding", dict(operation_id=tag+".bind", expected_order_version=1,
        customer_order_id=s["native_order"], lines=[dict(line_id="1", customer_order_row_id=s["native_row"])]))
    if "plan" not in s:s["plan"] = step("plan_created", "/api/picking/plans", dict(operation_id=tag+".plan", customer_order_id=s["native_order"]))["pick_plan_id"];save()
    if "wave" not in s:s["wave"] = step("wave_created", "/api/picking/waves", dict(wave_code=tag, wave_name="Factory CASE QA", ware_id=w,
        planned_start_at="2026-10-22T08:00:00+03:00", planned_finish_at="2026-10-22T09:00:00+03:00"))["pick_wave_id"];save()
    wave = f"/api/picking/waves/{s['wave']}"
    for key, suffix, body in [("added", "/plans", dict(pick_plan_id=s["plan"])), ("calculated", "/calculate", {}), ("launched", "/launch", dict(operation_id=tag+".launch"))]:
        step(key, wave+suffix, body)
    with oracle_connection() as conn:
        q=conn.cursor();q.execute("select TASK_ID,UID_PALLET,FROM_CELL,TO_CELL,QTY from RRL_WAREHOUSE_TASK where TASK_SOURCE='WAVE'and SOURCE_DOC_ID=:w and TASK_TYPE='REPLENISHMENT'",w=s["wave"])
        tasks=q.fetchall();s["replenishments"]=[list(x)for x in tasks];save()
    for tid,pallet,src,dst,qty in tasks:
        step("repl_"+str(tid),f"/api/warehouse-tasks/{tid}/complete",dict(operation_id=tag+".repl."+str(tid),scanned_pallet=pallet,scanned_from_cell=src,scanned_to_cell=dst,fact_qty=str(qty)))
    step("released",wave+"/release-picking",dict(operation_id=tag+".release"))
    with oracle_connection()as conn:
        q=conn.cursor();q.execute("select CASE_PICK_TASK_ID,CASE_PICK_LINE_ID,PICK_TASK_ID from RRL_CASE_PICK_LINE where PICK_WAVE_ID=:w",w=s["wave"])
        rows=q.fetchall();assert len(rows)==1,rows;s["case"],s["line"],s["pick_task"]=rows[0]
        q.execute("select RRL_TRADE_CASE_ACCESS.execution_allowed(:t,'admin')from dual",t=s["case"]);s.setdefault("admission_before",q.fetchone()[0]);save()
    print(json.dumps({k:s[k]for k in ["warehouse_id","case","line","wave","admission_before"]}))


def start():
    assert "case" in s
    case = f"/api/case-pick/tasks/{s['case']}"
    with oracle_connection()as conn:
        q=conn.cursor();q.execute("select RRL_TRADE_CASE_ACCESS.execution_allowed(:t,'admin')from dual",t=s["case"]);assert q.fetchone()[0]==1
        if "actor" not in s:
            actor="FC21"+uuid4().hex[:9];password=secrets.token_hex(24)
            q.execute("insert into RUSERS(ID,PASS,NAME,USER_GROUP,WARE_ID,DELETED,PRAVO_ADMIN_LOGIN)values(:a,:p,'Factory CASE QA','TC03QA',:w,0,1)",a=actor,p=password,w=w)
            q.execute("insert into RRL_ACCESS_ROLE(ROLE_ID,TITLE,ACTIVE,VERSION_NO)values(:a,'Factory CASE QA',1,1)",a=actor)
            for permission in ["case_pick_execute","case_pick_view"]:q.execute("insert into RRL_ACCESS_ROLE_RIGHT(ROLE_ID,PERMISSION)values(:a,:p)",a=actor,p=permission)
            q.execute("insert into RRL_ACCESS_ASSIGNMENT(ASSIGNMENT_ID,USERNAME,ROLE_ID,SCOPE_KIND,SCOPE_ID,MEMBERSHIP,VALID_FROM,VALID_UNTIL,ASSIGNED_BY,REASON,VERSION_NO)values(:a,:a,:a,'WAREHOUSE',:w,'CURRENT',systimestamp-interval '1'minute,systimestamp+interval '4'hour,'admin','Factory BOX piece CASE acceptance',1)",a=actor,w=str(w));conn.commit();s["actor"]=actor;save()
        q.execute("select PASS from RUSERS where ID=:a and nvl(DELETED,0)=0",a=s["actor"]);row=q.fetchone();assert row,"Do not reactivate retired QA actor";password=row[0]
        # The native CASE transit cell belongs to this isolated warehouse.
        cell="CPT_"+str(w);q.execute("select count(*)from RRL_CELLS where CELL=:c",c=cell)
        if not q.fetchone()[0]:
            q.callproc("RRL_STOCK_CONFIG_API.begin_change",["admin","warehouse_settings_edit"])
            try:
                q.execute("insert into RRL_CELLS(CELL,WARE_ID,X,Y,Z,OTBOR,IS_SYSTEM,LIMIT_WEIGHT,LIMIT_HEIGHT)values(:c,:w,0,0,0,0,1,0,0)",c=cell,w=w)
                q.execute("insert into RRL_STOCK_POLICY_GUARD(POLICY_KEY,LOCK_ID)select RRL_STOCK_LOCK_API.resource_key('CELL',:c),nvl(max(LOCK_ID),900000000)+1 from RRL_STOCK_POLICY_GUARD",c=cell);conn.commit()
            finally:q.callproc("RRL_STOCK_CONFIG_API.end_change")
    actor=s["actor"]
    def own(method,path,body=None):return http(method,path,body,actor,password)
    step("cpt_policy",base+"/stock/cells/CPT_"+str(w),dict(operation_id=tag+".cpt",expected_version=0,zone_kind="SORT",reason="Factory CASE transit cell"),"PUT")
    step("owner",base+"/stock/owner-grants",dict(operation_id=tag+".owner",expected_version=0,username=actor,owner_id="SNS",can_view=True,can_operate=True,reason="Factory CASE owner scoped execution"),"PUT")
    now=datetime.now(ZoneInfo("Europe/Moscow"));day=now.date().isoformat()
    shift=step("shift","/api/resources/shifts",dict(shift_code=tag,shift_date=day,start_at=day+"T00:00:00+03:00",finish_at=day+"T23:59:59+03:00",ware_id=w,status="OPEN"))["id"]
    resource=step("resource","/api/resources",dict(resource_code=tag,resource_name="Factory CASE QA",resource_type="CASE_PICKER",resource_class="PERSON",user_id=actor,ware_id=w))["id"]
    step("qualification",f"/api/resources/{resource}/qualifications",dict(task_type="CASE_PICK",active=True),"PUT")
    session=step("session","/api/resources/sessions/login",dict(shift_id=shift,resource_id=resource,operator_user_id=actor,terminal_id="QA_NOT_HARDWARE"))["id"]
    step("tare_count","/api/inventory/tare/count",dict(operation_id=tag+".tare.count",owner_ware_id=w,pallet_type_id=s.get("pallet_type_id",1),condition="GOOD",observed_quantity="1",expected_version=0,reason="Synthetic fixture, not physical tare survey",decision_reference="TEST_FIXTURE_NOT_HARDWARE:"+tag))
    step("tare_book","/api/inventory/tare/book",dict(operation_id=tag+".tare.book",place_kind="CASE",place_id=str(s["case"]),expected_warehouse_id=w,pallet_type_id=s.get("pallet_type_id",1)))
    for action in ["CLAIM","START"]:
        if action not in s:
            ctx=expect(200,own("GET",case+"/resource-context"))
            step(action,case+"/resource-commands",dict(operation_id=tag+"."+action,action=action,expected_assignment_version=ctx["assignment_version"],resource_session_id=session,resource_id=resource,reason="Factory BOX profile piece CASE proof"),actor=actor,password=password)
    return actor,password,case,resource,session


def execute(return_after=True):
    actor,password,case,resource,session=start()
    def own(method,path,body=None):return http(method,path,body,actor,password)
    if "pick_body" not in s:
        with oracle_connection()as conn:
            q=conn.cursor();q.execute("select c.SYSTEM_CODE,c.RAW_CODE from RRL_WMS_RECEIPT_UNIT u join RRL_WMS_RECEIPT_CODE c on c.UID_PALLET=u.UID_PALLET and c.UNIT_ID=u.UNIT_ID join RRL_STOCK_RESERVATION r on r.RESERVATION_ID=u.HARD_RESERVATION_ID where r.SOURCE_DOC_TYPE='PICK_WAVE'and r.SOURCE_LINE_ID=:p and r.STATUS in('ACTIVE','ALLOCATED','PICKING')",p=s["pick_task"])
            scans=[dict(system_code=system,profile_code="TOBACCO",code=raw.read()if hasattr(raw,"read")else raw)for system,raw in q];assert len(scans)==2
            q.execute("select SSCC from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=:t",t=s["case"]);carrier=q.fetchone()[0]
        s["pick_body"]=dict(operation_id=tag+".pick",fact_qty="2",scan_cell=s["pick"],scan_product=s["article"],scan_container=carrier,resource_id=resource,resource_session_id=session,unit_scans=scans);save()
    step("picked",case+f"/lines/{s['line']}/confirm",s["pick_body"],actor=actor,password=password)
    assert expect(200,own("POST",case+f"/lines/{s['line']}/confirm",s["pick_body"]))==s["picked"]
    if "close_body" not in s:
        with oracle_connection()as conn:
            q=conn.cursor();q.execute("select CONTENT_VERSION from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=:t",t=s["case"])
            s["close_body"]=dict(operation_id=tag+".close",expected_content_version=q.fetchone()[0]);save()
    step("closed",case+"/close-current",s["close_body"],actor=actor,password=password)
    if not return_after:return
    with oracle_connection()as conn:
        q=conn.cursor();q.execute("select SSCC,CONTENT_VERSION from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=:t",t=s["case"]);carrier,version=q.fetchone()
        q.execute("select lot.LOT_UID,l.CELL_CODE from RRL_CASE_CARRIER_LOT lot join RRL_CASE_PICK_LINE l on l.CASE_PICK_LINE_ID=lot.CASE_PICK_LINE_ID where lot.CASE_PICK_TASK_ID=:t",t=s["case"]);destinations=dict(q.fetchall())
    step("returned",case+"/return-carrier",dict(operation_id=tag+".return",scan_container=carrier,expected_content_version=version,destinations=destinations))
    step("logout",f"/api/resources/sessions/{session}/logout",dict(reason="Factory CASE verification complete"))
    # Disable grants while the test identity is still active; the current grant API rejects deleted users.
    step("cleanup_owner",base+"/stock/owner-grants",dict(operation_id=tag+".cleanup.owner",expected_version=1,
        username=actor,owner_id="SNS",can_view=False,can_operate=False,reason="Retire factory CASE owner access"),"PUT")
    step("cleanup_qualification",f"/api/resources/{resource}/qualifications",dict(task_type="CASE_PICK",active=False),"PUT")
    with oracle_connection()as conn:
        q=conn.cursor();q.execute("select sum(r.REMAIN),sum(r.HARD_RESERVED_BASE)from RRL_REMAINS r join RRL_CELLS c on c.CELL=r.CELL where c.WARE_ID=:w",w=w);s["physical_after"]=list(q.fetchone());assert s["physical_after"]==[10,0]
        q.execute("select count(*)from user_objects where STATUS='INVALID'");assert q.fetchone()[0]==0
        q.execute("update RUSERS set DELETED=1 where ID=:a and USER_GROUP='TC03QA'",a=actor)
        q.execute("update RRL_ACCESS_ASSIGNMENT set REVOKED_AT=systimestamp where ASSIGNMENT_ID=:a",a=actor);conn.commit()
    s["status"]="PASS";save()


if __name__=="__main__":
    os.environ.setdefault("TRADECASE_ADMIN_USER","admin")
    os.environ.setdefault("TRADECASE_ADMIN_PASSWORD",re.search(r"PASS=(\S+?)[`,)\s]",(ROOT/"AGENTS.md").read_text(encoding="utf-8"))[1])
    try:
        verify_fixture()
        if "--execute"in sys.argv:execute()
        else:prepare()
    except Exception as exc:s["error"]=str(exc);s["status"]="FAIL";raise
    finally:s["history"]+=CALLS;save()
