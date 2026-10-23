"""Real yard HTTP/Oracle with controlled accepted SUPPLY metadata; no goods receipt or stock effect."""
from concurrent.futures import ThreadPoolExecutor
from hashlib import sha256
import json
from pathlib import Path
import secrets
import sys
from threading import Barrier
import time
from uuid import uuid4

ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT),str(ROOT/'scripts')]
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment()
from tools.mcp.tms_mcp_server import oracle_connection
import requests

TAG='YI23'+uuid4().hex[:10]
WARE,OTHER=220793322,210564699
ACTOR=TAG+'.QA';PASSWORD=secrets.token_hex(24)
BASE=f'/api/tradecase/warehouses/{WARE}'
OUT=ROOT/'runtime/test-evidence/tradecase/2026-10-23/T10'/f'{TAG}.json'
report=dict(status='FAIL',tag=TAG,basis='Controlled accepted supply fixtures; actual yard API/native; no receipt/quantity commands',checks=[],requests=[],http=[])
created=False

def save():OUT.write_text(json.dumps(report,indent=2,default=str),encoding='utf-8')

def call(method,path,body=None,status=200,actor=False):
    report['requests'].append(dict(method=method,path=path,body=body));save()
    start=time.perf_counter();r=requests.request(method,'http://127.0.0.1:8088'+path,json=body,auth=(ACTOR,PASSWORD)if actor else ('admin','admin123'),timeout=30)
    result=r.json();report['http'].append(dict(method=method,path=path,status=r.status_code,ms=round((time.perf_counter()-start)*1000,2),result=result));save()
    assert r.status_code in ((status,)if isinstance(status,int)else status),(r.status_code,result)
    return r.status_code,result

def expect(name,ware=WARE,sources=None,vehicle=None,actor=False,status=200):
    body=dict(operation_id=TAG+'.expect.'+name,supply_ids=sources or [TAG+'.'+name],vehicle=vehicle or TAG+'.'+name,planned_arrival_at='2026-10-23T09:00:00+03:00')
    _,value=call('POST',f'/api/tradecase/warehouses/{ware}/yard/visits',body,status,actor)
    return value,body

def transition(visit,action,op=None,ware=WARE,status=200,**extra):
    return call('POST',f'/api/tradecase/warehouses/{ware}/yard/visits/{visit["visit_id"]}/transitions',dict(operation_id=op or TAG+'.'+action+'.'+uuid4().hex[:6],action=action,expected_version=visit['version'],**extra),status)[1]

def grant(version,view,operate):
    return call('PUT',BASE+'/stock/owner-grants',dict(operation_id=TAG+'.grant.'+str(version),expected_version=version,username=ACTOR,owner_id='SNS',can_view=view,can_operate=operate,reason='Owned inbound yard acceptance'))[1]['version']

def stock(q):
    q.execute('select c.WARE_ID,sum(r.REMAIN),sum(r.HARD_RESERVED_BASE)from RRL_REMAINS r join RRL_CELLS c on c.CELL=r.CELL where c.WARE_ID in(210564699,215266197,219023232,220793322)group by c.WARE_ID order by c.WARE_ID')
    return [list(r)for r in q]

try:
    with oracle_connection()as c:
        q=c.cursor();q.execute("select user,sys_context('USERENV','SERVICE_NAME')from dual");assert q.fetchone()==('RABAEV','orcl')
        before=stock(q)
        q.execute('select nvl(max(LOG_ID),0)from RRL_SQL_SLOW_LOG');marker=q.fetchone()[0]
        for ware,names in [(WARE,('A1','A2','B','SCOPE','MIXED')),(OTHER,('OTHER',))]:
            q.execute('select NAME from RRL_WARES where ID=:w',w=ware);assert q.fetchone()[0].startswith('TRADECASE QA ')
            for name in names:
                raw=json.dumps(dict(entity_type='SUPPLY',owner_id='BLC'if name=='MIXED'else 'SNS',pallet_identifier=TAG+'.'+name,fixture='Controlled yard source; not an ERP acceptance proof'))
                q.execute("insert into RRL_TRADE_DOCUMENT(WARE_ID,ENTITY_TYPE,EXTERNAL_ID,SOURCE_ID,VERSION_NO,CONTENT_HASH,BODY_JSON,STATUS,CHANGED_BY)values(:w,'SUPPLY',:id,'TC03.SAP',1,:h,:body,'ACCEPTED','admin')",w=ware,id=TAG+'.'+name,h=sha256(raw.encode()).hexdigest(),body=raw)
        q.execute("insert into RUSERS(ID,PASS,NAME,USER_GROUP,WARE_ID,DELETED,PRAVO_ADMIN_LOGIN)values(:a,:p,'Inbound yard QA','TC03QA',:w,0,1)",a=ACTOR,p=PASSWORD,w=WARE)
        q.execute("insert into RRL_ACCESS_ROLE(ROLE_ID,TITLE,ACTIVE,VERSION_NO)values(:a,'Inbound yard QA',1,1)",a=ACTOR)
        for p in ('tradecase_view','tradecase_yard_operate'):
            q.execute('insert into RRL_ACCESS_ROLE_RIGHT(ROLE_ID,PERMISSION)values(:a,:p)',a=ACTOR,p=p)
        q.execute("insert into RRL_ACCESS_ASSIGNMENT(ASSIGNMENT_ID,USERNAME,ROLE_ID,SCOPE_KIND,SCOPE_ID,MEMBERSHIP,VALID_FROM,VALID_UNTIL,ASSIGNED_BY,REASON,VERSION_NO)values(:a,:a,:a,'WAREHOUSE',:w,'CURRENT',systimestamp-interval '1'minute,systimestamp+interval '1'hour,'admin','Inbound yard acceptance',1)",a=ACTOR,w=str(WARE))
        c.commit();created=True
    a,body=expect('A',sources=[TAG+'.A1',TAG+'.A2'])
    assert a['visit_kind']=='INBOUND'and a['supply_ids']==[TAG+'.A1',TAG+'.A2'] and a['trip_id'] is None
    _,replay=call('POST',BASE+'/yard/visits',body);assert replay['replayed']
    call('POST',BASE+'/yard/visits',dict(body,vehicle='OTHER'),409)
    expect('duplicate',sources=[TAG+'.B',TAG+'.A1'],status=409)
    b,_=expect('B')
    a=transition(a,'ARRIVE');b=transition(b,'ARRIVE')
    other,_=expect('OTHER',ware=OTHER,vehicle=body['vehicle'])
    refused=transition(other,'ARRIVE',ware=OTHER,status=409);assert refused['detail']['code']=='YARD_VEHICLE_OCCUPIED'
    report['checks'].append('Inbound visit with two supplies, exact replay, payload conflict, duplicate supply and cross-warehouse vehicle exclusion')
    barrier=Barrier(2)
    def assign(v):
        barrier.wait(timeout=10)
        return transition(v,'ASSIGN_DOCK',dock='B22D1161',status=(200,409))
    with ThreadPoolExecutor(max_workers=2)as pool:out=list(pool.map(assign,(a,b)))
    winners=[v for v in out if v.get('state')=='AT_DOCK'];assert len(winners)==1,out
    assert next(v for v in out if 'detail'in v)['detail']['code'] in ('YARD_DOCK_OCCUPIED','YARD_DOCK_OR_VEHICLE_OCCUPIED')
    winner=winners[0];loser=b if winner['visit_id']==a['visit_id']else a
    for action in ('START','FINISH','DEPART'):winner=transition(winner,action)
    loser=transition(loser,'ASSIGN_DOCK',dock='B22D1161')
    for action in ('START','FINISH','DEPART'):loser=transition(loser,action)
    other=transition(other,'ARRIVE',ware=OTHER)
    other=transition(other,'CANCEL',ware=OTHER,reason='End simulated yard acceptance')
    report['checks'].append('Two different inbound vehicles compete for one dock; one winner; departure releases dock and vehicle for the next visit')
    expect('SCOPE',actor=True,status=409)
    version=grant(0,True,False)
    expect('SCOPE',actor=True,status=403)
    version=grant(version,True,True)
    expect('mixed-owner',sources=[TAG+'.SCOPE',TAG+'.MIXED'],actor=True,status=409)
    scoped,body=expect('SCOPE',actor=True)
    _,replay=call('POST',BASE+'/yard/visits',body,actor=True);assert replay['replayed']
    call('POST',BASE+'/yard/visits',body,status=409)
    with oracle_connection()as c:
        q=c.cursor();q.execute("update RRL_TRADE_DOCUMENT set VERSION_NO=2 where WARE_ID=:w and ENTITY_TYPE='SUPPLY'and EXTERNAL_ID=:id and VERSION_NO=1",w=WARE,id=TAG+'.SCOPE');assert q.rowcount==1;c.commit()
    refused=transition(scoped,'ARRIVE',status=409);assert refused['detail']['code']=='YARD_SUPPLY_CHANGED'
    _,replay=call('POST',BASE+'/yard/visits',body,actor=True);assert replay['replayed']
    version=grant(version,False,False)
    _,visits=call('GET',BASE+'/yard/visits',actor=True);assert all(v['visit_id']!=scoped['visit_id']for v in visits['visits'])
    call('POST',BASE+'/yard/visits',body,status=409,actor=True)
    with oracle_connection()as c:
        q=c.cursor();q.execute('update RRL_ACCESS_ASSIGNMENT set REVOKED_AT=systimestamp where ASSIGNMENT_ID=:a',a=ACTOR);c.commit()
    call('POST',BASE+'/yard/visits',body,status=403,actor=True)
    report['checks'].append('Every supply owner is checked: hidden BLC refuses mixed SNS/BLC visit; role-only access needs operate; changed source blocks arrival but not original receipt; owner/warehouse revocation denies read/replay')
    report['status']='PASS'
finally:
    if created:
        with oracle_connection()as c:
            q=c.cursor();q.execute('select distinct v.VISIT_ID,v.WARE_ID,v.VERSION_NO,v.STATE from RRL_YARD_VISIT v join RRL_YARD_VISIT_EVENT e on e.VISIT_ID=v.VISIT_ID where e.OPERATION_ID like :tag',tag=TAG+'%');visits=list(q)
        for visit,ware,version,state in visits:
            current=dict(visit_id=visit,version=version,state=state)
            if state=='WORKING':current=transition(current,'FINISH',ware=ware);state=current['state']
            if state=='WORK_DONE':transition(current,'DEPART',ware=ware)
            elif state not in ('DEPARTED','CANCELLED'):transition(current,'CANCEL',ware=ware,reason='End simulated yard acceptance')
        with oracle_connection()as c:
            q=c.cursor();q.execute("select nvl(max(VERSION_NO),0)from RRL_TRADE_OWNER_GRANT where USERNAME=:a and WARE_ID=:w and OWNER_ID='SNS'",a=ACTOR,w=WARE);version=q.fetchone()[0]
        grant(version,False,False)
        with oracle_connection()as c:
            q=c.cursor();q.execute('update RUSERS set DELETED=1 where ID=:a',a=ACTOR)
            q.execute('update RRL_ACCESS_ASSIGNMENT set REVOKED_AT=coalesce(REVOKED_AT,systimestamp)where ASSIGNMENT_ID=:a',a=ACTOR);c.commit()
            assert stock(q)==before
            q.execute("select count(*)from USER_OBJECTS where STATUS='INVALID'");assert q.fetchone()==(0,)
            q.execute('select LOG_ID,ELAPSED_MS,API_PATH,SQL_TEXT from RRL_SQL_SLOW_LOG where LOG_ID>:m order by ELAPSED_MS desc fetch first 8 rows only',m=marker)
            report.update(qa_retired=True,stock=before,slow_sql=[list(r)for r in q],visits=visits)
    save();print(json.dumps(dict(status=report['status'],groups=len(report['checks']),http=len(report['http']),evidence=str(OUT))))
