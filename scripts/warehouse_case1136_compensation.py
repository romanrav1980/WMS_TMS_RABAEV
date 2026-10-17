"""Root-review-only fixed TEST1136 compensation and historical scoped replay.
Default prepares immutable local commands from current native facts, no DB writes.
Execution requires explicit root flags/env; each Stock command uses a fresh owner TX.
Never merge parent/child UIDs, invent hardware, change protected rows or reset histories.
"""
import argparse
import hashlib
import json
import os
import sys
from pathlib import Path
from typing import Any
import oracledb
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/"scripts"),str(ROOT/"api/wms_api_server")]
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment()
from app.oracle_gateway import OracleGateway
from app.db import oracle_connection
from app.modules.inventory.public import StockCommand,StockPosting
from app.modules.resources.infrastructure.case_resource_commands import oracle_json
from app.services.resource_management_service import ResourceManagementService
from app.schemas import ResourceSessionStatusRequest,RightsGrantRequest
from app.routers.admin_rights import revoke_group_right,grant_group_right
from app.auth import AdminUser

REPORT=ROOT/"reports/retailcase/2026-10-15/warehouse-weigh-request/root-compensation1136.json"
ACTOR="WHREQ15.OP";SOURCE="REUSE.RETURN:e6c16d0bbd";CHILD="CASELOT:E8EAB9A962B9D19BA5AC8FCEE19D8021895BD0:1"
WARE=13583852;ORIGINAL="WHREQ15.ASM.PICK1136";PREFIX="WHREQ15.COMPENSATE1136"
NOTE="SIMULATED_TEST_NOT_HARDWARE; root-reviewed canonical compensation; preserve UID lineage/history"


def save(report:dict[str,Any])->None:
    REPORT.parent.mkdir(parents=True,exist_ok=True);REPORT.write_text(json.dumps(report,indent=2,default=str),encoding="utf-8")


def state(g:Any)->dict[str,Any]:
    return dict(case=g.fetch_all("select CASE_PICK_TASK_ID,STATUS,CONTENT_VERSION,ASSIGNMENT_VERSION,PICKED_QTY,SSCC,LEGACY_SBORKA_PALLET_ID,RESOURCE_SESSION_ID from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=1136"),
        stock=g.fetch_all("select r.UID_POLETA,r.CELL,r.REMAIN,r.HARD_RESERVED_BASE,r.STOCK_VERSION,p.STOCK_ORIGIN_UID,p.CREATED_BY_STOCK_OP from RRL_REMAINS r join RRL_PALLETS p on p.UID_PALLET=r.UID_POLETA where r.UID_POLETA in(:source,:child)order by r.UID_POLETA,r.CELL",{"source":SOURCE,"child":CHILD}),
        carrier=g.fetch_all("select LOT_UID from RRL_CASE_CARRIER_LOT where CASE_PICK_TASK_ID=1136"),
        fulfillment=g.fetch_all("select FULFILLMENT_ID,STATUS,FACT_QTY,PICKED_CASE_TASK_ID,PICKED_CONTENT_VERSION from RRL_CUSTOMER_ORDER_FULFILLMENT where FULFILLMENT_ID=190"),
        assembly=g.fetch_all("select SESSION_ID,STATE,FINAL_CAPTURE_KEY from RRL_ASSEMBLY_SESSION where SESSION_ID='WHREQ15.ASM.S1136'"),
        tare=g.fetch_all("select PHYSICAL_QTY,ASSEMBLY_QTY,AVAILABLE_QTY,BALANCE_VERSION from RRL_TARE_AVAILABILITY where OWNER_WARE_ID=13583852 and PALLET_TYPE_ID=32"),
        session=g.fetch_all("select SESSION_ID,STATUS from RRL_RESOURCE_SESSION where SESSION_ID=54"),
        wave=g.fetch_all("select STATUS from RRL_PICK_WAVE where PICK_WAVE_ID=567"),
        plan=g.fetch_all("select STATUS from RRL_PICK_PLAN where PICK_PLAN_ID=2199"),
        active_stock_hard=g.fetch_all("select RESERVATION_ID,BASE_QTY,STATUS from RRL_STOCK_RESERVATION where SOURCE_DOC_TYPE='PICK_WAVE'and SOURCE_DOC_ID=567 and STATUS in('ACTIVE','ALLOCATED','PICKING')and BASE_QTY>0"),
        active_legacy_plan=g.fetch_all("select PICK_RESERVATION_ID,RESERVATION_STATUS,RESERVED_QTY from RRL_PICK_RESERVATION where PICK_PLAN_ID=2199 and RESERVATION_STATUS in('ACTIVE','ALLOCATED','PICKING')"),
        active_legacy_wave=g.fetch_all("select PICK_WAVE_RESERVATION_ID,RESERVATION_STATUS,RESERVED_QTY from RRL_PICK_WAVE_RESERVATION where PICK_WAVE_ID=567 and RESERVATION_STATUS in('ACTIVE','ALLOCATED','PICKING')"),
        events=g.fetch_all("select count(*)N from RRL_CASE_PICK_EVENT where CASE_PICK_TASK_ID=1136"))


def command(kind:str,operation:str,source:dict[str,Any],metadata:dict[str,Any])->StockCommand:
    return StockCommand(operation,kind,"admin",(),source,metadata=metadata)


def freeze(report:dict[str,Any],key:str,cmd:StockCommand)->StockCommand:
    wire=cmd.canonical_json();saved=report.setdefault("commands",{}).get(key)
    if saved is None:
        report["commands"][key]={"canonical_request":wire,"sha256":hashlib.sha256(wire.encode()).hexdigest()};save(report)
    else:assert saved["canonical_request"]==wire,"Do not alter original immutable command intent"
    return cmd


def from_frozen(report:dict[str,Any],key:str)->StockCommand:
    wire=report["commands"][key]["canonical_request"];d=json.loads(wire)
    cmd=command(d["command_type"],d["operation_id"],d["source"],d["metadata"])
    assert cmd.canonical_json()==wire and hashlib.sha256(wire.encode()).hexdigest()==report["commands"][key]["sha256"]
    return cmd


def returned(s:dict[str,Any])->None:
    positive=[r for r in s["stock"]if r["remain"]>0]
    assert len(positive)==2 and sum(r["remain"]for r in positive)==24 and sum(r["hard_reserved_base"]for r in positive)==0
    assert all(r["cell"]=="QIPcdbf4c0962"and r["stock_origin_uid"]=="300000034518661218"for r in positive)
    assert {r["uid_poleta"]:r["remain"]for r in positive}=={SOURCE:23,CHILD:1}
    assert next(r for r in positive if r["uid_poleta"]==CHILD)["created_by_stock_op"]==ORIGINAL
    assert not s["carrier"]and s["case"][0]["status"]=="CANCELLED"and s["case"][0]["legacy_sborka_pallet_id"]is None
    f=s["fulfillment"][0];assert f["status"]=="PLANNED"and f["fact_qty"]==0 and f["picked_case_task_id"]is None


def native_trial(g:Any,cmd:StockCommand,report:dict[str,Any])->None:
    before=state(g)
    with oracle_connection()as conn:
        c=conn.cursor()
        try:
            out=c.var(oracledb.DB_TYPE_CLOB);c.callproc("RRL_STOCK_POSTING_API.prepare_command",[cmd.canonical_json(),cmd.actor,out])
            if out.getvalue()is None:c.callproc("RRL_STOCK_POSTING_API.execute_prepared",[out])
            report["return_caller_rollback_result"]=oracle_json(out.getvalue())
            c.execute("select sum(REMAIN),sum(HARD_RESERVED_BASE)from RRL_REMAINS where UID_POLETA in(:source,:child)and CELL='QIPcdbf4c0962'",source=SOURCE,child=CHILD);assert c.fetchone()==(24,0)
            c.execute("select STATUS from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=1136");assert c.fetchone()[0]=="CANCELLED"
        finally:conn.rollback();c.callproc("RRL_STOCK_POSTING_API.reset_connection")
    assert state(g)==before,"RETURN trial leaked a fact"
    assert not g.fetch_all("select OPERATION_ID from RRL_STOCK_OPERATION where OPERATION_ID=:op",{"op":cmd.operation_id})
    assert not g.fetch_all("select OPERATION_ID from RRL_STOCK_OP_CLOCK where OPERATION_ID=:op",{"op":cmd.operation_id})
    assert not g.fetch_all("select IDEMPOTENCY_KEY from RRL_EVENT_OUTBOX where IDEMPOTENCY_KEY=:key",{"key":"STOCK:"+hashlib.sha256(cmd.operation_id.encode()).hexdigest().upper()})
    report["return_caller_rollback"]="PASS exact scoped source/CASE/fulfillment/tare/session/events restored; stock operation/clock/outbox absent";save(report)


def replay_trial(g:Any,report:dict[str,Any])->None:
    # Root explicitly authorizes temporary flat revoke/restore, immutable original replay caller rollback only.
    admin=AdminUser(username="admin",display_name="Root reviewed TEST replay",user_group="GLOBAL_ADMIN",permissions={"*"})
    # Gateway decodes JSON CLOBs to dict: fetch original raw CLOB directly, never reserialize.
    with oracle_connection()as read_conn:
        read_cursor=read_conn.cursor()
        read_cursor.execute("select dbms_lob.getlength(CANONICAL_REQUEST),dbms_lob.substr(CANONICAL_REQUEST,30000,1),RESULT_JSON,ACTOR,STATE,REQUEST_HASH from RRL_STOCK_OPERATION where OPERATION_ID=:op",op=ORIGINAL)
        raw=read_cursor.fetchone();assert raw and raw[3]==ACTOR and raw[4]=="APPLIED"
        wire=raw[1];assert isinstance(wire,str)and raw[0]<=30000 and len(wire)==raw[0],"Exact bounded original canonical VARCHAR2 expression required"
        assert hashlib.sha256(wire.encode("utf-8")).hexdigest().upper()==raw[5].upper(),"Original request hash must match exact text"
        saved=oracle_json(raw[2]);read_conn.rollback()
    before=state(g);assert before["assembly"][0]["state"]=="FINALIZED"
    flat=g.fetch_all("select RRL_HAS_WRIGHT(:a,'case_pick_execute')N from dual",{"a":ACTOR})[0]["n"];assert flat==1
    try:
        report["flat_revoke"]=revoke_group_right("WHREQ15.OP","case_pick_execute",admin);save(report)
        eligibility=g.fetch_all("select RRL_HAS_WRIGHT(:a,'case_pick_execute')F,RRL_CASE_TASK_ACCESS.has_current_scoped_execute(1136,:a)R,RRL_CASE_TASK_ACCESS.scoped_executor(1136,:a)E from dual",{"a":ACTOR})[0]
        assert eligibility["f"]==0 and eligibility["r"]==1,eligibility
        with oracle_connection()as conn:
            c=conn.cursor()
            try:
                out=c.var(oracledb.DB_TYPE_CLOB);c.callproc("RRL_STOCK_POSTING_API.prepare_command",[wire,ACTOR,out])
                assert out.getvalue()is not None,"Historical APPLIED replay must not compile/execute new stock"
                assert oracle_json(out.getvalue())==saved
            finally:conn.rollback();c.callproc("RRL_STOCK_POSTING_API.reset_connection")
        assert state(g)==before
        report["scoped_original_replay"]={"status":"PASS","original_operation":ORIGINAL,"canonical_sha256":hashlib.sha256(wire.encode()).hexdigest(),"ordinary_scoped_helper":eligibility["e"],"helper_scope":"Ordinary type eligibility only, not full new-command authorization; canonical WAIT_CONTROL/status guards preserved; no new command attempted","current_scope":eligibility,"caller_rollback":True,"quantity_effects":0};save(report)
    finally:
        report["flat_restore"]=grant_group_right("WHREQ15.OP",RightsGrantRequest(right_name="case_pick_execute",description=NOTE),admin);save(report)


def execute(g:Any,report:dict[str,Any])->None:
    assert state(g)["assembly"][0]["state"]=="FINALIZED","Root must complete actual FINAL first"
    cmd=from_frozen(report,"return")
    exists=g.fetch_all("select STATE from RRL_STOCK_OPERATION where OPERATION_ID=:op",{"op":cmd.operation_id})
    if not exists:native_trial(g,cmd,report)
    report["return"]=StockPosting().post(cmd);save(report);returned(state(g))
    # Distinct clean StockPosting owner transactions; never chain native prepare in one dirty TX.
    for key,kind,source,metadata in [("wave_cancel","WAVE_CANCEL",{"document_type":"PICK_WAVE","document_id":567},{"reason":NOTE,"only_cancelled_replenishment":0,"reservation_kind":None}),("plan_cancel","PICK_PLAN_CANCEL",{"document_type":"PICK_PLAN","document_id":2199},{"reason":NOTE,"only_cancelled_replenishment":0,"reservation_kind":None}),("book_cancel","TARE_BOOK_CANCEL",{"booking_operation_id":"WHREQ15.AK06.TARE.BOOK"},{})]:
        cmd=freeze(report,key,command(kind,PREFIX+"."+key.upper(),source,metadata));report[key]=StockPosting().post(cmd);save(report)
    tare=state(g)["tare"][0]
    if "tare_count"not in report.get("commands",{}):
        assert(tare["physical_qty"],tare["assembly_qty"],tare["available_qty"])==(1,0,1)
        assert not g.fetch_all("select OPERATION_ID from RRL_TARE_BOOK where OWNER_WARE_ID=13583852 and PALLET_TYPE_ID=32 and STATUS='HELD'")
        freeze(report,"tare_count",command("TARE_COUNT",PREFIX+".TARE.COUNT0",{},{"owner_ware_id":WARE,"pallet_type_id":32,"condition":"GOOD","observed_quantity":"0","expected_version":int(tare["balance_version"]),"reason":NOTE,"decision_reference":"TEST_WHREQ15_COMPENSATION"}))
    report["tare_count"]=StockPosting().post(from_frozen(report,"tare_count"));save(report)
    current=state(g)
    if current["session"][0]["status"]!="CLOSED":ResourceManagementService(g).logout_session(54,ResourceSessionStatusRequest(updated_by="admin"))
    report["after"]=state(g);returned(report["after"])
    assert report["after"]["tare"][0]["physical_qty"]==0 and report["after"]["tare"][0]["assembly_qty"]==0 and report["after"]["session"][0]["status"]=="CLOSED"
    assert report["after"]["wave"]==[{"status":"CANCELLED"}]and report["after"]["plan"]==[{"status":"CANCELLED"}]
    assert not report["after"]["active_stock_hard"]and not report["after"]["active_legacy_plan"]and not report["after"]["active_legacy_wave"]
    assert not g.fetch_all("select OPERATION_ID from RRL_TARE_BOOK where PLACE_KIND='CASE'and PLACE_ID='1136'and STATUS='HELD'")
    report["status"]="CANONICAL_COMPENSATED_TEST_HISTORY_RETAINED";report["retained"]="ST641520/row16727999/fulfillment190, TYPE32/SSCC/start/version/captures/ASM_FINALIZED/events; no known metadata cancellation owner, no direct DML";save(report)


def main()->None:
    parser=argparse.ArgumentParser();parser.add_argument("--root-reviewed-execute",action="store_true");parser.add_argument("--root-reviewed-replay-rollback",action="store_true");args=parser.parse_args();g=OracleGateway()
    report=json.loads(REPORT.read_text(encoding="utf-8"))if REPORT.exists()else dict(status="PREPARED_NOT_EXECUTED",before=state(g),hardware_verified=False)
    if "return"not in report.get("commands",{}):
        s=state(g);t=s["case"][0];assert t["status"]=="WAIT_CONTROL"and t["content_version"]==3 and t["picked_qty"]==1 and t["legacy_sborka_pallet_id"]==641520
        assert s["carrier"]==[{"lot_uid":CHILD}]
        freeze(report,"return",command("CASE_CARRIER_RETURN",PREFIX+".RETURN",{"case_task_id":1136},{"destinations":{CHILD:"QIPcdbf4c0962"},"expected_content_version":3,"scan_container":t["sscc"],"reason":NOTE}))
    if args.root_reviewed_execute or args.root_reviewed_replay_rollback:
        assert os.environ.get("RUN_ROOT_REVIEWED_1136_COMPENSATION")=="1","Root review env opt-in required"
        if args.root_reviewed_replay_rollback:replay_trial(g,report)
        if args.root_reviewed_execute:execute(g,report)
    save(report);print(json.dumps({"status":report["status"],"report":str(REPORT.relative_to(ROOT)),"executed":args.root_reviewed_execute,"replay_trial":args.root_reviewed_replay_rollback}))


if __name__=="__main__":main()
