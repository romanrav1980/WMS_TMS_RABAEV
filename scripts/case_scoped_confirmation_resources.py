"""Explicit coordinator-approved shared DEV metadata stage; no stock commands.
Run only once numeric CASE provenance has been reviewed. No credentials in output.
"""
import argparse
import json
import sys
from datetime import datetime,timedelta,timezone
from zoneinfo import ZoneInfo
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/"scripts"),str(ROOT/"api/wms_api_server")]
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment()
from app.oracle_gateway import OracleGateway
from app.services.resource_management_service import ResourceManagementService
from app.services.case_pick_service import CasePickService
from app.schemas import ResourceCreateRequest,ResourceShiftCreateRequest,ResourceSessionLoginRequest,CasePickTaskActionRequest
from app.modules.resources.infrastructure.qualification_admin import QualificationAdmin
from app.modules.platform.public import AccessMetadataService
from app.modules.platform.api.metadata_inputs import Command,normalize
from app.routers.admin_rights import revoke_group_right,grant_group_right
from app.schemas import RightsGrantRequest
from app.auth import AdminUser

REPORT=ROOT/"reports/retailcase/2026-10-15/scoped-case-audit/shared-resources.json"
ACTOR="WHREQ15.OP";WARE=13583852;CODE="WHREQ15.CASE";NOTE="TEST_FIXTURE_NOT_HARDWARE shared scoped CASE proof; metadata only"


def save(report):
    REPORT.parent.mkdir(parents=True,exist_ok=True);REPORT.write_text(json.dumps(report,indent=2,default=str),encoding="utf-8")


def access(gateway,operation,kind,payload):
    return AccessMetadataService(gateway).command("admin",normalize(Command(operation_id=operation,command_type=kind,payload=payload),"ACCESS"))


def main():
    parser=argparse.ArgumentParser();parser.add_argument("--task",type=int,required=True);parser.add_argument("--native-only",action="store_true");parser.add_argument("--claim-start",action="store_true");args=parser.parse_args()
    gateway=OracleGateway();report=json.loads(REPORT.read_text(encoding="utf-8"))if REPORT.exists()else{"task_id":args.task,"actor":ACTOR,"warehouse_id":WARE,"physical_verified":False}
    assert report["task_id"]==args.task
    task=gateway.fetch_all("select WARE_ID,PICKED_QTY,ASSIGNED_TO,RESOURCE_SESSION_ID from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=:t",{"t":args.task})
    assert len(task)==1 and task[0]["ware_id"]==WARE and task[0]["picked_qty"]==0,task
    assert gateway.fetch_all("select count(*) N from RRL_ASSEMBLY_SESSION where CASE_PICK_TASK_ID=:t",{"t":args.task})[0]["n"]==0
    admin=AdminUser(username="admin",display_name="Fixture coordinator",user_group="GLOBAL_ADMIN",permissions={"*"})
    if not args.native_only and not args.claim_start:
        assert not REPORT.exists(),"Do not duplicate committed resource history; inspect saved stage"
        assert task[0]["assigned_to"]is None and task[0]["resource_session_id"]is None,task
        report["temporary_flat"]=grant_group_right("WHREQ15.OP",RightsGrantRequest(right_name="case_pick_execute",description=NOTE),admin);save(report)
        assert gateway.fetch_all("select RRL_HAS_WRIGHT(:a,'case_pick_execute') N from dual",{"a":ACTOR})[0]["n"]==1
        resources=ResourceManagementService(gateway)
        report["resource_id"]=resources.create_resource(ResourceCreateRequest(resource_code=CODE,resource_name=NOTE,resource_type="CASE_PICKER",user_id=ACTOR,ware_id=WARE,created_by="admin"));save(report)
        report["qualification"]=QualificationAdmin(gateway).set_qualification(report["resource_id"],"CASE_PICK",True,"admin");save(report)
        now=datetime.now(ZoneInfo("Europe/Moscow"))
        report["shift_time_zone"]="Europe/Moscow"
        report["shift_explicit_start"]=(now-timedelta(minutes=1)).isoformat()
        report["shift_explicit_finish"]=(now+timedelta(hours=4)).isoformat()
        report["shift_id"]=resources.create_shift(ResourceShiftCreateRequest(shift_code=CODE,shift_date=now.date(),start_at=now-timedelta(minutes=1),finish_at=now+timedelta(hours=4),ware_id=WARE,status="OPEN",created_by="admin"));save(report)
        report["session_id"]=resources.login_session(ResourceSessionLoginRequest(shift_id=report["shift_id"],resource_id=report["resource_id"],operator_user_id=ACTOR,terminal_id="TEST:WHREQ15",created_by="admin"));save(report)
    elif args.claim_start:
        assert report.get("session_id") and not report.get("started"),report
        request=CasePickTaskActionRequest(resource_id=report["resource_id"],resource_session_id=report["session_id"],actor=ACTOR,reason=NOTE)
        CasePickService(gateway).claim_task(args.task,request);report["claimed"]=True;save(report)
        CasePickService(gateway).start_task(args.task,request);report["started"]=True;save(report)
    else:
        assert report.get("started"),report
        report["role"]=access(gateway,"WHREQ15.CASE.ROLE","ROLE_SAVE",dict(role_id="WHREQ15.CASE.EXEC",title=NOTE,permissions=["case_pick_execute"],active=True,expected_version=0));save(report)
        now=datetime.now(timezone.utc)
        if "assignment_payload"not in report:
            report["assignment_payload"]=dict(assignment_id="WHREQ15.CASE.SELF",username=ACTOR,role_id="WHREQ15.CASE.EXEC",scope_kind="SELF",scope_id=None,valid_from=(now-timedelta(minutes=1)).isoformat(),valid_until=(now+timedelta(hours=4)).isoformat(),expected_version=0,reason=NOTE);save(report)
        report["assignment"]=access(gateway,"WHREQ15.CASE.ASSIGN","ASSIGN",report["assignment_payload"]);save(report)
        report["flat_revocation"]=revoke_group_right("WHREQ15.OP","case_pick_execute",admin);save(report)
        assert gateway.fetch_all("select RRL_HAS_WRIGHT(:a,'case_pick_execute') N,RRL_CASE_TASK_ACCESS.has_current_scoped_execute(:t,:a) CURRENT_OK,RRL_CASE_TASK_ACCESS.scoped_executor(:t,:a) EXECUTE_OK from dual",{"a":ACTOR,"t":args.task})==[{"n":0,"current_ok":1,"execute_ok":1}]
        report["native_only"]=True;save(report)
    print(json.dumps({"status":"METADATA_ONLY","task_id":args.task,"resource_id":report["resource_id"],"session_id":report["session_id"],"native_only":report.get("native_only",False)}))


if __name__=="__main__":main()
