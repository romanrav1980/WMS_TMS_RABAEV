exec(open('scripts/ni063_slow_queries.py',encoding='utf-8').read().split('with oracledb.connect',1)[0])
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select COLUMN_NAME,DATA_TYPE from USER_TAB_COLUMNS where TABLE_NAME='RRL_ADDR'and COLUMN_NAME in('ID','ADDR','SHIROTA','DOLGOTA','LATITUDE','LONGITUDE','GEO_FENCE_RADIUS_M','DELETED3')order by COLUMN_ID");print(q.fetchall())
 q.execute('select ADDR,SHIROTA,DOLGOTA,GEO_FENCE_RADIUS_M,DELETED3 from RRL_ADDR where SHIROTA is not null fetch first 3 rows only');print(q.fetchall())

