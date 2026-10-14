exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select TRIGGER_NAME from USER_TRIGGERS where TABLE_NAME in('RRL_WAREHOUSE_TASK','RRL_INTERWARE_PUT_PLAN','RRL_INTERWARE_PLACEMENT')");names=[r[0]for r in q];print(names)
 for name in names:
  q.execute("select TEXT from USER_SOURCE where NAME=:pkg and TYPE='TRIGGER'order by LINE",pkg=name);source="".join(r[0]for r in q).replace(chr(13)," ").strip()
  Path("tmp/317_"+name.lower()+".sql").write_text(source,encoding="utf-8")
