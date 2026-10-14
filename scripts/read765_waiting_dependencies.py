exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor()
 q.execute("select NAME,LINE,TEXT from USER_SOURCE where TYPE='PACKAGE BODY' and (upper(TEXT)like '%PICKED_STOCK_VERSION%' or upper(TEXT)like '%PICKED_OPERATION_ID%') order by NAME,LINE")
 for row in q:print(row[0],row[1],row[2].strip()[:360])
 q.execute("select TABLE_NAME,COLUMN_NAME from USER_TAB_COLUMNS where TABLE_NAME in('RRL_SHIPMENT_PICK_BIND','RRL_CUSTOMER_ORDER_FULFILLMENT','RRL_ST_DEFER_DECISION') order by TABLE_NAME,COLUMN_ID")
 print(q.fetchall())
 q.execute("select SQL_ID,EXECUTIONS,round(ELAPSED_TIME/nullif(EXECUTIONS,0)/1000,3),round(BUFFER_GETS/nullif(EXECUTIONS,0),1) from V$SQL where PARSING_SCHEMA_NAME='RABAEV' and upper(SQL_TEXT)like 'SELECT COUNT(*)%RRL_CELLS C%DEFER_WAIT_CELL%' and EXECUTIONS>0")
 print("WAIT_CELL_SQL",q.fetchall())
