exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor()
 for name in ("RRL_ST_DEFER_API","RRL_ST_DEFER_WAIT_API","RRL_STOCK_CASE_MOVE_CMD","RRL_STOCK_POSTING_API","RRL_STOCK_REQUEST_COMPILER","RRL_STOCK_PLAN_HELPER","RRL_WAREHOUSE_TASK_ACCESS"):
  for typ in ("PACKAGE","PACKAGE BODY"):
   q.execute("select TEXT from USER_SOURCE where NAME=:n and TYPE=:t order by LINE",n=name,t=typ)
   body="".join(r[0]for r in q)
   if body:Path("tmp/949_"+name.lower()+"_"+typ.lower().replace(" ","_")+".sql").write_text("create or replace "+body+"\n/\n",encoding="utf-8");print(name,typ,len(body))
 q.execute("select COLUMN_NAME,DATA_TYPE from USER_TAB_COLUMNS where TABLE_NAME='RRL_CASE_PICK_TASK' order by COLUMN_ID")
 print("CASE_COLUMNS",q.fetchall())
