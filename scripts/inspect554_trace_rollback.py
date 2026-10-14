exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor()
 q.execute("select COLUMN_NAME from USER_TAB_COLUMNS where TABLE_NAME='RRL_STOCK_OPERATION'and DATA_TYPE='CLOB'order by COLUMN_ID");print("COMMAND_COLUMNS",q.fetchall())
 q.execute("select OBJECT_NAME,ARGUMENT_NAME,POSITION,DATA_TYPE,IN_OUT from USER_ARGUMENTS where PACKAGE_NAME='RRL_STOCK_POSTING_API'and OBJECT_NAME like 'POST%'order by OBJECT_NAME,POSITION");print("POST_ARGS",q.fetchall())
 q.execute("""select SQL_ID,EXECUTIONS,round(ELAPSED_TIME/nullif(EXECUTIONS,0)/1000,3),round(BUFFER_GETS/nullif(EXECUTIONS,0),2)
 from V$SQL where PARSING_SCHEMA_NAME='RABAEV'and EXECUTIONS>0 and upper(SQL_TEXT)not like '%V$SQL%'
 and(upper(SQL_TEXT)like '%FROM RRL_TARE_DAMAGE_POSITION%'or upper(SQL_TEXT)like '%FROM RRL_TARE_DAMAGE_ORIGIN%'or upper(SQL_TEXT)like '%RRL_TARE_STORE_DEBT%')
 order by LAST_ACTIVE_TIME desc,ELAPSED_TIME desc fetch first 5 rows only""");print("SQL554",json.dumps(q.fetchall()))
