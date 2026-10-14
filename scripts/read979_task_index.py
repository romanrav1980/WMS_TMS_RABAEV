exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select COLUMN_NAME from USER_IND_COLUMNS where INDEX_NAME='RRL_WAREHOUSE_TASK_U2'order by COLUMN_POSITION");print("KEY",q.fetchall())
 q.execute("select COLUMN_EXPRESSION from USER_IND_EXPRESSIONS where INDEX_NAME='RRL_WAREHOUSE_TASK_U2'order by COLUMN_POSITION");print("EXPR",q.fetchall())
