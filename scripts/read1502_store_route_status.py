exec(open('scripts/ni063_slow_queries.py',encoding='utf-8').read().split('with oracledb.connect',1)[0])
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn) as c:
 c.call_timeout=10000;q=c.cursor()
 q.execute("select OBJECT_NAME,OBJECT_TYPE from USER_OBJECTS where STATUS='INVALID' and OBJECT_NAME not like 'BIN$%'");invalid=q.fetchall()
 q.execute("select MIGRATION_ID,STATUS from RRL_SCHEMA_MIGRATIONS where MIGRATION_ID in('2026-10-14-1490-ni051-store-profile','2026-10-14-ni022-vehicle-outer-dimensions','2026-10-14-ni081-store-weekly-windows','2026-10-14-ni022-store-access-dimensions') order by MIGRATION_ID");ledger=q.fetchall()
 assert not invalid and len(ledger)==4 and all(x[1]=='APPLIED' for x in ledger)
 Path('reports/nicora/2026-10-13/store_route_installed1502.json').write_text(json.dumps({'invalid':invalid,'ledger':ledger},indent=2),encoding='utf-8')
 print('PASS four migrations APPLIED; non-recycle-bin INVALID=0')
