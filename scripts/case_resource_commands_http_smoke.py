"""Root-approved CRES15 actual API metadata acceptance, zero goods posting.
Immutable receipts remain; no auto-retry/fresh nonce after uncertain outcomes.
"""
import hashlib
import json
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from contextlib import contextmanager
from pathlib import Path
from typing import Any
import httpx
import oracledb
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/"scripts"),str(ROOT/"api/wms_api_server")]
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment()
from app.oracle_gateway import OracleGateway
from app.db import oracle_connection
from app.modules.resources.contracts_case_resource import CaseResourceCommand,CaseResourceAck
from app.modules.resources.infrastructure.case_resource_commands import canonical,oracle_json
from app.modules.platform.public import AccessMetadataService
from app.modules.platform.api.metadata_inputs import Command,normalize
from case_resource_commands_native_smoke import call,snapshot

FOLDER=ROOT/"reports/retailcase/2026-10-15/case-resource-commands"
URL="http://127.0.0.1:8088/api/case-pick"
REPORT=FOLDER/"http-native-acceptance.json"


def save(report:dict[str,Any])->None:REPORT.write_text(json.dumps(report,indent=2,default=str),encoding="utf-8")


def checked(response:Any,body:CaseResourceCommand,ctx:dict[str,Any],status:int)->dict[str,Any]:
    assert response.status_code==status,(response.status_code,response.text[:600])
    data=response.json();ack=CaseResourceAck.model_validate(data)
    assert(ack.operation_id,ack.action,ack.actor,ack.task_id)==(body.operation_id,body.action,ctx["actor"],ctx["task_id"])
    assert ack.request_sha256==hashlib.sha256(canonical(body).encode()).hexdigest().upper()
    assert ack.stock_posted is False and ack.outcome_confirmed is True
    return data


def body(ctx:dict[str,Any],suffix:str,action:str,version:int)->CaseResourceCommand:
    return CaseResourceCommand(operation_id="CRES15.HTTP."+suffix,action=action,expected_assignment_version=version,resource_session_id=ctx["session_id"],resource_id=ctx["resource_id"],reason="TEST \u043f\u0440\u043e\u0432\u0435\u0440\u043a\u0430 UTF8 metadata only; no physical pick")


def role(g:Any,active:bool,version:int,operation:str)->dict[str,Any]:
    payload=dict(role_id="CRES15.CASE.EXEC",title="TEST_FIXTURE_NOT_HARDWARE CRES15 CASE metadata",permissions=["case_pick_execute"],active=active,expected_version=version)
    return AccessMetadataService(g).command("admin",normalize(Command(operation_id=operation,command_type="ROLE_SAVE",payload=payload),"ACCESS"))


def revoke_concurrency(g:Any,ctx:dict[str,Any],client:Any,receipts:list[tuple[CaseResourceCommand,dict[str,Any]]],report:dict[str,Any])->None:
    started=threading.Event();done=threading.Event();result:dict[str,Any]={};worker=None
    class ObservedGateway(OracleGateway):
        @contextmanager
        def transaction(self,label:Any)->Any:
            with super().transaction(label)as cursor:
                cursor.callproc("dbms_application_info.set_module",["CASE_RESOURCE_REVOKE","CRES15"]);started.set()
                try:yield cursor
                finally:cursor.callproc("dbms_application_info.set_module",[None,None])
    def revoke()->None:
        try:result["revoked"]=role(ObservedGateway(),False,1,"CRES15.ROLE.REVOKE")
        except Exception as error:result["error"]=str(error)
        finally:done.set()
    before=snapshot(g,ctx)
    try:
        with oracle_connection()as conn:
            c=conn.cursor()
            try:
                hold=body(ctx,"HOLD.REVOKE.ROLLBACK","CLAIM",2)
                ack=call(c,ctx["task_id"],canonical(hold),ctx["actor"]);assert ack["outcome"]=="APPLIED"and ack["changed"]is False
                worker=threading.Thread(target=revoke,daemon=True);worker.start();assert started.wait(2)
                c.execute("select to_number(sys_context('USERENV','SID'))from dual");sid=c.fetchone()[0]
                waits=[]
                for attempt in range(15):
                    c.execute("select EVENT,WAIT_CLASS,SID,BLOCKING_SESSION from V$SESSION where MODULE='CASE_RESOURCE_REVOKE'and ACTION='CRES15'and BLOCKING_SESSION=:sid",sid=sid);waits=c.fetchall()
                    if waits:break
                    time.sleep(.05)
                assert waits and not done.is_set(),("No actual current rights fence wait",result)
                result["actual_oracle_wait"]=waits
            finally:conn.rollback();c.callproc("RRL_STOCK_LOCK_API.clear_plan")
        assert done.wait(10)and"error"not in result,result
        assert snapshot(g,ctx)==before
        for original,ack in receipts:
            assert client.get(URL+"/resource-commands/"+original.operation_id).status_code==403
            assert client.post(URL+f"/tasks/{ctx['task_id']}/resource-commands",json=original.model_dump()).status_code==403
        assert client.get(URL+f"/tasks/{ctx['task_id']}/resource-context").status_code==403
        result["revoked_original_applied_and_rejected_receipt_denied"]=True
    finally:
        if worker:worker.join(12)
        current=g.fetch_all("select ACTIVE,VERSION_NO from RRL_ACCESS_ROLE where ROLE_ID='CRES15.CASE.EXEC'")
        if current==[{"active":0,"version_no":2}]:result["restored"]=role(g,True,2,"CRES15.ROLE.RESTORE")
        else:assert current==[{"active":1,"version_no":1}],current
        report["revoke_concurrency"]=result;save(report)
    for original,ack in receipts:assert client.get(URL+"/resource-commands/"+original.operation_id).json()==ack
    assert snapshot(g,ctx)==before


def main()->None:
    assert not REPORT.exists(),"Acceptance history exists; inspect saved receipts, never fork nonce"
    ctx=json.loads((FOLDER/"fixture.json").read_text(encoding="utf-8"));assert ctx["task_id"]==1138 and ctx["actor"]=="CRES15.OP"
    secret=json.loads((ROOT/"runtime/case-resource-qa-secrets.json").read_text(encoding="utf-8"))[ctx["actor"]]
    g=OracleGateway();before=snapshot(g,ctx);assert before["task"][0]["status"]=="NEW"and before["task"][0]["assignment_version"]==0
    report=dict(status="IN_PROGRESS",task_id=ctx["task_id"],source_before=before["stock"],checks=[],hardware_verified=False,goods_commands=0);save(report)
    endpoint=URL+f"/tasks/{ctx['task_id']}/resource-commands";checks=report["checks"]
    with httpx.Client(auth=(ctx["actor"],secret),timeout=15)as client:
        r=client.get(URL+f"/tasks/{ctx['task_id']}/resource-context");assert r.status_code==200 and r.json()["current_actor"]==ctx["actor"];checks.append("ordinary_scoped_context_HTTP200")
        invalid=body(ctx,"BROWSER.ACTOR","CLAIM",0).model_dump();invalid["actor"]="admin";assert client.post(endpoint,json=invalid).status_code==422;checks.append("browser_actor_422")
        wrong=body(ctx,"WRONG.VERSION","CLAIM",999);rejected=checked(client.post(endpoint,json=wrong.model_dump()),wrong,ctx,409);assert rejected["outcome"]=="REJECTED"and rejected["error_code"]=="CASE_RESOURCE_ASSIGNMENT_VERSION_CHANGED";checks.append("committed_UTF8_REJECTED_SHA_HTTP409")
        assert client.get(URL+"/resource-commands/"+wrong.operation_id).json()==rejected;assert checked(client.post(endpoint,json=wrong.model_dump()),wrong,ctx,409)==rejected;checks.append("REJECTED_exact_GET_and_POST")
        candidates=[body(ctx,"CLAIM.A","CLAIM",0),body(ctx,"CLAIM.B","CLAIM",0)]
        def race(b:CaseResourceCommand)->tuple[int,dict[str,Any]]:
            with httpx.Client(auth=(ctx["actor"],secret),timeout=15)as parallel:
                response=parallel.post(endpoint,json=b.model_dump());return response.status_code,checked(response,b,ctx,response.status_code)
        with ThreadPoolExecutor(max_workers=2)as pool:results=list(pool.map(race,candidates))
        assert sorted(code for code,ack in results)==[200,409],results
        win=next((b,ack)for b,(code,ack)in zip(candidates,results)if code==200);lose=next((b,ack)for b,(code,ack)in zip(candidates,results)if code==409)
        assert win[1]["assignment_version"]==1 and win[1]["status"]=="ASSIGNED"and lose[1]["outcome"]=="REJECTED";report["claim_race"]=[dict(operation=b.operation_id,http=code,ack=ack)for b,(code,ack)in zip(candidates,results)];checks.append("concurrent_distinct_intents_one_transition_one_stale_receipt");save(report)
        assert checked(client.post(endpoint,json=win[0].model_dump()),win[0],ctx,200)==win[1]
        start=body(ctx,"START","START",1);started=checked(client.post(endpoint,json=start.model_dump()),start,ctx,200);assert started["assignment_version"]==2 and started["status"]=="IN_PROGRESS"and started["started_at_instant"]is not None and started["started_shift_time_zone"]is None;checks.append("native_ONLY_scoped_START_actual_server_instant_unknown_zone_NULL")
        assert checked(client.post(endpoint,json=start.model_dump()),start,ctx,200)==started
        noop=body(ctx,"START.NOOP","START",2);noop_ack=checked(client.post(endpoint,json=noop.model_dump()),noop,ctx,200);assert noop_ack["changed"]is False and noop_ack["assignment_version"]==2 and noop_ack["started_at_instant"]==started["started_at_instant"];checks.append("START_replay_noop_no_new_instant")
        assert checked(client.post(endpoint,json=wrong.model_dump()),wrong,ctx,409)==rejected;assert checked(client.post(endpoint,json=lose[0].model_dump()),lose[0],ctx,409)==lose[1];checks.append("late_original_REJECTED_never_creates_after_correction")
        conflict=win[0].model_dump();conflict["reason"]+=" changed";r=client.post(endpoint,json=conflict);assert r.status_code==409 and r.json()["detail"]["outcome_confirmed"]is False;checks.append("same_operation_changed_body_not_definitive_receipt")
        receipts=[(wrong,rejected),win,lose,(start,started),(noop,noop_ack)]
        revoke_concurrency(g,ctx,client,receipts,report);checks.append("actual_Oracle_wait_revoke_denies_APPLIED_and_REJECTED_restore_v3")
        for original,ack in receipts:assert client.get(URL+"/resource-commands/"+original.operation_id).json()==ack
        report["receipts"]=[dict(request=b.model_dump(),ack=ack)for b,ack in receipts]
    after=snapshot(g,ctx);assert after["stock"]==before["stock"]
    assert after["task"][0]["picked_qty"]==0 and after["task"][0]["content_version"]==before["task"][0]["content_version"]and after["task"][0]["assignment_version"]==2
    assert after["events"][0]["n"]-before["events"][0]["n"]==2
    assert not g.fetch_all("select OPERATION_ID from RRL_STOCK_OPERATION where ACTOR=:a",{"a":ctx["actor"]})
    report.update(status="PASS",after=after,metadata_transitions=2,goods_stock_unchanged=True,role_versions=[1,2,3],limitations="No physical picker/scanner/hardware claim; WARE/SELF native paths proven, GROUP/NETWORK inherited scope engine not separately exercised here");save(report)
    print(json.dumps({"status":"PASS","groups":len(checks),"metadata_transitions":2,"goods_commands":0,"role_versions":[1,2,3]}))


if __name__=="__main__":main()
