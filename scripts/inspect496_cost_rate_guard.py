exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select trigger_name from user_triggers where table_name='RRL_LOGISTICS_COST_LINE'");names=[r[0]for r in q]
 for name in names:
  q.execute("select text from user_source where name=:n and type='TRIGGER'order by line",n=name)
  lines=[r[0].strip()for r in q];print(name)
  for i,line in enumerate(lines):
   if "EFFECTIVE_FROM"in line or "VERSION_NO"in line:print("\n".join(lines[max(0,i-1):i+2]))
