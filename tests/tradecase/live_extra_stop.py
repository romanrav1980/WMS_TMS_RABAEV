"""Owned planning metadata, real HTTP/native commands; synthetic road cache, no stock effects."""
from datetime import datetime
import json
from pathlib import Path
import secrets
import sys
import time
from uuid import uuid4

ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/'scripts'),str(ROOT/'api/wms_api_server'),str(ROOT)]
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment()
import oracledb
import requests
from tools.mcp.tms_mcp_server import oracle_connection
from app.oracle_gateway import OracleGateway
from app.modules.transport.infrastructure.warehouse_depot import WarehouseDepot

TAG='ES23'+uuid4().hex[:10]
WARE=240000000+secrets.randbelow(9000000)
DEPOT,STORE,EXTRA=[TAG+'.'+s for s in ('DEPOT','STORE','EXTRA')]
report=dict(status='FAIL',road_basis='SYNTHETIC controlled cache, not a provider response',checks=[],http=[])
trip=pallet=None
created=False
depot_version=0
url=None
ACTOR=TAG+'.QA'
PASSWORD=secrets.token_hex(24)
actor_created=False

def balances(q):
    q.execute('select c.WARE_ID,sum(r.REMAIN),sum(r.HARD_RESERVED_BASE)from RRL_REMAINS r join RRL_CELLS c on c.CELL=r.CELL where c.WARE_ID in(210564699,215266197,219023232,220793322)group by c.WARE_ID order by c.WARE_ID')
    return [list(r) for r in q]

def http(method,suffix='',body=None,status=200,actor=False,**params):
    start=time.perf_counter()
    r=requests.request(method,url+suffix,json=body,params=params,auth=(ACTOR,PASSWORD) if actor else ('admin','admin123'),timeout=30)
    data=r.json()
    report['http'].append(dict(method=method,suffix=suffix,status=r.status_code,ms=round((time.perf_counter()-start)*1000,2),result=data))
    assert r.status_code==status,(r.status_code,data)
    return data

def cmd(action,**kwargs):
    return dict(operation_id=TAG+'.'+action+'.'+uuid4().hex[:8],action=action,reason='Owned acceptance fixture',**kwargs)

def configure(q):
    q.callproc('RRL_STOCK_CONFIG_API.begin_change',['admin','warehouse_settings_edit'])

try:
    with oracle_connection() as c:
        q=c.cursor();q.execute("select user,sys_context('USERENV','SERVICE_NAME')from dual")
        assert q.fetchone()==('RABAEV','orcl')
        before=balances(q)
        q.execute('select nvl(max(LOG_ID),0)from RRL_SQL_SLOW_LOG');marker=q.fetchone()[0]
        q.execute('insert into RRL_WARES(ID,NAME)values(:w,:n)',w=WARE,n='TRADECASE QA extra stop '+TAG)
        q.execute("insert into RRL_ACCESS_OBJECT(KIND,OBJECT_ID,TITLE,ACTIVE,VERSION_NO)values('WAREHOUSE',:w,'Extra stop QA',1,1)",w=str(WARE))
        for a in (DEPOT,STORE,EXTRA):
            q.execute('insert into RRL_ADDR(ADDR,SHIROTA,DOLGOTA,DELETED3,UNLOAD_NORM_MIN,TW_STRICT)values(:a,56.84,60.60,0,15,1)',a=a)
        c.commit();created=True
    dep=WarehouseDepot(OracleGateway())
    depot_version=dep.apply(TAG+'.depot',dict(warehouse_id=WARE,expected_version=0,depot_address=DEPOT,reason='Owned extra-stop acceptance'),'admin')['version']
    with oracle_connection() as c:
        q=c.cursor();configure(q)
        out=q.var(oracledb.DB_TYPE_NUMBER)
        q.callproc('RRL_TRANSPORT_EDIT_API.create_trip',['1',datetime(2026,10,23),'admin',out]);trip=int(out.getvalue())
        pallet=int(q.callfunc('RRL_SBORKA_PALLETS_ADD2',oracledb.DB_TYPE_NUMBER,[TAG+'.ST',STORE,1,TAG+'.PALLET','1',datetime(2026,10,23),'','admin',WARE]))
        q.execute("update RRL_SBORKA_PALLETS set TRANSTASK_ID=:t,ORD=1,ZONE_TIME_PLAN_IN=to_date('2026-10-23 09:00','YYYY-MM-DD HH24:MI'),ZONE_TIME_PLAN_OUT=to_date('2026-10-23 14:00','YYYY-MM-DD HH24:MI')where ID=:p",t=trip,p=pallet)
        for i,(code,a,z) in enumerate([('DRIVE','10:00','10:00'),('DRIVE_BACK','13:00','15:00')],1):
            q.execute("insert into RRL_TT_OPERATIONS(ID,TT_ID,OPERATION_CODE,ORD,DURATION_MIN,PLAN_START,PLAN_END)values(SEQ_TT_OPERATIONS.nextval,:t,:code,:i,0,to_date('2026-10-23 '||:a,'YYYY-MM-DD HH24:MI'),to_date('2026-10-23 '||:z,'YYYY-MM-DD HH24:MI'))",t=trip,code=code,i=i,a=a,z=z)
        for a in (STORE,EXTRA):
            q.execute("insert into RRL_STORE_PROFILE(STORE_ADDR,PROFILE_VERSION,RECEIVING_WINDOW_MODE,TIMEZONE_REGION,UPDATED_BY,UPDATED_AT)values(:a,1,'WEEKLY','Europe/Moscow','admin',systimestamp)",a=a)
            for d in range(1,8):q.execute('insert into RRL_STORE_RECEIVING_WINDOW(STORE_ADDR,WEEKDAY,FROM_MINUTE,TO_MINUTE)values(:a,:d,0,1439)',a=a,d=d)
        for a in (DEPOT,STORE,EXTRA):
            for b in (DEPOT,STORE,EXTRA):
                if a!=b:q.execute("insert into RRL_ADDR_DISTANCE_MATRIX(FROM_ADDR,TO_ADDR,DISTANCE_KM,DURATION_MIN,SOURCE,UPDATED_AT,DURATION_BASIS)values(:a,:b,5,10,'osrm',sysdate,'ROAD_PROFILE_ESTIMATE')",a=a,b=b)
        q.callproc('RRL_STOCK_CONFIG_API.end_change');c.commit()
    url=f'http://127.0.0.1:8088/api/transport/preflight/trips/{trip}/extra-stops'
    proposal=http('GET',address=EXTRA,zone='Europe/Moscow')
    assert proposal['decision']=='PROPOSE',proposal
    selected=http('GET',address=EXTRA,zone='Europe/Moscow',position=proposal['position'])
    assert selected['proposal_fingerprint']==proposal['proposal_fingerprint'],(selected,proposal)
    report['checks'].append('Full current native route and insertion; selected proposal equals automatic proposal')
    basis=dict(address=EXTRA,zone='Europe/Moscow',position=proposal['position'],expected_version=proposal['time_version'],source_hash=proposal['source_hash'],proposal_fingerprint=proposal['proposal_fingerprint'])
    approve=cmd('APPROVE',**basis)
    first=http('POST',body=approve)
    assert first['decision_state']=='APPROVED' and first['next_stage']=='WAITING_SAP_ORDER'
    replay=http('POST',body=approve)
    assert {k:v for k,v in first.items() if k!='replayed'}=={k:v for k,v in replay.items() if k!='replayed'} and replay['replayed']
    history=http('GET','/decisions')
    assert history['decisions'][0]['validity']=='CURRENT',history
    conflict=http('POST',body=dict(approve,reason='Changed payload'),status=409)
    assert conflict['detail']['code']=='EXTRA_STOP_OPERATION_CONFLICT'
    duplicate=http('POST',body=cmd('APPROVE',**basis),status=409)
    assert duplicate['detail']['code']=='EXTRA_STOP_ALREADY_APPROVED'
    report['checks'].append('Actual approval, exact replay, changed-body rejection, duplicate rejection and timezone-correct history')
    with oracle_connection() as c:
        q=c.cursor();configure(q)
        q.execute('update RRL_ADDR_DISTANCE_MATRIX set DISTANCE_KM=DISTANCE_KM+1 where FROM_ADDR=:a and TO_ADDR=:b',a=DEPOT,b=EXTRA)
        q.callproc('RRL_STOCK_CONFIG_API.end_change');c.commit()
    changed=http('GET',address=EXTRA,zone='Europe/Moscow',position=proposal['position'])
    assert changed['proposal_fingerprint']!=basis['proposal_fingerprint']
    stale=http('POST',body=cmd('APPROVE',**basis),status=409)
    assert stale['detail']['code'] in ('EXTRA_STOP_PROPOSAL_CHANGED','EXTRA_STOP_SOURCE_CHANGED'),stale
    assert http('GET','/decisions')['decisions'][0]['validity']!='CURRENT'
    report['checks'].append('Mileage change invalidates shown proposal and archived decision')
    policy=cmd('SET_POLICY',new_stops_forbidden=True,expected_policy_version=0)
    ban=http('POST',body=policy);assert ban['policy_version']==1
    assert http('POST',body=policy)['replayed']
    assert http('GET',address=EXTRA,zone='Europe/Moscow')['decision']=='FORBIDDEN'
    http('POST',body=cmd('SET_POLICY',new_stops_forbidden=False,expected_policy_version=0),status=409)
    report['checks'].append('Versioned trip ban, exact replay and stale-policy rejection')
    with oracle_connection() as c:
        q=c.cursor()
        q.execute("insert into RUSERS(ID,PASS,NAME,USER_GROUP,WARE_ID,DELETED,PRAVO_ADMIN_LOGIN)values(:a,:p,'Extra stop scope QA','TC03QA',:w,0,1)",a=ACTOR,p=PASSWORD,w=WARE)
        q.execute("insert into RRL_ACCESS_ROLE(ROLE_ID,TITLE,ACTIVE,VERSION_NO)values(:a,'Extra stop scope QA',1,1)",a=ACTOR)
        for permission in ('transport_dispatch_edit','transport_dispatch_view'):
            q.execute('insert into RRL_ACCESS_ROLE_RIGHT(ROLE_ID,PERMISSION)values(:a,:p)',a=ACTOR,p=permission)
        q.execute("insert into RRL_ACCESS_ASSIGNMENT(ASSIGNMENT_ID,USERNAME,ROLE_ID,SCOPE_KIND,SCOPE_ID,MEMBERSHIP,VALID_FROM,VALID_UNTIL,ASSIGNED_BY,REASON,VERSION_NO)values(:a,:a,:a,'WAREHOUSE',:w,'CURRENT',systimestamp-interval '1'minute,systimestamp+interval '1'hour,'admin','Extra stop scope acceptance',1)",a=ACTOR,w=str(WARE))
        c.commit();actor_created=True
        q.execute("select RRL_HAS_WRIGHT(:a,'transport_dispatch_edit')from dual",a=ACTOR);assert q.fetchone()==(0,)
    http('GET','/decisions',actor=True)
    scoped=cmd('SET_POLICY',new_stops_forbidden=False,expected_policy_version=1)
    assert http('POST',body=scoped,actor=True)['policy_version']==2
    assert http('POST',body=scoped,actor=True)['replayed']
    with oracle_connection() as c:
        q=c.cursor();q.execute('update RRL_ACCESS_ASSIGNMENT set REVOKED_AT=systimestamp where ASSIGNMENT_ID=:a',a=ACTOR);c.commit()
    http('GET','/decisions',actor=True,status=403)
    http('POST',body=scoped,actor=True,status=403)
    report['checks'].append('Assigned warehouse role without legacy permission: metadata command and replay; revocation denies read and archived replay')
    report['status']='PASS'
finally:
    if created:
        if depot_version:
            dep.apply(TAG+'.depot.retire',dict(warehouse_id=WARE,expected_version=depot_version,depot_address=None,reason='Retire owned fixture'),'admin')
        with oracle_connection() as c:
            q=c.cursor()
            if actor_created:
                q.execute('update RUSERS set DELETED=1 where ID=:a',a=ACTOR)
                q.execute('update RRL_ACCESS_ASSIGNMENT set REVOKED_AT=coalesce(REVOKED_AT,systimestamp)where ASSIGNMENT_ID=:a',a=ACTOR)
            if pallet is not None:q.execute('delete from RRL_SBORKA_PALLETS where ID=:p and PALLET_UID=:u',p=pallet,u=TAG+'.PALLET')
            if trip is not None:
                q.execute('delete from RRL_TT_OPERATIONS where TT_ID=:t and FACT_START is null and FACT_END is null',t=trip)
                q.execute("update RRL_TRANSPORT_TASK set DELETED=1 where ID=:t and USER_ID='admin'",t=trip)
            q.execute('delete from RRL_ADDR_DISTANCE_MATRIX where FROM_ADDR in(:a,:b,:c)or TO_ADDR in(:a,:b,:c)',a=DEPOT,b=STORE,c=EXTRA)
            q.execute('update RRL_ADDR set DELETED3=1 where ADDR in(:a,:b,:c)',a=DEPOT,b=STORE,c=EXTRA)
            q.execute("update RRL_ACCESS_OBJECT set ACTIVE=0 where KIND='WAREHOUSE' and OBJECT_ID=:w",w=str(WARE))
            c.commit();assert balances(q)==before
            q.execute("select count(*)from USER_OBJECTS where STATUS='INVALID'");assert q.fetchone()==(0,)
            q.execute('select LOG_ID,ELAPSED_MS,OPERATION_KIND from RRL_SQL_SLOW_LOG where LOG_ID>:m order by ELAPSED_MS desc fetch first 8 rows only',m=marker)
            report.update(fixture_retired=True,stock=before,slow_sql=[list(r) for r in q])
    report.update(tag=TAG,trip=trip,warehouse=WARE)
    path=ROOT/'runtime/test-evidence/tradecase/2026-10-23/T09'/f'{TAG}.json'
    path.write_text(json.dumps(report,indent=2,default=str),encoding='utf-8')
    print(json.dumps(dict(status=report['status'],checks=len(report['checks']),evidence=str(path))))
