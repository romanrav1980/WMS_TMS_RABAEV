exec(open('scripts/ni063_slow_queries.py',encoding='utf-8').read().split('with oracledb.connect',1)[0])
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn) as c:
 q=c.cursor();q.execute("select NAME,LINE,TEXT from USER_SOURCE where TYPE='PACKAGE BODY' and (upper(TEXT) like '%QC_GATE.ASSERT_APPROVED%' or upper(TEXT) like '%QC_GATE.STATUS_JSON%') order by NAME,LINE");print(json.dumps(q.fetchall()))
 q.execute("select TEXT from USER_SOURCE where NAME='RRL_STOCK_PALLET_QC_CMD' and TYPE='PACKAGE BODY' order by LINE");Path('tmp/qc1443/RRL_STOCK_PALLET_QC_CMD_PACKAGE_BODY.sql').write_text('create or replace '+''.join(r[0] for r in q.fetchall())+'\n/\n',encoding='utf-8')
