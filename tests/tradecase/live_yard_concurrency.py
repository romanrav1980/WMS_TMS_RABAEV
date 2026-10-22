"""Two dispatchers on one owned QA trip; genuine HTTP/Oracle, simulated yard facts."""
from concurrent.futures import ThreadPoolExecutor
import json
from pathlib import Path
import sys
from threading import Barrier
from uuid import uuid4

ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT),str(ROOT/'scripts'),str(ROOT/'tests/tradecase')]
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment()
from tools.mcp.tms_mcp_server import oracle_connection
from live_document_acceptance import http,CALLS

WARE=220793322
TAG='YC23'+uuid4().hex[:10]
BASE=f'/api/tradecase/warehouses/{WARE}/yard/visits'
report=dict(status='FAIL',fixture='Own QA native trip, simulated arrival, real concurrent API/Oracle commands',checks=[],http=CALLS)
visit=None

def call(method,path,body=None):
    return http(method,path,body,'admin','admin123')

def race(requests):
    barrier=Barrier(2)
    def run(request):
        barrier.wait(timeout=10)
        return call('POST',*request)
    with ThreadPoolExecutor(max_workers=2)as pool:
        out=list(pool.map(run,requests))
    assert sorted(code for code,_ in out)==[200,409],out
    return out

def balances(q):
    q.execute('select c.WARE_ID,sum(r.REMAIN),sum(r.HARD_RESERVED_BASE)from RRL_REMAINS r join RRL_CELLS c on c.CELL=r.CELL where c.WARE_ID in(210564699,215266197,219023232,220793322)group by c.WARE_ID order by c.WARE_ID')
    return [list(r)for r in q]

try:
    with oracle_connection()as c:
        q=c.cursor();q.execute('select NAME from RRL_WARES where ID=:w',w=WARE)
        assert q.fetchone()[0].startswith('TRADECASE QA ')
        q.execute("select count(*)from RRL_YARD_VISIT where WARE_ID=:w and TRIP_ID='R1.1168'and STATE not in('DEPARTED','CANCELLED')",w=WARE)
        assert q.fetchone()==(0,),'Another active visit; leave it unchanged'
        q.execute('select nvl(max(LOG_ID),0)from RRL_SQL_SLOW_LOG');marker=q.fetchone()[0]
        before=balances(q)
    bodies=[dict(operation_id=TAG+'.expect.'+str(i),trip_id='R1.1168')for i in range(2)]
    out=race([(BASE,b)for b in bodies])
    winner=next(result for code,result in out if code==200)
    visit=winner['visit_id']
    assert next(result for code,result in out if code==409)['detail']['code']=='YARD_TRIP_VISIT_ACTIVE'
    winning_body=bodies[next(i for i,(code,_)in enumerate(out)if code==200)]
    code,replay=call('POST',BASE,winning_body);assert code==200 and replay['replayed']
    report['checks'].append('Concurrent expectations: one active trip visit; exact winner replay')
    path=BASE+f'/{visit}/transitions'
    code,arrived=call('POST',path,dict(operation_id=TAG+'.arrive',action='ARRIVE',expected_version=winner['version']))
    assert code==200,(code,arrived)
    bodies=[dict(operation_id=TAG+'.dock.'+str(i),action='ASSIGN_DOCK',expected_version=arrived['version'],dock=dock)for i,dock in enumerate(('B22D1161','N22DA1168'))]
    out=race([(path,b)for b in bodies])
    winner=next(result for code,result in out if code==200)
    code,replay=call('POST',path,bodies[next(i for i,(code,_)in enumerate(out)if code==200)])
    assert code==200 and replay['replayed']
    with oracle_connection()as c:
        q=c.cursor();q.execute('select STATE,DOCK,VERSION_NO from RRL_YARD_VISIT where VISIT_ID=:v',v=visit)
        assert q.fetchone()==('AT_DOCK',winner['dock'],winner['version'])
        q.execute("select count(*)from RRL_YARD_VISIT_EVENT where VISIT_ID=:v and ACTION='ASSIGN_DOCK'",v=visit);assert q.fetchone()==(1,)
    report['checks'].append('Concurrent assignments of one visit: one dock fact and one version; loser rejected, winner replays')
    report['status']='PASS'
finally:
    if visit is not None:
        with oracle_connection()as c:
            q=c.cursor();q.execute('select VERSION_NO,STATE from RRL_YARD_VISIT where VISIT_ID=:v',v=visit);version,state=q.fetchone()
        if state not in ('CANCELLED','DEPARTED'):
            code,result=call('POST',BASE+f'/{visit}/transitions',dict(operation_id=TAG+'.cancel',action='CANCEL',expected_version=version,reason='End simulated QA yard concurrency'))
            assert code==200,(code,result)
    with oracle_connection()as c:
        q=c.cursor();assert balances(q)==before
        q.execute("select count(*)from USER_OBJECTS where STATUS='INVALID'");assert q.fetchone()==(0,)
        q.execute('select LOG_ID,ELAPSED_MS,API_PATH,SQL_TEXT from RRL_SQL_SLOW_LOG where LOG_ID>:m order by ELAPSED_MS desc fetch first 8 rows only',m=marker)
        report.update(stock=before,slow_sql=[list(r)for r in q],visit=visit)
    path=ROOT/'runtime/test-evidence/tradecase/2026-10-23/T10'/f'{TAG}.json'
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(report,indent=2,default=str),encoding='utf-8')
    print(json.dumps(dict(status=report['status'],checks=len(report['checks']),evidence=str(path))))
