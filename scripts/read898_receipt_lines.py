exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor()
 q.execute("select COLUMN_NAME,DATA_TYPE from USER_TAB_COLUMNS where TABLE_NAME='RRL_SAP_PALLET_RECEIPT'order by COLUMN_ID");print("COLUMNS",q.fetchall())
 q.execute("select ORDER_ID,ARTICUL,count(*)from RRL_SAP_SUPPLY_LINE group by ORDER_ID,ARTICUL having count(*)>1 fetch first 5 rows only");print("DUPLICATE_SKU_LINES",q.fetchall())
 q.execute("select NAME,LINE,TEXT from USER_SOURCE where TYPE='PACKAGE BODY'and(TEXT like '%POSTED_BASE_QTY%'or TEXT like '%RRL_SAP_PALLET_RECEIPT%')and NAME like '%REVER%'order by NAME,LINE");print("REVERSAL",q.fetchall()[:35])
