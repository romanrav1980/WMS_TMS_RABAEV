exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select OBJECT_NAME from USER_OBJECTS where OBJECT_TYPE='PACKAGE'and(OBJECT_NAME like '%HU%CASE%'or OBJECT_NAME like '%HU%MOVE%')order by OBJECT_NAME")
 names=[r[0]for r in q];print("PACKAGES",names)
 for name in names:
  q.execute("select TEXT from USER_SOURCE where NAME=:n and TYPE='PACKAGE BODY'order by LINE",n=name)
  Path("tmp/989_"+name.lower()+".sql").write_text("".join(r[0]for r in q),encoding="utf-8")
