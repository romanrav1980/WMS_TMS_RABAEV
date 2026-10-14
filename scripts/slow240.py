exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select SQL_ID,EXECUTIONS,round(ELAPSED_TIME/nullif(EXECUTIONS,0)/1000,3),substr(SQL_TEXT,1,150)from V$SQL where PARSING_SCHEMA_NAME='RABAEV'and EXECUTIONS>0 and SQL_TEXT not like '%V$SQL%'and(SQL_TEXT like 'SELECT *FROM RRL_INTERWARE_THERMAL_FACT%'or SQL_TEXT like 'INSERT INTO RRL_INTERWARE_THERMAL_FACT%'or SQL_TEXT like 'SELECT TEMP_MIN,TEMP_MAX%RRL_RECEIPT_CELL_RULE%'or SQL_TEXT like 'SELECT TEMP_DECISION_OPERATION_ID,TASK_TEMP_MIN,TASK_TEMP_MAX%')order by ELAPSED_TIME desc fetch first 7 rows only")
 for row in q:print(json.dumps(row,ensure_ascii=True))
