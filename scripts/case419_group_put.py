exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
from app.modules.inventory.infrastructure.warehouse_hu import WarehouseHu
from app.modules.inventory.public import build_stock_posting_service
from app.modules.inventory.contracts_stock import StockCommand
from app.modules.platform.public import read_oracle_json
from app.oracle_gateway import OracleGateway
p=Path('tmp/context406.json');saved=json.loads(p.read_text(encoding='utf-8'));first=saved['first'];tag=first['tag'];target=saved['group_plan']['outbound_dock'];ware=saved['group_plan']['target_warehouse_id']
if 'group_put_cell'not in saved:
 with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
  q=c.cursor();q.callproc('RRL_STOCK_CONFIG_API.begin_change',['admin','warehouse_settings_edit'])
  try:
   q.execute('insert into RRL_CELLS(CELL,WARE_ID,X,Y,Z,OTBOR,IS_SYSTEM,BLOCKED_FOR_REMAINS,BLOCKED_FOR_POPOLNENIE,BLOCKED_FOR_ACCEPT)values(:cell,:ware,0,0,0,0,1,0,0,0)',cell=target,ware=ware)
   q.execute("insert into RRL_STOCK_POLICY_GUARD(POLICY_KEY,LOCK_ID)select RRL_STOCK_LOCK_API.resource_key('CELL',:cell),nvl(max(LOCK_ID),900000000)+1 from RRL_STOCK_POLICY_GUARD",cell=target);c.commit()
  finally:q.callproc('RRL_STOCK_CONFIG_API.end_change')
 saved['group_put_cell']=target;p.write_text(json.dumps(saved,indent=2),encoding='utf-8')
hu=WarehouseHu(OracleGateway())
if 'group_put_plan'not in saved:
 tree=hu.preview(saved['root'],'admin')
 meta=dict(target_cell=target,expected_version=tree['nodes'][0]['version'],scan_container=saved['root'],scanned_from_cell=saved['group_receive_cell'],scanned_to_cell=target,group_receipt_operation_id=saved['group_receipt_operation_id'],measurements=dict(origin='MANUAL_CONFIRMED',content_version=tree['nodes'][0]['version'],gross_weight_kg='7',width_m='1',depth_m='1',height_m='1.5'))
 saved.update(group_put_plan=hu.command('HU_PLAN_MOVE',saved['root'],'GROUP419.PUT.PLAN:'+tag,meta,'admin'),group_put_metadata=meta);p.write_text(json.dumps(saved,indent=2),encoding='utf-8')
task=saved['group_put_plan']['task_id'];op='GROUP419.PUT.DONE:'+tag
meta=dict(fact_qty='1',scanned_pallet=saved['root'],scanned_from_cell=saved['group_receive_cell'],scanned_to_cell=target)
if 'group_put_done'not in saved:
 with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
  q=c.cursor();request=dict(contract_version=2,operation_id=op,command_type='HU_TASK_COMPLETE',actor='admin',source=dict(task_id=task),lines=[],units=[],metadata=meta);out=q.var(oracledb.DB_TYPE_CLOB)
  try:
   q.callproc('RRL_STOCK_POSTING_API.prepare_command',[json.dumps(request),'admin',out,None])
   if out.getvalue()is None:q.callproc('RRL_STOCK_POSTING_API.execute_prepared',[out])
   trial=read_oracle_json(out.getvalue())
   q.execute('select count(*)from RRL_IW_GROUP_PLACEMENT where OPERATION_ID=:op',op=op);assert q.fetchone()[0]==1
   c.rollback();q.execute('select STATUS from RRL_WAREHOUSE_TASK where TASK_ID=:task_id',task_id=task);assert q.fetchone()[0]=='PLANNED'
  finally:q.callproc('RRL_STOCK_POSTING_API.reset_connection')
 saved['group_put_done']=build_stock_posting_service().post(StockCommand(operation_id=op,command_type='HU_TASK_COMPLETE',actor='admin',source=dict(task_id=task),lines=(),metadata=meta));p.write_text(json.dumps(saved,indent=2),encoding='utf-8')
assert build_stock_posting_service().post(StockCommand(operation_id=op,command_type='HU_TASK_COMPLETE',actor='admin',source=dict(task_id=task),lines=(),metadata=meta))==saved['group_put_done']
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor()
 for ctx in(saved['first'],saved['second']):
  q.execute('select REMAIN,HARD_RESERVED_BASE from RRL_REMAINS where UID_POLETA=:lot_id and CELL=:cell',lot_id=ctx['lot'],cell=target);assert q.fetchone()==(3,0)
 q.execute('select count(*),sum(BASE_QTY)from RRL_WAREHOUSE_TASK_STOCK_MOVE where TASK_ID=:task_id',task_id=task);assert q.fetchone()==(2,6)
 q.execute('select FACT_QTY,UNIT_CODE from RRL_WAREHOUSE_TASK where TASK_ID=:task_id',task_id=task);assert q.fetchone()==(1,'HU')
 q.execute("select sum(r.REMAIN),sum(r.HARD_RESERVED_BASE)from RRL_REMAINS r join RRL_CELLS x on x.CELL=r.CELL where x.WARE_ID=6667491");assert q.fetchone()==(20,20)
print('PASS419 whole existingHU task1HU/commodity2x3EA/original6keys9codes/wholelate rollback/replay/groupplacementproof/P20H20')
