exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
names=("RRL_ST_DEFER_CASE_WAIT","RRL_ST_DEFER_WAIT_API","RRL_ST_DEFER_API","RRL_ST_DEFER_PHYSICAL","RRL_STOCK_HU_TASK","RRL_HU_TASK_PLAN_GUARD","RRL_STOCK_HU_CMD","RRL_STOCK_POSTING_API")
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn) as c:
 c.call_timeout=10000;q=c.cursor()
 for n in names:
  for t in("PACKAGE","PACKAGE BODY"):
   q.execute("select TEXT from USER_SOURCE where NAME=:n and TYPE=:t order by LINE",n=n,t=t)
   body="".join(r[0]for r in q)
   if not body:continue
   Path("tmp/1051_"+n.lower()+"_"+t.lower().replace(" ","_")+".sql").write_text("create or replace "+body+"\n/\n",encoding="utf-8")
   print(n,t,len(body))
 q.execute("select OBJECT_NAME,OBJECT_TYPE from USER_OBJECTS where STATUS='INVALID' and OBJECT_NAME not like 'BIN$%'")
 print("INVALID",q.fetchall())
 q.execute("select COLUMN_NAME,DATA_TYPE from USER_TAB_COLUMNS where TABLE_NAME='RRL_ST_WAIT_MOVE_PLAN' order by COLUMN_ID")
 Path("tmp/1051_wait_plan_columns.json").write_text(json.dumps(q.fetchall(),indent=2),encoding="utf-8")
