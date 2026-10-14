exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select SQL_ID,round(ELAPSED_TIME/nullif(EXECUTIONS,0)/1000,3),round(BUFFER_GETS/nullif(EXECUTIONS,0),2),substr(SQL_TEXT,1,120)from V$SQL where PARSING_SCHEMA_NAME='RABAEV'and EXECUTIONS>0 and upper(SQL_TEXT)not like '%V$SQL%'and(dbms_lob.instr(SQL_FULLTEXT,'MAPPED_COUNT')>0 or(upper(SQL_TEXT)like '%VODITEL_ID=:DRIVER_ID%'and upper(SQL_TEXT)like '%RRL_TT_OPERATIONS%'))order by LAST_ACTIVE_TIME desc fetch first 4 rows only")
 print("SQL657",json.dumps(q.fetchall()))
