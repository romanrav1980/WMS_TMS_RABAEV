exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor()
 for table in("RRL_CUSTOMER_ORDER_FULFILLMENT_LINE","RRL_CASE_PICK_TASK","RRL_WAREHOUSE_TASK"):
  q.execute("select COLUMN_NAME from USER_TAB_COLUMNS where TABLE_NAME=:t order by COLUMN_ID",t=table);print(table,q.fetchall())
