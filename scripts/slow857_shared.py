exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("""select SQL_ID,EXECUTIONS,round(ELAPSED_TIME/nullif(EXECUTIONS,0)/1000,3),round(BUFFER_GETS/nullif(EXECUTIONS,0),2),substr(SQL_TEXT,1,200) from V$SQL where PARSING_SCHEMA_NAME='RABAEV' and EXECUTIONS>0 and upper(SQL_TEXT)not like '%V$SQL%' and(upper(SQL_TEXT)like '%WITH CANDIDATES AS%' or upper(SQL_TEXT)like '%PENDING.PICK_WAVE_REPLENISH_TASK_ID%' or upper(SQL_TEXT)like '%RT.PARENT_REPLENISH_TASK_ID IS NOT NULL%')order by LAST_ACTIVE_TIME desc fetch first 8 rows only""")
 print(json.dumps(q.fetchall(),ensure_ascii=True))
