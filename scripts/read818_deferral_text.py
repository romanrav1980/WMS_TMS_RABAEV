exec(open('scripts/ni063_slow_queries.py',encoding='utf-8').read().split('with oracledb.connect',1)[0])
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select COLUMN_NAME,DATA_TYPE,DATA_LENGTH,CHAR_LENGTH,CHAR_USED from USER_TAB_COLUMNS where TABLE_NAME='RRL_ST_DEFER_DECISION'and COLUMN_NAME in('REASON','REFERENCE','ST_NUMBER')");print('TEXT_CONTRACT',q.fetchall())
