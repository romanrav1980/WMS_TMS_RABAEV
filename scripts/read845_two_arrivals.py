exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
ctx=json.loads(Path("tmp/context840.json").read_text(encoding="utf-8"))
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor()
 q.execute("select nvl(sum(r.REMAIN),0),nvl(sum(r.HARD_RESERVED_BASE),0)from RRL_REMAINS r join RRL_PALLETS p on p.UID_PALLET=r.UID_POLETA where p.ARTICUL=:a",a=ctx["article"])
 clean=q.fetchone();assert clean==(0,0),clean
 q.execute("select TASK_ID,STATUS,FACT_QTY from RRL_WAREHOUSE_TASK where TASK_ID in(:first_id,:second_id)order by TASK_ID",first_id=ctx["task"],second_id=ctx["second_task"])
 facts=q.fetchall();assert [(x[1],x[2])for x in facts]==[("DONE",20),("DONE",8)],facts
 q.execute("select NAME,TYPE,LINE,TEXT from USER_ERRORS where NAME not like 'BIN$%'");errors=q.fetchall();assert not errors,errors
 q.execute("select OBJECT_NAME,OBJECT_TYPE from USER_OBJECTS where STATUS='INVALID'and OBJECT_NAME not like 'BIN$%'");invalid=q.fetchall();assert not invalid,invalid
 q.execute("select SQL_ID,EXECUTIONS,round(ELAPSED_TIME/nullif(EXECUTIONS,0)/1000,3),round(BUFFER_GETS/nullif(EXECUTIONS,0),1),substr(SQL_TEXT,1,130)from V$SQL where PARSING_SCHEMA_NAME='RABAEV'and EXECUTIONS>0 and upper(SQL_TEXT)not like '%V$SQL%'and (upper(SQL_TEXT)like '%PALLET_RANK%'or upper(SQL_TEXT)like '%OWN TARGET COVERAGE DELIVERED%'or upper(SQL_TEXT)like '%SELECT DISTINCT RT.PICK_WAVE_ID%')order by LAST_ACTIVE_TIME desc fetch first 6 rows only")
 sql=q.fetchall()
 ctx.update(stage="TWO_ARRIVALS_PASS_OWN_CLEANED",facts=facts,clean=list(clean),errors=errors,invalid=invalid,sql=sql)
 Path("tmp/context845.json").write_text(json.dumps(ctx,indent=2,default=str),encoding="utf-8")
 print("845 PASS facts",facts,"ownP/H",clean,"SQL",sql)
