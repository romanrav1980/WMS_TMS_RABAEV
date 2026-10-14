exec(open('scripts/ni063_slow_queries.py',encoding='utf-8').read().split('with oracledb.connect',1)[0])
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn) as c:
 q=c.cursor();q.execute("select TASK_ID,STATUS,ASSIGNED_TO,TASK_SOURCE from RRL_WAREHOUSE_TASK where TASK_ID in (564,633,634,1163,1164) or (STATUS in ('ASSIGNED','IN_PROGRESS') and TASK_ID>1100) order by TASK_ID desc fetch first 12 rows only");print(json.dumps(q.fetchall(),default=str))
