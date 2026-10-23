"""Real HTTP execution of an empty owned HU task; does not prove movement of goods or hardware."""
import json
import os
from pathlib import Path
import sys
from uuid import uuid4

ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT),str(ROOT/'scripts'),str(ROOT/'tests/tradecase')]
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment()
from tools.mcp.tms_mcp_server import oracle_connection
from live_document_acceptance import http,expect,CALLS
os.environ['TRADECASE_ADMIN_USER']='admin'
os.environ['TRADECASE_ADMIN_PASSWORD']='admin123'
FILE=ROOT/'runtime/test-evidence/tradecase/2026-10-23/T11/paper-hu-execution.json'
s=json.loads(FILE.read_text(encoding='utf-8'))if FILE.exists()else dict(tag='PH23.'+uuid4().hex[:8],warehouse=212476763,requests={},results={},checks=[],status='RUNNING')

def save():
    FILE.write_text(json.dumps(s,indent=2,default=str),encoding='utf-8')

def query(sql,**binds):
    with oracle_connection()as connection:
        q=connection.cursor();q.execute(sql,binds);return q.fetchall()

def step(name,method,path,body=None,status=200):
    if name not in s['requests']:
        s['requests'][name]=dict(method=method,path=path,body=body,status=status);save()
    if name not in s['results']:
        r=s['requests'][name]
        s['results'][name]=expect(r['status'],http(r['method'],r['path'],r['body']));save()
    return s['results'][name]

def balances():
    return query('select c.WARE_ID,nvl(sum(r.REMAIN),0),nvl(sum(r.HARD_RESERVED_BASE),0) from RRL_CELLS c left join RRL_REMAINS r on r.CELL=c.CELL where c.WARE_ID in (210564699,215266197,219023232,220793322,212476763) group by c.WARE_ID order by c.WARE_ID')

def run():
    if s['status']=='PASS':
        print('Already PASS; no new commands');return
    tag=s['tag'];ware=s['warehouse'];uid=tag+'.HU';source=tag+'.A';target=tag+'.B'
    if 'cells'not in s:
        assert query("select user,sys_context('USERENV','SERVICE_NAME')from dual")==[('RABAEV','orcl')]
        assert query("select NAME from RRL_WARES where ID=:w",w=ware)==[('TRADECASE QA 25cadbfc',)]
        s['before']=balances();assert next(r for r in s['before']if r[0]==ware)[1:]==(0,0)
        s['slow_marker']=query('select nvl(max(LOG_ID),0)from RRL_SQL_SLOW_LOG')[0][0];save()
        with oracle_connection()as connection:
            q=connection.cursor();q.callproc('RRL_STOCK_CONFIG_API.begin_change',['admin','warehouse_settings_edit'])
            try:
                for cell in (source,target):
                    q.execute('insert into RRL_CELLS(CELL,WARE_ID,X,Y,Z,OTBOR,IS_SYSTEM,LIMIT_WEIGHT,LIMIT_HEIGHT)values(:c,:w,0,0,0,0,0,0,0)',c=cell,w=ware)
                    q.execute("insert into RRL_STOCK_POLICY_GUARD(POLICY_KEY,LOCK_ID)select RRL_STOCK_LOCK_API.resource_key('CELL',:c),nvl(max(LOCK_ID),900000000)+1 from RRL_STOCK_POLICY_GUARD",c=cell)
                connection.commit();s['cells']=[source,target];save()
            finally:q.callproc('RRL_STOCK_CONFIG_API.end_change')
    step('create','POST','/api/warehouse-hus/create',dict(operation_id=tag+'.create',identifier=uid,cell=source,warehouse=ware,container_type='PALLET',tare_weight_kg='0.1',scan_container=uid,scan_cell=source))
    version=query('select HU_CONTENT_VERSION from RRL_PALLETS where UID_PALLET=:u',u=uid)[0][0]
    plan=step('plan','POST','/api/warehouse-hus/plan-move',dict(operation_id=tag+'.plan',identifier=uid,target_cell=target,expected_version=version,scan_container=uid,scanned_from_cell=source,scanned_to_cell=target))
    task=plan['task_id'];s['task_id']=task;save();path=f'/api/warehouse-tasks/{task}'
    step('assign','POST',path+'/assign',dict(assigned_to='admin'))
    printed=step('printed','GET',path+'/paper')
    assert printed['reference']=='WTASK:'+str(task)+':'+printed['task']['task_signature']
    step('start','POST',path+'/start',{})
    old=dict(operation_id=tag+'.stale',expected_task_signature=printed['task']['task_signature'],fact_qty='1',scanned_pallet=uid,scanned_from_cell=source,scanned_to_cell=target)
    refused=step('stale','POST',path+'/complete',old,status=409)
    assert 'TASK_EXPECTED_SIGNATURE_CHANGED'in json.dumps(refused),refused
    assert query('select HU_CURRENT_CELL from RRL_PALLETS where UID_PALLET=:u',u=uid)==[(source,)]
    current=step('current','GET',path+'/paper')
    assert current['task']['task_signature']!=printed['task']['task_signature']
    body=dict(old,operation_id=tag+'.complete',expected_task_signature=current['task']['task_signature'])
    completed=step('complete','POST',path+'/complete',body)
    assert completed['result']['operation_id']==body['operation_id']
    assert expect(200,http('POST',path+'/complete',s['requests']['complete']['body']))==completed
    expect(409,http('POST',path+'/complete',dict(s['requests']['complete']['body'],fact_qty='2')))
    assert query('select STATUS,FACT_QTY from RRL_WAREHOUSE_TASK where TASK_ID=:t',t=task)==[('DONE',1)]
    assert query('select HU_CURRENT_CELL from RRL_PALLETS where UID_PALLET=:u',u=uid)==[(target,)]
    assert query('select count(*)from RRL_WAREHOUSE_TASK_STOCK_MOVE where TASK_ID=:t',t=task)==[(0,)]
    assert query('select count(*)from RRL_STOCK_OPERATION where OPERATION_ID=:op',op=body['operation_id'])==[(1,)]
    assert [list(r)for r in balances()]==[list(r)for r in s['before']]
    s['checks']=['Own empty HU task assigned/printed/started; old paper version refused without movement','Current paper version completed; exact replay same receipt, changed body409','One DONE task, one completion journal entry; zero goods movement, protected balances unchanged']
    s['after']=balances();s['status']='PASS';save()

try:
    run()
finally:
    s['http']=s.get('http',[])+CALLS
    if 'slow_marker'in s:
        s['slow_sql']=query('select LOG_ID,ELAPSED_MS,API_PATH,SQL_TEXT from RRL_SQL_SLOW_LOG where LOG_ID>:m order by ELAPSED_MS desc fetch first 6 rows only',m=s['slow_marker'])
    save();print(json.dumps(dict(status=s['status'],task=s.get('task_id'),evidence=str(FILE))))
