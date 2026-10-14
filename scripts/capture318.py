exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor()
 q.execute("select OBJECT_NAME from USER_OBJECTS where OBJECT_TYPE='PACKAGE BODY'and OBJECT_NAME like '%INTERWARE%CUSTODY%'");names=[r[0]for r in q];print("Packages",names)
 for name in names:
  q.execute("select TEXT from USER_SOURCE where NAME=:pkg and TYPE='PACKAGE BODY'order by LINE",pkg=name)
  body="".join(r[0]for r in q).replace(chr(13)," ").strip();Path("tmp/318_"+name.lower()+".sql").write_text(body,encoding="utf-8")
 q.execute("select TRIGGER_NAME from USER_TRIGGERS where TABLE_NAME='RRL_INTERWARE_CUSTODY_RELEASE'");print("Custody guards",q.fetchall())
