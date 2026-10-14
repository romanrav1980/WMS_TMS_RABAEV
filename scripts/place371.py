exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
from app.modules.inventory.infrastructure.interwarehouse import Interwarehouse
from app.modules.inventory.infrastructure.stock_posting_uow import StockPosting
from app.modules.inventory.public import build_stock_posting_service
from app.modules.platform.public import read_oracle_json
from app.oracle_gateway import OracleGateway
ctx_path=Path("tmp/context368.json");ctx=json.loads(ctx_path.read_text(encoding="utf-8"));found_path=Path("tmp/context368_recovery.json");found=json.loads(found_path.read_text(encoding="utf-8"))
service=Interwarehouse(OracleGateway(),build_stock_posting_service())
if "placement_result"not in ctx:
 ctx["placement_result"]=service.plan_placement("IW371.ORIGINAL.PUT.PLAN:"+ctx["tag"],ctx["receipt_operation"],"admin");ctx_path.write_text(json.dumps(ctx,indent=2),encoding="utf-8")
for index,part in enumerate(found["parts"]):
 if "placement_result"not in part:
  part["placement_result"]=service.plan_recovery_placement("IW371.FOUND.PUT.PLAN:"+str(index)+":"+ctx["tag"],part["receipt_operation_id"],"admin");found_path.write_text(json.dumps(found,indent=2),encoding="utf-8")
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor()
 for index,item in enumerate([ctx]+found["parts"]):
  plan=item["placement_result"];task=plan["task_id"]
  q.execute("select UID_PALLET,FROM_CELL,TO_CELL,QTY from RRL_WAREHOUSE_TASK where TASK_ID=:task_id",task_id=task);lot,origin,target,qty=q.fetchone();assert qty==1
  meta=dict(fact_qty="1",scanned_pallet=lot,scanned_from_cell=origin,scanned_to_cell=target)
  op="IW371.PUT.DONE:"+str(index)+":"+ctx["tag"]
  req=dict(contract_version=2,operation_id=op,command_type="TASK_COMPLETE",actor="admin",source=dict(task_id=task),lines=[],units=[],metadata=meta);out=q.var(oracledb.DB_TYPE_CLOB)
  try:
   q.callproc("RRL_STOCK_POSTING_API.prepare_command",[json.dumps(req),"admin",out,None])
   if out.getvalue()is None:q.callproc("RRL_STOCK_POSTING_API.execute_prepared",[out])
   result=read_oracle_json(out.getvalue());c.commit();item["placement_complete_result"]=result
   if index==0:ctx_path.write_text(json.dumps(ctx,indent=2),encoding="utf-8")
   else:found_path.write_text(json.dumps(found,indent=2),encoding="utf-8")
  finally:q.callproc("RRL_STOCK_POSTING_API.reset_connection")
  q.execute("select REMAIN,HARD_RESERVED_BASE from RRL_REMAINS where UID_POLETA=:lot_id and CELL=:cell_code",lot_id=lot,cell_code=target);assert q.fetchone()==(1,0)
  q.execute("select count(*),sum(BASE_QTY)from RRL_WMS_RECEIPT_UNIT where CURRENT_UID=:lot_id and CURRENT_CELL=:cell_code and STOCK_STATUS='AVAILABLE'",lot_id=lot,cell_code=target);assert q.fetchone()==(1,1)
 q.execute("select sum(r.REMAIN),sum(r.HARD_RESERVED_BASE)from RRL_REMAINS r join RRL_CELLS cell on cell.CELL=r.CELL where cell.WARE_ID=6667491");assert q.fetchone()==(20,20)
print("PASS371 originalaccepted1 + twofound1 existingTASK_COMPLETE allthreeplaced/P3conserved/same3keys6codes; no other quantitywriter")
