exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select COLUMN_NAME from USER_TAB_COLUMNS where TABLE_NAME='RRL_STORE_RETURN_APPROVAL'and(COLUMN_NAME like '%UID%'or COLUMN_NAME like '%ARTICLE%')");print(q.fetchall())
 q.execute("select TEXT from USER_SOURCE where NAME='RRL_STORE_RETURN_UNIT_CORE'and TYPE='PACKAGE BODY'order by LINE");Path("tmp/388_before_return.sql").write_text("create or replace "+"".join(x[0]for x in q).replace("\r","")+"\n/\n",encoding="utf-8")
