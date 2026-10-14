exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
d=Path("db/migrations/2026-10-11_ni061_partial_custody")
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select TEXT from USER_SOURCE where NAME='RRL_TT_HU_LOAD_FACT_GUARD'and TYPE='TRIGGER'order by LINE")
 source="".join(r[0]for r in q).replace(chr(13)," ").strip();assert source
 (d/"000_before_load_fact_guard.sql").write_text("create or replace "+source+"\n/\n",encoding="utf-8")
print(source[:5200])
