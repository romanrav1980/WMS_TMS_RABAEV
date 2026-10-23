"""Actual role-scoped paper snapshots of completed own QA tasks; no execution or quantity commands."""
import json
from decimal import Decimal
from pathlib import Path
import secrets
import sys
import time
from uuid import uuid4

ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT),str(ROOT/'scripts')]
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment()
from tools.mcp.tms_mcp_server import oracle_connection
import requests

TAG='PR23'+uuid4().hex[:10];PASSWORD=secrets.token_hex(24);WARE=212476763
report=dict(status='FAIL',checks=[],http=[]);created=False

def call(task=1231,signature=None,status=200):
    start=time.perf_counter()
    r=requests.get(f'http://127.0.0.1:8088/api/warehouse-tasks/{task}/paper',params={}if signature is None else dict(expected_signature=signature),auth=(TAG,PASSWORD),timeout=30)
    value=r.json();report['http'].append(dict(task=task,status=r.status_code,ms=round((time.perf_counter()-start)*1000,2)))
    assert r.status_code==status,(r.status_code,value)
    return value

try:
    with oracle_connection()as c:
        q=c.cursor();q.execute("select user,sys_context('USERENV','SERVICE_NAME')from dual");assert q.fetchone()==('RABAEV','orcl')
        q.execute("select UID_PALLET,STATUS from RRL_WAREHOUSE_TASK where TASK_ID=1231 and FROM_WARE_ID=:w",w=WARE)
        assert q.fetchone()==('690000000340515809','DONE')
        q.execute("insert into RUSERS(ID,PASS,NAME,USER_GROUP,WARE_ID,DELETED,PRAVO_ADMIN_LOGIN)values(:a,:p,'Paper snapshot QA','TC03QA',:w,0,1)",a=TAG,p=PASSWORD,w=WARE)
        q.execute("insert into RRL_ACCESS_ROLE(ROLE_ID,TITLE,ACTIVE,VERSION_NO)values(:a,'Paper snapshot QA',1,1)",a=TAG)
        q.execute("insert into RRL_ACCESS_ROLE_RIGHT(ROLE_ID,PERMISSION)values(:a,'warehouse_task_view')",a=TAG)
        q.execute("insert into RRL_ACCESS_ASSIGNMENT(ASSIGNMENT_ID,USERNAME,ROLE_ID,SCOPE_KIND,SCOPE_ID,MEMBERSHIP,VALID_FROM,VALID_UNTIL,ASSIGNED_BY,REASON,VERSION_NO)values(:a,:a,:a,'WAREHOUSE',:w,'CURRENT',systimestamp-interval '1'minute,systimestamp+interval '1'hour,'admin','Paper snapshot acceptance',1)",a=TAG,w=str(WARE))
        q.execute('select nvl(max(LOG_ID),0)from RRL_SQL_SLOW_LOG');marker=q.fetchone()[0]
        q.execute('select min(TASK_ID)from RRL_WAREHOUSE_TASK where FROM_WARE_ID=220793322');foreign=q.fetchone()[0];assert foreign
        c.commit();created=True
    paper=call();signature=paper['task']['task_signature']
    assert paper['reference']=='WTASK:1231:'+signature and '<svg'in paper['barcode_svg']
    report['snapshot_fields']={key:paper['task'].get(key)for key in ('task_id','qty_exact','assigned_to','assigned_to_name','from_warehouse_name','to_warehouse_name','task_signature')}
    assert Decimal(paper['task']['qty_exact'])==2 and paper['task']['assigned_to']=='admin'
    assert paper['task']['from_warehouse_name'] and paper['task']['to_warehouse_name']
    assert call(signature=signature)['reference']==paper['reference']
    assert call(signature='0'*64,status=409)['detail']['code']=='PAPER_TASK_CHANGED'
    call(task=foreign,status=404)
    report['checks'].append('Role-only own snapshot with exact quantity/warehouse/employee names; same printed version repeats, stale version409, foreign task404')
    with oracle_connection()as c:
        q=c.cursor();q.execute('update RRL_ACCESS_ASSIGNMENT set REVOKED_AT=systimestamp where ASSIGNMENT_ID=:a',a=TAG);c.commit()
    call(status=403)
    report['checks'].append('Revocation removes paper snapshot access on the next request')
    report['status']='PASS'
finally:
    if created:
        with oracle_connection()as c:
            q=c.cursor();q.execute('update RUSERS set DELETED=1 where ID=:a',a=TAG)
            q.execute('update RRL_ACCESS_ASSIGNMENT set REVOKED_AT=coalesce(REVOKED_AT,systimestamp)where ASSIGNMENT_ID=:a',a=TAG);c.commit()
            q.execute('select LOG_ID,ELAPSED_MS,API_PATH,SQL_TEXT from RRL_SQL_SLOW_LOG where LOG_ID>:m order by ELAPSED_MS desc fetch first 6 rows only',m=marker)
            report.update(qa_retired=True,slow_sql=[list(r)for r in q])
    out=ROOT/'runtime/test-evidence/tradecase/2026-10-23/T11'/f'{TAG}.json';out.write_text(json.dumps(report,indent=2,default=str),encoding='utf-8')
    print(json.dumps(dict(status=report['status'],evidence=str(out),calls=len(report['http']))))
