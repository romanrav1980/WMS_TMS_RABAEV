exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("""select SQL_ID,EXECUTIONS,round(ELAPSED_TIME/nullif(EXECUTIONS,0)/1000,3),round(BUFFER_GETS/nullif(EXECUTIONS,0),1),substr(SQL_TEXT,1,210)from V$SQL
 where PARSING_SCHEMA_NAME='RABAEV'and EXECUTIONS>0 and SQL_TEXT not like '%V$SQL%'
 and(SQL_TEXT like '%RRL_TRACE_AGG_BLOCK%'or SQL_TEXT like '%RRL_TRACE_AGG_INVALIDATION%'or SQL_TEXT like '%PARENT_ID%RRL_TRACE_SENDER%')
 order by ELAPSED_TIME desc fetch first 8 rows only""")
 print(json.dumps(q.fetchall()))
