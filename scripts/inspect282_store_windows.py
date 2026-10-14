exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select COLUMN_NAME,DATA_TYPE from USER_TAB_COLUMNS where TABLE_NAME='RRL_ADDR'order by COLUMN_ID");print(q.fetchall())
 q.execute("select COLUMN_NAME,DATA_TYPE from USER_TAB_COLUMNS where TABLE_NAME='RRL_WARES'and(COLUMN_NAME like '%ADDR%'or COLUMN_NAME like '%LAT%'or COLUMN_NAME like '%LON%'or COLUMN_NAME like '%TIME%')");print("WARE_FIELDS",q.fetchall())
