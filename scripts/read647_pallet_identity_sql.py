exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor()
 q.execute("select TABLE_NAME,INDEX_NAME,COLUMN_NAME,COLUMN_POSITION from USER_IND_COLUMNS where TABLE_NAME in('RRL_CASE_CARRIER_LOT','RRL_WMS_RECEIPT_UNIT','RRL_WMS_HU_LINK')and COLUMN_POSITION<=2 order by TABLE_NAME,INDEX_NAME,COLUMN_POSITION")
 print("KEYS647",json.dumps(q.fetchall()))
 q.execute("select SQL_ID,round(ELAPSED_TIME/nullif(EXECUTIONS,0)/1000,3),round(BUFFER_GETS/nullif(EXECUTIONS,0),2),substr(SQL_TEXT,1,140)from V$SQL where PARSING_SCHEMA_NAME='RABAEV'and EXECUTIONS>0 and upper(SQL_TEXT)not like '%V$SQL%'and(upper(SQL_TEXT)like 'SELECT COUNT(*)%FROM RRL_CASE_CARRIER_LOT%'or upper(SQL_TEXT)like 'SELECT COUNT(*)%FROM RRL_WMS_HU_LINK%'or upper(SQL_TEXT)like '%QTY FROM RRL_WMS_RECEIPT_UNIT%')order by LAST_ACTIVE_TIME desc fetch first 5 rows only")
 print("SQL647",json.dumps(q.fetchall()))
