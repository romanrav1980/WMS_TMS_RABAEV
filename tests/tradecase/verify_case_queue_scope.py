"""Compare frozen and current list SQL under actual owner and warehouse revocation."""
import json
import os
from pathlib import Path
import re
import secrets
import sys
from uuid import uuid4
ROOT=Path(__file__).resolve().parents[2];sys.path[:0]=[str(ROOT),str(Path(__file__).parent)]
from profile_case_queue import capture_query,fingerprint,OUT
from live_document_acceptance import http,expect,CALLS
from tools.mcp.tms_mcp_server import oracle_connection

report=dict(status='FAIL',checks=[]);actor=None;owner=False


def compare(label,**kwargs):
    before=capture_query(actor=actor,before=True,**kwargs);after=capture_query(actor=actor,**kwargs)
    with oracle_connection()as c:
        q=c.cursor();q.execute('set transaction read only');q.execute(before.sql,before.params);old=q.fetchall();q.execute(after.sql,after.params);new=q.fetchall();assert old==new,label
    report['checks'].append(dict(label=label,rows=len(new),sha=fingerprint(new)));return [x[0]for x in new]


if __name__=='__main__':
    os.environ['TRADECASE_ADMIN_USER']='admin';os.environ['TRADECASE_ADMIN_PASSWORD']=re.search(r'PASS=(\S+?)[`,)\s]',(ROOT/'AGENTS.md').read_text(encoding='utf-8'))[1]
    try:
        with oracle_connection()as c:
            q=c.cursor();q.execute('select STATUS,ASSIGNED_RESOURCE_ID from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=1159 and WARE_ID=219023232');status,resource=q.fetchone()
            actor='CQ22'+uuid4().hex[:10];pwd=secrets.token_hex(24)
            q.execute("insert into RUSERS(ID,PASS,NAME,USER_GROUP,WARE_ID,DELETED,PRAVO_ADMIN_LOGIN)values(:a,:p,'CASE list scope QA','TC03QA',222823304,0,1)",a=actor,p=pwd)
            q.execute("insert into RRL_ACCESS_ROLE(ROLE_ID,TITLE,ACTIVE,VERSION_NO)values(:a,'CASE list scope QA',1,1)",a=actor)
            q.execute("insert into RRL_ACCESS_ROLE_RIGHT(ROLE_ID,PERMISSION)values(:a,'case_pick_view')",a=actor)
            q.execute("insert into RRL_ACCESS_ASSIGNMENT(ASSIGNMENT_ID,USERNAME,ROLE_ID,SCOPE_KIND,SCOPE_ID,MEMBERSHIP,VALID_FROM,VALID_UNTIL,ASSIGNED_BY,REASON,VERSION_NO)values(:a,:a,:a,'WAREHOUSE','219023232','CURRENT',systimestamp-interval '1'minute,systimestamp+interval '2'hour,'admin','CASE list query equivalence under current grants',1)",a=actor);c.commit()
            q.execute("select RRL_HAS_WRIGHT(:a,'case_pick_view'),RRL_ACCESS_API.allowed(:a,'case_pick_view','WAREHOUSE','219023232')from dual",a=actor);assert q.fetchone()==(0,1)
        report.update(actor=actor,warehouse=219023232,case_id=1159,native_status=status)
        kwargs=dict(warehouse=219023232,status=status,limit=1)
        assert compare('No owner grant excludes before limit',**kwargs)==[]
        url='/api/tradecase/warehouses/219023232/stock/owner-grants'
        grant=dict(operation_id=actor+'.owner',expected_version=0,username=actor,owner_id='SNS',can_view=True,can_operate=False,reason='Read-only equality of CASE list and totals')
        expect(200,http('PUT',url,grant));owner=True
        assert compare('Current SNS view returns known case with limit1',**kwargs)==[1159]
        for scope in ['all','mine','free','self']:
            compare('Scope '+scope,warehouse=219023232,status=status,scope=scope,resource=resource if scope=='mine'else None)
        assert compare('Foreign warehouse excluded',warehouse=222823304,status=status)==[]
        query='/api/case-pick/tasks?scope=all&status='+status+'&limit=1&ware_id=219023232'
        current=expect(200,http('GET',query,actor=actor,password=pwd));assert [x['case_pick_task_id']for x in current]==[1159]
        expect(403,http('GET',query.replace('219023232','222823304'),actor=actor,password=pwd))
        expect(200,http('PUT',url,dict(grant,operation_id=actor+'.retire.owner',expected_version=1,can_view=False)));owner=False
        assert compare('Revoked SNS hides case and no stale totals',**kwargs)==[]
        assert expect(200,http('GET',query,actor=actor,password=pwd))==[]
        with oracle_connection()as c:
            q=c.cursor();q.execute('update RRL_ACCESS_ASSIGNMENT set REVOKED_AT=systimestamp where ASSIGNMENT_ID=:a',a=actor);c.commit()
        expect(403,http('GET',query,actor=actor,password=pwd))
        with oracle_connection()as c:
            q=c.cursor();q.execute('select sum(REMAIN),sum(HARD_RESERVED_BASE)from RRL_REMAINS r join RRL_CELLS c on c.CELL=r.CELL where c.WARE_ID=219023232');assert q.fetchone()==(10,0)
        report['status']='PASS'
    finally:
        if actor:
            try:
                if owner:expect(200,http('PUT','/api/tradecase/warehouses/219023232/stock/owner-grants',dict(operation_id=actor+'.retire.owner',expected_version=1,username=actor,owner_id='SNS',can_view=False,can_operate=False,reason='Retire CASE list QA')))
            finally:
                with oracle_connection()as c:
                    q=c.cursor();q.execute("update RUSERS set DELETED=1 where ID=:a and USER_GROUP='TC03QA'",a=actor);q.execute('update RRL_ACCESS_ASSIGNMENT set REVOKED_AT=coalesce(REVOKED_AT,systimestamp)where ASSIGNMENT_ID=:a',a=actor);c.commit()
            report['retired']=True
        report['http']=CALLS;(OUT/'case-queue-scope.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    print(json.dumps({k:v for k,v in report.items()if k!='http'}))
