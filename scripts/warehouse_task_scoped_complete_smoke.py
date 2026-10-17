"""AK06-A real Oracle: temporary metadata, caller-owned rollback, no stock commit."""
import json,sys,secrets,os,hashlib
from copy import deepcopy
from datetime import datetime,timedelta,timezone
from pathlib import Path
from uuid import uuid4
import oracledb
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'scripts'),str(ROOT/'api/wms_api_server')]
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment()
from app.oracle_gateway import OracleGateway
from app.modules.platform.public import AccessMetadataService,read_oracle_json,stock_configuration_transaction
from app.modules.platform.api.metadata_inputs import Command,normalize

SOURCE='FULL.QA:d9a5c53b54'
OLD_REPLAY='NI032:PART:55edaf9dce'

class RollbackTrial(Exception):pass

def scalar(c,sql,**bind):
 c.execute(sql,bind);return c.fetchone()[0]

def post(c,body,prepare_only=False):
 out=c.var(oracledb.DB_TYPE_CLOB)
 try:
  c.callproc('RRL_STOCK_POSTING_API.prepare_command',[json.dumps(body,sort_keys=True,separators=(',',':'),ensure_ascii=True),body['actor'],out])
  if out.getvalue()is None and not prepare_only:c.callproc('RRL_STOCK_POSTING_API.execute_prepared',[out])
  return read_oracle_json(out.getvalue())if out.getvalue()is not None else None
 finally:c.callproc('RRL_STOCK_POSTING_API.reset_connection')

def refusal(c,body,text):
 try:post(c,body)
 except oracledb.DatabaseError as error:assert text in str(error),(text,str(error))
 else:raise AssertionError('Expected refusal '+text)

def access(g,ctx,kind,payload):
 op=ctx['prefix']+':'+uuid4().hex
 return AccessMetadataService(g).command('admin',normalize(Command(operation_id=op,command_type=kind,payload=payload),'ACCESS'))

def grant(g,ctx,actor,suffix,permission='warehouse_task_execute',scope='SELF',scope_id=None):
 role=ctx['prefix']+'r'+suffix;assignment=ctx['prefix']+'a'+suffix
 access(g,ctx,'ROLE_SAVE',dict(role_id=role,title='Scoped task rollback fixture',permissions=[permission],active=True,expected_version=0))
 now=datetime.now(timezone.utc)
 ctx['grants'].append((role,assignment))
 access(g,ctx,'ASSIGN',dict(assignment_id=assignment,username=actor,role_id=role,scope_kind=scope,scope_id=scope_id,
  valid_from=(now-timedelta(minutes=5)).isoformat(),valid_until=(now+timedelta(hours=1)).isoformat(),expected_version=0,reason='Isolated AK06 task completion fixture; no stock commit'))
 return assignment

def setup(g,ctx):
 with stock_configuration_transaction(g,'AK06 temporary metadata fixture','admin','warehouse_settings_edit')as c:
  row=g.fetch_all("select r.CELL,r.REMAIN,r.HARD_RESERVED_BASE,r.BASE_UOM,c.WARE_ID,p.ARTICUL from RRL_REMAINS r join RRL_PALLETS p on p.UID_PALLET=r.UID_POLETA join RRL_CELLS c on c.CELL=r.CELL where r.UID_POLETA=:lot_id and r.REMAIN>0",{'lot_id':SOURCE})
  assert len(row)==1 and row[0]['hard_reserved_base']==20,row
  ctx.update(row[0]);ctx['remain']=12;ctx['source_cell']=row[0]['cell'];ctx['source']=SOURCE;ctx['actor']='wt'+ctx['tag'];ctx['other']='wo'+ctx['tag'];ctx['cell']='WK'+ctx['tag']
  ctx['password']=secrets.token_urlsafe(24);ctx['other_password']=secrets.token_urlsafe(24)
  for actor in(ctx['actor'],ctx['other']):
   c.execute("insert into RUSERS(ID,NAME,PASS,USER_GROUP,WARE_ID,DELETED,PRAVO_ADMIN_LOGIN)values(:id,'AK06 rollback fixture',:pw,'NONE',null,0,0)",id=actor,pw=ctx['password']if actor==ctx['actor']else ctx['other_password'])
  for name,seq in(('task','RRL_WAREHOUSE_TASK_SQ'),('equipment','RRL_RESOURCE_EQUIPMENT_SQ'),('resource','RRL_RESOURCE_SQ'),('shift','RRL_RESOURCE_SHIFT_SQ'),('session','RRL_RESOURCE_SESSION_SQ')):
   ctx[name]=int(scalar(c,'select '+seq+'.nextval from dual'))
  c.execute("insert into RRL_CELLS(CELL,WARE_ID,X,Y,Z,OTBOR,IS_SYSTEM,LIMIT_WEIGHT,LIMIT_HEIGHT,BLOCKED_FOR_ACCEPT,BLOCKED_FOR_REMAINS,BLOCKED_FOR_POPOLNENIE)values(:cell,:ware,0,0,0,0,0,0,0,0,0,0)",cell=ctx['cell'],ware=ctx['ware_id'])
  c.execute("insert into RRL_STOCK_POLICY_GUARD(POLICY_KEY,LOCK_ID)select RRL_STOCK_LOCK_API.resource_key('CELL',:cell),nvl(max(LOCK_ID),900000000)+1 from RRL_STOCK_POLICY_GUARD",cell=ctx['cell'])
  c.execute("insert into RRL_RESOURCE_EQUIPMENT(EQUIPMENT_ID,EQUIPMENT_CODE,EQUIPMENT_TYPE,WARE_ID,SERVICE_STATUS,ACTIVE,CREATED_BY)values(:id,:code,'REACHTRUCK',:ware,'ACTIVE',1,'admin')",id=ctx['equipment'],code=ctx['prefix'],ware=ctx['ware_id'])
  c.execute("""insert into RRL_RESOURCE(RESOURCE_ID,RESOURCE_CODE,RESOURCE_NAME,RESOURCE_CLASS,RESOURCE_TYPE,EQUIPMENT_ID,USER_ID,WARE_ID,STATUS,ACTIVE,CREATED_BY)
   select :id,:code,'AK06 rollback',RESOURCE_CLASS,'REACHTRUCK',:equipment,:actor,:ware,'AVAILABLE',1,'admin'from RRL_RESOURCE_TYPE where RESOURCE_TYPE='REACHTRUCK'""",
   id=ctx['resource'],code=ctx['prefix'],equipment=ctx['equipment'],actor=ctx['actor'],ware=ctx['ware_id'])
  c.execute("insert into RRL_RESOURCE_TASK_QUAL(RESOURCE_ID,TASK_TYPE,VALID_FROM,ACTIVE,UPDATED_BY)values(:id,'PICKING_MOVE',localtimestamp-interval '1'day,1,'admin')",id=ctx['resource'])
  c.execute("insert into RRL_RESOURCE_SHIFT(SHIFT_ID,SHIFT_CODE,SHIFT_DATE,WARE_ID,START_AT,FINISH_AT,STATUS,CREATED_BY)values(:id,:code,trunc(sysdate),:ware,localtimestamp-interval '1'hour,localtimestamp+interval '1'hour,'OPEN','admin')",id=ctx['shift'],code=ctx['prefix'],ware=ctx['ware_id'])
  c.execute("insert into RRL_RESOURCE_SESSION(SESSION_ID,SHIFT_ID,RESOURCE_ID,EQUIPMENT_ID,OPERATOR_USER_ID,STATUS,CREATED_BY)values(:id,:shift_id,:machine_id,:equipment,:actor,'ACTIVE','admin')",id=ctx['session'],shift_id=ctx['shift'],machine_id=ctx['resource'],equipment=ctx['equipment'],actor=ctx['actor'])
  c.execute("""insert into RRL_WAREHOUSE_TASK(TASK_ID,TASK_TYPE,TASK_SOURCE,SOURCE_TASK_ID,SOURCE_DOC_TYPE,SOURCE_DOC_ID,UID_PALLET,FROM_CELL,TO_CELL,FROM_WARE_ID,TO_WARE_ID,QTY,UNIT_CODE,QTY_MODE,STATUS,CREATED_BY,ASSIGNED_TO,RESOURCE_ID,RESOURCE_SESSION_ID,EQUIPMENT_ID)
   values(:id,'PICKING_MOVE','WAVE',1810,'PICK_WAVE',395,:lot_id,:src,:dst,:ware,:ware,:qty,:uom,'BOX','ASSIGNED','admin',:actor,:machine_id,:session_id,:equipment)""",
   id=ctx['task'],lot_id=SOURCE,src=ctx['source_cell'],dst=ctx['cell'],ware=ctx['ware_id'],qty=ctx['remain'],uom=ctx['base_uom'],actor=ctx['actor'],machine_id=ctx['resource'],session_id=ctx['session'],equipment=ctx['equipment'])
 ctx['assignment']=grant(g,ctx,ctx['actor'],'own')
 grant(g,ctx,ctx['actor'],'view',permission='warehouse_task_view')
 grant(g,ctx,ctx['other'],'other')

def snapshot(g,ctx):
 return g.fetch_all("select CELL,REMAIN,HARD_RESERVED_BASE,STOCK_VERSION from RRL_REMAINS where UID_POLETA=:lot_id order by CELL",{'lot_id':SOURCE})

def ordinary_trial(g,ctx,checks):
 source_cell=g.fetch_all('select FROM_CELL from RRL_WAREHOUSE_TASK where TASK_ID=:id',{'id':ctx['task']})[0]['from_cell']
 signature=g.fetch_all('select RRL_WAREHOUSE_TASK_ACCESS.task_signature(:id) SIGNATURE from dual',{'id':ctx['task']})[0]['signature']
 ctx['operation']='TASK.SCOPED:'+uuid4().hex
 body=dict(contract_version=2,operation_id=ctx['operation'],command_type='TASK_COMPLETE',actor=ctx['actor'],source=dict(type='WAREHOUSE_TASK',task_id=ctx['task']),lines=[],units=[],
  metadata=dict(expected_task_signature=signature,fact_qty=str(ctx['remain']),scanned_pallet=SOURCE,scanned_from_cell=source_cell,scanned_to_cell=ctx['cell'],resource_id=ctx['resource'],resource_session_id=ctx['session'],equipment_id=ctx['equipment']))
 before=snapshot(g,ctx)
 domain_before=[g.fetch_all('select STATUS,FACT_QTY,DONE_AT,DONE_BY,TARGET_CELL_CODE from '+table+' where '+key+'=:id',{'id':value})for table,key,value in [('RRL_PICK_WAVE_TASK','PICK_WAVE_TASK_ID',1810),('RRL_PICK_TASK','PICK_TASK_ID',1903)]]
 for change,reason in (({'actor':ctx['other']},'TASK_USER_WAREHOUSE_FORBIDDEN'),):
  try:
   with g.transaction('Scoped task foreign actor refusal')as c:refusal(c,{**body,**change},reason);raise RollbackTrial()
  except RollbackTrial:pass
 checks.append('foreign_assigned_actor_denied')
 stale=deepcopy(body);stale['metadata']['expected_task_signature']='0'*64
 try:
  with g.transaction('Scoped task stale version refusal')as c:refusal(c,stale,'TASK_EXPECTED_SIGNATURE_CHANGED');raise RollbackTrial()
 except RollbackTrial:pass
 checks.append('stale_expected_task_signature_rejected')
 try:
  with g.transaction('Scoped assigned task physical completion rollback')as c:
   assert scalar(c,"select RRL_HAS_WRIGHT(:actor,'warehouse_task_execute')from dual",actor=ctx['actor'])==0
   result=post(c,body);assert result['status']=='DONE',result
   assert scalar(c,'select count(*)from RRL_STOCK_OPERATION where OPERATION_ID=:op and STATE=\'APPLIED\'',op=ctx['operation'])==1
   assert scalar(c,'select count(*)from RRL_EVENT_OUTBOX where IDEMPOTENCY_KEY=:key',key='STOCK:'+hashlib.sha256(ctx['operation'].encode()).hexdigest().upper())==1
   checks.append('native_only_assigned_actor_physical_completion')
   raise RollbackTrial()
 except RollbackTrial:pass
 assert snapshot(g,ctx)==before
 assert [g.fetch_all('select STATUS,FACT_QTY,DONE_AT,DONE_BY,TARGET_CELL_CODE from '+table+' where '+key+'=:id',{'id':value})for table,key,value in [('RRL_PICK_WAVE_TASK','PICK_WAVE_TASK_ID',1810),('RRL_PICK_TASK','PICK_TASK_ID',1903)]]==domain_before
 assert g.fetch_all('select count(*) N from RRL_EVENT_OUTBOX where IDEMPOTENCY_KEY=:key',{'key':'STOCK:'+hashlib.sha256(ctx['operation'].encode()).hexdigest().upper()})[0]['n']==0
 assert g.fetch_all('select count(*) N from RRL_PALLETS where CREATED_BY_STOCK_OP=:op',{'op':ctx['operation']})[0]['n']==0
 for table,key,value in(('RRL_STOCK_OPERATION','OPERATION_ID',ctx['operation']),('RRL_WAREHOUSE_TASK_STOCK_MOVE','TASK_ID',ctx['task']),('RRL_RESOURCE_FACT_EVENT','TASK_ID',ctx['task']),('RRL_WAREHOUSE_TASK_SYNC','TASK_ID',ctx['task']),('RRL_WAREHOUSE_TASK','PARENT_TASK_ID',ctx['task'])):
  assert g.fetch_all('select count(*) N from '+table+' where '+key+'=:id',{'id':value})[0]['n']==0,(table,value)
 checks.append('stock_operation_movement_event_sync_residual_rollback_verified')
 checks.append('domain_facts_outbox_and_new_partial_unit_rollback_verified')

def cleanup(g,ctx):
 if ctx.get('old_actor'):
  with g.transaction('Restore original historical QA identity')as c:
   c.execute('update RUSERS set USER_GROUP=:grp,DELETED=:deleted,WARE_ID=:ware where ID=:actor',grp=ctx['old_group'],deleted=ctx['old_deleted'],ware=ctx['old_ware'],actor=ctx['old_actor'])
 from warehouse_task_fixture_retirement import retire_metadata
 retire_metadata(g,ctx)

def main():
 g=OracleGateway();ctx=dict(tag=uuid4().hex[:9],grants=[]);ctx['prefix']='tsk'+ctx['tag'];checks=[]
 try:
  setup(g,ctx);ordinary_trial(g,ctx,checks)
  from warehouse_task_scoped_extra import extra_command_guards,original_replay,mixed_scope
  extra_command_guards(g,ctx,checks);mixed_scope(g,ctx,checks);original_replay(g,ctx,checks)
  if os.environ.get('RUN_TASK_SCOPED_HTTP')=='1':
   from warehouse_task_scoped_http import verify_http
   verify_http(g,ctx,checks)
 finally:cleanup(g,ctx)
 assert g.fetch_all('select STATUS from RRL_WAREHOUSE_TASK where TASK_ID=:id',{'id':ctx['task']})[0]['status']=='CANCELLED'
 assert g.fetch_all('select STATUS from RRL_RESOURCE_SESSION where SESSION_ID=:id',{'id':ctx['session']})[0]['status']=='CLOSED'
 assert g.fetch_all('select count(*)N from RUSERS where ID in(:a,:b)and nvl(DELETED,0)=0',{'a':ctx['actor'],'b':ctx['other']})[0]['n']==0
 assert g.fetch_all('select USER_GROUP,DELETED,WARE_ID from RUSERS where ID=:actor',{'actor':ctx['old_actor']})==[dict(user_group=ctx['old_group'],deleted=ctx['old_deleted'],ware_id=ctx['old_ware'])]
 checks.append('temporary_metadata_retired_history_retained_and_historical_identity_exactly_restored')
 result=dict(status='PASS',checks=checks,metadata_fixture_committed_temporarily=True,metadata_fixture_retired=True,metadata_history_retained=True,native_access_audit_retained=True,stock_execute='CALLER_ROLLBACK_ONLY',physical_hardware=False)
 (ROOT/'reports/retailcase/2026-10-15/resource-timeline/task-scoped-complete-native.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
 print(json.dumps(result))
if __name__=='__main__':main()
