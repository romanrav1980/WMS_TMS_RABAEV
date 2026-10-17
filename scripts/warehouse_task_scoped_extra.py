"""Additional scoped task guards; every stock call is rollback-only."""
import json
from copy import deepcopy
import oracledb
from app.modules.platform.public import read_oracle_json,stock_configuration_transaction
from warehouse_task_scoped_complete_smoke import access,grant,scalar,refusal,post,RollbackTrial,OLD_REPLAY

def rollback_refusal(g,body,text):
 try:
  with g.transaction('Scoped task negative native rollback')as c:
   refusal(c,body,text);raise RollbackTrial()
 except RollbackTrial:pass

def command_body(g,ctx):
 row=g.fetch_all('select FROM_CELL from RRL_WAREHOUSE_TASK where TASK_ID=:task',{'task':ctx['task']})[0]
 signature=g.fetch_all('select RRL_WAREHOUSE_TASK_ACCESS.task_signature(:task) SIGNATURE from dual',{'task':ctx['task']})[0]['signature']
 return dict(contract_version=2,operation_id='TASK.SCOPED.EXTRA:'+ctx['tag'],command_type='TASK_COMPLETE',actor=ctx['actor'],
  source=dict(type='WAREHOUSE_TASK',task_id=ctx['task']),lines=[],units=[],metadata=dict(expected_task_signature=signature,fact_qty=str(ctx['remain']),
  scanned_pallet=ctx['source'],scanned_from_cell=row['from_cell'],scanned_to_cell=ctx['cell'],resource_id=ctx['resource'],resource_session_id=ctx['session'],equipment_id=ctx['equipment']))

def extra_command_guards(g,ctx,checks):
 body=command_body(g,ctx)
 missing=deepcopy(body);missing['metadata'].pop('expected_task_signature');rollback_refusal(g,missing,'TASK_EXPECTED_SIGNATURE_REQUIRED')
 wrong=deepcopy(body);wrong['metadata']['scanned_to_cell']='WRONG.PHYSICAL.CELL';rollback_refusal(g,wrong,'TASK_SCAN_CONFLICT')
 checks.extend(['missing_signature_rejected','physical_wrong_target_scan_rejected'])
 hu=g.fetch_all("select TASK_ID from RRL_WAREHOUSE_TASK where HU_CONTENT_VERSION is not null order by TASK_ID desc fetch first 1 rows only")[0]['task_id']
 hu_body={**body,'command_type':'HU_TASK_COMPLETE','source':{'task_id':hu}}
 rollback_refusal(g,hu_body,'TASK_USER_WAREHOUSE_FORBIDDEN')
 carrier=g.fetch_all("select CASE_TASK_ID from RRL_ST_DEFER_WAIT_PLAN where CASE_TASK_ID is not null order by TASK_ID desc fetch first 1 rows only")[0]['case_task_id']
 case_body={**body,'command_type':'CASE_CARRIER_MOVE','source':{'case_task_id':carrier}}
 rollback_refusal(g,case_body,'FORBIDDEN')
 checks.extend(['native_warehouse_execute_does_not_enable_hu','native_warehouse_execute_does_not_enable_case_carrier'])
 try:
  with g.transaction('Scoped task closure change after prepare rollback')as c:
   out=c.var(oracledb.DB_TYPE_CLOB)
   try:
    c.callproc('RRL_STOCK_POSTING_API.prepare_command',[json.dumps(body,sort_keys=True,separators=(',',':')),body['actor'],out])
    assert out.getvalue()is None
    c.execute("update RRL_WAREHOUSE_TASK set STATUS='IN_PROGRESS'where TASK_ID=:task",task=ctx['task'])
    try:c.callproc('RRL_STOCK_POSTING_API.execute_prepared',[out])
    except oracledb.DatabaseError as e:assert 'CLOSURE_CHANGED'in str(e),str(e)
    else:raise AssertionError('Closure change accepted')
   finally:c.callproc('RRL_STOCK_POSTING_API.reset_connection')
   raise RollbackTrial()
 except RollbackTrial:pass
 checks.append('closure_changed_after_prepare_cannot_execute')

def raw_replay(c,source,actor):
 out=c.var(oracledb.DB_TYPE_CLOB)
 try:
  c.callproc('RRL_STOCK_POSTING_API.prepare_command',[source,actor,out])
  assert out.getvalue()is not None,'Committed replay attempted fresh execute'
  return read_oracle_json(out.getvalue())
 finally:c.callproc('RRL_STOCK_POSTING_API.reset_connection')

def original_replay(g,ctx,checks):
 row=g.fetch_all("""select dbms_lob.substr(o.CANONICAL_REQUEST,4000,1) CANONICAL_REQUEST,dbms_lob.getlength(o.CANONICAL_REQUEST) REQUEST_LENGTH,o.RESULT_JSON,o.ACTOR,u.USER_GROUP,u.DELETED,u.WARE_ID
  from RRL_STOCK_OPERATION o join RUSERS u on u.ID=o.ACTOR where o.OPERATION_ID=:op and o.STATE='APPLIED'""",{'op':OLD_REPLAY})[0]
 assert row['deleted']==1,'Historical fixture actor is active; do not modify'
 actor=row['actor'];ctx.update(old_actor=actor,old_group=row['user_group'],old_deleted=row['deleted'],old_ware=row['ware_id'])
 assert g.fetch_all("select count(*) N from RRL_RESOURCE_SESSION where OPERATOR_USER_ID=:actor and STATUS in('ACTIVE','PAUSED')",{'actor':actor})[0]['n']==0
 source=row['canonical_request'];assert isinstance(source,str)and len(source)==row['request_length'];expected=row['result_json']if isinstance(row['result_json'],dict)else json.loads(row['result_json'])
 with g.transaction('Temporarily reactivate isolated historical QA actor as native-only')as c:
  c.execute("update RUSERS set USER_GROUP='NONE',WARE_ID=null,DELETED=0 where ID=:actor",actor=actor)
 assignment=grant(g,ctx,actor,'replay')
 try:
  with g.transaction('Exact committed original native-only replay rollback')as c:
   assert scalar(c,"select RRL_HAS_WRIGHT(:actor,'warehouse_task_execute')from dual",actor=actor)==0
   assert raw_replay(c,source,actor)==expected
   raise RollbackTrial()
 except RollbackTrial:pass
 checks.append('original_committed_canonical_receipt_replayed_by_current_native_role')
 changed=json.loads(source);changed['metadata']['fact_qty']='0'
 rollback_refusal(g,changed,'OPERATION_CONFLICT')
 checks.append('original_operation_changed_body_conflicts')
 access(g,ctx,'REVOKE',dict(assignment_id=assignment,expected_version=1,reason='Verify current access on committed completion replay'))
 try:
  with g.transaction('Revoked receiver cannot obtain old task receipt')as c:
   try:raw_replay(c,source,actor)
   except oracledb.DatabaseError as e:assert 'TASK_USER_WAREHOUSE_FORBIDDEN'in str(e),str(e)
   else:raise AssertionError('Revoked native actor replayed')
   raise RollbackTrial()
 except RollbackTrial:pass
 checks.append('current_revoke_denies_original_committed_replay')

def mixed_scope(g,ctx,checks):
 # Actor's warehouse role is deliberately not SELF: permissionA + viewB is insufficient.
 for role,assignment in list(ctx['grants']):
  if assignment.endswith('other'):
   access(g,ctx,'REVOKE',dict(assignment_id=assignment,expected_version=1,reason='Replace SELF fixture by explicit warehouse test'))
 grant(g,ctx,ctx['other'],'warea',scope='WAREHOUSE',scope_id=str(ctx['ware_id']))
 grant(g,ctx,ctx['other'],'viewb',permission='warehouse_task_view',scope='WAREHOUSE',scope_id='1')
 def result():
  try:
   with stock_configuration_transaction(g,'Mixed warehouse task guard-only rollback','admin','warehouse_settings_edit')as c:
    c.execute("update RRL_WAREHOUSE_TASK set ASSIGNED_TO=:actor,TO_CELL='QS55edaf9dce',TO_WARE_ID=1 where TASK_ID=:task",actor=ctx['other'],task=ctx['task'])
    value=scalar(c,'select RRL_WAREHOUSE_TASK_ACCESS.scoped_stock_executor(:task,:actor)from dual',task=ctx['task'],actor=ctx['other'])
    raise RollbackTrial(value)
  except RollbackTrial as e:return e.args[0]
 assert ctx['ware_id']!=1
 assert result()==0
 assignment=grant(g,ctx,ctx['other'],'wareb',scope='WAREHOUSE',scope_id='1')
 assert result()==1
 access(g,ctx,'REVOKE',dict(assignment_id=assignment,expected_version=1,reason='Verify destination warehouse execution revoke'))
 assert result()==0
 checks.append('both_actual_warehouses_require_execute_and_destination_revoke')
