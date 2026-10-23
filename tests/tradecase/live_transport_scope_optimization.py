"""Apply checkpointed scope optimization between matched real context/HTTP measurements."""
from hashlib import sha256
import json
from pathlib import Path
import secrets
import statistics
import subprocess
import sys
import time
from uuid import uuid4

ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT),str(ROOT/'scripts')]
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment()
from tools.mcp.tms_mcp_server import oracle_connection
import oracledb
import requests

assert '--apply-migration'in sys.argv or '--installed'in sys.argv,'Explicit mode required'
TAG='TP23'+uuid4().hex[:10]
PASSWORD=secrets.token_hex(24)
WARE,TRIP=220793322,33665
OUT=ROOT/'runtime/test-evidence/tradecase/2026-10-23/T09'
report=dict(status='FAIL',tag=TAG,warehouse=WARE,trip=TRIP,stages={},checks=[])
created=False

def native(denied=False):
    start=time.perf_counter()
    with oracle_connection()as c:
        q=c.cursor();q.execute('set transaction read only');out=q.var(oracledb.DB_TYPE_CLOB)
        try:
            q.callproc('RRL_TT_TIME_API.context',[TRIP,TAG,out]);value=out.getvalue();value=json.loads(value.read()if hasattr(value,'read')else value)
        except oracledb.DatabaseError as error:
            assert denied and getattr(error.args[0],'code',0)==20882,str(error)
            return None
        assert not denied,'Revoked context accepted'
    return dict(ms=round((time.perf_counter()-start)*1000,2),hash=sha256(json.dumps(value,sort_keys=True,separators=(',',':')).encode()).hexdigest())

def stage(name):
    result=dict(native=[native()for _ in range(6)],http=[])
    for _ in range(3):
        start=time.perf_counter();r=requests.get(f'http://127.0.0.1:8088/api/transport/preflight/trips/{TRIP}/extra-stops/decisions',auth=(TAG,PASSWORD),timeout=30)
        assert r.status_code==200,(r.status_code,r.text)
        result['http'].append(round((time.perf_counter()-start)*1000,2))
    result['warm_native_median']=statistics.median(x['ms']for x in result['native'][1:])
    result['http_median']=statistics.median(result['http'])
    report['stages'][name]=result
    return result

try:
    with oracle_connection()as c:
        q=c.cursor();q.execute("select user,sys_context('USERENV','SERVICE_NAME')from dual");assert q.fetchone()==('RABAEV','orcl')
        q.execute("insert into RUSERS(ID,PASS,NAME,USER_GROUP,WARE_ID,DELETED,PRAVO_ADMIN_LOGIN)values(:a,:p,'Transport context QA','TC03QA',:w,0,1)",a=TAG,p=PASSWORD,w=WARE)
        q.execute("insert into RRL_ACCESS_ROLE(ROLE_ID,TITLE,ACTIVE,VERSION_NO)values(:a,'Transport context QA',1,1)",a=TAG)
        q.execute("insert into RRL_ACCESS_ROLE_RIGHT(ROLE_ID,PERMISSION)values(:a,'transport_dispatch_view')",a=TAG)
        q.execute("insert into RRL_ACCESS_ASSIGNMENT(ASSIGNMENT_ID,USERNAME,ROLE_ID,SCOPE_KIND,SCOPE_ID,MEMBERSHIP,VALID_FROM,VALID_UNTIL,ASSIGNED_BY,REASON,VERSION_NO)values(:a,:a,:a,'WAREHOUSE',:w,'CURRENT',systimestamp-interval '1'minute,systimestamp+interval '1'hour,'admin','Transport context comparison',1)",a=TAG,w=str(WARE))
        c.commit();created=True
    before=stage('before') if '--installed'not in sys.argv else json.loads((OUT/'TP2389cdbba1f0.json').read_text(encoding='utf-8'))['stages']['before']
    if '--installed'in sys.argv:
        report['stages']['before']=before
        report['before_evidence']='TP2389cdbba1f0.json: same warehouse, role permissions, source JSON; fresh QA actor after API pool restart'
    for action in (()if '--installed'in sys.argv else ('apply','rollback','apply')):
        index=len(report.setdefault('migration',[]))
        path=OUT/f'{TAG}.{index}.{action}.txt'
        with path.open('w',encoding='utf-8')as output:
            done=subprocess.run([sys.executable,str(ROOT/'scripts/stock_posting_apply.py'),str(ROOT/'db/migrations/2026-10-23_transport_scope_precheck'/f'{action}.sql')],stdout=output,stderr=subprocess.STDOUT,cwd=ROOT)
        report['migration'].append(dict(action=action,exit_code=done.returncode,evidence=str(path)))
        assert done.returncode==0,path
    after=stage('after')
    assert len({x['hash']for phase in (before,after)for x in phase['native']})==1,'Context result changed'
    report['checks'].append('Six native contexts per stage have identical complete JSON; same warehouse and permissions; three actual HTTP reads per stage')
    with oracle_connection()as c:
        q=c.cursor();q.execute('update RUSERS set WARE_ID=219023232 where ID=:a',a=TAG);c.commit()
    assert native()['hash']==after['native'][0]['hash']
    report['checks'].append('Assigned right on a warehouse other than the current user warehouse still works via unchanged fallback')
    with oracle_connection()as c:
        q=c.cursor();q.execute('update RRL_ACCESS_ASSIGNMENT set REVOKED_AT=systimestamp where ASSIGNMENT_ID=:a',a=TAG);c.commit()
    native(denied=True)
    r=requests.get(f'http://127.0.0.1:8088/api/transport/preflight/trips/{TRIP}/extra-stops/decisions',auth=(TAG,PASSWORD),timeout=30);assert r.status_code==403,(r.status_code,r.text)
    report['checks'].append('Revocation immediately denies native context and actual HTTP read')
    report['status']='PASS'
finally:
    if created:
        with oracle_connection()as c:
            q=c.cursor();q.execute('update RUSERS set DELETED=1 where ID=:a',a=TAG)
            q.execute('update RRL_ACCESS_ASSIGNMENT set REVOKED_AT=coalesce(REVOKED_AT,systimestamp)where ASSIGNMENT_ID=:a',a=TAG);c.commit()
            q.execute("select count(*)from USER_OBJECTS where STATUS='INVALID'");assert q.fetchone()==(0,)
        report['qa_retired']=True
    path=OUT/f'{TAG}.json';path.write_text(json.dumps(report,indent=2),encoding='utf-8')
    print(json.dumps(dict(status=report['status'],stages=report['stages'],evidence=str(path))))
