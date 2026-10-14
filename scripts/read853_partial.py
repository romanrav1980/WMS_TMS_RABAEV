exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
ctx=json.loads(Path("tmp/context850.json").read_text(encoding="utf-8"))
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn) as c:
 q=c.cursor()
 for label,sql,params in [
 ("TASKS","select TASK_ID,SOURCE_TASK_ID,STATUS,UID_PALLET,QTY,FACT_QTY from RRL_WAREHOUSE_TASK where TASK_SOURCE='WAVE' and SOURCE_DOC_ID=:w",{"w":ctx["wave"]}),
 ("RT","select PICK_WAVE_REPLENISH_TASK_ID,PARENT_REPLENISH_TASK_ID,STATUS,DEMAND_BASE_QTY,PALLET_UID,SOURCE_RESERVATION_ID,WAIT_REASON from RRL_PICK_WAVE_REPLENISH_TASK where PICK_WAVE_ID=:w",{"w":ctx["wave"]}),
 ("STOCK","select REMAIN,HARD_RESERVED_BASE from RRL_REMAINS where ARTICUL=:a",{"a":ctx["article"]}),
 ("MIGRATION","select MIGRATION_ID from RRL_SCHEMA_MIGRATION where MIGRATION_ID like '%852%'",{})]:
  try:q.execute(sql,params);print(label,q.fetchall())
  except Exception as e:print(label,str(e))
