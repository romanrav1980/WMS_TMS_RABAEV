exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("""select SQL_ID,EXECUTIONS,round(ELAPSED_TIME/1000,3)TOTAL_MS,BUFFER_GETS,substr(SQL_TEXT,1,110)
 from V$SQL where PARSING_SCHEMA_NAME='RABAEV'and EXECUTIONS>0
 and(SQL_TEXT like 'SELECT COUNT(*)%RRL_TRACE_SENDER_AGG A JOIN RRL_TRACE_MANIFEST_USE%'
 or SQL_TEXT like 'SELECT A.UNITS_JSON,A.PROFILE_VERSION%RRL_TRACE_SENDER_AGG%'
 or SQL_TEXT like 'SELECT COUNT(*),JSON_ARRAYAGG(JSON_OBJECT(%V_SYSTEM_CODE%')
 order by ELAPSED_TIME desc fetch first 12 rows only""")
 result=q.fetchall();Path("tmp/slow310.json").write_text(json.dumps(result,indent=2),encoding="utf-8")
 print(json.dumps(result))

