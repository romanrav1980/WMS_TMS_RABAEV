exec(open('scripts/ni063_slow_queries.py',encoding='utf-8').read().split('with oracledb.connect',1)[0])
p=Path('db/migrations/2026-10-14_ni051_scoped_quality/saved')
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn) as c:
 q=c.cursor()
 for name in ['RRL_STOCK_SHIPPING_CORE','RRL_STOCK_PALLET_QC_CMD']:
  q.execute("select TEXT from USER_SOURCE where NAME=:n and TYPE='PACKAGE BODY' order by LINE",n=name)
  (p/(name+'_PACKAGE_BODY.sql')).write_text('create or replace '+''.join(r[0] for r in q.fetchall())+'\n/\n',encoding='utf-8')
