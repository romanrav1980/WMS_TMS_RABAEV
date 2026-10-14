exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
from app.modules.inventory.infrastructure.interwarehouse import Interwarehouse
from app.modules.inventory.public import build_stock_posting_service
from app.modules.platform.public import read_oracle_json
from app.oracle_gateway import OracleGateway
p=Path("tmp/context324.json");receipt=json.loads(Path("tmp/context322_received.json").read_text(encoding="utf-8"));source=receipt["source"];saved=json.loads(p.read_text(encoding="utf-8"))if p.exists()else{};retained=json.loads(Path("tmp/context323.json").read_text(encoding="utf-8"));saved.setdefault("plan",retained["replan"])
service=Interwarehouse(OracleGateway(),build_stock_posting_service())
def save():p.write_text(json.dumps(saved,indent=2),encoding="utf-8")
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.callproc("RRL_STOCK_CONFIG_API.begin_change",["admin","warehouse_settings_edit"])
 try:
  q.execute("select count(*)from RRL_CELLS where CELL=:cell_code",cell_code=source["outbound"])
  if not q.fetchone()[0]:
   q.execute("insert into RRL_CELLS(CELL,WARE_ID,X,Y,Z,OTBOR,IS_SYSTEM,LIMIT_WEIGHT,LIMIT_HEIGHT)values(:cell_code,:ware_no,0,0,0,0,0,0,0)",cell_code=source["outbound"],ware_no=source["target_warehouse"])
   q.execute("insert into RRL_STOCK_POLICY_GUARD(POLICY_KEY,LOCK_ID)select RRL_STOCK_LOCK_API.resource_key('CELL',:cell_code),nvl(max(LOCK_ID),900000000)+1 from RRL_STOCK_POLICY_GUARD",cell_code=source["outbound"])
  c.commit()
 finally:q.callproc("RRL_STOCK_CONFIG_API.end_change")
if "plan"not in saved:saved["plan"]=service.plan_placement("IW324.PLAN:"+source["tag"],receipt["operation_id"],"admin");save()
task=saved["plan"]["task_id"]
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select UID_PALLET,QTY,UNIT_CODE,HU_CONTENT_VERSION,FROM_CELL,TO_CELL from RRL_WAREHOUSE_TASK where TASK_ID=:task_id",task_id=task);root,qty,unit,version,origin,target=q.fetchone()
 assert root==source["physical_root"]and qty==1 and unit=="HU"
 meta=dict(fact_qty="1",scanned_pallet=root,scanned_from_cell=origin,scanned_to_cell=target)
 operation="IW324.COMPLETE:"+source["tag"];request=dict(contract_version=2,operation_id=operation,command_type="HU_TASK_COMPLETE",actor="admin",source=dict(task_id=task),lines=[],units=[],metadata=meta)
 def native():
  out=q.var(oracledb.DB_TYPE_CLOB)
  try:
   q.callproc("RRL_STOCK_POSTING_API.prepare_command",[json.dumps(request),"admin",out,None])
   if out.getvalue()is None:q.callproc("RRL_STOCK_POSTING_API.execute_prepared",[out])
   return read_oracle_json(out.getvalue())
  finally:q.callproc("RRL_STOCK_POSTING_API.reset_connection")
 if "complete"not in saved:
  trial=native()
  q.execute("select count(*)from RRL_INTERWARE_PLACEMENT where TASK_ID=:task_id",task_id=task);assert q.fetchone()[0]==1
  c.rollback()
  q.execute("select REMAIN,HARD_RESERVED_BASE from RRL_REMAINS where UID_POLETA=:lot_id and CELL=:cell_code",lot_id=source["lot"],cell_code=origin);assert q.fetchone()==(3,0)
  q.execute("select count(*)from RRL_INTERWARE_PLACEMENT where TASK_ID=:task_id",task_id=task);assert q.fetchone()[0]==0;c.rollback()
  result=native();c.commit();saved.update(complete=result,operation_id=operation,metadata=meta,source=source,receipt_operation_id=receipt["operation_id"]);save()
 assert native()==saved["complete"];c.commit()
 q.execute("select REMAIN,HARD_RESERVED_BASE from RRL_REMAINS where UID_POLETA=:lot_id and CELL=:cell_code",lot_id=source["lot"],cell_code=target);assert q.fetchone()==(3,0)
 q.execute("select BASE_QTY,BASE_UOM,ROOT_UID from RRL_INTERWARE_PLACEMENT where TASK_ID=:task_id",task_id=task);assert q.fetchone()==(3,"EA",source["lot"])
 q.execute("select count(*)from RRL_WMS_HU_LINK where PARENT_UID in(:top_id,:inner_id)and ACTIVE_FLAG=1",top_id=root,inner_id=source["inner_root"]);assert q.fetchone()[0]==2
 q.execute("select count(*)from RRL_PALLETS where UID_PALLET in(:top_id,:inner_id)and HU_CURRENT_CELL=:cell_code",top_id=root,inner_id=source["inner_root"],cell_code=target);assert q.fetchone()[0]==2
 q.execute("select sum(r.REMAIN),sum(r.HARD_RESERVED_BASE)from RRL_REMAINS r join RRL_CELLS cell on cell.CELL=r.CELL where cell.WARE_ID=6667491");assert q.fetchone()==(20,20)
print("PASS324 originaltask oneHU whole3 oldunits6codes moved/PLACEMENT3EA/rootTOP-BOX retained/late rollback/exact replay/oldsync; no second task or quantityengine")
