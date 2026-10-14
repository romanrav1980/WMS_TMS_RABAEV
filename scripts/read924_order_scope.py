exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select TEXT from USER_SOURCE where NAME='RRL_STORE_ORDER_SCOPE'and TYPE='PACKAGE BODY' order by LINE")
 t='create or replace '+''.join(x[0]for x in q)+'\n/\n';Path("tmp/924_scope_body.sql").write_text(t,encoding="utf-8");print(t[:3200])
