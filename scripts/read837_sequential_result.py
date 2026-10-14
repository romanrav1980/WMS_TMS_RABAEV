exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
ctx=json.loads(Path("tmp/context835.json").read_text(encoding="utf-8"))
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor()
 q.execute("select NAME,TYPE,LINE,TEXT from USER_ERRORS where NAME not like 'BIN$%'")
 errors=q.fetchall();assert not errors,errors
 q.execute("select OBJECT_NAME,OBJECT_TYPE from USER_OBJECTS where STATUS='INVALID'and OBJECT_NAME not like 'BIN$%'")
 invalid=q.fetchall();assert not invalid,invalid
 q.execute("select nvl(sum(r.REMAIN),0),nvl(sum(r.HARD_RESERVED_BASE),0) from RRL_REMAINS r join RRL_PALLETS p on p.UID_PALLET=r.UID_POLETA where p.ARTICUL=:a",a=ctx["article"])
 clean=q.fetchone();assert clean==(0,0),clean
 q.execute("select STATUS,FACT_QTY from RRL_WAREHOUSE_TASK where TASK_ID=:id",id=ctx["task"]);task=q.fetchone();assert task==("DONE",20),task
 q.execute("select STATUS,DEMAND_BASE_QTY from RRL_PICK_WAVE_REPLENISH_TASK where PICK_WAVE_REPLENISH_TASK_ID=:id",id=ctx["next_rt"]);nextrow=q.fetchone();assert nextrow==("CANCELLED",0),nextrow
 q.execute("select SQL_ID,EXECUTIONS,round(ELAPSED_TIME/nullif(EXECUTIONS,0)/1000,3),round(BUFFER_GETS/nullif(EXECUTIONS,0),1),substr(SQL_TEXT,1,170) from V$SQL where PARSING_SCHEMA_NAME='RABAEV'and EXECUTIONS>0 and LAST_ACTIVE_TIME>sysdate-10/1440 and upper(SQL_TEXT)not like '%V$SQL%'and (upper(SQL_TEXT)like '%RRL_STOCK_RESERVATION%'or upper(SQL_TEXT)like '%RRL_REMAINS%')order by ELAPSED_TIME/nullif(EXECUTIONS,0)desc fetch first 5 rows only")
 slow=q.fetchall();print("SLOW",slow)
 ctx.update(stage="PASS_OWN_CLEANED",clean_stock=list(clean),task_status=task[0],task_fact=str(task[1]),next_status=nextrow[0],native_errors=errors,native_invalid=invalid,sql_decision="Retain bounded owner/target201 and ordered stock closure; no index without measured plan regression",slow_sql=slow)
 Path("tmp/context837.json").write_text(json.dumps(ctx,indent=2,default=str),encoding="utf-8")
print("837 PASS native VALID; first taskDONE20; original continuation fulfilled; own P/H0")
