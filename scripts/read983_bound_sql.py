exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select sql_id,executions,round(elapsed_time/1000/nullif(executions,0),3),round(buffer_gets/nullif(executions,0),1)from V$SQL where(sql_text like 'SELECT%RRL_CUSTOMER_ORDER_FULFILLMENT%LEGACY_SBORKA_PALLET_ID%'or sql_text like 'SELECT%RRL_ST_DEFER_WAIT_PLAN%CASE_TASK_ID%')and executions>0 order by last_active_time desc fetch first 8 rows only")
 evidence=q.fetchall();Path("tmp/bound983_sql.json").write_text(json.dumps(evidence),encoding="utf-8");print(evidence)
 q.execute("select SOURCE_TASK_ID,TASK_ID,SOURCE_DOC_TYPE from RRL_WAREHOUSE_TASK where TASK_ID=(select max(TASK_ID)from RRL_ST_DEFER_WAIT_PLAN where CASE_TASK_ID=1129)");print("CURRENT_TASK",q.fetchone())
