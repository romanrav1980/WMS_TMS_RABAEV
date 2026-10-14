exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor()
 for name in ("RRL_IW_GROUP_REC","RRL_INTERWARE_MARK_SCAN"):
  q.execute("select TEXT from USER_SOURCE where NAME=:name and TYPE='PACKAGE BODY'order by LINE",name=name)
  body="".join(row[0]for row in q);Path("tmp/666_"+name.lower()+".sql").write_text(body,encoding="utf-8")
  print(name,len(body))
