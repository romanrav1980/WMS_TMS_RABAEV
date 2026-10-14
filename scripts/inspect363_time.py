exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select TABLE_NAME,COLUMN_NAME from USER_TAB_COLUMNS where COLUMN_NAME like '%ZONE%'and(TABLE_NAME like '%SHIFT%'or TABLE_NAME like '%TIME%'or TABLE_NAME='RRL_RESOURCE_SESSION')");print(json.dumps(q.fetchall()))
 q.execute("select LINE,TEXT from USER_SOURCE where NAME='RRL_CASE_RESOURCE_POLICY'and TYPE='PACKAGE BODY'and(lower(TEXT)like '%shift%'or lower(TEXT)like '%resource_session%')order by LINE");print(json.dumps(q.fetchall())[:3200])
