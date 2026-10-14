exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("""select SQL_ID,EXECUTIONS,round(ELAPSED_TIME/nullif(EXECUTIONS,0)/1000,3),round(BUFFER_GETS/nullif(EXECUTIONS,0),1),substr(SQL_TEXT,1,190)
 from V$SQL where PARSING_SCHEMA_NAME='RABAEV'and EXECUTIONS>0 and SQL_TEXT not like '%V$SQL%'
 and(SQL_TEXT like 'SELECT%RETURN_BASIS%'or SQL_TEXT like 'select%RETURN_BASIS%'or SQL_TEXT like '%STORE_RETURN_SOURCE_DISPOSITION_QUANTITY%'or SQL_TEXT like 'INSERT INTO RRL_STORE_RETURN_APPROVAL%')
 order by ELAPSED_TIME desc fetch first 8 rows only""");print(json.dumps(q.fetchall()))
