exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor()
 for t in("PACKAGE","PACKAGE BODY"):
  q.execute("select TEXT from USER_SOURCE where NAME='RRL_STOCK_CASE_BIND_MOVE'and TYPE=:t order by LINE",t=t)
  Path("tmp/992_case_bind_"+t.lower().replace(" ","_")+".sql").write_text("create or replace "+"".join(r[0]for r in q)+"\n/\n",encoding="utf-8")
 print("Captured current binding metadata core")
