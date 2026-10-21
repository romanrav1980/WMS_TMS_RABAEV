"""Revoke an existing retired QA grant without reactivating its identity."""
import json
import os
from pathlib import Path
import re
import secrets
import sys
from uuid import uuid4

ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT),str(Path(__file__).parent)]
from live_document_acceptance import http,expect,CALLS
from tools.mcp.tms_mcp_server import oracle_connection


if __name__=="__main__":
    os.environ.setdefault("TRADECASE_ADMIN_USER","admin")
    os.environ.setdefault("TRADECASE_ADMIN_PASSWORD",re.search(r"PASS=(\S+?)[`,)\s]",(ROOT/"AGENTS.md").read_text(encoding="utf-8"))[1])
    out=ROOT/"runtime/test-evidence/tradecase/2026-10-21/T11";out.mkdir(parents=True,exist_ok=True)
    fixture=json.loads((out.parent/"T06/factory-case.json").read_text());ware=fixture["warehouse_id"];actor=fixture["actor"]
    tag="G21"+uuid4().hex[:10];password=secrets.token_hex(24);created=False
    report=dict(status="FAIL",warehouse_id=ware,target_user=actor,checks=[])
    path=f"/api/tradecase/warehouses/{ware}/stock/owner-grants"
    try:
        with oracle_connection()as conn:
            q=conn.cursor();q.execute("select user,sys_context('USERENV','SERVICE_NAME')from dual");assert q.fetchone()==("RABAEV","orcl")
            q.execute("select DELETED,USER_GROUP,WARE_ID from RUSERS where ID=:a",a=actor);assert q.fetchone()==(1,"TC03QA",ware)
            assert actor.startswith("FC21")
            q.execute("select VERSION_NO from RRL_TRADE_OWNER_GRANT where USERNAME=:a and WARE_ID=:w and OWNER_ID='SNS'",a=actor,w=ware);version=q.fetchone()[0]
            q.execute("select nvl(max(LOG_ID),0)from RRL_SQL_SLOW_LOG");marker=q.fetchone()[0]
        body=dict(operation_id=tag+".revoke",expected_version=version,username=actor,owner_id="SNS",can_view=False,can_operate=False,reason="Revoke retained grant of retired factory CASE identity")
        report["request"]=body
        response=http("PUT",path,body)
        if response[0]==503:
            # Preserve the command: Oracle package recompilation can discard a pooled session's state.
            response=http("PUT",path,body)
        first=expect(200,response);assert first["version"]==version+1
        second=expect(200,http("PUT",path,body));assert second["replayed"] and second["version"]==first["version"]
        assert "OPERATION"in expect(409,http("PUT",path,dict(body,can_view=True)))["detail"]["code"]
        assert expect(409,http("PUT",path,dict(body,operation_id=tag+".stale")))["detail"]["code"]=="VERSION_CONFLICT"
        assert expect(409,http("PUT",path,dict(body,operation_id=tag+".enable",expected_version=version+1,can_view=True)))["detail"]["code"]=="TRADE_GRANT_USER_OR_OWNER_NOT_FOUND"
        assert expect(409,http("PUT",path,dict(body,operation_id=tag+".missing",expected_version=0,username=tag+".MISSING")))["detail"]["code"]=="TRADE_GRANT_USER_OR_OWNER_NOT_FOUND"
        report["checks"] += ["existing retired grant revoked without reactivation", "immutable replay/version/content conflict", "enabling retired identity and missing-target creation denied"]
        # A scoped settings editor remains unable to grant/revoke owner rights reserved to admin.
        with oracle_connection()as conn:
            q=conn.cursor()
            q.execute("insert into RUSERS(ID,PASS,NAME,USER_GROUP,WARE_ID,DELETED,PRAVO_ADMIN_LOGIN)values(:a,:p,'Grant boundary QA','TC03QA',:w,0,1)",a=tag,p=password,w=ware)
            q.execute("insert into RRL_ACCESS_ROLE(ROLE_ID,TITLE,ACTIVE,VERSION_NO)values(:a,'Grant boundary QA',1,1)",a=tag)
            q.execute("insert into RRL_ACCESS_ROLE_RIGHT(ROLE_ID,PERMISSION)values(:a,'warehouse_settings_edit')",a=tag)
            q.execute("insert into RRL_ACCESS_ASSIGNMENT(ASSIGNMENT_ID,USERNAME,ROLE_ID,SCOPE_KIND,SCOPE_ID,MEMBERSHIP,VALID_FROM,VALID_UNTIL,ASSIGNED_BY,REASON,VERSION_NO)values(:a,:a,:a,'WAREHOUSE',:w,'CURRENT',systimestamp-interval '1'minute,systimestamp+interval '1'hour,'admin','Admin-only owner grant boundary',1)",a=tag,w=str(ware));conn.commit();created=True
        # Retain the older active-user API behavior: an explicit empty grant can be created.
        empty=expect(200,http("PUT",path,dict(body,operation_id=tag+".active-empty",username=tag,expected_version=0)))
        assert empty["version"]==1
        report["checks"] += ["active-user empty-grant creation remains compatible"]
        denial=expect(403,http("PUT",path,dict(body,operation_id=tag+".nonadmin",expected_version=version+1),tag,password))
        assert denial["detail"]["code"]=="TRADE_OWNER_GRANT_ADMIN_REQUIRED",denial
        report["checks"] += ["scoped settings editor still denied by native admin-only rule"]
        with oracle_connection()as conn:
            q=conn.cursor();q.execute("select CAN_VIEW,CAN_OPERATE,VERSION_NO from RRL_TRADE_OWNER_GRANT where USERNAME=:a and WARE_ID=:w and OWNER_ID='SNS'",a=actor,w=ware)
            assert q.fetchone()==(0,0,version+1)
            q.execute("select sum(r.REMAIN),sum(r.HARD_RESERVED_BASE)from RRL_REMAINS r join RRL_CELLS c on c.CELL=r.CELL where c.WARE_ID=:w",w=ware);assert q.fetchone()==(10,0)
            q.execute("select count(*)from user_objects where STATUS='INVALID'");assert q.fetchone()[0]==0
            q.execute("select LOG_ID,ELAPSED_MS,OPERATION_KIND from RRL_SQL_SLOW_LOG where LOG_ID>:n order by LOG_ID fetch first 20 rows only",n=marker);report["slow_sql"]=[list(x)for x in q]
        report.update(status="PASS",final_version=version+1,physical=[10,0])
    except Exception as exc:report["error"]=str(exc);raise
    finally:
        if created:
            with oracle_connection()as conn:
                q=conn.cursor();q.execute("update RUSERS set DELETED=1 where ID=:a and USER_GROUP='TC03QA'",a=tag)
                q.execute("update RRL_ACCESS_ASSIGNMENT set REVOKED_AT=systimestamp where ASSIGNMENT_ID=:a",a=tag);conn.commit()
        report["http"]=CALLS;(out/("retired-grant-"+tag+".json")).write_text(json.dumps(report,indent=2,ensure_ascii=True),encoding="utf-8")
    print(json.dumps({k:v for k,v in report.items()if k!="http"}))
