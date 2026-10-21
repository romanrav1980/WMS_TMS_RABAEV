"""Compare the shared Gantt and native CASE reader under current TRADECASE owner grants."""
import json
import os
from pathlib import Path
import re
import secrets
import sys
from urllib.parse import urlencode
from uuid import uuid4

ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT),str(Path(__file__).parent)]
from live_document_acceptance import http,expect,CALLS
from tools.mcp.tms_mcp_server import oracle_connection

OUT=ROOT/"runtime/test-evidence/tradecase/2026-10-21/T10"
FILE=OUT/"timeline-owner-fixture.json"
WARE=219023232
CASE=1159


def timeline(actor,password):
    query=urlencode(dict(warehouse_id=WARE,start_at="2026-10-21T00:00:00+03:00",finish_at="2026-10-22T00:00:00+03:00"))
    return http("GET","/api/resources/timeline?"+query,actor=actor,password=password)


def has_case(result):
    return any(x["event_id"]=="CASE_PICK_TASK:"+str(CASE) for x in result["events"]+result["unscheduled"])


def prepare():
    assert not FILE.exists(),"Existing fixture must be examined; do not overwrite a live QA identity"
    actor="T10"+uuid4().hex[:10];password=secrets.token_hex(24)
    with oracle_connection()as conn:
        q=conn.cursor();q.execute("select user,sys_context('USERENV','SERVICE_NAME')from dual");assert q.fetchone()==("RABAEV","orcl")
        q.execute("select NAME from RRL_WARES where ID=:w",w=WARE);assert q.fetchone()==("TRADECASE QA 89af0087",)
        q.execute("insert into RUSERS(ID,PASS,NAME,USER_GROUP,WARE_ID,DELETED,PRAVO_ADMIN_LOGIN)values(:a,:p,'Timeline owner QA','TC03QA',:w,0,1)",a=actor,p=password,w=WARE)
        q.execute("insert into RRL_ACCESS_ROLE(ROLE_ID,TITLE,ACTIVE,VERSION_NO)values(:a,'Timeline owner QA',1,1)",a=actor)
        for permission in ["resource_gantt_view","case_pick_view","resource_management_view","resource_session_view"]:
            q.execute("insert into RRL_ACCESS_ROLE_RIGHT(ROLE_ID,PERMISSION)values(:a,:p)",a=actor,p=permission)
        q.execute("insert into RRL_ACCESS_ASSIGNMENT(ASSIGNMENT_ID,USERNAME,ROLE_ID,SCOPE_KIND,SCOPE_ID,MEMBERSHIP,VALID_FROM,VALID_UNTIL,ASSIGNED_BY,REASON,VERSION_NO)values(:a,:a,:a,'WAREHOUSE',:w,'CURRENT',systimestamp-interval '1'minute,systimestamp+interval '2'hour,'admin','Shared Gantt must match current CASE owner visibility',1)",a=actor,w=str(WARE));conn.commit()
    f=dict(actor=actor,warehouse_id=WARE,case_id=CASE)
    FILE.write_text(json.dumps(f,indent=2),encoding="utf-8")
    detail=http("GET",f"/api/case-pick/tasks/{CASE}",actor=actor,password=password)
    before=expect(200,timeline(actor,password))
    f.update(detail_status=detail[0],timeline_exposed_case=has_case(before),status="GAP"if has_case(before)and detail[0]==404 else"CHECK")
    f["history"]=CALLS;FILE.write_text(json.dumps(f,indent=2),encoding="utf-8")
    print(json.dumps({k:v for k,v in f.items()if k!="history"}))


def verify():
    f=json.loads(FILE.read_text());actor=f["actor"];report=dict(status="FAIL",checks=[])
    with oracle_connection()as conn:
        q=conn.cursor();q.execute("select PASS from RUSERS where ID=:a and USER_GROUP='TC03QA'and nvl(DELETED,0)=0",a=actor)
        row=q.fetchone();assert row,"Do not reactivate retired QA identity";password=row[0]
        q.execute("select nvl(max(LOG_ID),0)from RRL_SQL_SLOW_LOG");marker=q.fetchone()[0]
    base=f"/api/tradecase/warehouses/{WARE}/stock/owner-grants"
    def grant(owner,version,view):
        return expect(200,http("PUT",base,dict(operation_id=actor+"."+owner+"."+str(version),expected_version=version,username=actor,
            owner_id=owner,can_view=view,can_operate=False,reason="Current owner visibility parity across CASE and resource timeline")))
    try:
        value=expect(200,timeline(actor,password));assert not has_case(value)
        expect(404,http("GET",f"/api/case-pick/tasks/{CASE}",actor=actor,password=password));report["checks"].append("no owner grant hides CASE in both readers")
        # BLC does not exist in this fixture's reference yet; use SNS grant only for the positive/current-owner branch.
        grant("SNS",0,True);value=expect(200,timeline(actor,password));assert has_case(value)
        expect(200,http("GET",f"/api/case-pick/tasks/{CASE}",actor=actor,password=password));report["checks"].append("current SNS view exposes returned CASE in both readers")
        grant("SNS",1,False);assert not has_case(expect(200,timeline(actor,password)))
        expect(404,http("GET",f"/api/case-pick/tasks/{CASE}",actor=actor,password=password));report["checks"].append("owner revoke clears timeline and CASE detail")
        with oracle_connection()as conn:
            q=conn.cursor();q.execute("update RRL_ACCESS_ASSIGNMENT set REVOKED_AT=systimestamp where ASSIGNMENT_ID=:a",a=actor);conn.commit()
        expect(403,timeline(actor,password));report["checks"].append("warehouse assignment revoke denies timeline")
        with oracle_connection()as conn:
            q=conn.cursor();q.execute("select sum(r.REMAIN),sum(r.HARD_RESERVED_BASE)from RRL_REMAINS r join RRL_CELLS c on c.CELL=r.CELL where c.WARE_ID=:w",w=WARE);assert q.fetchone()==(10,0)
            q.execute("select count(*)from user_objects where STATUS='INVALID'");assert q.fetchone()[0]==0
            q.execute("select LOG_ID,ELAPSED_MS,OPERATION_KIND from RRL_SQL_SLOW_LOG where LOG_ID>:n order by LOG_ID fetch first 20 rows only",n=marker);report["slow_sql"]=[list(x)for x in q]
        report.update(status="PASS",physical=[10,0],actor=actor,warehouse_id=WARE)
    except Exception as exc:report["error"]=str(exc);raise
    finally:
        with oracle_connection()as conn:
            q=conn.cursor();q.execute("update RUSERS set DELETED=1 where ID=:a and USER_GROUP='TC03QA'",a=actor)
            q.execute("update RRL_ACCESS_ASSIGNMENT set REVOKED_AT=coalesce(REVOKED_AT,systimestamp)where ASSIGNMENT_ID=:a",a=actor);conn.commit()
        report["http"]=CALLS;(OUT/"timeline-owner-result.json").write_text(json.dumps(report,indent=2),encoding="utf-8")
    print(json.dumps({k:v for k,v in report.items()if k!="http"}))


if __name__=="__main__":
    os.environ.setdefault("TRADECASE_ADMIN_USER","admin")
    os.environ.setdefault("TRADECASE_ADMIN_PASSWORD",re.search(r"PASS=(\S+?)[`,)\s]",(ROOT/"AGENTS.md").read_text(encoding="utf-8"))[1])
    OUT.mkdir(parents=True,exist_ok=True)
    if "--prepare"in sys.argv:prepare()
    else:verify()
