exec(open('scripts/ni063_slow_queries.py',encoding='utf-8').read().split('with oracledb.connect',1)[0])
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select SQL_ID,substr(SQL_TEXT,1,250),PARSE_CALLS,EXECUTIONS,CPU_TIME,ELAPSED_TIME from V$SQL where SQL_ID in('gr0ntpgzds00p','am9g7rdb9jbu8','7ddtmt2f234kp')");print(q.fetchall())
