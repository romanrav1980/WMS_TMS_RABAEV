exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select TABLE_NAME,COLUMN_NAME from USER_TAB_COLUMNS where COLUMN_NAME like '%ZONE%'and TABLE_NAME in('RRL_RESOURCE_SHIFT','RRL_RESOURCE_SESSION','RRL_WAVE_TIME_PLAN','RRL_WARES')");print(json.dumps(q.fetchall()))
 q.execute("select LINE,TEXT from USER_SOURCE where NAME='RRL_CASE_RESOURCE_POLICY'and TYPE='PACKAGE BODY'and(lower(TEXT)like '%zone%'or lower(TEXT)like '%put(%shift%')order by LINE");print(json.dumps(q.fetchall()))
