exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select COLUMN_NAME,DATA_TYPE from USER_TAB_COLUMNS where TABLE_NAME='RRL_SBORKA_PALLETS'and(COLUMN_NAME like '%ORD%'or COLUMN_NAME like '%ADR%'or COLUMN_NAME in('ADDR','STDATE'))order by COLUMN_ID");print(q.fetchall())
 q.execute("select TEXT from USER_SOURCE where NAME='RRL_TT_REORDER_ADR'order by LINE")
 text="".join(x[0]for x in q.fetchall())
 print(text[:4500])
