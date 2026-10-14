exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select TRIGGER_NAME from USER_TRIGGERS where TABLE_NAME='RRL_TARE_RESOLUTION'")
 for(name,)in q.fetchall():
  q.execute("select TEXT from USER_SOURCE where NAME=:name order by LINE",name=name)
  print(name+"\n"+"".join(row[0]for row in q.fetchall()))
