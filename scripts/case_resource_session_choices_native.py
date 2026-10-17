"""Read-only service + native guard probes, scoped QA metadata caller rollback only.
Guard probes use current caller TX: production SET TRANSACTION READ ONLY is never suppressed.
"""
import json
import sys
from pathlib import Path
from contextlib import contextmanager
from typing import Any
import oracledb
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/"scripts"),str(ROOT/"api/wms_api_server")]
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment()
from app.oracle_gateway import OracleGateway
from app.db import oracle_connection
from app.modules.resources.infrastructure.case_resource_commands import CaseResourceCommands,oracle_json
from app.modules.resources.contracts_case_resource import CaseResourceError
from app.modules.platform.public import stock_configuration_transaction,AccessMetadataService
from app.modules.platform.api.metadata_inputs import Command,normalize
from case_resource_commands_native_smoke import snapshot

FOLDER=ROOT/"reports/retailcase/2026-10-15/case-resource-commands"


class GuardRollback(Exception):pass


def probe(g:Any,ctx:dict[str,Any],kind:str)->dict[str,Any]:
    result:dict[str,Any]={}
    try:
        with stock_configuration_transaction(g,"CRES15 choices native guard caller rollback","admin","warehouse_settings_edit")as c:
            if kind=="paused":c.execute("update RRL_RESOURCE_SESSION set STATUS='PAUSED'where SESSION_ID=:id",id=ctx["session_id"])
            else:c.execute("update RRL_RESOURCE_TASK_QUAL set ACTIVE=0 where RESOURCE_ID=:id and TASK_TYPE='CASE_PICK'",id=ctx["resource_id"])
            assert c.rowcount==1
            out=c.var(oracledb.DB_TYPE_CLOB);c.callproc("RRL_CASE_ASSIGNMENT_API.task_context",[ctx["task_id"],ctx["actor"],out]);current=oracle_json(out.getvalue())
            c.execute("select s.SESSION_ID,s.RESOURCE_ID,s.EQUIPMENT_ID from RRL_RESOURCE_SESSION s join RRL_RESOURCE r on r.RESOURCE_ID=s.RESOURCE_ID where s.OPERATOR_USER_ID=:actor and s.STATUS='ACTIVE'and r.WARE_ID=:ware order by s.SESSION_ID desc fetch first 21 rows only",actor=ctx["actor"],ware=current["warehouse_id"])
            rows=c.fetchall()
            if kind=="paused":assert rows==[];result=dict(own_active_projection=[],current_authorization=True)
            else:
                assert len(rows)==1 and rows[0][0]==ctx["session_id"]
                try:c.callfunc("RRL_CASE_RESOURCE_POLICY.context_json",oracledb.DB_TYPE_CLOB,[ctx["task_id"],"START",ctx["actor"],rows[0][1],rows[0][0],rows[0][2]])
                except oracledb.DatabaseError as error:assert"CASE_RESOURCE_QUALIFICATION_REQUIRED"in str(error);result=dict(own_session_preserved=ctx["session_id"],native_ready=False,native_code="CASE_RESOURCE_QUALIFICATION_REQUIRED")
                else:raise AssertionError("Inactive qualification admitted")
            raise GuardRollback()
    except GuardRollback:pass
    return result


def revoke_probe(g:Any,ctx:dict[str,Any])->dict[str,Any]:
    with oracle_connection()as conn:
        c=conn.cursor()
        class CallerGateway:
            @contextmanager
            def transaction(self,label:Any)->Any:yield c
        try:
            payload=dict(role_id="CRES15.CASE.EXEC",title="CRES15 choices revoke rollback",permissions=["case_pick_execute"],active=False,expected_version=3)
            result=AccessMetadataService(CallerGateway()).command("admin",normalize(Command(operation_id="CRES15.CHOICES.REVOKE.ROLLBACK",command_type="ROLE_SAVE",payload=payload),"ACCESS"))
            out=c.var(oracledb.DB_TYPE_CLOB)
            try:c.callproc("RRL_CASE_ASSIGNMENT_API.task_context",[ctx["task_id"],ctx["actor"],out])
            except oracledb.DatabaseError as error:assert error.args[0].code==20882
            else:raise AssertionError("Revoked current actor read context")
            return dict(native_owner_revoke_receipt=result,current_context_denied=403,session_rows_read=False,caller_rollback=True)
        finally:conn.rollback();c.callproc("RRL_STOCK_LOCK_API.clear_plan")


def main()->None:
    g=OracleGateway();ctx=json.loads((FOLDER/"fixture.json").read_text(encoding="utf-8"));before=snapshot(g,ctx)
    assert ctx["task_id"]==1138 and ctx["session_id"]==55 and before["task"][0]["status"]=="IN_PROGRESS"
    service=CaseResourceCommands(g);normal=service.sessions(ctx["task_id"],ctx["actor"])
    assert len(normal["items"])==1 and normal["items"][0]["resource_session_id"]==55 and normal["items"][0]["ready"]is True
    report=dict(status="IN_PROGRESS",normal_full_readonly_service=normal,hardware_verified=False,quantity_commands=0)
    report["paused_caller_tx_projection"]=probe(g,ctx,"paused")
    report["qualification_caller_tx_policy"]=probe(g,ctx,"qualification")
    try:service.sessions(ctx["task_id"],"WHREQ15.GW")
    except CaseResourceError as error:assert error.status==403
    else:raise AssertionError("Foreign gateway obtained own-session choices")
    report["foreign_gateway_full_readonly_service_denied"]=403
    report["role_revoke_native_caller_tx"]=revoke_probe(g,ctx)
    assert g.fetch_all("select ACTIVE,VERSION_NO from RRL_ACCESS_ROLE where ROLE_ID='CRES15.CASE.EXEC'")==[{"active":1,"version_no":3}]
    assert not g.fetch_all("select OPERATION_ID from RRL_PLATFORM_COMMAND where OPERATION_ID='CRES15.CHOICES.REVOKE.ROLLBACK'")
    assert service.sessions(ctx["task_id"],ctx["actor"])==normal and snapshot(g,ctx)==before
    report.update(status="PASS",guards_rolled_back=True,source_case_events_receipts_unchanged=True,limitation="Uncommitted CFG mutations cannot be observed by separate READONLY service TX. PAUSED/qualification probes execute own-session projection and authoritative native policy in caller CFG TX; no suppression of production READONLY. Revoked-role probe invokes native task_context before any session query. Fullservice normal/foreign denial run real READONLY TX.")
    (FOLDER/"own-sessions-native-guards.json").write_text(json.dumps(report,indent=2,default=str),encoding="utf-8")
    print(json.dumps({"status":"PASS","groups":5,"all_guard_mutations_caller_rollback":True}))


if __name__=="__main__":main()
