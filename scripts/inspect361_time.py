exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select TABLE_NAME,COLUMN_NAME,DATA_TYPE from USER_TAB_COLUMNS where COLUMN_NAME='TIME_ZONE'and(TABLE_NAME like '%WARE%'or TABLE_NAME like '%SHIFT%')");print(json.dumps(q.fetchall()))
 q.execute("select TABLE_NAME,COLUMN_NAME,DATA_TYPE from USER_TAB_COLUMNS where TABLE_NAME like 'RRL_CASE%COMMAND%'or TABLE_NAME='RRL_CASE_PICK_EVENT'order by TABLE_NAME,COLUMN_ID");print(json.dumps(q.fetchall()))
