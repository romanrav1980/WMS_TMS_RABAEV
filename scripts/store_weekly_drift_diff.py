exec(open('scripts/ni063_slow_queries.py',encoding='utf-8').read().split('with oracledb.connect')[0])
import difflib
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn) as c:
 q=c.cursor();q.execute("select text from user_source where name='RRL_TT_ROUTE_SCHEDULE' and type='PACKAGE BODY' order by line")
 a=('create or replace '+''.join(x[0]for x in q)+'\n/\n').splitlines()
 b=Path('db/migrations/2026-10-14_ni081_store_weekly_windows/000_before_rrl_tt_route_schedule_package_body.sql').read_text(encoding='utf-8').splitlines()
 print('\n'.join(list(difflib.unified_diff(b,a))[:30]))
