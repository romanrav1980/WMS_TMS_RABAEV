exec(open('scripts/ni063_slow_queries.py',encoding='utf-8').read().split('with oracledb.connect',1)[0])
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select NAME,LINE,TEXT from USER_SOURCE where TYPE='PACKAGE BODY'and(upper(TEXT)like '%RRL_TRANSPORT_PLAN_RULES.CHECK_VEHICLE%'or upper(TEXT)like '%RRL_STOCK_LOAD_THERMAL.%')order by NAME,LINE");print(q.fetchall())
 q.execute("select COLUMN_NAME,DATA_TYPE from USER_TAB_COLUMNS where TABLE_NAME='RRL_STORE_PROFILE' order by COLUMN_ID");print(q.fetchall())
 for name in ['RRL_STOCK_LOAD_THERMAL','RRL_STOCK_TRIP_LOAD_CORE','RRL_STOCK_TRIP_DEPART_CMD']:
  q.execute("select count(*)from USER_OBJECTS where OBJECT_NAME=:n and OBJECT_TYPE='PACKAGE BODY'",n=name)
  if not q.fetchone()[0]:continue
  q.execute("select TEXT from USER_SOURCE where NAME=:n and TYPE='PACKAGE BODY'order by LINE",n=name);Path('tmp/'+name.lower()+'.sql').write_text(''.join(x[0]for x in q.fetchall()),encoding='utf-8')
