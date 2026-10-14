exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor()
 for name in ("RRL_STOCK_TASK_PLAN","RRL_STOCK_TASK_CORE","RRL_STOCK_TASK_DOMAIN","RRL_STOCK_STORE_RETURN_PUT","RRL_ST_DEFER_API","RRL_ST_DEFER_PHYSICAL"):
  for kind in ("PACKAGE","PACKAGE BODY"):
   q.execute("select TEXT from USER_SOURCE where NAME=:n and TYPE=:t order by LINE",n=name,t=kind)
   text="".join(x[0]for x in q)
   if text:Path("tmp/760_"+name.lower()+"_"+kind.lower().replace(" ","_")+".sql").write_text("create or replace "+text+"/\n",encoding="utf-8")
 q.execute("select TABLE_NAME,COLUMN_NAME,DATA_TYPE from USER_TAB_COLUMNS where TABLE_NAME in('RRL_ST_DEFER_JOURNAL','RRL_RECEIPT_WARE_SETTINGS') order by TABLE_NAME,COLUMN_ID")
 print(q.fetchall())
 print("760 captured six native packages, read only")
