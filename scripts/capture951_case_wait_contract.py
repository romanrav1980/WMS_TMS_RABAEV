exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor()
 for name in ("RRL_STOCK_CASE_PICK_CMD","RRL_CASE_TASK_ACCESS"):
  q.execute("select TEXT from USER_SOURCE where NAME=:n and TYPE='PACKAGE BODY'order by LINE",n=name)
  Path("tmp/951_"+name.lower()+".sql").write_text("".join(r[0]for r in q),encoding="utf-8")
 q.execute("select TRIGGER_NAME,TABLE_NAME from USER_TRIGGERS where TABLE_NAME in('RRL_WAREHOUSE_TASK','RRL_WAREHOUSE_TASK_SYNC','RRL_CUSTOMER_ORDER_FULFILLMENT')")
 for name,table in q.fetchall():
  q.execute("select TEXT from USER_SOURCE where NAME=:n and TYPE='TRIGGER'order by LINE",n=name)
  Path("tmp/951_"+name.lower()+".sql").write_text("".join(r[0]for r in q),encoding="utf-8");print(name,table)
 q.execute("select COLUMN_NAME,DATA_TYPE from USER_TAB_COLUMNS where TABLE_NAME='RRL_ST_DEFER_WAIT_PLAN'order by COLUMN_ID");print("WAIT_PLAN",q.fetchall())
 q.execute("select CASE_PICK_TASK_ID,STATUS,CURRENT_CELL,LEGACY_SBORKA_PALLET_ID from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID in(1031,1032)");print("RETAINED",q.fetchall())
