exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select trigger_name from user_triggers where table_name='RRL_LOGISTICS_RATE_HISTORY'");names=[r[0]for r in q]
 for name in names:
  q.execute("select text from user_source where name=:n and type='TRIGGER'order by line",n=name);print(name,"".join(r[0]for r in q))
