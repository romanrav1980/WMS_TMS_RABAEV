exec(open('scripts/ni063_slow_queries.py',encoding='utf-8').read().split('with oracledb.connect',1)[0])
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn) as c:
 q=c.cursor();q.execute("select i.TABLE_NAME,i.INDEX_NAME,c.COLUMN_NAME,c.COLUMN_POSITION from USER_INDEXES i join USER_IND_COLUMNS c on c.INDEX_NAME=i.INDEX_NAME where i.TABLE_NAME in('RRL_TT_OPERATIONS','RRL_TRANSPORT_TASK') order by 1,2,4")
 print(json.dumps(q.fetchall()))
