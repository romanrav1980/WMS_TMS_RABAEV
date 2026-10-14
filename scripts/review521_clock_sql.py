exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("""select SQL_ID,EXECUTIONS,round(ELAPSED_TIME/nullif(EXECUTIONS,0)/1000,3),
 round(BUFFER_GETS/nullif(EXECUTIONS,0),2),substr(SQL_TEXT,1,150)
 from V$SQL where PARSING_SCHEMA_NAME='RABAEV'and EXECUTIONS>0 and SQL_TEXT not like '%V$SQL%'
 and(upper(SQL_TEXT)like '%FROM RRL_HU_PACK_CYCLE%'or upper(SQL_TEXT)like '%RRL_LOG_COST_SOURCE_CLAIM%'
 or upper(SQL_TEXT)like '%RRL_BOX_ASSEMBLY_READ.CLOCKS_JSON%')
 order by ELAPSED_TIME desc fetch first 8 rows only""")
 print(json.dumps(q.fetchall(),default=str))
