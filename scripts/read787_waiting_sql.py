exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
ctx=json.loads(Path("tmp/context744.json").read_text(encoding="utf-8"));m=json.loads(Path("tmp/context773.json").read_text(encoding="utf-8"))
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor()
 q.execute("select COLUMN_NAME from USER_TAB_COLUMNS where TABLE_NAME='RRL_STOCK_OUTBOX'order by COLUMN_ID");print("OUTBOX_COLUMNS",q.fetchall())
 q.execute("""select SQL_ID,EXECUTIONS,round(ELAPSED_TIME/nullif(EXECUTIONS,0)/1000,3),round(BUFFER_GETS/nullif(EXECUTIONS,0),1),substr(SQL_TEXT,1,180)
 from V$SQL where PARSING_SCHEMA_NAME='RABAEV'and EXECUTIONS>0 and SQL_TEXT not like '%V$SQL%'
 and (upper(SQL_TEXT)like '%FROM RRL_ST_DEFER_WAIT_RUN%'or upper(SQL_TEXT)like '%FROM RRL_ST_DEFER_WAIT_PLAN%'or upper(SQL_TEXT)like '%FROM RRL_CUSTOMER_ORDER_FULFILLMENT F JOIN RRL_SBORKA_PALLETS%')
 order by ELAPSED_TIME/nullif(EXECUTIONS,0) desc fetch first 6 rows only""")
 print("WAIT_SQL",q.fetchall())
 q.execute("select RRL_STOCK_LOCK_API.resource_key('CONFIG','WAREHOUSE')from dual")
 print("CONFIG_KEY_PRESENT",q.fetchone()[0]is not None)
 q.execute("select NAME from USER_SOURCE where NAME='RRL_STOCK_TASK_PLAN'and TEXT like '%fence(v_p,%CONFIG%WAREHOUSE%6)%'");assert q.fetchall()==[]
 print("786 shared CONFIG fence installed; sorted ST/FF resource declarations retained. New independent two-session case not yet run.")
