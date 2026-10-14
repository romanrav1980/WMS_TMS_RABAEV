exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor()
 q.execute("select COLUMN_NAME,DATA_TYPE from USER_TAB_COLUMNS where TABLE_NAME='RRL_CELLS' order by COLUMN_ID");print(json.dumps(q.fetchall()))
 q.execute("select CELL,WARE_ID,OTBOR,IS_SYSTEM,BLOCKED_FOR_REMAINS,BLOCKED_FOR_POPOLNENIE from RRL_CELLS where WARE_ID=9807 order by CELL fetch first 30 rows only");print(json.dumps(q.fetchall()))
 q.execute("select TRIGGER_NAME from USER_TRIGGERS where TABLE_NAME='RRL_WAREHOUSE_TASK'and STATUS='ENABLED'");print(json.dumps(q.fetchall()))

