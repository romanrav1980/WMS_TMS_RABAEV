exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select NAME from USER_OBJECTS where OBJECT_TYPE='PACKAGE BODY'and OBJECT_NAME like '%STORE_RECEIPT%'" .replace("select NAME","select OBJECT_NAME"))
 names=[r[0]for r in q];print(json.dumps(names))
 for name in names:
  q.execute("select TEXT from USER_SOURCE where NAME=:name and TYPE='PACKAGE BODY'order by LINE",name=name)
  Path("tmp/"+name+"_537.sql").write_text("create or replace "+"".join(r[0]for r in q)+"\n/\n",encoding="utf-8")
