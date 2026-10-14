exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor()
 for n in("RRL_STOCK_HU_CMD","RRL_STOCK_HU_TASK"):
  for t in("PACKAGE","PACKAGE BODY"):
   q.execute("select TEXT from USER_SOURCE where NAME=:n and TYPE=:t order by LINE",n=n,t=t)
   body="".join(r[0]for r in q);Path("tmp/990_"+n.lower()+"_"+t.lower().replace(" ","_")+".sql").write_text("create or replace "+body+"\n/\n",encoding="utf-8");print(n,t,len(body))
