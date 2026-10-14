exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor()
 for name in ["RRL_STOCK_HU_SHIP_CMD","RRL_STOCK_SHIPPING_CORE"]:
  q.execute("select TEXT from USER_SOURCE where NAME=:pkg and TYPE='PACKAGE BODY'order by LINE",pkg=name)
  body="".join(r[0]for r in q);Path("tmp/312_"+name.lower()+".sql").write_text(body,encoding="utf-8")
 q.execute("select SQL_ID,EXECUTIONS,round(ELAPSED_TIME/1000,3),BUFFER_GETS from V$SQL where PARSING_SCHEMA_NAME='RABAEV'and EXECUTIONS>0 and SQL_TEXT like '%RRL_SAP_TRACE_AGG A JOIN RRL_SAP_PALLET_RECEIPT%'and SQL_TEXT not like '%V$SQL%'")
 print("SQL311 proof",q.fetchall())
