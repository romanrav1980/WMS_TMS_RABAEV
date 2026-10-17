"""Actual HTTP metadata commits only; no physical task completion or stock command."""
import sys,json
from pathlib import Path
from uuid import uuid4
from concurrent.futures import ThreadPoolExecutor
import httpx
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT/'scripts'),str(ROOT/'api/wms_api_server')]
from warehouse_task_assignment_fixture import RUNTIME,REPORT,snapshot
from warehouse_task_assignment_native import state
from app.oracle_gateway import OracleGateway


def run(action):
 g=OracleGateway();ctx=json.loads(RUNTIME.read_text(encoding='utf-8'));base='http://127.0.0.1:8088';url='/api/warehouse-tasks/'+str(ctx['task']);checks=[];before=snapshot(g)
 with httpx.Client(base_url=base,auth=(ctx['actor'],ctx['password']),timeout=30)as c:
  r=c.get(url+'/resource-context');assert r.status_code==200,r.text[:500];current=r.json();checks.append('authenticated_no_flat_permission_context')
  body=dict(operation_id='TASK.HTTP:'+uuid4().hex,action=action,target=ctx['actor'],expected_assignment_version=current['assignment_version'],expected_task_signature=current['task_signature'],resource_session_id=ctx['session'],resource_id=ctx['resource'],equipment_id=ctx['equipment'])
  if action=='ASSIGN':
   def send(_):
    with httpx.Client(base_url=base,auth=(ctx['actor'],ctx['password']),timeout=30)as worker:return worker.post(url+'/resource-commands',json=body)
   with ThreadPoolExecutor(max_workers=2)as pool:responses=list(pool.map(send,range(2)))
   assert all(r.status_code==200 for r in responses),[(r.status_code,r.text[:500])for r in responses]
   saved=responses[0].json();assert saved==responses[1].json();checks.append('two_concurrent_identical_assign_one_durable_effect')
  else:
   r=c.post(url+'/resource-commands',json=body);assert r.status_code==200,r.text[:500];saved=r.json();checks.append('actual_start_metadata_committed')
  assert saved['outcome']=='APPLIED'and saved['changed']and not saved['stock_posted']and saved['assignment_version']==current['assignment_version']+1,saved
  r=c.post(url+'/resource-commands',json=body);assert r.status_code==200 and r.json()==saved,r.text[:500];checks.append('exact_original_command_replay')
  r=c.get('/api/warehouse-tasks/resource-commands/'+body['operation_id']);assert r.status_code==200 and r.json()==saved,r.text[:500];checks.append('durable_original_receipt')
  changed={**body,'resource_session_id':ctx['session']+999999};r=c.post(url+'/resource-commands',json=changed);assert r.status_code==409 and r.json()['detail']['outcome_confirmed']is False,r.text[:500];checks.append('changed_body_never_reuses_or_confirms_original_intent')
  r=c.post(url+'/resource-commands',json={**body,'actor':'admin'});assert r.status_code==422,r.text[:500];checks.append('browser_actor_rejected')
  r=c.get('/api/warehouse-tasks/resource-commands/'+body['operation_id'],auth=(ctx['other'],ctx['other_password']));assert r.status_code==403,r.text[:500];checks.append('receipt_not_transferable_to_other_actor')
  for legacy in('assign','start'):
   r=c.post(url+'/'+legacy,json={'assigned_to':ctx['actor'],'resource_session_id':ctx['session']});assert r.status_code==403,(legacy,r.status_code,r.text[:500])
  checks.append('legacy_flat_routes_unchanged_no_fallback')
  if action=='ASSIGN':
   rejected={**body,'operation_id':'TASK.REJECTED:'+uuid4().hex,'expected_assignment_version':saved['assignment_version']+1,'expected_task_signature':saved['task_signature']}
   r=c.post(url+'/resource-commands',json=rejected);assert r.status_code==409 and r.json()['outcome']=='REJECTED'and r.json()['error_code']=='WTASK_EXPECTED_VERSION_CHANGED',r.text[:500]
   original=r.json();r=c.post(url+'/resource-commands',json=rejected);assert r.status_code==409 and r.json()==original,r.text[:500];checks.append('definitive_rejection_durable_exact_repeat')
   ctx['rejected_body']=rejected;ctx['rejected_ack']=original
  elif 'rejected_body'in ctx:
   r=c.post(url+'/resource-commands',json=ctx['rejected_body']);assert r.status_code==409 and r.json()==ctx['rejected_ack'],r.text[:500];checks.append('old_rejected_intent_cannot_execute_after_later_state_change')
 assert snapshot(g)==before
 assert g.fetch_all('select count(*)N from RRL_RESOURCE_FACT_EVENT where TASK_ID=:id and EVENT_TYPE=:event',{'id':ctx['task'],'event':'ASSIGNED'if action=='ASSIGN'else'STARTED'})[0]['n']==1
 assert g.fetch_all('select count(*)N from RRL_WTASK_RESOURCE_COMMAND where OPERATION_ID=:op',{'op':body['operation_id']})[0]['n']==1
 ctx[action.lower()+'_body']=body;ctx[action.lower()+'_ack']=saved;RUNTIME.write_text(json.dumps(ctx,default=str),encoding='utf-8')
 report=dict(status='PASS',checks=checks,operation_id=body['operation_id'],state=state(g,ctx),goods_commit=False,metadata_command_committed=True,main_and_CRES_mutated=False)
 (REPORT/('http-'+action.lower()+'.json')).write_text(json.dumps(report,indent=2,default=str),encoding='utf-8');print(json.dumps({'status':'PASS','action':action,'groups':len(checks),'version':saved['assignment_version']}))


if __name__=='__main__':run(sys.argv[1])
