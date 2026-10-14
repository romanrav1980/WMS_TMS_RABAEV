exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn) as c:
 q=c.cursor()
 q.execute("select TRIGGER_NAME from USER_TRIGGERS where TABLE_NAME in('RRL_WAREHOUSE_TASK','RRL_ST_DEFER_WAIT_PLAN')")
 for n, in q.fetchall():
  q.execute("select TEXT from USER_SOURCE where NAME=:n and TYPE='TRIGGER' order by LINE",n=n)
  t="".join(r[0]for r in q)
  Path("tmp/1053_"+n.lower()+".sql").write_text("create or replace "+t+"\n/\n",encoding="utf-8")
  print(n,t[:3500])
