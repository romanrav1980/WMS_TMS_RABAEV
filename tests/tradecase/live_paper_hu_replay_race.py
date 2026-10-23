"""Three concurrent identical HTTP completions of an owned empty HU; no goods receipt or stock effect."""
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
import os
from pathlib import Path
import sys
from threading import Barrier
import time
import requests

ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT),str(ROOT/'scripts'),str(ROOT/'tests/tradecase')]
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment()
from tools.mcp.tms_mcp_server import oracle_connection
from live_document_acceptance import http,expect,CALLS
os.environ['TRADECASE_ADMIN_USER']='admin';os.environ['TRADECASE_ADMIN_PASSWORD']='admin123'
OUT=ROOT/'runtime/test-evidence/tradecase/2026-10-23/T11'
FILE=OUT/'paper-hu-replay-race.json'
s=json.loads(FILE.read_text())if FILE.exists()else dict(status='RUNNING',tag='PH23.68eb5dba',requests={},results={})

def save():FILE.write_text(json.dumps(s,indent=2,default=str),encoding='utf-8')
def query(sql,**binds):
    with oracle_connection()as c:
        q=c.cursor();q.execute(sql,binds);return q.fetchall()
def step(key,path,body):
    if key not in s['requests']:s['requests'][key]=dict(path=path,body=body);save()
    if key not in s['results']:
        r=s['requests'][key];s['results'][key]=expect(200,http('POST',r['path'],r['body']));save()
    return s['results'][key]
def balances():return query('select c.WARE_ID,nvl(sum(r.REMAIN),0),nvl(sum(r.HARD_RESERVED_BASE),0) from RRL_CELLS c left join RRL_REMAINS r on r.CELL=c.CELL where c.WARE_ID in(210564699,215266197,219023232,220793322,212476763)group by c.WARE_ID order by c.WARE_ID')

def run():
    if s['status']=='PASS':return
    tag=s['tag'];uid=tag+'.HU';source=tag+'.B';target=tag+'.A'
    if 'before'not in s:
        assert query("select user,sys_context('USERENV','SERVICE_NAME')from dual")==[('RABAEV','orcl')]
        assert query('select HU_CURRENT_CELL from RRL_PALLETS where UID_PALLET=:u',u=uid)==[(source,)]
        s['before']=balances();s['slow_marker']=query('select nvl(max(LOG_ID),0)from RRL_SQL_SLOW_LOG')[0][0];save()
    version=query('select HU_CONTENT_VERSION from RRL_PALLETS where UID_PALLET=:u',u=uid)[0][0]
    plan=step('plan','/api/warehouse-hus/plan-move',dict(operation_id=tag+'.race.plan',identifier=uid,target_cell=target,expected_version=version,scan_container=uid,scanned_from_cell=source,scanned_to_cell=target))
    task=plan['task_id'];s['task_id']=task;save();path=f'/api/warehouse-tasks/{task}'
    if 'wire'not in s:
        step('assign',path+'/assign',dict(assigned_to='admin'))
        paper=expect(200,http('GET',path+'/paper'));s['paper_reference']=paper['reference']
        s['wire']=json.dumps(dict(operation_id=tag+'.race.complete',expected_task_signature=paper['task']['task_signature'],fact_qty='1',scanned_pallet=uid,scanned_from_cell=source,scanned_to_cell=target),separators=(',',':'));save()
    barrier=Barrier(3)
    def send(_):
        barrier.wait(timeout=10);start=time.perf_counter()
        r=requests.post('http://127.0.0.1:8088'+path+'/complete',data=s['wire'],headers={'Content-Type':'application/json'},auth=('admin','admin123'),timeout=35)
        return dict(status=r.status_code,ms=round((time.perf_counter()-start)*1000,2),body=r.json())
    with ThreadPoolExecutor(max_workers=3)as executor:s['concurrent']=list(executor.map(send,range(3)))
    save();assert all(r['status']==200 for r in s['concurrent']),s['concurrent']
    assert s['concurrent'][0]['body']==s['concurrent'][1]['body']==s['concurrent'][2]['body']
    assert query('select count(*)from RRL_STOCK_OPERATION where OPERATION_ID=:op',op=tag+'.race.complete')==[(1,)]
    assert query('select STATUS,FACT_QTY from RRL_WAREHOUSE_TASK where TASK_ID=:t',t=task)==[('DONE',1)]
    assert query('select HU_CURRENT_CELL from RRL_PALLETS where UID_PALLET=:u',u=uid)==[(target,)]
    assert query('select count(*)from RRL_WAREHOUSE_TASK_STOCK_MOVE where TASK_ID=:t',t=task)==[(0,)]
    assert [list(r)for r in balances()]==[list(r)for r in s['before']]
    s.update(status='PASS',after=balances(),wire_sha256=hashlib.sha256(s['wire'].encode()).hexdigest(),goods_moves=0)

try:run()
finally:
    s['http']=s.get('http',[])+CALLS
    if 'slow_marker'in s:s['slow_sql']=query('select LOG_ID,ELAPSED_MS,API_PATH,SQL_TEXT from RRL_SQL_SLOW_LOG where LOG_ID>:m order by ELAPSED_MS desc fetch first 8 rows only',m=s['slow_marker'])
    save();print(json.dumps(dict(status=s['status'],task=s.get('task_id'),calls=s.get('concurrent'),evidence=str(FILE))))
