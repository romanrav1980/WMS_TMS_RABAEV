"""Real native metadata proof; command effects rolled back, isolated fixture retained."""
import json,sys,hashlib
from pathlib import Path
from uuid import uuid4
import oracledb
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT/'scripts'),str(ROOT/'api/wms_api_server')]
from warehouse_task_assignment_fixture import RUNTIME,REPORT,snapshot
from warehouse_task_scoped_complete_smoke import RollbackTrial,scalar,access,grant
from app.oracle_gateway import OracleGateway
from app.modules.resources.contracts_task_resource import TaskResourceAck,TaskResourceCommand
from app.modules.resources.infrastructure.task_resource_commands import canonical


def source_verify(g):
 base=ROOT/'db/migrations/2026-10-15_warehouse_task_scoped_assignment';cp=json.loads((base/'checkpoint.json').read_text())
 forward=json.loads((ROOT/'db/migrations/2026-10-15_warehouse_task_session_warehouse/checkpoint.json').read_text())
 for x in cp['after_sources']:
  raw=''.join(r['text']for r in g.fetch_all('select TEXT from USER_SOURCE where NAME=:n and TYPE=:k order by LINE',{'n':x['name'],'k':x['type']})).replace('\r','')
  expected=forward['after_sha256']if x['name']=='RRL_WTASK_ASSIGN_API'and x['type']=='PACKAGE BODY'else x['sha256']
  assert hashlib.sha256(raw.encode()).hexdigest()==expected,(x['name'],x['type'])
 assert g.fetch_all("select count(*)N from USER_OBJECTS where STATUS='INVALID'")[0]['n']==0
 assert not g.fetch_all("select NAME,TEXT from USER_ERRORS where NAME not like 'BIN$%'")
 return 16


def state(g,ctx):
 return {'stock':snapshot(g),'tasks':g.fetch_all('select t.TASK_ID,t.STATUS,t.ASSIGNED_TO,t.RESOURCE_ID,t.RESOURCE_SESSION_ID,t.EQUIPMENT_ID,t.STARTED_AT,t.STARTED_AT_INSTANT,t.STARTED_SHIFT_TIME_ZONE,t.FACT_QTY,v.ASSIGNMENT_VERSION from RRL_WAREHOUSE_TASK t join RRL_WTASK_ASSIGN_VERSION v on v.TASK_ID=t.TASK_ID where t.TASK_ID in(:a,:b)order by t.TASK_ID',{'a':ctx['task'],'b':ctx['mixed_task']}),'session':g.fetch_all('select STATUS,CURRENT_TASK_ID from RRL_RESOURCE_SESSION where SESSION_ID=:id',{'id':ctx['session']}),'events':g.fetch_all('select count(*)N from RRL_RESOURCE_FACT_EVENT where TASK_ID in(:a,:b)',{'a':ctx['task'],'b':ctx['mixed_task']})[0]['n'],'receipts':g.fetch_all('select count(*)N from RRL_WTASK_RESOURCE_COMMAND where TASK_ID in(:a,:b)',{'a':ctx['task'],'b':ctx['mixed_task']})[0]['n']}


def intent(g,ctx,action,task=None):
 task=task or ctx['task'];row=g.fetch_all('select RRL_WAREHOUSE_TASK_ACCESS.task_signature(:id)SIGNATURE,nvl((select ASSIGNMENT_VERSION from RRL_WTASK_ASSIGN_VERSION where TASK_ID=:id),0)VERSION from dual',{'id':task})[0]
 return dict(operation_id='TASK.METADATA:'+uuid4().hex,action=action,target=ctx['actor'],expected_assignment_version=int(row['version']),expected_task_signature=row['signature'],resource_id=ctx['resource'],resource_session_id=ctx['session'],equipment_id=ctx['equipment'])


def post(c,task,body,actor):
 out=c.var(oracledb.DB_TYPE_CLOB);wire=canonical(TaskResourceCommand.model_validate(body));c.callproc('RRL_WTASK_ASSIGN_API.execute_command',[task,wire,actor,out]);raw=out.getvalue();result=json.loads(raw.read()if hasattr(raw,'read')else raw)
 ack=TaskResourceAck.model_validate(result);assert ack.request_sha256==hashlib.sha256(wire.encode()).hexdigest().upper();return result


def trial(g,ctx,checks,name,callback):
 before=state(g,ctx)
 try:
  with g.transaction('TASK native rollback '+name)as c:callback(c);raise RollbackTrial()
 except RollbackTrial:pass
 assert state(g,ctx)==before,name;checks.append(name)


def rejected(c,task,body,actor,code):
 value=post(c,task,body,actor);assert value['outcome']=='REJECTED'and value['error_code']==code and not value['changed'],value
 assert scalar(c,'select count(*)from RRL_WTASK_RESOURCE_COMMAND where OPERATION_ID=:op',op=body['operation_id'])==1


def denied(c,task,body,actor,text):
 try:post(c,task,body,actor)
 except oracledb.DatabaseError as e:assert text in str(e),(text,str(e))
 else:raise AssertionError('Expected native refusal '+text)
 assert scalar(c,'select count(*)from RRL_WTASK_RESOURCE_COMMAND where OPERATION_ID=:op',op=body['operation_id'])==0


def identity_guards(g,ctx,checks):
 for sql,expected in [('delete from RRL_WAREHOUSE_TASK where TASK_ID=:id','WTASK_IDENTITY_HISTORY_NO_DELETE'),('update RRL_WAREHOUSE_TASK set TASK_ID=TASK_ID+1000000 where TASK_ID=:id','WTASK_IDENTITY_IMMUTABLE')]:
  def check(c,sql=sql,expected=expected):
   try:c.execute(sql,id=631)
   except oracledb.DatabaseError as e:assert expected in str(e),str(e)
   else:raise AssertionError('Unseeded historical identity was mutable')
  trial(g,ctx,checks,'unseeded_parent_'+expected,check)
 def direct(c):
  try:c.execute('update RRL_WTASK_ASSIGN_VERSION set ASSIGNMENT_VERSION=ASSIGNMENT_VERSION+1 where TASK_ID=:id',id=ctx['task'])
  except oracledb.DatabaseError as e:assert 'WTASK_VERSION_SERVER_DERIVED'in str(e),str(e)
  else:raise AssertionError('Direct version assignment succeeded')
 trial(g,ctx,checks,'direct_sidecar_write_denied',direct)
 def monotonic(c):
  before=scalar(c,'select ASSIGNMENT_VERSION from RRL_WTASK_ASSIGN_VERSION where TASK_ID=:id',id=ctx['task'])
  c.execute("update RRL_WAREHOUSE_TASK set TASK_ID=TASK_ID where TASK_ID=:id",id=ctx['task']);assert scalar(c,'select ASSIGNMENT_VERSION from RRL_WTASK_ASSIGN_VERSION where TASK_ID=:id',id=ctx['task'])==before
  c.execute("update RRL_WAREHOUSE_TASK set STATUS='ASSIGNED'where TASK_ID=:id",id=ctx['task']);c.execute("update RRL_WAREHOUSE_TASK set STATUS='PLANNED'where TASK_ID=:id",id=ctx['task'])
  assert scalar(c,'select ASSIGNMENT_VERSION from RRL_WTASK_ASSIGN_VERSION where TASK_ID=:id',id=ctx['task'])==before+2
 trial(g,ctx,checks,'same_id_noop_and_legacy_ABA_version_increments',monotonic)


def run(g,ctx,action):
 checks=[];assert source_verify(g)==16;checks.append('exact16_sources_errors0_invalid0')
 body=intent(g,ctx,action);task=ctx['task']
 def positive(c):
  assert scalar(c,"select RRL_HAS_WRIGHT(:actor,'warehouse_task_execute')from dual",actor=ctx['actor'])==0
  result=post(c,task,body,ctx['actor']);assert result['outcome']=='APPLIED'and result['changed']and result['assignment_version']==body['expected_assignment_version']+1,result
  assert result['status']==('ASSIGNED'if action=='ASSIGN'else'IN_PROGRESS')
  assert result['resource_session_id']==ctx['session']and result['assigned_to']==ctx['actor']
  if action=='START':assert result['started_at_instant']and scalar(c,'select CURRENT_TASK_ID from RRL_RESOURCE_SESSION where SESSION_ID=:id',id=ctx['session'])==task
 trial(g,ctx,checks,'native_only_'+action+'_effect_receipt_event_version_caller_rollback',positive)
 for delta,reason in [({'expected_assignment_version':body['expected_assignment_version']+1},'WTASK_EXPECTED_VERSION_CHANGED'),({'expected_task_signature':'0'*64},'WTASK_EXPECTED_SIGNATURE_CHANGED'),({'equipment_id':ctx['equipment']+999999},'TASK_SESSION_RESOURCE_IDENTITY_CONFLICT')]:
  changed={**body,**delta,'operation_id':'TASK.NEG:'+uuid4().hex}
  trial(g,ctx,checks,reason,lambda c,b=changed,r=reason:rejected(c,task,b,ctx['actor'],r))
 foreign={**body,'target':ctx['other'],'operation_id':'TASK.FOREIGN:'+uuid4().hex}
 trial(g,ctx,checks,'other_target_without_dispatch_denied',lambda c:denied(c,task,foreign,ctx['actor'],'WTASK_CURRENT_SCOPED_AUTHORITY_REQUIRED'))
 if action=='ASSIGN':
  identity_guards(g,ctx,checks)
  mixed=intent(g,ctx,'ASSIGN',ctx['mixed_task']);mixed['target']=ctx['other']
  trial(g,ctx,checks,'executeA_viewB_not_executeBoth',lambda c:denied(c,ctx['mixed_task'],mixed,ctx['other'],'WTASK_CURRENT_SCOPED_AUTHORITY_REQUIRED'))
  mixed['target']=ctx['actor'];mixed['operation_id']='TASK.MIXED:'+uuid4().hex
  trial(g,ctx,checks,'both_rights_cannot_start_unsupported_crosswarehouse_workflow',lambda c:rejected(c,ctx['mixed_task'],mixed,'admin','WTASK_PHYSICAL_WAREHOUSE_REQUIRED'))
  access(g,ctx,'REVOKE',dict(assignment_id=ctx['assign_grant'],expected_version=1,reason='Prove SELF execute cannot claim an unassigned task'))
  try:trial(g,ctx,checks,'SELF_alone_cannot_claim_unassigned',lambda c:denied(c,task,body,ctx['actor'],'WTASK_CURRENT_SCOPED_AUTHORITY_REQUIRED'))
  finally:
   ctx['assign_grant']=grant(g,ctx,ctx['actor'],'restore'+uuid4().hex[:6],'warehouse_task_assign','WAREHOUSE',str(ctx['ware_id']))
   RUNTIME.write_text(json.dumps(ctx,default=str),encoding='utf-8')

 result=dict(status='PASS',checks=checks,command_effects='CALLER_ROLLBACK_ONLY',goods_commit=False,source_after=snapshot(g),case1136_1138_mutated=False)
 (REPORT/('native-'+action.lower()+'.json')).write_text(json.dumps(result,indent=2,default=str),encoding='utf-8');print(json.dumps({'status':'PASS','action':action,'checks':len(checks)}))


if __name__=='__main__':
 from datetime import datetime,timedelta,timezone
 g=OracleGateway();ctx=json.loads(RUNTIME.read_text(encoding='utf-8'));run(g,ctx,sys.argv[1])
