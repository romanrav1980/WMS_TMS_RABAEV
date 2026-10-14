exec(open('scripts/ni063_slow_queries.py',encoding='utf-8').read().split('with oracledb.connect',1)[0])
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select TABLE_NAME,COLUMN_NAME,DATA_TYPE from USER_TAB_COLUMNS where TABLE_NAME in('RRL_TR_VEHICLE','RRL_VEHICLE_PROFILE_HIST','RRL_TRANSPORT_TYPES') order by TABLE_NAME,COLUMN_ID");print(q.fetchall())
