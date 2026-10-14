exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor()
 for name in ("RRL_STOCK_TRANSFER_CORE","RRL_STOCK_SHIPPING_CORE","RRL_STOCK_FULFILLMENT_FACT"):
  q.execute("select TEXT from USER_SOURCE where NAME=:n and TYPE='PACKAGE BODY'order by LINE",n=name)
  Path("tmp/768_"+name.lower()+".sql").write_text("create or replace "+"".join(x[0]for x in q)+"/\n",encoding="utf-8")
 q.execute("select NAME,LINE,TEXT from USER_SOURCE where NAME='RRL_STOCK_METADATA_TX' and TYPE='PACKAGE BODY' and (upper(TEXT)like '%CONFIG%'or upper(TEXT)like '%REQUEST%'or upper(TEXT)like '%LOCK%')order by LINE")
 for n,l,t in q:print(l,t.strip()[:260])
 q.execute("select SQL_ID,EXECUTIONS,round(ELAPSED_TIME/nullif(EXECUTIONS,0)/1000,3),round(BUFFER_GETS/nullif(EXECUTIONS,0),1) from V$SQL where PARSING_SCHEMA_NAME='RABAEV' and upper(SQL_TEXT) like 'SELECT COUNT(*)%RRL_CELLS C%' and upper(SQL_TEXT)like '%C.EXPEDITION_GROUP IS NULL%' and EXECUTIONS>0")
 print("WAIT_CELL_SQL",q.fetchall())
