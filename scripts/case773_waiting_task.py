exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
from app.modules.platform.public import read_oracle_json
ctx=json.loads(Path("tmp/context744.json").read_text(encoding="utf-8"));probe=json.loads(Path("tmp/context753.json").read_text(encoding="utf-8"))
path=Path("tmp/context773.json");assert not path.exists(),"773 already used; read or replay stored context instead"
plan_op="WAIT773:"+ctx["tag"];move_op="WAITMOVE773:"+ctx["tag"]
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor()
 q.execute("select PICKED_WAREHOUSE_TASK_ID,PICKED_OPERATION_ID,PICKED_AT,PICKED_BY,FACT_QTY,FACT_UOM,PICKED_STOCK_VERSION from RRL_CUSTOMER_ORDER_FULFILLMENT where FULFILLMENT_ID=:id",id=ctx["ids"][9]);before=q.fetchone()
 q.execute("select REMAIN,HARD_RESERVED_BASE from RRL_REMAINS where UID_POLETA=:p_uid and CELL=:cell",p_uid=ctx["lot"],cell=ctx["dst"]);assert q.fetchone()==(3,3)
 def plan():
  out=q.var(oracledb.DB_TYPE_CLOB);q.callproc("RRL_ST_DEFER_WAIT_API.plan_waiting",[plan_op,ctx["defer_operation"],"admin",out]);return read_oracle_json(out.getvalue())
 trial=plan();assert len(trial["tasks"])==1;c.rollback()
 q.execute("select count(*)from RRL_ST_DEFER_WAIT_RUN where OPERATION_ID=:op",op=plan_op);assert q.fetchone()==(0,)
 result=plan();task=result["tasks"][0]["task_id"];c.commit()
 assert plan()==result;c.rollback()
 record={"plan_operation":plan_op,"plan_result":result,"task":task,"move_operation":move_op,"stage":"PLANNED","source_context":744}
 path.write_text(json.dumps(record,ensure_ascii=True),encoding="utf-8")
 request={"contract_version":2,"operation_id":move_op,"command_type":"TASK_COMPLETE","actor":"admin","source":{"task_id":task},"lines":[],"units":[],
 "metadata":{"fact_qty":"3","scanned_pallet":ctx["lot"],"scanned_from_cell":ctx["dst"],"scanned_to_cell":probe["cell"]}}
 def post(body):
  out=q.var(oracledb.DB_TYPE_CLOB);q.callproc("RRL_STOCK_POSTING_API.prepare_command",[json.dumps(body,sort_keys=True,separators=(",",":")),"admin",out,None])
  if out.getvalue()is None:q.callproc("RRL_STOCK_POSTING_API.execute_prepared",[out])
  return read_oracle_json(out.getvalue())
 record["move_request"]=request;path.write_text(json.dumps(record),encoding="utf-8")
 try:
  moved=post(request);assert moved["status"]=="DONE"
  q.execute("select REMAIN,HARD_RESERVED_BASE from RRL_REMAINS where UID_POLETA=:p_uid and CELL=:cell",p_uid=ctx["lot"],cell=probe["cell"]);assert q.fetchone()==(3,3)
 finally:c.rollback();q.callproc("RRL_STOCK_POSTING_API.reset_connection")
 q.execute("select STATUS from RRL_WAREHOUSE_TASK where TASK_ID=:id",id=task);assert q.fetchone()==("PLANNED",)
 q.execute("select REMAIN,HARD_RESERVED_BASE from RRL_REMAINS where UID_POLETA=:p_uid and CELL=:cell",p_uid=ctx["lot"],cell=ctx["dst"]);assert q.fetchone()==(3,3)
 moved=post(request);c.commit()
 record["move_result"]=moved;record["stage"]="DONE";path.write_text(json.dumps(record),encoding="utf-8")
 assert post(request)==moved;c.rollback()
 q.execute("select PICKED_WAREHOUSE_TASK_ID,PICKED_OPERATION_ID,PICKED_AT,PICKED_BY,FACT_QTY,FACT_UOM,PICKED_STOCK_VERSION from RRL_CUSTOMER_ORDER_FULFILLMENT where FULFILLMENT_ID=:id",id=ctx["ids"][9]);after=q.fetchone()
 assert after[:6]==before[:6] and after[6]!=before[6],(before,after)
 q.execute("select STOCK_VERSION from RRL_REMAINS where UID_POLETA=:p_uid and CELL=:cell",p_uid=ctx["lot"],cell=probe["cell"]);assert q.fetchone()==(after[6],)
 q.execute("select SYNC_STATUS from RRL_WAREHOUSE_TASK_SYNC where TASK_ID=:id",id=task);assert q.fetchone()==("SYNCED",)
 q.execute("select sum(REMAIN),sum(HARD_RESERVED_BASE)from RRL_REMAINS where UID_POLETA=:p_uid",p_uid=ctx["lot"]);assert q.fetchone()==(3,3)
 print("773 PASS native plan rollback/exact replay + original ROOT move rollback/commit/replay; P3/H3 and pick facts preserved; current binding updated; task SYNCED")
