"""Approved isolated metadata only: new tasks/resources, no reserve or goods posting."""
import sys,json,secrets
from pathlib import Path
from uuid import uuid4
from datetime import datetime,timedelta,timezone
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'scripts'),str(ROOT/'api/wms_api_server')]
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment()
from app.oracle_gateway import OracleGateway
from app.modules.platform.public import stock_configuration_transaction
from warehouse_task_scoped_complete_smoke import grant,access,scalar,RollbackTrial
SOURCE='REUSE.RETURN:e6c16d0bbd'
RUNTIME=ROOT/'tmp/task_assignment_fixture.json'
REPORT=ROOT/'reports/retailcase/2026-10-15/task-assignment'


def snapshot(g):
 return g.fetch_all("select UID_POLETA,CELL,REMAIN,HARD_RESERVED_BASE,STOCK_VERSION from RRL_REMAINS where UID_POLETA in(:lot,'CASELOT:E8EAB9A962B9D19BA5AC8FCEE19D8021895BD0:1')order by UID_POLETA,CELL",{'lot':SOURCE})


def create_metadata(c,ctx):
 for actor,pw in((ctx['actor'],ctx['password']),(ctx['other'],ctx['other_password'])):
  c.execute("insert into RUSERS(ID,NAME,PASS,USER_GROUP,WARE_ID,DELETED,PRAVO_ADMIN_LOGIN)values(:id,'QA TASK assignment',:pw,'NONE',null,0,0)",id=actor,pw=pw)
 for name,seq in(('task','RRL_WAREHOUSE_TASK_SQ'),('mixed_task','RRL_WAREHOUSE_TASK_SQ'),('equipment','RRL_RESOURCE_EQUIPMENT_SQ'),('resource','RRL_RESOURCE_SQ'),('shift','RRL_RESOURCE_SHIFT_SQ'),('session','RRL_RESOURCE_SESSION_SQ')):
  ctx[name]=int(scalar(c,'select '+seq+'.nextval from dual'))
 c.execute("insert into RRL_CELLS(CELL,WARE_ID,X,Y,Z,OTBOR,IS_SYSTEM,LIMIT_WEIGHT,LIMIT_HEIGHT,BLOCKED_FOR_ACCEPT,BLOCKED_FOR_REMAINS,BLOCKED_FOR_POPOLNENIE)values(:cell,:ware,0,0,0,0,0,0,0,0,0,0)",cell=ctx['cell'],ware=ctx['ware_id'])
 c.execute("insert into RRL_STOCK_POLICY_GUARD(POLICY_KEY,LOCK_ID)select RRL_STOCK_LOCK_API.resource_key('CELL',:cell),nvl(max(LOCK_ID),900000000)+1 from RRL_STOCK_POLICY_GUARD",cell=ctx['cell'])
 c.execute("insert into RRL_RESOURCE_EQUIPMENT(EQUIPMENT_ID,EQUIPMENT_CODE,EQUIPMENT_TYPE,WARE_ID,SERVICE_STATUS,ACTIVE,CREATED_BY)values(:id,:code,'REACHTRUCK',:ware,'ACTIVE',1,'admin')",id=ctx['equipment'],code=ctx['prefix'],ware=ctx['ware_id'])
 c.execute("""insert into RRL_RESOURCE(RESOURCE_ID,RESOURCE_CODE,RESOURCE_NAME,RESOURCE_CLASS,RESOURCE_TYPE,EQUIPMENT_ID,USER_ID,WARE_ID,STATUS,ACTIVE,CREATED_BY)
 select :id,:code,'QA TASK assignment',RESOURCE_CLASS,'REACHTRUCK',:equipment,:actor,:ware,'AVAILABLE',1,'admin'from RRL_RESOURCE_TYPE where RESOURCE_TYPE='REACHTRUCK'""",id=ctx['resource'],code=ctx['prefix'],equipment=ctx['equipment'],actor=ctx['actor'],ware=ctx['ware_id'])
 c.execute("insert into RRL_RESOURCE_TASK_QUAL(RESOURCE_ID,TASK_TYPE,VALID_FROM,ACTIVE,UPDATED_BY)values(:id,'PUTAWAY',localtimestamp-interval '1'day,1,'admin')",id=ctx['resource'])
 c.execute("insert into RRL_RESOURCE_SHIFT(SHIFT_ID,SHIFT_CODE,SHIFT_DATE,WARE_ID,START_AT,FINISH_AT,STATUS,CREATED_BY)values(:id,:code,trunc(sysdate),:ware,localtimestamp-interval '1'hour,localtimestamp+interval '2'hour,'OPEN','admin')",id=ctx['shift'],code=ctx['prefix'],ware=ctx['ware_id'])
 c.execute("insert into RRL_RESOURCE_SESSION(SESSION_ID,SHIFT_ID,RESOURCE_ID,EQUIPMENT_ID,OPERATOR_USER_ID,STATUS,CREATED_BY)values(:id,:shift_id,:machine,:equipment,:actor,'ACTIVE','admin')",id=ctx['session'],shift_id=ctx['shift'],machine=ctx['resource'],equipment=ctx['equipment'],actor=ctx['actor'])
 for task,cell,ware in((ctx['task'],ctx['cell'],ctx['ware_id']),(ctx['mixed_task'],ctx['foreign_cell'],ctx['foreign_ware'])):
  c.execute("""insert into RRL_WAREHOUSE_TASK(TASK_ID,TASK_TYPE,TASK_SOURCE,SOURCE_TASK_ID,UID_PALLET,FROM_CELL,TO_CELL,FROM_WARE_ID,TO_WARE_ID,QTY,UNIT_CODE,QTY_MODE,STATUS,CREATED_BY)
   values(:id,'PUTAWAY','MANUAL',:id,:lot,:src,:dst,:ware,:to_ware,1,:uom,'BASE','PLANNED','admin')""",id=task,lot=SOURCE,src=ctx['source_cell'],dst=cell,ware=ctx['ware_id'],to_ware=ware,uom=ctx['base_uom'])


def stage(g):
 assert not RUNTIME.exists(),'Existing fixture must be explicitly cleaned before a new stage'
 rows=g.fetch_all("select r.CELL,c.WARE_ID,r.BASE_UOM,r.REMAIN,r.HARD_RESERVED_BASE from RRL_REMAINS r join RRL_CELLS c on c.CELL=r.CELL where r.UID_POLETA=:lot and r.REMAIN>0",{'lot':SOURCE})
 assert len(rows)==1 and rows[0]['ware_id']==13583852 and rows[0]['remain']==23,rows
 foreign=g.fetch_all("select CELL,WARE_ID from RRL_CELLS where CELL='QS55edaf9dce'");assert len(foreign)==1 and foreign[0]['ware_id']!=rows[0]['ware_id']
 tag=uuid4().hex[:8];ctx=dict(tag=tag,prefix='wta'+tag,actor='wa'+tag,other='wb'+tag,password=secrets.token_urlsafe(20),other_password=secrets.token_urlsafe(20),grants=[],cell='WTA'+tag,source_cell=rows[0]['cell'],ware_id=rows[0]['ware_id'],base_uom=rows[0]['base_uom'],foreign_cell=foreign[0]['cell'],foreign_ware=foreign[0]['ware_id'])
 before=snapshot(g)
 try:
  with stock_configuration_transaction(g,'Preflight isolated TASK metadata caller rollback','admin','warehouse_settings_edit')as c:
   create_metadata(c,ctx);raise RollbackTrial()
 except RollbackTrial:pass
 assert snapshot(g)==before
 for key in('task','mixed_task'):
  assert not g.fetch_all('select TASK_ID from RRL_WAREHOUSE_TASK where TASK_ID=:id',{'id':ctx[key]})
 with stock_configuration_transaction(g,'Create approved isolated TASK metadata; no goods','admin','warehouse_settings_edit')as c:create_metadata(c,ctx)
 ctx['before_source']=json.loads(json.dumps(before,default=str));RUNTIME.write_text(json.dumps(ctx,default=str),encoding='utf-8')
 try:
  ctx['assign_grant']=grant(g,ctx,ctx['actor'],'assign','warehouse_task_assign','WAREHOUSE',str(ctx['ware_id']))
  grant(g,ctx,ctx['actor'],'execute','warehouse_task_execute','SELF')
  grant(g,ctx,ctx['other'],'executea','warehouse_task_execute','WAREHOUSE',str(ctx['ware_id']))
  grant(g,ctx,ctx['other'],'assigna','warehouse_task_assign','WAREHOUSE',str(ctx['ware_id']))
  grant(g,ctx,ctx['other'],'viewb','warehouse_task_view','WAREHOUSE',str(ctx['foreign_ware']))
 finally:RUNTIME.write_text(json.dumps(ctx,default=str),encoding='utf-8')
 RUNTIME.write_text(json.dumps(ctx,default=str),encoding='utf-8');assert snapshot(g)==before
 REPORT.mkdir(parents=True,exist_ok=True);public={k:v for k,v in ctx.items()if 'password'not in k};public.update(metadata_fixture_committed=True,goods_commit=False,reserve_created=False,setup_preflight_rollback=True)
 (REPORT/'fixture.json').write_text(json.dumps(public,indent=2,default=str),encoding='utf-8');print(json.dumps({k:ctx[k]for k in('task','mixed_task','resource','session','shift','actor','other','ware_id')}))


def cleanup(g):
 from warehouse_task_fixture_retirement import retire_metadata
 from app.services.warehouse_task_service import WarehouseTaskService
 from app.schemas import WarehouseTaskStatusRequest
 ctx=json.loads(RUNTIME.read_text(encoding='utf-8'));before=snapshot(g)
 WarehouseTaskService(g).cancel_task(ctx['mixed_task'],WarehouseTaskStatusRequest(updated_by='admin',reason='Retire only owned metadata-only mixed-scope QA task'))
 retire_metadata(g,ctx)
 assert snapshot(g)==before
 rows=g.fetch_all('select t.TASK_ID,t.STATUS,t.FACT_QTY,v.ASSIGNMENT_VERSION from RRL_WAREHOUSE_TASK t join RRL_WTASK_ASSIGN_VERSION v on v.TASK_ID=t.TASK_ID where t.TASK_ID in(:a,:b)',{'a':ctx['task'],'b':ctx['mixed_task']})
 assert len(rows)==2 and all(r['status']=='CANCELLED'and(r['fact_qty']or 0)==0 for r in rows),rows
 (REPORT/'cleanup.json').write_text(json.dumps(dict(status='CANONICALLY_CANCELLED_RETIRED_HISTORY_RETAINED',tasks=rows,source_before=before,source_after=snapshot(g),goods_commit=False),indent=2,default=str),encoding='utf-8');ctx['retired']=True;RUNTIME.write_text(json.dumps(ctx,default=str),encoding='utf-8');print('TASK_FIXTURE_RETIRED_NO_GOODS_HISTORY_RETAINED')


if __name__=='__main__':
 g=OracleGateway()
 {'stage':stage,'cleanup':cleanup}[sys.argv[1]](g)
