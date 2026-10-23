"""Compare actual old/new permission SQL on the same role and connection; no stock commands."""
import json
from pathlib import Path
import secrets
import statistics
import sys
import time
from uuid import uuid4

ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/'api/wms_api_server'),str(ROOT),str(ROOT/'scripts')]
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment()
from tools.mcp.tms_mcp_server import oracle_connection
from app.modules.inventory.infrastructure.task_scoped_view import require_task_viewer

class Capture:
    def execute(self, sql, **binds): self.sql=sql
    def fetchone(self): return (1,)

capture=Capture();require_task_viewer(capture,'unused',None);new=capture.sql
old="""select count(*) from RUSERS u where u.ID=:actor and nvl(u.DELETED,0)=0
        and exists(select 1 from RRL_WARES w where (:ware is null or w.ID=:ware)
        and RRL_ACCESS_API.allowed(:actor,'warehouse_task_view','WAREHOUSE',to_char(w.ID),:actor)=1)"""
actor='PV23'+uuid4().hex[:10];ware=212476763
report=dict(status='FAIL',actor=actor,checks=[])
with oracle_connection()as connection:
    q=connection.cursor();q.execute("select user,sys_context('USERENV','SERVICE_NAME')from dual");assert q.fetchone()==('RABAEV','orcl')
    try:
        q.execute("insert into RUSERS(ID,PASS,NAME,USER_GROUP,WARE_ID,DELETED,PRAVO_ADMIN_LOGIN)values(:a,:p,'Paper view precheck QA','TC03QA',:w,0,1)",a=actor,p=secrets.token_hex(24),w=ware)
        q.execute("insert into RRL_ACCESS_ROLE(ROLE_ID,TITLE,ACTIVE,VERSION_NO)values(:a,'Paper view precheck QA',1,1)",a=actor)
        q.execute("insert into RRL_ACCESS_ROLE_RIGHT(ROLE_ID,PERMISSION)values(:a,'warehouse_task_view')",a=actor)
        q.execute("insert into RRL_ACCESS_ASSIGNMENT(ASSIGNMENT_ID,USERNAME,ROLE_ID,SCOPE_KIND,SCOPE_ID,MEMBERSHIP,VALID_FROM,VALID_UNTIL,ASSIGNED_BY,REASON,VERSION_NO)values(:a,:a,:a,'WAREHOUSE',:w,'CURRENT',systimestamp-interval '1'minute,systimestamp+interval '1'hour,'admin','Paper view precheck SQL comparison',1)",a=actor,w=str(ware))
        connection.commit()
        for title,current_warehouse,requested,revoked,deleted,expected in [
            ('same current warehouse',ware,None,False,False,1),
            ('explicit current warehouse',ware,ware,False,False,1),
            ('different current warehouse fallback',220793322,None,False,False,1),
            ('no current warehouse fallback',None,None,False,False,1),
            ('foreign requested warehouse',ware,220793322,False,False,0),
            ('revoked assignment',ware,None,True,False,0),
            ('retired user',ware,None,False,True,0),
        ]:
            q.execute('update RUSERS set WARE_ID=:w,DELETED=:d where ID=:a',w=current_warehouse,d=int(deleted),a=actor)
            q.execute('update RRL_ACCESS_ASSIGNMENT set REVOKED_AT=case when :r=1 then systimestamp else null end where ASSIGNMENT_ID=:a',r=int(revoked),a=actor)
            connection.commit();timings={'old':[],'new':[]}
            for repeat in range(5):
                for label,sql in [('old',old),('new',new)]:
                    start=time.perf_counter();q.execute(sql,actor=actor,ware=requested);value=q.fetchone()[0]
                    assert value==expected,(title,label,value,expected)
                    if repeat:timings[label].append(round((time.perf_counter()-start)*1000,2))
            report['checks'].append(dict(case=title,value=expected,median_ms={k:statistics.median(v)for k,v in timings.items()},samples_ms=timings))
        report['status']='PASS'
    finally:
        connection.rollback()
        q.execute('update RUSERS set DELETED=1 where ID=:a',a=actor)
        q.execute('update RRL_ACCESS_ASSIGNMENT set REVOKED_AT=coalesce(REVOKED_AT,systimestamp)where ASSIGNMENT_ID=:a',a=actor)
        connection.commit();report['qa_retired']=True
out=ROOT/'runtime/test-evidence/tradecase/2026-10-23/T11/task-view-precheck.json'
out.write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps(dict(status=report['status'],cases=len(report['checks']),first=report['checks'][0]['median_ms'],evidence=str(out))))
