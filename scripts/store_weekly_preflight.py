"""Read-only drift check before root applies the prepared native window migration."""
from pathlib import Path
exec(open('scripts/ni063_slow_queries.py',encoding='utf-8').read().split('with oracledb.connect')[0])
p=Path('db/migrations/2026-10-14_ni081_store_weekly_windows')
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn) as c:
 q=c.cursor()
 for name in ['RRL_TT_ROUTE_SCHEDULE','RRL_TT_TIME_API']:
  q.execute("select text from user_source where name=:n and type='PACKAGE BODY' order by line",n=name)
  current='create or replace '+''.join(row[0]for row in q)+'\n/\n'
  expected=(p/('000_before_'+name.lower()+'_package_body.sql')).read_text(encoding='utf-8')
  if current.replace('\r\n','\n')!=expected.replace('\r\n','\n'):raise RuntimeError('Native source drift: '+name)
 print('PASS: native package bodies match prepared checkpoint; no writes')
