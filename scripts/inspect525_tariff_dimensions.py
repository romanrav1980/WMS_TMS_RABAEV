exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor()
 for table in ["RRL_STORE_RECEIPT_FACT","RRL_TRANSPORT_TYPE"]:
  q.execute("select COLUMN_NAME,DATA_TYPE from USER_TAB_COLUMNS where TABLE_NAME=:table_name order by COLUMN_ID",table_name=table)
  print(table,json.dumps(q.fetchall()))
 q.execute("select NAME,TYPE from USER_DEPENDENCIES where REFERENCED_NAME='RRL_TRANSPORT_PRICE'order by NAME")
 print("PRICE_DEPENDENCIES",json.dumps(q.fetchall()))
 q.execute("select count(*),count(distinct ID)from RRL_TRANSPORT_PRICE");print("PRICE_KEYS",q.fetchone())
