exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
ctx=json.loads(Path("tmp/context840.json").read_text(encoding="utf-8"))
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor()
 q.execute("select PICK_WAVE_REPLENISH_TASK_ID,PARENT_REPLENISH_TASK_ID,STATUS,PALLET_UID,SOURCE_CELL_CODE,TARGET_CELL_CODE,QTY,DEMAND_BASE_QTY,SOURCE_RESERVATION_ID,REPLENISHMENT_QTY_MODE,WAIT_REASON,RESERVE_OPERATION_ID from RRL_PICK_WAVE_REPLENISH_TASK where PICK_WAVE_ID=:w order by PICK_WAVE_REPLENISH_TASK_ID",w=ctx["wave"]);rows=q.fetchall();print("RT",rows)
 for rt in rows:
  if rt[-1]:
   q.execute("select STATE,RESOLVED_PLAN_JSON from RRL_STOCK_OPERATION where OPERATION_ID=:op",op=rt[-1])
   result=q.fetchone()
   if result and result[1]:
    plan=json.loads(result[1].read()if hasattr(result[1],"read")else result[1]);print("PLAN",rt[0],result[0],json.dumps(plan.get("domain"),ensure_ascii=True)[:6500])
