exec(open('scripts/ni063_slow_queries.py',encoding='utf-8').read().split('with oracledb.connect',1)[0])
import difflib
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn) as c:
 q=c.cursor();q.execute("select TEXT from USER_SOURCE where NAME='RRL_TRANSPORT_PLAN_RULES' and TYPE='PACKAGE BODY' order by LINE")
 live='create or replace '+''.join(r[0] for r in q)+'\n/\n'
saved=Path('db/migrations/2026-10-14_ni022_store_access_dimensions/000_before_rules_package_body.sql').read_text(encoding='utf-8')
a=[x for x in saved.splitlines() if x.strip()];b=[x for x in live.splitlines() if x.strip()]
print('nonempty lines equal',a==b)
print('\n'.join(list(difflib.unified_diff(a,b))[:50]))
