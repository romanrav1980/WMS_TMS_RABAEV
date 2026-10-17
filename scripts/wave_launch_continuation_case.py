"""Explicitly authorized bounded DEV proof. No physical start/scan/move; preserve all history."""
import sys,json,os,secrets
from pathlib import Path
from uuid import uuid4
from datetime import datetime,timedelta,timezone
from concurrent.futures import ThreadPoolExecutor
import oracledb
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'scripts'),str(ROOT/'api/wms_api_server')]
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment()
from app.oracle_gateway import OracleGateway
from app.modules.inventory.public import StockCommand,StockPosting,StockPostingError
from app.modules.platform.public import stock_configuration_transaction
from app.modules.fulfillment.public import resume_wave_launch,read_launch_receipt
from app.modules.fulfillment.application.wave_launch_continuation import run_wave_launch
from app.modules.fulfillment.infrastructure.wave_continuation import WaveContinuation
from app.modules.fulfillment.infrastructure.wave_launch_adapter import launch_steps,post_frozen_sources
from app.services.picking_service import PickingService
from warehouse_task_scoped_complete_smoke import access,post,RollbackTrial,scalar

SOURCE='REUSE.RETURN:e6c16d0bbd';CELL='QIPcdbf4c0962';WARE=13583852;ARTICLE='REUSE.QA:cdbf4c0962'

def stock(g):
 return g.fetch_all('select REMAIN,HARD_RESERVED_BASE,STOCK_VERSION from RRL_REMAINS where UID_POLETA=:lot_id and CELL=:cell',{'lot_id':SOURCE,'cell':CELL})[0]

def setup(g,x):
 assert stock(g)==dict(remain=24,hard_reserved_base=0,stock_version=int(os.environ.get('EXPECTED_WAVE_QA_STOCK_VERSION','9'))),stock(g)
 assert not g.fetch_all("select RESERVATION_ID from RRL_STOCK_RESERVATION where UID_PALLET=:lot_id and STATUS in('ACTIVE','ALLOCATED','PICKING')",{'lot_id':SOURCE})
 assert not g.fetch_all("select TASK_ID from RRL_WAREHOUSE_TASK where UID_PALLET=:lot_id and STATUS not in('DONE','CANCELLED')",{'lot_id':SOURCE})
 with stock_configuration_transaction(g,'Approved isolated durable wave QA metadata','admin','warehouse_settings_edit')as c:
  for name,seq in [('order','RRL_CUSTOMER_ORDER_SQ'),('order_row','RRL_CUSTOMER_ORDER_ROW_SQ'),('plan','RRL_PICK_PLAN_SQ'),('line','RRL_PICK_PLAN_LINE_SQ'),('task','RRL_PICK_TASK_SQ'),('reservation','RRL_PICK_RESERVATION_SQ'),('wave','RRL_PICK_WAVE_SQ'),('wave_order','RRL_PICK_WAVE_ORDER_SQ'),('face','RRL_PICK_FACE_SQ'),('face_article','RRL_PICK_FACE_ARTICUL_SQ')]:
   x[name]=int(scalar(c,'select '+seq+'.nextval from dual'))
  c.execute("insert into RUSERS(ID,NAME,PASS,USER_GROUP,WARE_ID,DELETED,PRAVO_ADMIN_LOGIN)values(:actor,'Isolated durable wave QA',:pw,'NONE',null,0,0)",actor=x['actor'],pw=secrets.token_urlsafe(24))
  c.execute("insert into RRL_CELLS(CELL,WARE_ID,X,Y,Z,OTBOR,IS_SYSTEM,BLOCKED_FOR_ACCEPT,BLOCKED_FOR_REMAINS,BLOCKED_FOR_POPOLNENIE)values(:cell,:ware,0,0,0,1,0,0,0,0)",cell=x['cell'],ware=WARE)
  c.execute("insert into RRL_STOCK_POLICY_GUARD(POLICY_KEY,LOCK_ID)select RRL_STOCK_LOCK_API.resource_key('CELL',:cell),nvl(max(LOCK_ID),900000000)+1 from RRL_STOCK_POLICY_GUARD",cell=x['cell'])
  c.execute("insert into RRL_PICK_FACE(PICK_FACE_ID,WARE_ID,CELL_CODE,PICK_FACE_TYPE,MAX_VOLUME,ACTIVE,CREATED_BY)values(:id,:ware,:cell,'REGULAR',1,1,'admin')",id=x['face'],ware=WARE,cell=x['cell'])
  c.execute("""insert into RRL_PICK_FACE_ARTICUL(PICK_FACE_ARTICUL_ID,PICK_FACE_ID,ARTICUL,MIN_QTY,MAX_QTY,USE_ARTICUL_REPLENISH_RULE,
   REPLENISHMENT_METHOD,REPLENISHMENT_QTY_MODE,BOXES_PER_PALLET,BOX_VOLUME_M3,ACTIVE,CREATED_BY)
   values(:id,:face,:article,0,24,0,'IMMEDIATE','FULL_PALLET',24,0.001,1,'admin')""",id=x['face_article'],face=x['face'],article=ARTICLE)
  create_demand(c,x)
 from app.services.picking_service import PickingService
 from app.schemas import PickWaveActionRequest
 PickingService(g).preview_wave(x['wave'],PickWaveActionRequest(updated_by='admin'))
 demands=g.fetch_all('select PICK_WAVE_DEMAND_ID from RRL_PICK_WAVE_DEMAND where PICK_WAVE_ID=:wave',{'wave':x['wave']})
 assert len(demands)==1,demands
 capacity=g.fetch_all('select RRL_STOCK_REPL_CAPACITY.remaining_base_quantity(:target,:article,null) CAPACITY from dual',{'target':x['cell'],'article':ARTICLE})[0]['capacity']
 assert capacity is not None and capacity>=24,capacity
 now=datetime.now(timezone.utc)
 access(g,x,'ROLE_SAVE',dict(role_id=x['role'],title='Durable wave recovery QA',permissions=['pick_wave_launch'],active=True,expected_version=0))
 assignment(g,x,0,now)

def create_demand(c,x):
 c.execute("insert into RRL_CUSTOMER_ORDER(CUSTOMER_ORDER_ID,ORDER_NO,CUSTOMER_ID,WARE_ID,STATUS,SHIPMENT_DATE)values(:id,:code,-980701,:ware,'OPEN',trunc(sysdate)+1)",id=x['order'],code=x['prefix'],ware=WARE)
 c.execute("insert into RRL_CUSTOMER_ORDER_ROW(CUSTOMER_ORDER_ROW_ID,CUSTOMER_ORDER_ID,LINE_NO,ARTICUL,UNIT_CODE,ORDER_QTY,WARE_ID,STATUS)values(:id,:parent,1,:article,'EA',1,:ware,'OPEN')",id=x['order_row'],parent=x['order'],article=ARTICLE,ware=WARE)
 c.execute("insert into RRL_PICK_PLAN(PICK_PLAN_ID,CUSTOMER_ORDER_ID,CUSTOMER_ID,WARE_ID,STATUS,TOTAL_ORDER_QTY,TOTAL_PLANNED_QTY)values(:id,:parent,-980701,:ware,'PLANNED_FULL',1,1)",id=x['plan'],parent=x['order'],ware=WARE)
 c.execute("insert into RRL_PICK_PLAN_LINE(PICK_PLAN_LINE_ID,PICK_PLAN_ID,CUSTOMER_ORDER_ROW_ID,ARTICUL,REQUESTED_QTY,PLANNED_QTY,CASE_PICK_QTY,STATUS)values(:id,:parent,:row_id,:article,1,1,1,'PLANNED_FULL')",id=x['line'],parent=x['plan'],row_id=x['order_row'],article=ARTICLE)
 c.execute("""insert into RRL_PICK_TASK(PICK_TASK_ID,PICK_PLAN_ID,PICK_PLAN_LINE_ID,CUSTOMER_ORDER_ID,CUSTOMER_ID,TASK_TYPE,ARTICUL,
  PALLET_UID,SOURCE_CELL_CODE,TARGET_CELL_CODE,PICK_FACE_ID,QTY)
  values(:id,:plan,:line,:parent,-980701,'CASE_PICK',:article,:lot_id,:src,:dst,:face,1)""",id=x['task'],plan=x['plan'],line=x['line'],parent=x['order'],article=ARTICLE,lot_id=SOURCE,src=CELL,dst=x['cell'],face=x['face'])
 c.execute("""insert into RRL_PICK_RESERVATION(PICK_RESERVATION_ID,PICK_PLAN_ID,PICK_PLAN_LINE_ID,PICK_TASK_ID,CUSTOMER_ORDER_ID,CUSTOMER_ID,
  RESERVATION_SCOPE,ARTICUL,PALLET_UID,SOURCE_CELL_CODE,RESERVED_QTY)values(:id,:plan,:line,:task,:parent,-980701,'CASE',:article,:lot_id,:cell,1)""",
  id=x['reservation'],plan=x['plan'],line=x['line'],task=x['task'],parent=x['order'],article=ARTICLE,lot_id=SOURCE,cell=CELL)
 c.execute("insert into RRL_PICK_WAVE(PICK_WAVE_ID,WAVE_CODE,WARE_ID,STATUS,WAVE_KIND,CREATED_BY)values(:id,:code,:ware,'PREVIEW','CUSTOMER_ORDER','admin')",id=x['wave'],code=x['prefix'],ware=WARE)
 c.execute("insert into RRL_PICK_WAVE_ORDER(PICK_WAVE_ORDER_ID,PICK_WAVE_ID,PICK_PLAN_ID,CUSTOMER_ORDER_ID,CUSTOMER_ID,ORDER_NO,STATUS,CREATED_BY)values(:id,:wave,:plan,:parent,-980701,:code,'ACTIVE','admin')",id=x['wave_order'],wave=x['wave'],plan=x['plan'],parent=x['order'],code=x['prefix'])

def assignment(g,x,version,now=None):
 now=now or datetime.now(timezone.utc)
 if version:
  x['assignment']+='r';version=0
 x.setdefault('assignments',[]).append(x['assignment'])
 return access(g,x,'ASSIGN',dict(assignment_id=x['assignment'],username=x['actor'],role_id=x['role'],scope_kind='WAREHOUSE',scope_id=str(WARE),valid_from=(now-timedelta(minutes=5)).isoformat(),valid_until=(now+timedelta(hours=2)).isoformat(),expected_version=version,reason='Bounded durable launch recovery proof'))

def command(x,kind):
 if kind=='WAVE_LAUNCH':return StockCommand(operation_id=x['launch'],command_type=kind,actor=x['actor'],lines=(),source={'wave_id':x['wave']},metadata={})
 key='cancel'if kind=='WAVE_CANCEL'else'plan_cancel';doc='PICK_WAVE'if kind=='WAVE_CANCEL'else'PICK_PLAN';identity=x['wave']if kind=='WAVE_CANCEL'else x['plan']
 return StockCommand(operation_id=x[key],command_type=kind,actor='admin',lines=(),source={'document_type':doc,'document_id':identity},metadata={'reason':'Compensate approved isolated durable wave QA','only_cancelled_replenishment':0,'reservation_kind':None})

def body(cmd):return json.loads(cmd.canonical_json())

def trial(g,cmd,inside=None):
 try:
  with g.transaction('Caller-owned canonical trial; all stock effects rollback')as c:
   result=post(c,body(cmd))
   if inside:inside(c,result)
   raise RollbackTrial()
 except RollbackTrial:pass

def context_guards(g,x,checks):
 for ending in('commit','rollback'):
  try:
   with g.transaction('Native metadata context cannot cross transaction boundary')as c:
    run=c.var(int);c.callproc('RRL_WAVE_CONTINUE_API.begin_step',[x['launch'],x['wave'],x['actor'],1,run])
    getattr(c.connection,ending)()
    try:c.callproc('RRL_WAVE_CONTINUE_API.finish_step')
    except oracledb.DatabaseError as e:assert'WAVE_CONTINUATION_CONTEXT_REQUIRED'in str(e),str(e)
    else:raise AssertionError('Context leaked across '+ending)
    finally:c.callproc('RRL_WAVE_CONTINUE_API.end_step')
    raise RollbackTrial()
  except RollbackTrial:pass
 checks.append('native_metadata_context_rejects_commit_and_rollback_reuse')
 try:
  with g.transaction('Fractional step is not a valid workflow identity')as c:
   run=c.var(int)
   try:c.callproc('RRL_WAVE_CONTINUE_API.begin_step',[x['launch'],x['wave'],x['actor'],1.5,run])
   except oracledb.DatabaseError as e:assert'WAVE_CONTINUATION_STEP_REQUIRED'in str(e),str(e)
   else:raise AssertionError('Fractional step accepted')
   finally:c.callproc('RRL_WAVE_CONTINUE_API.end_step')
   raise RollbackTrial()
 except RollbackTrial:pass
 checks.append('native_fractional_step_denied')

def projection_steps(bound,wave,actor):
 return launch_steps(bound,wave,actor,PickingService)

def recovery(g,x,checks):
 repo=WaveContinuation(g,x['wave'],x['launch'],x['actor']);launch=lambda:StockPosting().post(command(x,'WAVE_LAUNCH'))
 def unknown(repository):post_frozen_sources(repository);raise TimeoutError('Injected answer loss after source APPLIED commit')
 try:run_wave_launch(x['wave'],x['launch'],x['actor'],launch,repo,projection_steps,unknown)
 except Exception as e:
  assert getattr(e,'detail',{}).get('continuation_step')=='RESERVE_SOURCES',str(e)
  assert isinstance(e.__cause__,TimeoutError),repr(e.__cause__)
 else:raise AssertionError('Expected source answer loss')
 receipts=repo.sources();assert len(receipts)==1 and receipts[0]['state']=='APPLIED',receipts
 x['source_operation']=receipts[0]['operation_id'];x['source_body']=receipts[0]['body']
 assert stock(g)['remain']==24 and 1<=stock(g)['hard_reserved_base']<=24,stock(g)
 assert read_launch_receipt(g,x['wave'],x['launch'],x['actor'])['continuation_state']=='FAILED'
 checks.append('source_commit_answer_loss_launch_APPLIED_continuation_FAILED_and_frozen_original_body')
 def fail_queue(bound,wave,actor):
  actions=projection_steps(bound,wave,actor);original=actions['RELEASE_QUEUE']
  def fail():original();raise RuntimeError('Injected middle metadata failure')
  actions['RELEASE_QUEUE']=fail;return actions
 try:run_wave_launch(x['wave'],x['launch'],x['actor'],launch,repo,fail_queue,post_frozen_sources)
 except Exception as e:assert getattr(e,'detail',{}).get('continuation_step')=='RELEASE_QUEUE',str(e)
 else:raise AssertionError('Expected metadata fault')
 saved=repo.sources();assert saved==receipts
 step=g.fetch_all('select STEP_NO,STATE from RRL_WAVE_CONTINUE_STEP where LAUNCH_OPERATION_ID=:op order by STEP_NO',{'op':x['launch']})
 assert [r['state']for r in step]==['DONE','DONE','DONE','DONE','FAILED','PENDING','PENDING'],step
 checks.append('middle_metadata_fault_atomic_rollback_and_done_prefix_preserved')
 access(g,x,'REVOKE',dict(assignment_id=x['assignment'],expected_version=1,reason='Verify current warehouse revoke after launch/source commit'))
 try:launch()
 except StockPostingError as e:assert e.oracle_code==20882,str(e)
 else:raise AssertionError('Revoked original launch replay accepted')
 assert read_launch_receipt(g,x['wave'],x['launch'],x['actor'])['state']=='NOT_VISIBLE'
 try:
  with repo.step(6):pass
 except oracledb.DatabaseError as e:assert'CURRENT_WARE_REQUIRED'in str(e),str(e)
 else:raise AssertionError('Revoked direct continuation accepted')
 checks.append('current_revoke_denies_launch_replay_continuation_and_minimal_receipt')
 assignment(g,x,2)
 with ThreadPoolExecutor(max_workers=2)as pool:
  futures=[pool.submit(resume_wave_launch,g,x['wave'],x['launch'],x['actor'],launch,PickingService)for _ in range(2)]
  result=[f.result()for f in futures]
 assert all(r['continuation_state']=='COMPLETE'for r in result),result
 assert repo.sources()==receipts
 assert g.fetch_all("select count(*) N from RRL_STOCK_OPERATION where OPERATION_ID in(:launch,:source_op)and STATE='APPLIED'",{'launch':x['launch'],'source_op':x['source_operation']})[0]['n']==2
 assert g.fetch_all('select count(*) N from RRL_CASE_PICK_TASK where PICK_WAVE_ID=:wave',{'wave':x['wave']})[0]['n']==1
 assert g.fetch_all("select count(*) N from RRL_WAREHOUSE_TASK where SOURCE_DOC_TYPE='PICK_WAVE'and SOURCE_DOC_ID=:wave",{'wave':x['wave']})[0]['n']==1
 checks.append('concurrent_exact_recovery_runs_only_remaining_steps_no_second_launch_source_CASE_or_warehouse_task')

def compensate(g,x,checks):
 rows=g.fetch_all('select STATE from RRL_STOCK_OPERATION where OPERATION_ID=:op',{'op':x['launch']})if'wave'in x else[]
 if rows and rows[0]['state']=='APPLIED':
  trial(g,command(x,'WAVE_CANCEL'),lambda c,r:assert_zero(c))
  StockPosting().post(command(x,'WAVE_CANCEL'))
  StockPosting().post(command(x,'PICK_PLAN_CANCEL'))
  checks.append('canonical_cancel_preflight_rollback_then_wave_and_plan_compensation_APPLIED')
 if'wave'not in x:return
 with stock_configuration_transaction(g,'Retire only zero-fact QA metadata; preserve all journals','admin','warehouse_settings_edit')as c:
  assert scalar(c,"select count(*)from RRL_CASE_CARRIER_LOT where CASE_PICK_TASK_ID in(select CASE_PICK_TASK_ID from RRL_CASE_PICK_TASK where PICK_WAVE_ID=:wave)",wave=x['wave'])==0
  assert scalar(c,"select count(*)from RRL_CASE_PICK_TASK where PICK_WAVE_ID=:wave and(STARTED_AT is not null or SHIPPED_OPERATION is not null)",wave=x['wave'])==0
  assert scalar(c,"select count(*)from RRL_CASE_PICK_LINE where CASE_PICK_TASK_ID in(select CASE_PICK_TASK_ID from RRL_CASE_PICK_TASK where PICK_WAVE_ID=:wave)and nvl(PICKED_QTY,0)!=0",wave=x['wave'])==0
  assert scalar(c,"select count(*)from RRL_TARE_BOOK where PLACE_KIND='CASE'and STATUS='HELD'and PLACE_ID in(select to_char(CASE_PICK_TASK_ID,'TM9')from RRL_CASE_PICK_TASK where PICK_WAVE_ID=:wave)",wave=x['wave'])==0
  c.execute("update RRL_CASE_PICK_LINE set STATUS='CANCELLED'where CASE_PICK_TASK_ID in(select CASE_PICK_TASK_ID from RRL_CASE_PICK_TASK where PICK_WAVE_ID=:wave)",wave=x['wave'])
  c.execute("update RRL_CASE_PICK_TASK set STATUS='CANCELLED',UPDATED_BY='admin'where PICK_WAVE_ID=:wave and STATUS='NEW'",wave=x['wave'])
  c.execute("update RRL_PICK_WAVE_REPLENISH_TASK set STATUS='CANCELLED',WAIT_REASON='Isolated QA compensated; no physical work',UPDATED_BY='admin'where PICK_WAVE_ID=:wave",wave=x['wave'])
  c.execute("update RRL_CUSTOMER_ORDER set STATUS='CANCELLED'where CUSTOMER_ORDER_ID=:id",id=x['order'])
  c.execute("update RRL_PICK_FACE_ARTICUL set ACTIVE=0 where PICK_FACE_ARTICUL_ID=:id",id=x['face_article'])
  c.execute("update RRL_PICK_FACE set ACTIVE=0 where PICK_FACE_ID=:id",id=x['face'])
  c.execute("update RRL_CELLS set BLOCKED_FOR_ACCEPT=1,BLOCKED_FOR_REMAINS=1,BLOCKED_FOR_POPOLNENIE=1 where CELL=:cell",cell=x['cell'])
  c.execute("update RUSERS set DELETED=1 where ID=:actor",actor=x['actor'])
 with g.transaction('Remove temporary grants only; native access audit retained')as c:
  for identity in x.get('assignments',[x['assignment']]):c.execute('delete from RRL_ACCESS_ASSIGNMENT where ASSIGNMENT_ID=:id',id=identity)
  c.execute('delete from RRL_ACCESS_ROLE_RIGHT where ROLE_ID=:id',id=x['role'])
  c.execute('delete from RRL_ACCESS_ROLE where ROLE_ID=:id',id=x['role'])
 assert stock(g)['remain']==24 and stock(g)['hard_reserved_base']==0,stock(g)

def assert_zero(c):
 assert_h(c,0)

def assert_h(c,value):
 assert scalar(c,'select HARD_RESERVED_BASE from RRL_REMAINS where UID_POLETA=:lot_id and CELL=:cell',lot_id=SOURCE,cell=CELL)==value

def main():
 assert os.environ.get('RUN_APPROVED_WAVE_DURABLE_QA')=='1','Explicit bounded DEV commit authorization switch required'
 g=OracleGateway();tag=uuid4().hex[:9];prefix='wld'+tag
 x=dict(prefix=prefix,actor=prefix,cell='WL'+tag,role=prefix+'r',assignment=prefix+'a',launch='WAVE.DURABLE.LAUNCH:'+tag,cancel='WAVE.DURABLE.CANCEL:'+tag,plan_cancel='WAVE.DURABLE.PLAN.CANCEL:'+tag)
 checks=[];failure=None
 try:
  setup(g,x)
  before=stock(g);trial(g,command(x,'PICK_PLAN_CANCEL'))
  trial(g,command(x,'WAVE_LAUNCH'),lambda c,r:assert_h(c,1))
  assert stock(g)==before
  checks.append('metadata_only_setup_and_positive_launch_plan_cancel_caller_rollback_no_stock_commit')
  StockPosting().post(command(x,'WAVE_LAUNCH'))
  assert stock(g)['hard_reserved_base']==1
  trial(g,command(x,'WAVE_CANCEL'),lambda c,r:assert_zero(c))
  checks.append('explicit_authorized_launch_commit_H1_and_cancel_compensator_rollback_proven')
  context_guards(g,x,checks);recovery(g,x,checks)
 except Exception as e:
  failure=repr(e);raise
 finally:
  try:compensate(g,x,checks)
  except Exception as cleanup_error:
   failure=str(failure or '')+'; compensation failure: '+repr(cleanup_error);raise
  finally:
   result=dict(status='PASS'if failure is None else'FAILED',checks=checks,context=x,error=failure,source=SOURCE,stock_final=stock(g),stock_commit='EXPLICIT_AUTHORIZED_RESERVATION_ONLY',physical_moves=0,history_retained=True)
   (ROOT/'reports/retailcase/2026-10-15/resource-timeline/wave-continuation-native.json').write_text(json.dumps(result,indent=2,default=str),encoding='utf8')
   print(json.dumps({k:v for k,v in result.items()if k!='context'},default=str))
if __name__=='__main__':main()
