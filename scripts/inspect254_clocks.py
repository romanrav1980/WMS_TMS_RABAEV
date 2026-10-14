exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select TABLE_NAME,COLUMN_NAME,DATA_TYPE from USER_TAB_COLUMNS where(TABLE_NAME='RRL_WAREHOUSE_TASK'and(COLUMN_NAME like '%INSTANT%'or COLUMN_NAME like '%FINISH%'))or(TABLE_NAME='RRL_RESOURCE_FACT_EVENT'and(COLUMN_NAME like '%AT%'or COLUMN_NAME like '%TIME%'))");print(q.fetchall())
 q.execute("select TASK_ID,to_char(STARTED_AT_INSTANT at time zone 'Asia/Tbilisi','YYYY-MM-DD')from RRL_WAREHOUSE_TASK where TASK_ID=953");print(q.fetchall())
