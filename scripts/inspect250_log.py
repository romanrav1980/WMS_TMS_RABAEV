exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("""select LOG_ID,ELAPSED_MS,ERROR_TEXT from RRL_SQL_SLOW_LOG
 where API_PATH='/api/transport/preflight/time-approvals' and ERROR_TEXT is not null
 order by LOG_ID desc fetch first 3 rows only""")
 for row in q:print(tuple(x.read()if hasattr(x,"read")else x for x in row))
