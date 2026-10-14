exec(open("scripts/inspect226.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select COLUMN_NAME from USER_TAB_COLUMNS where TABLE_NAME='RRL_WAREHOUSE_TASK'and COLUMN_NAME like '%SYNC%'");print(q.fetchall())
 q.execute("select TASK_ID,STATUS,COMPLETION_JSON from RRL_WAREHOUSE_TASK where TASK_ID=(select TASK_ID from RRL_INTERWARE_PUT_PLAN where OPERATION_ID='IW227.PLAN:13508027ed')");r=q.fetchone();print(r[:2]);print(r[2].read()if hasattr(r[2],"read")else r[2])
 q.execute("select OPERATION_ID,STATE from RRL_STOCK_OPERATION where OPERATION_ID like 'IW227.COMPLETE:%'");print(q.fetchall())
