exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor()
 for name,label in [("RRL_STOCK_POSTING_API","root"),("RRL_WAVE_EXEC_ACCESS","access")]:
  q.execute("select TEXT from USER_SOURCE where NAME=:n and TYPE='PACKAGE BODY' order by LINE",n=name)
  source='create or replace '+''.join(row[0]for row in q)+'\n/\n';Path("tmp/876_"+label+"_body.sql").write_text(source,encoding="utf-8");print("captured",name,len(source))
