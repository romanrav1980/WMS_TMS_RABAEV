"""Explicit root-approved fresh CRES15 metadata/tare/reserve fixture; no goods PICK.
Requires ZERO-owner window release. Fixed existing parent23/source/QIP; retain all journals.
"""
import json
import os
import secrets
import sys
import oracledb
from datetime import datetime,timedelta,timezone
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/"scripts"),str(ROOT/"api/wms_api_server")]
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment()
from app.oracle_gateway import OracleGateway
from app.db import oracle_connection
from app.modules.resources.contracts_case_resource import CaseResourceCommand
from app.modules.resources.infrastructure.case_resource_commands import canonical
from app.modules.inventory.public import StockCommand,StockPosting
from app.modules.platform.public import stock_configuration_transaction,AccessMetadataService
from app.modules.platform.api.metadata_inputs import Command,normalize
from app.services.picking_service import PickingService
from app.services.resource_management_service import ResourceManagementService
from app.schemas import PickWaveActionRequest,ResourceCreateRequest,ResourceShiftCreateRequest,ResourceSessionLoginRequest,RightsGrantRequest
from app.modules.resources.infrastructure.qualification_admin import QualificationAdmin
from app.routers.admin_rights import grant_group_right,revoke_group_right
from app.auth import AdminUser
from app.modules.inventory.infrastructure.configuration import ReceiptConfiguration
from app.modules.inventory.infrastructure.case_labels import CaseLabels
from app.modules.inventory.contracts_case_labels import CaseSsccLabelRequest
from wave_launch_continuation_case import create_demand

WARE=13583852;SOURCE="REUSE.RETURN:e6c16d0bbd";CELL="QIPcdbf4c0962";ARTICLE="REUSE.QA:cdbf4c0962"
ACTOR="CRES15.OP";PREFIX="CRES15.AK06";NOTE="SIMULATED_TEST_LABEL_NOT_PHYSICAL; TEST_FIXTURE_NOT_HARDWARE CRES15 metadata proof"
REPORT=ROOT/"reports/retailcase/2026-10-15/case-resource-commands/fixture.json"


def save(x:dict[str,Any])->None:
    REPORT.parent.mkdir(parents=True,exist_ok=True);REPORT.write_text(json.dumps(x,indent=2,default=str),encoding="utf-8")


def post(kind:str,op:str,source:dict[str,Any],metadata:dict[str,Any])->dict[str,Any]:
    return StockPosting().post(StockCommand(op,kind,"admin",(),source,metadata=metadata))


def access(g:Any,op:str,kind:str,payload:dict[str,Any])->dict[str,Any]:
    return AccessMetadataService(g).command("admin",normalize(Command(operation_id=op,command_type=kind,payload=payload),"ACCESS"))


def metadata(g:Any,x:dict[str,Any])->None:
    password=secrets.token_urlsafe(24)
    private=ROOT/"runtime/case-resource-qa-secrets.json";private.parent.mkdir(exist_ok=True);private.write_text(json.dumps({ACTOR:password}),encoding="utf-8")
    prior=json.loads((ROOT/"reports/retailcase/2026-10-15/warehouse-weigh-request/fixture.json").read_text(encoding="utf-8"));x["face"]=prior["face"]
    assert g.fetch_all("select WARE_ID,CELL_CODE,ACTIVE from RRL_PICK_FACE where PICK_FACE_ID=:f",{"f":x["face"]})==[{"ware_id":WARE,"cell_code":CELL,"active":1}]
    with stock_configuration_transaction(g,NOTE,"admin","warehouse_settings_edit")as c:
        for key,sequence in [("order","RRL_CUSTOMER_ORDER_SQ"),("order_row","RRL_CUSTOMER_ORDER_ROW_SQ"),("plan","RRL_PICK_PLAN_SQ"),("line","RRL_PICK_PLAN_LINE_SQ"),("task","RRL_PICK_TASK_SQ"),("reservation","RRL_PICK_RESERVATION_SQ"),("wave","RRL_PICK_WAVE_SQ"),("wave_order","RRL_PICK_WAVE_ORDER_SQ")]:
            c.execute("select "+sequence+".nextval from dual");x[key]=int(c.fetchone()[0])
        c.execute("insert into RUSERS(ID,NAME,PASS,USER_GROUP,WARE_ID,DELETED,PRAVO_ADMIN_LOGIN)values(:id,:name,:pw,:grp,:w,0,0)",id=ACTOR,name=NOTE,pw=password,grp=ACTOR,w=WARE)
        create_demand(c,x)
    x["metadata_created"]=True;save(x)


def resources(g:Any,x:dict[str,Any])->None:
    admin=AdminUser(username="admin",display_name="Root TEST owner",user_group="GLOBAL_ADMIN",permissions={"*"})
    x["temporary_flat"]=grant_group_right(ACTOR,RightsGrantRequest(right_name="case_pick_execute",description=NOTE),admin);save(x)
    service=ResourceManagementService(g)
    x["resource_id"]=service.create_resource(ResourceCreateRequest(resource_code="CRES15.CASE",resource_name=NOTE,resource_type="CASE_PICKER",user_id=ACTOR,ware_id=WARE,created_by="admin"));save(x)
    x["qualification"]=QualificationAdmin(g).set_qualification(x["resource_id"],"CASE_PICK",True,"admin");save(x)
    now=datetime.now(ZoneInfo("Europe/Moscow"))
    x["shift_id"]=service.create_shift(ResourceShiftCreateRequest(shift_code="CRES15.CASE",shift_date=now.date(),start_at=now-timedelta(minutes=1),finish_at=now+timedelta(hours=3),ware_id=WARE,status="OPEN",created_by="admin"));save(x)
    x["session_id"]=service.login_session(ResourceSessionLoginRequest(shift_id=x["shift_id"],resource_id=x["resource_id"],operator_user_id=ACTOR,terminal_id="TEST:CRES15",created_by="admin"));save(x)
    x["flat_revoked"]=revoke_group_right(ACTOR,"case_pick_execute",admin);save(x)
    x["role"]=access(g,PREFIX+".ROLE","ROLE_SAVE",dict(role_id="CRES15.CASE.EXEC",title=NOTE,permissions=["case_pick_execute"],active=True,expected_version=0));save(x)
    now=datetime.now(timezone.utc);x["assignment_until"]=(now+timedelta(hours=3)).isoformat()
    for scope,suffix,scope_id in [("SELF","SELF",None)]:
        x["grant_"+suffix]=access(g,PREFIX+".ASSIGN."+suffix,"ASSIGN",dict(assignment_id="CRES15."+suffix,username=ACTOR,role_id="CRES15.CASE.EXEC",scope_kind=scope,scope_id=scope_id,valid_from=(now-timedelta(minutes=1)).isoformat(),valid_until=x["assignment_until"],expected_version=0,reason=NOTE));save(x)


def launch(g:Any,x:dict[str,Any])->None:
    service=PickingService(g);service.preview_wave(x["wave"],PickWaveActionRequest(updated_by="admin"))
    x["launch"]=service.launch_wave(x["wave"],PickWaveActionRequest(updated_by="admin",operation_id=PREFIX+".LAUNCH"));save(x)
    physical=g.fetch_all("select TASK_ID,STATUS from RRL_WAREHOUSE_TASK where SOURCE_DOC_TYPE='PICK_WAVE'and SOURCE_DOC_ID=:w",{"w":x["wave"]});x["warehouse_tasks"]=physical;save(x)
    if physical:
        x["abort_wave"]=post("WAVE_CANCEL",PREFIX+".ABORT.WAVE",{"document_type":"PICK_WAVE","document_id":x["wave"]},{"reason":NOTE,"only_cancelled_replenishment":0,"reservation_kind":None});save(x)
        raise RuntimeError("Unexpected physical warehouse task; aborted wave, do not continue")
    cases=g.fetch_all("select CASE_PICK_TASK_ID,CONTENT_VERSION,SSCC,STATUS,PICKED_QTY from RRL_CASE_PICK_TASK where PICK_WAVE_ID=:w",{"w":x["wave"]});assert len(cases)==1 and cases[0]["status"]=="NEW"and cases[0]["picked_qty"]==0
    x["task_id"]=cases[0]["case_pick_task_id"];x["case_before_type"]=cases[0];save(x)
    lines=g.fetch_all("select CASE_PICK_LINE_ID,CELL_CODE,ARTICUL,PLANNED_QTY,PICKED_QTY from RRL_CASE_PICK_LINE where CASE_PICK_TASK_ID=:t",{"t":x["task_id"]});assert len(lines)==1 and lines[0]["cell_code"]==CELL and lines[0]["planned_qty"]==1 and lines[0]["picked_qty"]==0
    x["case_line_id"]=lines[0]["case_pick_line_id"];save(x)
    x["pick_release"]=post("WAVE_PICK_RELEASE",PREFIX+".RELEASE",{"wave_id":x["wave"]},{});save(x)


def warehouse_grant(g:Any,x:dict[str,Any])->None:
    assert g.fetch_all("select RRL_HAS_WRIGHT(:a,'case_pick_execute')F,RRL_CASE_TASK_ACCESS.scoped_metadata_actor(:t,'CLAIM',:a)S from dual",{"a":ACTOR,"t":x["task_id"]})==[{"f":0,"s":0}]
    body=CaseResourceCommand(operation_id=PREFIX+".SELF.DENY",action="CLAIM",expected_assignment_version=0,resource_session_id=x["session_id"],reason=NOTE)
    with oracle_connection()as conn:
        c=conn.cursor()
        try:
            out=c.var(oracledb.DB_TYPE_CLOB)
            try:c.callproc("RRL_CASE_ASSIGNMENT_API.execute_command",[x["task_id"],canonical(body),ACTOR,out])
            except oracledb.DatabaseError as error:assert error.args[0].code==20882,str(error)
            else:raise AssertionError("SELF granted unassigned CLAIM")
        finally:conn.rollback()
    x["self_unassigned_denied"]="Native403 callerrollback; no definitive receipt";save(x)
    now=datetime.now(timezone.utc)
    x["grant_WARE"]=access(g,PREFIX+".ASSIGN.WARE","ASSIGN",dict(assignment_id="CRES15.WARE",username=ACTOR,role_id="CRES15.CASE.EXEC",scope_kind="WAREHOUSE",scope_id=str(WARE),valid_from=(now-timedelta(minutes=1)).isoformat(),valid_until=x["assignment_until"],expected_version=0,reason=NOTE));save(x)


def tare_label(g:Any,x:dict[str,Any])->None:
    case=x["case_before_type"]
    x["type_change"]=post("CASE_PALLET_TYPE_CHANGE",PREFIX+".TYPE",{"case_task_id":x["task_id"]},{"expected_version":case["content_version"],"scan_container":case["sscc"],"pallet_type_id":32,"reason":NOTE});save(x)
    settings=ReceiptConfiguration(g);old=settings.get(WARE);x["warehouse_settings_before"]=old;save(x)
    try:
        settings.save(WARE,{**old,"company_prefix":"900000","extension_digit":0},"admin")
        current=g.fetch_all("select SSCC,CONTENT_VERSION from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=:t",{"t":x["task_id"]})[0]
        labels=CaseLabels(g);x["label"]=labels.issue(x["task_id"],CaseSsccLabelRequest(operation_id=PREFIX+".LABEL",scan_container=current["sscc"],expected_content_version=int(current["content_version"])),"admin");save(x)
        x["label_confirmation"]=labels.confirm(x["task_id"],x["label"]["sscc"],"admin");save(x)
    finally:settings.save(WARE,old,"admin")
    balance=g.fetch_all("select PHYSICAL_QTY,ASSEMBLY_QTY,AVAILABLE_QTY,BALANCE_VERSION from RRL_TARE_AVAILABILITY where OWNER_WARE_ID=:w and PALLET_TYPE_ID=32",{"w":WARE});assert len(balance)==1 and(balance[0]["physical_qty"],balance[0]["assembly_qty"],balance[0]["available_qty"])==(0,0,0)
    x["tare_count"]=post("TARE_COUNT",PREFIX+".TARE.COUNT",{},{"owner_ware_id":WARE,"pallet_type_id":32,"condition":"GOOD","observed_quantity":"1","expected_version":int(balance[0]["balance_version"]),"reason":NOTE,"decision_reference":"TEST_CRES15_NOT_HARDWARE"});save(x)
    x["tare_book"]=post("TARE_BOOK",PREFIX+".TARE.BOOK",{"place_kind":"CASE","place_id":str(x["task_id"])},{"pallet_type_id":32,"expected_warehouse_id":WARE});save(x)


def main()->None:
    assert os.environ.get("RUN_ROOT_APPROVED_CRES15_STAGE")=="1"and os.environ.get("ZERO_OWNER_WINDOW_RELEASED")=="1","Root stage+ZERO exclusivewindow release required"
    assert not REPORT.exists(),"Do not fork/recreate recorded fixture; inspect exact checkpoint before resume"
    g=OracleGateway();assert not g.fetch_all("select ID from RUSERS where ID=:a",{"a":ACTOR})
    before=g.fetch_all("select CELL,REMAIN,HARD_RESERVED_BASE,STOCK_VERSION from RRL_REMAINS where UID_POLETA=:s order by CELL",{"s":SOURCE});assert sum(r["remain"]for r in before)==23 and sum(r["hard_reserved_base"]for r in before)==0 and[r["cell"]for r in before if r["remain"]>0]==[CELL]
    x=dict(approved_case_resource_fixture=True,prefix=PREFIX,cell=CELL,actor=ACTOR,source=SOURCE,warehouse_id=WARE,source_before=before,hardware_verified=False,state="STAGING")
    metadata(g,x);resources(g,x);launch(g,x);warehouse_grant(g,x);tare_label(g,x)
    after=g.fetch_all("select CELL,REMAIN,HARD_RESERVED_BASE,STOCK_VERSION from RRL_REMAINS where UID_POLETA=:s order by CELL",{"s":SOURCE});assert sum(r["remain"]for r in after)==23 and sum(r["hard_reserved_base"]for r in after)==1
    assert g.fetch_all("select STATUS,ASSIGNED_TO,PICKED_QTY,ASSIGNMENT_VERSION from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=:t",{"t":x["task_id"]})==[{"status":"NEW","assigned_to":None,"picked_qty":0,"assignment_version":0}]
    x["source_after"]=after;x["state"]="NEW_UNASSIGNED_READY_METADATA_ACCEPTANCE";save(x)
    print(json.dumps({k:x[k]for k in("state","task_id","case_line_id","wave","plan","actor","resource_id","session_id")}))


if __name__=="__main__":main()
