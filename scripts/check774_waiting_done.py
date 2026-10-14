exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
from app.modules.platform.public import read_oracle_json
ctx=json.loads(Path("tmp/context744.json").read_text(encoding="utf-8"));probe=json.loads(Path("tmp/context753.json").read_text(encoding="utf-8"));m=json.loads(Path("tmp/context773.json").read_text(encoding="utf-8"));assert m["stage"]=="DONE"
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();out=q.var(oracledb.DB_TYPE_CLOB)
 q.callproc("RRL_STOCK_POSTING_API.prepare_command",[json.dumps(m["move_request"],sort_keys=True,separators=(",",":")),"admin",out,None])
 assert read_oracle_json(out.getvalue())==m["move_result"]
 c.rollback();q.callproc("RRL_STOCK_POSTING_API.reset_connection")
 q.execute("select REMAIN,HARD_RESERVED_BASE,STOCK_VERSION from RRL_REMAINS where UID_POLETA=:p_uid and CELL=:cell",p_uid=ctx["lot"],cell=probe["cell"]);p,h,ver=q.fetchone();assert(p,h)==(3,3)
 q.execute("select STATUS,FACT_QTY,FACT_UOM,PICKED_WAREHOUSE_TASK_ID,PICKED_OPERATION_ID,PICKED_STOCK_VERSION from RRL_CUSTOMER_ORDER_FULFILLMENT where FULFILLMENT_ID=:id",id=ctx["ids"][9]);ff=q.fetchone();assert ff[0:4]==("PICKED",3,"EA",ctx["ids"][7])and ff[5]==ver
 q.execute("select STATUS from RRL_WAREHOUSE_TASK where TASK_ID=:id",id=ctx["ids"][7]);assert q.fetchone()==("DONE",)
 q.execute("select STATUS,FACT_QTY from RRL_WAREHOUSE_TASK where TASK_ID=:id",id=m["task"]);assert q.fetchone()==("DONE",3)
 q.execute("select SYNC_STATUS from RRL_WAREHOUSE_TASK_SYNC where TASK_ID=:id",id=m["task"]);assert q.fetchone()==("SYNCED",)
 q.execute("select count(*),count(distinct PHYSICAL_UNIT_KEY)from RRL_WMS_RECEIPT_UNIT where CURRENT_UID=:p_uid and CURRENT_CELL=:cell and STOCK_STATUS!='ISSUED'",p_uid=ctx["lot"],cell=probe["cell"]);assert q.fetchone()==(3,3)
 q.execute("select count(*)from RRL_WMS_RECEIPT_CODE where UID_PALLET=:p_uid",p_uid=ctx["lot"]);assert q.fetchone()==(6,)
 q.execute("select count(*)from RRL_STOCK_OPERATION where OPERATION_ID=:op",op=m["move_operation"]);assert q.fetchone()==(1,)
 out=q.var(oracledb.DB_TYPE_CLOB);q.callproc("RRL_ST_DEFER_WAIT_API.plan_waiting",[m["plan_operation"],ctx["defer_operation"],"admin",out]);assert read_oracle_json(out.getvalue())==m["plan_result"];c.rollback()
 try:q.execute("update RRL_ST_DEFER_WAIT_PLAN set BASE_QTY=BASE_QTY where TASK_ID=:id",id=m["task"])
 except oracledb.DatabaseError as e:assert "DEFER_WAIT_PLAN_APPEND_ONLY" in str(e)
 else:raise AssertionError("immutable plan accepted update")
 c.rollback()
 print("774 PASS committed773 exact replay/source3-H3/current binding/original DONE pick/3physical6codes/taskDONE-SYNCED/immutable plan")
