exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select TEXT from USER_SOURCE where NAME='RRL_STOCK_WAVE_CMD' and TYPE='PACKAGE BODY' order by LINE")
 source='create or replace '+''.join(row[0]for row in q)+'\n/\n'
 Path("tmp/865_wave_body.sql").write_text(source,encoding="utf-8")
 print("captured current wave body",len(source))
