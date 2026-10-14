exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select TEXT from USER_SOURCE where NAME='RRL_STORE_MARK_CORE'and TYPE='PACKAGE BODY'order by LINE");body="create or replace "+"".join(x[0]for x in q)+"/\n"
Path("tmp/714_store_mark.sql").write_text(body,encoding="utf-8")
print(body[:6500])
