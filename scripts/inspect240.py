exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor()
 for table in ["RRL_WAREHOUSE_TASK","RRL_INTERWARE_PUT_PLAN","RRL_RECEIPT_SKU_RULE","RRL_RECEIPT_CELL_RULE"]:
  q.execute("select column_name,data_type from USER_TAB_COLUMNS where TABLE_NAME=:t order by COLUMN_ID",t=table);print(table,q.fetchall())
 q.execute("select NAME,TYPE from USER_DEPENDENCIES where REFERENCED_NAME='RRL_STOCK_INTERWARE_PUT'order by NAME,TYPE");print("PUT_DEPS",q.fetchall())
