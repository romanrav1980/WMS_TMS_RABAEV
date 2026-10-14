exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor()
 for table in["RRL_RESOURCE_SESSION","RRL_RESOURCE_FACT_EVENT","RRL_RESOURCE"]:
  q.execute("select COLUMN_NAME,DATA_TYPE from USER_TAB_COLUMNS where TABLE_NAME=:t order by COLUMN_ID",t=table);print(table,q.fetchall())
 q.execute("select SESSION_ID,RESOURCE_ID,STATUS,CURRENT_TASK_ID,CURRENT_INVENTORY_TASK_ID from RRL_RESOURCE_SESSION where SESSION_ID=40");print("OWN226_SESSION",q.fetchall())
 q.execute("select CONSTRAINT_NAME,SEARCH_CONDITION from USER_CONSTRAINTS where TABLE_NAME='RRL_RESOURCE_FACT_EVENT'and CONSTRAINT_TYPE='C'");print("EVENT_CHECKS",[(a,b.read()if hasattr(b,"read")else b)for a,b in q.fetchall()])
