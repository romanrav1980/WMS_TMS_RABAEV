exec(open('scripts/ni063_slow_queries.py',encoding='utf-8').read().split('with oracledb.connect',1)[0])
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select NAME,TYPE,LINE,POSITION,TEXT from USER_ERRORS where NAME in('RRL_TT_ROUTE_SCHEDULE','RRL_TT_TIME_API')order by NAME,SEQUENCE");print(json.dumps(q.fetchall()))
