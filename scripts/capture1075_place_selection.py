exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor()
 for n in("RRL_ST_DEFER_HU_WAIT","RRL_ST_DEFER_WAIT_API","RRL_ST_DEFER_PHYSICAL","RRL_ST_DEFER_API"):
  for t in("PACKAGE","PACKAGE BODY"):
   q.execute("select TEXT from USER_SOURCE where NAME=:n and TYPE=:t order by LINE",n=n,t=t)
   text="".join(x[0]for x in q)
   Path("tmp/1075_"+n.lower()+"_"+t.lower().replace(" ","_")+".sql").write_text("create or replace "+text+"\n/\n",encoding="utf-8")
 q.execute("select OBJECT_NAME,OBJECT_TYPE from USER_OBJECTS where STATUS='INVALID'and OBJECT_NAME not like 'BIN$%'")
 print("Captured current1075; INVALID",q.fetchall())
