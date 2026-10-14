exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor()
 q.execute("select c.CONSTRAINT_NAME,c.CONSTRAINT_TYPE,c.SEARCH_CONDITION_VC from USER_CONSTRAINTS c where c.TABLE_NAME='RRL_WAREHOUSE_TASK'and(c.CONSTRAINT_NAME='RRL_WAREHOUSE_TASK_U2'or c.CONSTRAINT_TYPE='C')")
 print("CONSTRAINTS",q.fetchall())
 q.execute("select COLUMN_NAME from USER_CONS_COLUMNS where CONSTRAINT_NAME='RRL_WAREHOUSE_TASK_U2'order by POSITION");print("UNIQUE",q.fetchall())
 q.execute("select max(SOURCE_TASK_ID),max(TASK_ID)from RRL_WAREHOUSE_TASK where TASK_SOURCE='MANUAL'and TASK_TYPE='PUTAWAY'");print("SOURCE_MAX",q.fetchall())
