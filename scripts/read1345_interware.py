exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor()
 q.execute("select RESULT_JSON from RRL_IW_GROUP_PLAN where OPERATION_ID='GROUP672.PLAN:6207f7b382'")
 v=q.fetchone()[0];print(v.read()if hasattr(v,"read")else v)
 q.execute("""select SQL_ID,EXECUTIONS,round(ELAPSED_TIME/nullif(EXECUTIONS,0)/1000,3),BUFFER_GETS,substr(SQL_TEXT,1,130)from V$SQL where PARSING_SCHEMA_NAME='RABAEV'and EXECUTIONS>0 and SQL_TEXT not like '%V$SQL%'and(SQL_TEXT like '%from RRL_IW_GROUP_PLAN p left join%'or SQL_TEXT like '%from RRL_INTERWARE_PLAN p%')order by ELAPSED_TIME/nullif(EXECUTIONS,0)desc fetch first 5 rows only""")
 print(json.dumps(q.fetchall(),default=str))
