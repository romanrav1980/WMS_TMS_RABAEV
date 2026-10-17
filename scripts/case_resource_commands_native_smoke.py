"""Caller-rollback only proof on a separately coordinator-staged NEW CASE.
No fixture creation, no commits, no StockPosting.post or goods commands.
"""
import argparse
import hashlib
import json
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
from app.modules.platform.public import stock_configuration_transaction
from app.modules.resources.contracts_case_resource import CaseResourceCommand,CaseResourceAck
from app.modules.resources.infrastructure.case_resource_commands import canonical,oracle_json


def snapshot(gateway:Any,ctx:dict[str,Any])->dict[str,Any]:
    return dict(task=gateway.fetch_all("select STATUS,ASSIGNED_TO,ASSIGNED_RESOURCE_ID,RESOURCE_SESSION_ID,EQUIPMENT_ID,ASSIGNMENT_VERSION,CONTENT_VERSION,PICKED_QTY,STARTED_AT_INSTANT from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=:t",{"t":ctx["task_id"]}),
        stock=gateway.fetch_all("select CELL,REMAIN,HARD_RESERVED_BASE,STOCK_VERSION from RRL_REMAINS where UID_POLETA=:u order by CELL",{"u":ctx["source"]}),
        events=gateway.fetch_all("select count(*) N from RRL_CASE_PICK_EVENT where CASE_PICK_TASK_ID=:t",{"t":ctx["task_id"]}),
        receipts=gateway.fetch_all("select count(*) N from RRL_CASE_RESOURCE_COMMAND where CASE_PICK_TASK_ID=:t",{"t":ctx["task_id"]}))


def call(cursor:Any,task:int,wire:str,actor:str)->dict[str,Any]:
    output=cursor.var(oracledb.DB_TYPE_CLOB)
    cursor.callproc("RRL_CASE_ASSIGNMENT_API.execute_command",[task,wire,actor,output])
    return oracle_json(output.getvalue())


def trial(gateway:Any,ctx:dict[str,Any],body:CaseResourceCommand,checks:list[str],expected_error:str|None=None)->None:
    before=snapshot(gateway,ctx);wire=canonical(body)
    with oracle_connection()as connection:
        cursor=connection.cursor()
        try:
            result=call(cursor,ctx["task_id"],wire,ctx["actor"])
            ack=CaseResourceAck.model_validate(result)
            assert ack.request_sha256==hashlib.sha256(wire.encode("utf-8")).hexdigest().upper()
            assert ack.actor==ctx["actor"]and ack.task_id==ctx["task_id"]and ack.operation_id==body.operation_id
            if expected_error:
                assert ack.outcome=="REJECTED"and ack.error_code==expected_error and not ack.changed,result
                assert ack.assignment_version==body.expected_assignment_version-1 if expected_error=="CASE_RESOURCE_ASSIGNMENT_VERSION_CHANGED"else True
            else:
                assert ack.outcome=="APPLIED"and ack.changed and ack.assignment_version==body.expected_assignment_version+1,result
                assert ack.status=="ASSIGNED"and ack.assigned_to==ctx["actor"]and ack.resource_session_id==ctx["session_id"]
                cursor.execute("select RESOURCE_ID,RESOURCE_SESSION_ID,EQUIPMENT_ID from RRL_CASE_PICK_EVENT where CASE_PICK_TASK_ID=:t and EVENT_TYPE='CLAIMED'order by CASE_PICK_EVENT_ID desc fetch first 1 row only",t=ctx["task_id"])
                event=cursor.fetchone();assert event and event[0]==ctx["resource_id"]and event[1]==ctx["session_id"],event
            cursor.execute("select SOURCE_SHA256,RESULT_JSON from RRL_CASE_RESOURCE_COMMAND where OPERATION_ID=:o",o=body.operation_id)
            saved=cursor.fetchone();assert saved[0]==ack.request_sha256 and oracle_json(saved[1])==result
        finally:
            connection.rollback();cursor.callproc("RRL_STOCK_LOCK_API.clear_plan")
    assert snapshot(gateway,ctx)==before,"Caller rollback changed fixture"
    checks.append(expected_error or"native_scoped_claim_assignment_version_event_hash_rollback")


class GuardRollback(Exception):pass


def physical_guards(gateway:Any,ctx:dict[str,Any],checks:list[str])->None:
    cases=[("update RRL_RESOURCE_TASK_QUAL set ACTIVE=0 where RESOURCE_ID=:id and TASK_TYPE='CASE_PICK'",ctx["resource_id"],"CASE_RESOURCE_QUALIFICATION_REQUIRED"),
        ("update RRL_RESOURCE_SHIFT set STATUS='PLANNED' where SHIFT_ID=:id",ctx["shift_id"],"CASE_SHIFT_UNAVAILABLE"),
        ("update RRL_RESOURCE_SHIFT set START_AT=localtimestamp+interval'1'hour where SHIFT_ID=:id",ctx["shift_id"],"CASE_SHIFT_UNAVAILABLE"),
        ("update RRL_RESOURCE_SHIFT set START_AT=localtimestamp-interval'2'hour,FINISH_AT=localtimestamp-interval'1'hour where SHIFT_ID=:id",ctx["shift_id"],"CASE_SHIFT_UNAVAILABLE"),
        ("update RRL_RESOURCE_SESSION set STATUS='PAUSED'where SESSION_ID=:id",ctx["session_id"],"CASE_SCOPED_ACTIVE_SESSION_REQUIRED"),
        ("update RRL_RESOURCE set WARE_ID=6667491 where RESOURCE_ID=:id",ctx["resource_id"],"CASE_RESOURCE_UNAVAILABLE"),
        ("update RRL_RESOURCE_SHIFT set WARE_ID=6667491 where SHIFT_ID=:id",ctx["shift_id"],"CASE_SCOPED_SHIFT_WAREHOUSE_CONFLICT"),
        ("update RRL_RESOURCE_SESSION set OPERATOR_USER_ID='admin'where SESSION_ID=:id",ctx["session_id"],"CASE_SESSION_OWNER_CONFLICT")]
    for sql,identity,expected in cases:
        before=snapshot(gateway,ctx)
        try:
            with stock_configuration_transaction(gateway,"CRES15 scoped physical guard caller rollback","admin","warehouse_settings_edit")as c:
                c.execute(sql,{"id":identity});assert c.rowcount==1
                try:c.callfunc("RRL_CASE_RESOURCE_POLICY.context_json",oracledb.DB_TYPE_CLOB,[ctx["task_id"],"CLAIM",ctx["actor"],ctx["resource_id"],ctx["session_id"],None])
                except oracledb.DatabaseError as error:assert expected in str(error),(expected,str(error))
                else:raise AssertionError(expected+" admitted: "+sql)
                raise GuardRollback()
        except GuardRollback:pass
        assert snapshot(gateway,ctx)==before
        checks.append(expected+"_purepolicy_callerrollback")


def main()->None:
    parser=argparse.ArgumentParser();parser.add_argument("--fixture",type=Path,required=True);args=parser.parse_args()
    ctx=json.loads(args.fixture.read_text(encoding="utf-8"));assert ctx.get("approved_case_resource_fixture")is True
    assert ctx["actor"].startswith("CRES15.")and ctx["task_id"]not in(1031,1032,1136),"Dedicated new fixture required"
    gateway=OracleGateway();before=snapshot(gateway,ctx);task=before["task"][0]
    assert task["status"]=="NEW"and task["assigned_to"]is None and task["picked_qty"]==0
    assert gateway.fetch_all("select RRL_HAS_WRIGHT(:a,'case_pick_execute') N from dual",{"a":ctx["actor"]})==[{"n":0}]
    checks=[]
    physical_guards(gateway,ctx,checks)
    body=CaseResourceCommand(operation_id="CRES15.CLAIM.ROLLBACK",action="CLAIM",expected_assignment_version=int(task["assignment_version"]),resource_session_id=ctx["session_id"],resource_id=ctx["resource_id"],reason="SIMULATED_TEST_NOT_HARDWARE native metadata rollback")
    trial(gateway,ctx,body,checks)
    trial(gateway,ctx,body.model_copy(update={"operation_id":"CRES15.VERSION.ROLLBACK","expected_assignment_version":body.expected_assignment_version+1}),checks,"CASE_RESOURCE_ASSIGNMENT_VERSION_CHANGED")
    trial(gateway,ctx,body.model_copy(update={"operation_id":"CRES15.MISSING.ROLLBACK","resource_session_id":2147483647}),checks,"CASE_RESOURCE_IDENTITY_MISSING")
    with oracle_connection()as connection:
        cursor=connection.cursor()
        try:
            try:cursor.execute("update RRL_CASE_PICK_TASK set ASSIGNMENT_VERSION=ASSIGNMENT_VERSION where CASE_PICK_TASK_ID=:t",t=ctx["task_id"])
            except oracledb.DatabaseError as error:assert "CASE_ASSIGNMENT_VERSION_SERVER_DERIVED"in str(error),str(error)
            else:raise AssertionError("Direct version UPDATE admitted")
        finally:connection.rollback()
    checks.append("explicit_version_update_denied")
    assert snapshot(gateway,ctx)==before
    report=dict(status="PASS",checks=checks,fixture=ctx["task_id"],before=before,after=snapshot(gateway,ctx),quantity_commands=0,hardware_verified=False,limitations="Durable receipt/revoke/START/concurrency and HTTP require separate approved metadata phase")
    output=ROOT/"reports/retailcase/2026-10-15/case-resource-commands/native-rollback.json";output.parent.mkdir(parents=True,exist_ok=True);output.write_text(json.dumps(report,indent=2,default=str),encoding="utf-8")
    print(json.dumps({"status":"PASS","groups":len(checks),"all_caller_rollback":True}))


if __name__=="__main__":main()
