exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select TEXT from USER_SOURCE where NAME='RRL_HAS_WRIGHT'and TYPE='FUNCTION'order by LINE")
 print("".join(row[0]for row in q))
 q.execute("select COLUMN_NAME from USER_TAB_COLUMNS where TABLE_NAME='RIGHTS'order by COLUMN_ID");print(q.fetchall())
