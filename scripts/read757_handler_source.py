exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor()
 for name,start,end in[("RRL_STOCK_TASK_DOMAIN",20,46),("RRL_STOCK_TASK_CORE",112,136)]:
  q.execute("select LINE,TEXT from USER_SOURCE where NAME=:name and TYPE='PACKAGE BODY'and LINE between :a and :b order by LINE",name=name,a=start,b=end)
  for line,txt in q:print(name,line,txt.strip())
