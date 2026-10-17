"""Current-access/HTTP replay on compensated wave565; all native stock trials roll back."""
import sys,json,secrets
from pathlib import Path
from datetime import datetime,timedelta,timezone
from uuid import uuid4
import httpx,oracledb
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'scripts'),str(ROOT/'api/wms_api_server')]
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment()
from app.oracle_gateway import OracleGateway
from app.modules.platform.public import stock_configuration_transaction
from app.modules.fulfillment.public import read_launch_receipt
from warehouse_task_scoped_complete_smoke import access,post,RollbackTrial

def trial(g,body,denial=None):
 try:
  with g.transaction('Current source/launch replay guard; caller-owned rollback')as c:
   try:
    result=post(c,body)
    assert denial is None,'Expected '+str(denial)
    assert result['operation_id']==body['operation_id'],result
   except oracledb.DatabaseError as error:
    assert denial and denial in str(error),(denial,str(error))
   raise RollbackTrial()
 except RollbackTrial:pass

def assign(g,x,identity,ware):
 now=datetime.now(timezone.utc)
 access(g,x,'ASSIGN',dict(assignment_id=identity,username=x['actor'],role_id=x['extra_role'],scope_kind='WAREHOUSE',scope_id=str(ware),
  valid_from=(now-timedelta(minutes=5)).isoformat(),valid_until=(now+timedelta(hours=1)).isoformat(),expected_version=0,reason='Current scope and compensated exact-replay proof; no new stock command'))

def api_positive(g,x,password,checks):
 base='/api/picking/waves/'+str(x['wave']);receipt_url=base+'/launch-receipts/'+x['launch']
 with httpx.Client(base_url='http://127.0.0.1:8088',auth=(x['actor'],password),timeout=30)as c:
  value=c.get(receipt_url);assert value.status_code==200,value.text[:500]
  data=value.json();assert data['state']=='APPLIED'and data['wave_status']=='CANCELLED'and data['continuation_state']=='COMPLETE',data
  assert len(data['continuation_steps'])==7 and all(s['state']=='DONE'for s in data['continuation_steps'])
  r=c.post(base+'/launch',json={'operation_id':x['launch'],'updated_by':'admin'});assert r.status_code==200,r.text[:500]
  assert r.json()['status']=='CANCELLED'and r.json()['wave_status']=='CANCELLED'and r.json()['launch_outcome']=='APPLIED',r.text
  assert g.fetch_all('select ACTOR from RRL_STOCK_OPERATION where OPERATION_ID=:op',{'op':x['launch']})[0]['actor']==x['actor']
  absent=c.post(base+'/launch',json={});assert absent.status_code==422,absent.text[:500]
  for action in('cancel','calculate'):
   r=c.post(base+'/'+action,json={'operation_id':x['launch']});assert r.status_code==403,(action,r.text[:500])
  x['foreign_operation']='WAVE.HTTP.FOREIGN:'+uuid4().hex
  r=c.post('/api/picking/waves/398/launch',json={'operation_id':x['foreign_operation']});assert r.status_code==403,r.text[:500]
  assert not r.json()['detail']['outcome_confirmed']
  assert g.fetch_all('select count(*) N from RRL_STOCK_OPERATION where OPERATION_ID=:op',{'op':x['foreign_operation']})[0]['n']==0
 checks.extend(['actual_http_current_scoped_receipt_APPLIED_separate_CANCELLED_wave_COMPLETE_steps',
  'actual_http_exact_cancelled_replay_200_no_false_LAUNCHED_and_authenticated_actor_binding',
  'actual_http_missing_operation422_foreignWARE403_no_operation_other_actions_remain403'])

def main():
 data=json.loads((ROOT/'reports/retailcase/2026-10-15/resource-timeline/wave-continuation-native.json').read_text(encoding='utf8'));x=data['context'];checks=[];g=OracleGateway()
 before=g.fetch_all("select CELL,REMAIN,HARD_RESERVED_BASE,STOCK_VERSION from RRL_REMAINS where UID_POLETA='REUSE.RETURN:e6c16d0bbd'order by CELL")
 x['extra_role']=x['prefix']+'xr';own=x['prefix']+'xa';wrong=x['prefix']+'xw'
 prior=g.fetch_all('select DELETED,USER_GROUP,WARE_ID,PASS from RUSERS where ID=:actor',{'actor':x['actor']})[0]
 assert prior['deleted']==1 and prior['user_group']=='NONE'and prior['ware_id']is None
 try:
  with stock_configuration_transaction(g,'Temporarily restore only owned retired QA identity','admin','warehouse_settings_edit')as c:
   c.execute('update RUSERS set DELETED=0 where ID=:actor',actor=x['actor'])
  access(g,x,'ROLE_SAVE',dict(role_id=x['extra_role'],title='Current durable wave replay QA',permissions=['pick_wave_launch'],active=True,expected_version=0));assign(g,x,own,13583852)
  source=json.loads(x['source_body']);launch=dict(contract_version=2,operation_id=x['launch'],command_type='WAVE_LAUNCH',actor=x['actor'],lines=[],units=[],source={'wave_id':x['wave']},metadata={})
  trial(g,source);trial(g,launch)
  checks.append('native_exact_source_and_launch_replay_after_compensation_returns_original_receipts_without_effect')
  changed=json.loads(x['source_body']);changed['metadata']['allow_unissued_source_rebind']=False
  trial(g,changed,'WAVE_SOURCE_FROZEN_IDENTITY_CONFLICT')
  checks.append('native_changed_frozen_source_same_key_denied')
  for action in('update','delete'):
   try:
    with g.transaction('Append-only source intents reject direct metadata mutation')as c:
     sql="update RRL_WAVE_CONTINUE_SOURCE set CANONICAL_REQUEST=CANONICAL_REQUEST where SOURCE_OPERATION_ID=:op"if action=='update'else'delete from RRL_WAVE_CONTINUE_SOURCE where SOURCE_OPERATION_ID=:op'
     try:c.execute(sql,op=x['source_operation'])
     except oracledb.DatabaseError as error:assert'WAVE_SOURCE_INTENTS_APPEND_ONLY'in str(error),str(error)
     else:raise AssertionError(action+' unexpectedly allowed')
     raise RollbackTrial()
   except RollbackTrial:pass
  checks.append('native_frozen_source_UPDATE_DELETE_append_only_denied')
  api_positive(g,x,prior['pass'],checks)
  access(g,x,'REVOKE',dict(assignment_id=own,expected_version=1,reason='Verify replay current actual warehouse scope, not cached launch author'))
  assign(g,x,wrong,1)
  trial(g,source,'WAVE_CONTINUATION_CURRENT_WARE_REQUIRED');trial(g,launch,'WAVE_LAUNCH_SCOPE_REQUIRED')
  with httpx.Client(base_url='http://127.0.0.1:8088',auth=(x['actor'],prior['pass']),timeout=30)as c:
   base='/api/picking/waves/'+str(x['wave'])
   r=c.post(base+'/launch',json={'operation_id':x['launch']});assert r.status_code==403,r.text[:500]
   assert c.get(base+'/launch-receipts/'+x['launch']).json()['state']=='NOT_VISIBLE'
  checks.append('native_and_actualHTTP_wrong_WARE_after_revoke_denies_exact_replay_and_receipt')
 finally:
  with g.transaction('Remove only extra QA grants; retain native audit and original history')as c:
   for identity in(own,wrong):c.execute('delete from RRL_ACCESS_ASSIGNMENT where ASSIGNMENT_ID=:id',id=identity)
   c.execute('delete from RRL_ACCESS_ROLE_RIGHT where ROLE_ID=:id',id=x['extra_role'])
   c.execute('delete from RRL_ACCESS_ROLE where ROLE_ID=:id',id=x['extra_role'])
  with stock_configuration_transaction(g,'Restore exact retired QA identity','admin','warehouse_settings_edit')as c:
   c.execute('update RUSERS set DELETED=:deleted where ID=:actor',deleted=prior['deleted'],actor=x['actor'])
 after=g.fetch_all("select CELL,REMAIN,HARD_RESERVED_BASE,STOCK_VERSION from RRL_REMAINS where UID_POLETA='REUSE.RETURN:e6c16d0bbd'order by CELL");assert after==before,(before,after)
 final=read_launch_receipt(g,x['wave'],x['launch'],'admin');assert final['state']=='APPLIED'and final['wave_status']=='CANCELLED'and final['continuation_state']=='COMPLETE',final
 checks.append('final_admin_receipt_CANCELLED_distinct_original_launch_APPLIED_and_P_H_version_unchanged')
 (ROOT/'reports/retailcase/2026-10-15/resource-timeline/wave-continuation-replay.json').write_text(json.dumps(dict(status='PASS',checks=checks,final_receipt=final,stock_before=before,stock_after=after),indent=2,default=str),encoding='utf8')
 print(json.dumps(dict(status='PASS',checks=checks)))
if __name__=='__main__':main()
