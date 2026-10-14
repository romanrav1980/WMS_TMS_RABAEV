exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select LINE,TEXT from USER_SOURCE where NAME='RRL_TT_OPERATION_PLAN_API'and TYPE='PACKAGE BODY'and(upper(TEXT)like '%FACT_%'or upper(TEXT)like '%UPDATE RRL_TT_%')order by LINE")
 for line,value in q.fetchall():print(str(line)+":"+value.strip())
