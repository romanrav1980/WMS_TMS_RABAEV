exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select TEXT from USER_SOURCE where NAME='RRL_PICKING_API'and TYPE='PACKAGE BODY'order by LINE");text="".join(r[0]for r in q)
 at=text.lower().find("function create_plan")
 print(text[at:at+6200])
