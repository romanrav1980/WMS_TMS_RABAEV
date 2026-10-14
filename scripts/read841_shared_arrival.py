exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor()
 q.execute("select TEXT from USER_SOURCE where NAME='RRL_STOCK_REPL_BIND'and TYPE='PACKAGE BODY'order by LINE")
 lines=''.join(x[0]for x in q).splitlines()
 Path("tmp/841_bind_body.sql").write_text('\n'.join(lines),encoding="utf-8")
 for i,line in enumerate(lines):
  if any(x in line for x in ("SHARED","RRL_PICK_WAVE_REPLENISH_TASK","p_task.TASK_ID")):
   print('\n'.join(lines[max(0,i-2):min(len(lines),i+8)]))
 q.execute("select t.TASK_ID,t.SOURCE_TASK_ID,rt.PICK_TASK_ID,rt.STATUS,rt.QTY,rt.DEMAND_BASE_QTY,rt.SOURCE_RESERVATION_ID,rt.RESERVE_OPERATION_ID from RRL_WAREHOUSE_TASK t join RRL_PICK_WAVE_REPLENISH_TASK rt on rt.PICK_WAVE_REPLENISH_TASK_ID=t.SOURCE_TASK_ID where t.TASK_ID in(1082,1083)")
 print("DUPLICATE_HISTORY",q.fetchall())
