exec(open('scripts/ni063_slow_queries.py',encoding='utf-8').read().split('with oracledb.connect',1)[0])
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn) as c:
 q=c.cursor();q.execute("select COLUMN_NAME from USER_TAB_COLUMNS where TABLE_NAME='RRL_EVENT_OUTBOX' order by COLUMN_ID");print('OUTBOX_COLUMNS',[r[0]for r in q])
 q.execute("select SQL_ID,EXECUTIONS,round(ELAPSED_TIME/nullif(EXECUTIONS,0)/1000,3),round(BUFFER_GETS/nullif(EXECUTIONS,0),1),substr(SQL_TEXT,1,100) from V$SQL where PARSING_SCHEMA_NAME='RABAEV'and EXECUTIONS>0 and upper(SQL_TEXT)like '%FROM RRL_WAREHOUSE_TASK%' order by LAST_ACTIVE_TIME desc fetch first 4 rows only");print('TASK_SQL',q.fetchall())
