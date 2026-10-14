exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("""select SQL_ID,EXECUTIONS,round(ELAPSED_TIME/nullif(EXECUTIONS,0)/1000,3),round(BUFFER_GETS/nullif(EXECUTIONS,0),2),substr(SQL_TEXT,1,150)from V$SQL where PARSING_SCHEMA_NAME='RABAEV'and EXECUTIONS>0 and upper(SQL_TEXT)not like '%V$SQL%'and(upper(SQL_TEXT)like '%SELECT W.PICK_WAVE_ID%'and upper(SQL_TEXT)like '%W.WAVE_CODE%'or upper(SQL_TEXT)like '%SELECT WARE_ID,UPPER(TRIM(USER_GROUP))%')order by LAST_ACTIVE_TIME desc fetch first 5 rows only""")
 print(json.dumps(q.fetchall(),ensure_ascii=True))
