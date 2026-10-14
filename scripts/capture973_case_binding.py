exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor()
 for name in ("RRL_STOCK_CASE_MOVE_CMD","RRL_ST_DEFER_CASE_WAIT"):
  for typ in("PACKAGE","PACKAGE BODY"):
   q.execute("select TEXT from USER_SOURCE where NAME=:n and TYPE=:t order by LINE",n=name,t=typ)
   Path("tmp/973_"+name.lower()+"_"+typ.lower().replace(" ","_")+".sql").write_text("create or replace "+"".join(r[0]for r in q)+"\n/\n",encoding="utf-8")
 print("Captured current CASE mover and current waiting finisher")
 q.execute("select c.CASE_PICK_TASK_ID,c.CURRENT_CELL,c.CONTENT_VERSION,f.PICKED_CONTENT_VERSION,f.STATUS from RRL_CASE_PICK_TASK c join RRL_CUSTOMER_ORDER_FULFILLMENT f on f.PICKED_CASE_TASK_ID=c.CASE_PICK_TASK_ID where c.CASE_PICK_TASK_ID in(1129,1130)")
 print("BOUND",q.fetchall())
