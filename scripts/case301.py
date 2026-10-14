exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
from app.modules.platform.public import read_oracle_json
import uuid
def command(q,kind,op,source,meta):
 out=q.var(oracledb.DB_TYPE_CLOB)
 req=dict(contract_version=2,operation_id=op,command_type=kind,actor="admin",source=source,lines=[],units=[],metadata=meta)
 try:
  q.callproc("RRL_STOCK_POSTING_API.prepare_command",[json.dumps(req),"admin",out,None])
  if out.getvalue()is None:q.callproc("RRL_STOCK_POSTING_API.execute_prepared",[out])
  return read_oracle_json(out.getvalue())
 finally:q.callproc("RRL_STOCK_POSTING_API.reset_connection")
for number in [291,292]:
 ctx=json.loads(Path("tmp/context"+str(number)+".json").read_text(encoding="utf-8"))
 recovery=json.loads(Path("tmp/context300_"+str(number)+".json").read_text(encoding="utf-8"))
 p=Path("tmp/context301_"+str(number)+".json");saved=json.loads(p.read_text(encoding="utf-8"))if p.exists()else {}
 with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
  q=c.cursor();q.execute("select OPERATION_ID,ROOT_UID,RECEIVE_CELL from RRL_INTERWARE_RECOVERY_RECEIPT where APPROVAL_OPERATION_ID=:approval_id",approval_id=recovery["approval_operation_id"]);rid,lot,origin=q.fetchone()
  if not saved:
   preview=command(q,"INTERWARE_RECOVERY_PUTAWAY_PLAN","IW301.ROLL:"+uuid.uuid4().hex,dict(recovery_operation_id=rid),{})
   assert preview["quantity"]=="2";task=preview["task_id"];c.rollback()
   q.execute("select count(*)from RRL_WAREHOUSE_TASK where TASK_ID=:task_id",task_id=task);assert q.fetchone()==(0,)
   plan_op="IW301.PLAN:"+str(number)+":"+ctx["tag"]
   plan=command(q,"INTERWARE_RECOVERY_PUTAWAY_PLAN",plan_op,dict(recovery_operation_id=rid),{});c.commit()
   assert command(q,"INTERWARE_RECOVERY_PUTAWAY_PLAN",plan_op,dict(recovery_operation_id=rid),{})==plan;c.rollback()
   saved=dict(plan_operation_id=plan_op,plan=plan,recovery_operation_id=rid)
   p.write_text(json.dumps(saved,indent=2),encoding="utf-8")
  plan=saved["plan"];meta=dict(fact_qty="2",scanned_pallet=lot,scanned_from_cell=origin,scanned_to_cell=plan["to_cell"])
  if "completed"not in saved:
   result=command(q,"TASK_COMPLETE","IW301.PUT.ROLL:"+uuid.uuid4().hex,dict(task_id=plan["task_id"]),meta)
   q.execute("select REMAIN,HARD_RESERVED_BASE from RRL_REMAINS where UID_POLETA=:lot_id and CELL=:cell_code",lot_id=lot,cell_code=plan["to_cell"]);assert q.fetchone()==(2,0)
   c.rollback();q.execute("select count(*)from RRL_IW_RECOVERY_PLACEMENT where TASK_ID=:task_id",task_id=plan["task_id"]);assert q.fetchone()==(0,)
   q.execute("select REMAIN,HARD_RESERVED_BASE from RRL_REMAINS where UID_POLETA=:lot_id and CELL=:cell_code",lot_id=lot,cell_code=origin);assert q.fetchone()==(2,0)
   op="IW301.DONE:"+str(number)+":"+ctx["tag"];result=command(q,"TASK_COMPLETE",op,dict(task_id=plan["task_id"]),meta);c.commit()
   saved.update(completed=result,completion_operation_id=op,completion_metadata=meta);p.write_text(json.dumps(saved,indent=2),encoding="utf-8")
  assert command(q,"TASK_COMPLETE",saved["completion_operation_id"],dict(task_id=plan["task_id"]),saved["completion_metadata"])==saved["completed"];c.rollback()
  q.execute("select REMAIN,HARD_RESERVED_BASE from RRL_REMAINS where UID_POLETA=:lot_id and CELL=:cell_code",lot_id=lot,cell_code=plan["to_cell"]);assert q.fetchone()==(2,0)
  q.execute("select nvl(sum(REMAIN),0),nvl(sum(HARD_RESERVED_BASE),0)from RRL_REMAINS where UID_POLETA=:lot_id and CELL=:cell_code",lot_id=lot,cell_code=origin);assert q.fetchone()==(0,0)
  q.execute("select count(*),nvl(sum(BASE_QTY),0)from RRL_WMS_RECEIPT_UNIT where CURRENT_UID=:lot_id and CURRENT_CELL=:cell_code and STOCK_STATUS='AVAILABLE'",lot_id=lot,cell_code=plan["to_cell"]);assert q.fetchone()==((2,2)if number==292 else(0,0))
  q.execute("select sum(r.REMAIN),sum(r.HARD_RESERVED_BASE)from RRL_REMAINS r join RRL_CELLS cell on cell.CELL=r.CELL where cell.WARE_ID=6667491");assert q.fetchone()==(20,20)
print("PASS301 originalTASK_COMPLETE wholeordinary+markedrecovery2 placement/outerrollback/replay/sameUID/Pconserved/no newcodes/protected20-20")
