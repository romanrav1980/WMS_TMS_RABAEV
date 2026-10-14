exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("""select SQL_ID,EXECUTIONS,round(ELAPSED_TIME/nullif(EXECUTIONS,0)/1000,3),substr(SQL_TEXT,1,130)from V$SQL where PARSING_SCHEMA_NAME='RABAEV'and EXECUTIONS>0 and SQL_TEXT like 'select p.OPERATION_ID,p.SOURCE_LOAD_OPERATION_ID,p.SOURCE_ST_ID%'order by LAST_ACTIVE_TIME desc fetch first 3 rows only""")
 for row in q:print(json.dumps(row,ensure_ascii=True))
