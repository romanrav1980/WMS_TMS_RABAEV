exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
from app.modules.inventory.infrastructure.interwarehouse import Interwarehouse
from app.modules.inventory.public import build_stock_posting_service
from app.modules.platform.public import read_oracle_json
from app.oracle_gateway import OracleGateway
receipt=json.loads(Path("tmp/context322_received.json").read_text(encoding="utf-8"));source=receipt["source"];p=Path("tmp/context323.json")
saved=json.loads(p.read_text(encoding="utf-8"))if p.exists()else{}
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
if "plan"not in saved:saved["plan"]=service.plan_placement("IW323.PLAN:"+source["tag"],receipt["operation_id"],"admin");save()
old=saved["plan"]["task_id"];operation="IW323.REPLAN:"+source["tag"];reason="Перепланирование ещё не назначенного целого грузового места"
request=dict(contract_version=2,operation_id=operation,command_type="INTERWARE_PUTAWAY_PLAN",actor="admin",source=dict(receipt_operation_id=receipt["operation_id"]),lines=[],units=[],metadata=dict(superseded_task_id=old,replan_reason=reason))
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor()
 def native():
  out=q.var(oracledb.DB_TYPE_CLOB)
  try:
   q.callproc("RRL_STOCK_POSTING_API.prepare_command",[json.dumps(request),"admin",out,None])
   if out.getvalue()is None:q.callproc("RRL_STOCK_POSTING_API.execute_prepared",[out])
   return read_oracle_json(out.getvalue())
  finally:q.callproc("RRL_STOCK_POSTING_API.reset_connection")
 if "replan"not in saved:
  trial=native()
  q.execute("select STATUS from RRL_WAREHOUSE_TASK where TASK_ID=:id",id=old);assert q.fetchone()[0]=="CANCELLED"
  c.rollback()
  q.execute("select STATUS from RRL_WAREHOUSE_TASK where TASK_ID=:id",id=old);assert q.fetchone()[0]=="PLANNED"
  q.execute("select count(*)from RRL_INTERWARE_PUT_PLAN where OPERATION_ID=:op",op=operation);assert q.fetchone()[0]==0;c.rollback()
  saved["replan"]=native();c.commit();saved.update(source=source,receipt=receipt["operation_id"],operation_id=operation);save()
 assert native()==saved["replan"];c.commit()
 q.execute("select STATUS,QTY,UNIT_CODE,UID_PALLET from RRL_WAREHOUSE_TASK where TASK_ID=:id",id=saved["replan"]["task_id"]);assert q.fetchone()==("PLANNED",1,"HU",source["physical_root"])
 q.execute("select STATUS from RRL_WAREHOUSE_TASK where TASK_ID=:id",id=old);assert q.fetchone()[0]=="CANCELLED"
 q.execute("select sum(REMAIN),sum(HARD_RESERVED_BASE)from RRL_REMAINS where UID_POLETA=:lot",lot=source["lot"]);assert q.fetchone()==(3,0)
 q.execute("select count(*)from RRL_WMS_HU_LINK where PARENT_UID in(:a,:b)and ACTIVE_FLAG=1",a=source["physical_root"],b=source["inner_root"]);assert q.fetchone()[0]==2
print("PASS323 atomic wholeHU cancel-replan/late rollback/exact repeat/oldhistory/no physicalmovement")
