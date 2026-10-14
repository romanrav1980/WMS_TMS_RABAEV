exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("""select SQL_ID,EXECUTIONS,round(ELAPSED_TIME/nullif(EXECUTIONS,0)/1000,3),round(BUFFER_GETS/nullif(EXECUTIONS,0),1),substr(SQL_TEXT,1,120)
 from V$SQL where PARSING_SCHEMA_NAME='RABAEV'and EXECUTIONS>0
 and(upper(SQL_TEXT)like 'SELECT T.ID,T.SHIPMENT_DATE,T.TRANSPORT%'or upper(SQL_TEXT)like 'SELECT DISTINCT P.TRANSTASK_ID,A.RAION,M.STORE_CODE%')
 order by ELAPSED_TIME/nullif(EXECUTIONS,0) desc fetch first 5 rows only""");print(q.fetchall())
 q.execute("select TABLE_NAME,COLUMN_NAME from USER_TAB_COLUMNS where TABLE_NAME like '%OUTBOX%' and COLUMN_NAME='OPERATION_ID'");print("OUTBOX_TABLES",q.fetchall())
