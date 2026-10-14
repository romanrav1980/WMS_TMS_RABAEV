exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor()
 q.execute("select TABLE_NAME,COLUMN_NAME,DATA_TYPE from USER_TAB_COLUMNS where TABLE_NAME in('RRL_SAP_RECEIPT','RRL_PALLETS')and(TABLE_NAME='RRL_SAP_RECEIPT'or COLUMN_NAME like '%NAKLAD%'or COLUMN_NAME like '%ROW%')order by TABLE_NAME,COLUMN_ID");print("COLUMNS",q.fetchall())
 q.execute("select NAME,LINE,TEXT from USER_SOURCE where NAME in('RRL_STOCK_RECEIPT_PLAN','RRL_STOCK_RECEIPT_CORE','RRL_SAP_RECEIPT_API','RRL_SAP_RECEIPT_API_V2')and TYPE='PACKAGE BODY'and(upper(TEXT)like '%SUM(%'or upper(TEXT)like '%ACCEPTED%'or upper(TEXT)like '%LINE_NUMBER%'or upper(TEXT)like '%RRL_SAP_RECEIPT%')order by NAME,LINE");print("SOURCE",q.fetchall()[:40])
