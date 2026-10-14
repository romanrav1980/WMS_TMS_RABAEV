exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select COLUMN_NAME,DATA_TYPE,DATA_LENGTH from USER_TAB_COLUMNS where TABLE_NAME='RRL_SBORKA_PALLETS'and COLUMN_NAME like 'ZONE%'order by COLUMN_ID");print(q.fetchall())
 q.execute("select ST_NUMBER,ZONE_TIME_PLAN_IN,ZONE_TIME_PLAN_OUT from RRL_SBORKA_PALLETS where TRANSTASK_ID=33564 order by ID");print("OWN_WINDOWS",q.fetchall())
