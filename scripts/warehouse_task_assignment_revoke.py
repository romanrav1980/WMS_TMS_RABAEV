"""Actual Oracle revision fence wait, canonical revoke commit and exact replay restore."""
import sys,json,time,hashlib
from pathlib import Path
from uuid import uuid4
from concurrent.futures import ThreadPoolExecutor
import httpx,oracledb
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT/'scripts'),str(ROOT/'api/wms_api_server')]
from warehouse_task_assignment_native import RUNTIME,REPORT,state,post
from warehouse_task_scoped_complete_smoke import grant
from app.oracle_gateway import OracleGateway
from app.modules.platform.api.metadata_inputs import Command,normalize


def run():
 g=OracleGateway();ctx=json.loads(RUNTIME.read_text());before=state(g,ctx);role,assignment=next((r,a)for r,a in ctx['grants']if r==ctx['prefix']+'rexecute');row=g.fetch_all('select VERSION_NO,REVOKED_AT from RRL_ACCESS_ASSIGNMENT where ASSIGNMENT_ID=:id',{'id':assignment})[0];assert row['revoked_at']is None
 cmd=normalize(Command(operation_id=ctx['prefix']+':REV:'+uuid4().hex,command_type='REVOKE',payload=dict(assignment_id=assignment,expected_version=int(row['version_no']),reason='Verify native task revision fence while exact replay waits')),'ACCESS');wire=json.dumps(cmd,ensure_ascii=False,sort_keys=True,separators=(',',':'));digest=hashlib.sha256(wire.encode()).hexdigest();sid_box={};wait=None;committed=False
 def waiting():
  try:
   with g.transaction('TASK exact receipt current-access waiter')as c:
    c.execute("select to_number(sys_context('USERENV','SID'))from dual");sid_box['sid']=int(c.fetchone()[0]);return post(c,ctx['task'],ctx['assign_body'],ctx['actor'])
  except oracledb.DatabaseError as e:return {'error':str(e),'code':e.args[0].code}
 try:
  with ThreadPoolExecutor(max_workers=1)as pool:
   with g.transaction('Canonical fixture execute revoke holds revision fence until commit')as c:
    c.execute("select to_number(sys_context('USERENV','SID'))from dual");revoker_sid=int(c.fetchone()[0]);out=c.var(oracledb.DB_TYPE_CLOB);c.callproc('RRL_ACCESS_API.execute_command',['admin',cmd['operation_id'],digest,wire,out])
    future=pool.submit(waiting);deadline=time.monotonic()+1.3
    while time.monotonic()<deadline:
     if 'sid'in sid_box:
      rows=g.fetch_all('select SID,EVENT,BLOCKING_SESSION,P2 from V$SESSION where SID=:id',{'id':sid_box['sid']})
      if rows and rows[0]['blocking_session']==revoker_sid and rows[0]['event']=='enq: TM - contention':wait=rows[0];break
     time.sleep(.04)
    assert wait is not None and not future.done(),('No actual revision lock wait observed',sid_box)
    oid=g.fetch_all("select OBJECT_ID from USER_OBJECTS where OBJECT_NAME='RRL_ACCESS_REV'and OBJECT_TYPE='TABLE'")[0]['object_id'];assert wait['p2']==oid,wait
   committed=True;result=future.result(timeout=5);assert result.get('code')==20882 and 'WTASK_CURRENT_SCOPED_AUTHORITY_REQUIRED'in result['error'],result
  assert state(g,ctx)==before,'Replay after revoke must not mutate task, receipt, event or stock'
  with httpx.Client(base_url='http://127.0.0.1:8088',auth=(ctx['actor'],ctx['password']),timeout=20)as client:
   r=client.get('/api/warehouse-tasks/resource-commands/'+ctx['assign_body']['operation_id']);assert r.status_code==403,r.text[:500]
   r=client.post('/api/warehouse-tasks/'+str(ctx['task'])+'/resource-commands',json=ctx['assign_body']);assert r.status_code==403,r.text[:500]
 finally:
  live=g.fetch_all('select REVOKED_AT from RRL_ACCESS_ASSIGNMENT where ASSIGNMENT_ID=:id',{'id':assignment})[0]
  if live['revoked_at']is not None:
   grant(g,ctx,ctx['actor'],'executerestore'+uuid4().hex[:5],'warehouse_task_execute','SELF');RUNTIME.write_text(json.dumps(ctx,default=str),encoding='utf-8')
 with httpx.Client(base_url='http://127.0.0.1:8088',auth=(ctx['actor'],ctx['password']),timeout=20)as client:
  r=client.post('/api/warehouse-tasks/'+str(ctx['task'])+'/resource-commands',json=ctx['assign_body']);assert r.status_code==200 and r.json()==ctx['assign_ack'],r.text[:500]
 assert state(g,ctx)==before
 (REPORT/'revoke-wait.json').write_text(json.dumps(dict(status='PASS',checks=['actual_revision_SHARE_wait_observed','canonical_revoke_commit_before_waiter_continues','current_authority_rechecked_before_original_receipt','HTTP_receipt_and_replay_denied_while_revoked','new_canonical_SELF_grant_restores_exact_original_replay','task_receipt_events_versions_stock_unchanged'],observed_wait=wait,metadata_revoke_commit=committed,access_history_retained=True,goods_commit=False),indent=2,default=str),encoding='utf-8');print('TASK_ACTUAL_REVISION_WAIT_REVOKE_RESTORE_6_PASS')


if __name__=='__main__':run()
