exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor()
 for n,t in(("RRL_STOCK_HU_CMD","PACKAGE"),("RRL_STOCK_HU_CMD","PACKAGE BODY"),("RRL_STOCK_HU_TASK","PACKAGE BODY")):
  q.execute("select TEXT from USER_SOURCE where NAME=:n and TYPE=:t order by LINE",n=n,t=t)
  Path("tmp/1085_"+n.lower()+"_"+t.lower().replace(" ","_")+".sql").write_text("create or replace "+"".join(x[0]for x in q).replace("\r\n","\n")+"\n/\n",encoding="utf-8",newline="\n")
 print("Captured1085 HU planning boundary")
