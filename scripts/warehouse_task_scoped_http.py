"""Actual scoped API negatives enter native posting but never commit a stock effect."""
import httpx
from uuid import uuid4
from warehouse_task_scoped_extra import command_body
from warehouse_task_scoped_complete_smoke import snapshot

def verify_http(g,ctx,checks):
 url='/api/warehouse-tasks/'+str(ctx['task'])
 before=snapshot(g,ctx)
 with httpx.Client(base_url='http://127.0.0.1:8088',auth=(ctx['actor'],ctx['password']),timeout=30)as c:
  detail=c.get(url);assert detail.status_code==200,detail.text[:500]
  signature=detail.json()['task_signature'];assert len(signature)==64
  body=command_body(g,ctx)['metadata'];body['operation_id']='TASK.SCOPED.HTTP:'+uuid4().hex;body['expected_task_signature']=signature
  absent={**body};absent.pop('operation_id')
  r=c.post(url+'/complete',json=absent);assert r.status_code==422,r.text[:500]
  assert r.json()['detail']['code']=='TASK_OPERATION_ID_REQUIRED'
  absent={**body};absent.pop('expected_task_signature')
  r=c.post(url+'/complete',json=absent);assert r.status_code==422,r.text[:500]
  assert r.json()['detail']['code']=='TASK_EXPECTED_SIGNATURE_REQUIRED'
  wrong={**body,'scanned_to_cell':'WRONG.PHYSICAL.CELL'}
  r=c.post(url+'/complete',json=wrong);assert r.status_code==409,r.text[:500]
  assert r.json()['detail']['reason']=='TASK_SCAN_CONFLICT'and r.json()['detail']['operation_id']==body['operation_id']
  assert r.json()['detail']['outcome_confirmed']is True
  for action in('assign','start','cancel'):
   r=c.post(url+'/'+action,json=body);assert r.status_code==403,(action,r.text[:500])
  r=c.post(url+'/complete',json=body,auth=(ctx['other'],ctx['other_password']))
  assert r.status_code==403,r.text[:500]
  hu=g.fetch_all("select TASK_ID from RRL_WAREHOUSE_TASK where HU_CONTENT_VERSION is not null order by TASK_ID desc fetch first 1 rows only")[0]['task_id']
  r=c.post('/api/warehouse-tasks/'+str(hu)+'/complete',json=body)
  assert r.status_code==403,r.text[:500]
  for mode in('operation_id','expected_task_signature'):
   assert mode in c.get('/openapi.json').json()['components']['schemas']['WarehouseTaskStatusRequest']['properties']
 assert snapshot(g,ctx)==before
 assert g.fetch_all('select count(*) N from RRL_STOCK_OPERATION where OPERATION_ID=:op',{'op':body['operation_id']})[0]['n']==0
 checks.extend(['actual_http_native_identity_detail_signature','actual_http_missing_correlation_version_rejected',
  'actual_http_physical_scan_native_rejection_rollback','actual_http_assign_start_cancel_remain_separate',
  'actual_http_other_assignee_and_hu_denied'])
