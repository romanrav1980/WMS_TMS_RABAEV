exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select COLUMN_NAME,DATA_TYPE from USER_TAB_COLUMNS where TABLE_NAME='RRL_WMS_RECEIPT_CODE'order by COLUMN_ID");print(q.fetchall())
 q.execute("select CASE_PICK_TASK_ID,STATUS,SHIPPED_OPERATION from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=1112");print(q.fetchall())
 q.execute("""select SQL_ID,EXECUTIONS,round(ELAPSED_TIME/nullif(EXECUTIONS,0)/1000,3),BUFFER_GETS,substr(SQL_TEXT,1,160)
 from V$SQL where PARSING_SCHEMA_NAME='RABAEV'and EXECUTIONS>0 and SQL_TEXT not like '%V$SQL%'and(SQL_TEXT like '%STORE_CASE%'or SQL_TEXT like '%CASE_VERSION+1%'or SQL_TEXT like '%CASE_CARRIER_LOT%C.LOT_UID%'or SQL_TEXT like '%RRL_STORE_RECEIPT_UNIT%'or SQL_TEXT like '%STARTED_AT_INSTANT AT TIME ZONE%')
 order by ELAPSED_TIME desc fetch first 7 rows only""");rows=q.fetchall();Path("tmp/382_slow_sql.json").write_text(json.dumps(rows,default=str),encoding="utf-8");print(json.dumps(rows,default=str))
