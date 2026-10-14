exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("""select LINE,TEXT from USER_SOURCE where NAME='RRL_STORE_MARK_CORE'and TYPE='PACKAGE BODY'
 and(upper(TEXT)like '%SCAN_MODE%'or upper(TEXT)like '%CODE_HASH%'or upper(TEXT)like '%UNIT_SCANS%'or upper(TEXT)like '%RESOLVE_DISPOSITION%')order by LINE""")
 print(json.dumps(q.fetchall()))
 q.execute("select TEXT from USER_SOURCE where NAME='RRL_STORE_MARK_CORE'and TYPE='PACKAGE BODY'order by LINE")
 v="create or replace "+"".join(r[0]for r in q.fetchall()).strip()+"\n/\n"
 p=Path("db/migrations/2026-10-12_ni062_return_aggregation/000_before_rrl_store_mark_core_package_body.sql")
 if not p.exists():p.write_text(v,encoding="utf-8")
