exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select TEXT from USER_SOURCE where NAME='RRL_STOCK_FULLPAL_BIND_CMD'and TYPE='PACKAGE BODY'order by LINE")
 text="".join(x[0]for x in q).replace("\r","");Path("tmp/fullpal1259.sql").write_text(text,encoding="utf-8");print(text[:21000])
