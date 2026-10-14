exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select LINE,TEXT from USER_SOURCE where NAME='RRL_STOCK_POSTING_API' and TYPE='PACKAGE BODY' and(TEXT like '%RRL_WAVE_EXEC_ACCESS%'or TEXT like '%WAVE_PICK_RELEASE%')order by LINE");print(q.fetchall())
