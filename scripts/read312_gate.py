exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select TEXT from USER_SOURCE where NAME='RRL_INTERWARE_DEPART_GATE'and TYPE='PACKAGE BODY'order by LINE")
 source="create or replace "+"".join(r[0]for r in q).replace(chr(13)," ").strip()+"\n/\n"
 Path("db/migrations/2026-10-12_ni061_nested_onward/000_before_depart_gate.sql").write_text(source,encoding="utf-8")
 print(source)
