exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor()
 for n in("RRL_ST_DEFER_CASE_WAIT","RRL_ST_DEFER_WAIT_API","RRL_ST_DEFER_API","RRL_ST_DEFER_PHYSICAL"):
  for t in("PACKAGE","PACKAGE BODY"):
   q.execute("select TEXT from USER_SOURCE where NAME=:n and TYPE=:t order by LINE",n=n,t=t)
   Path("tmp/985_"+n.lower()+"_"+t.lower().replace(" ","_")+".sql").write_text("create or replace "+"".join(r[0]for r in q)+"\n/\n",encoding="utf-8")
 print("Captured current single CASE deferral contracts, native985")
