exec(open('scripts/ni063_slow_queries.py',encoding='utf-8').read().split('with oracledb.connect',1)[0])
out=Path('tmp/qc1443');out.mkdir(exist_ok=True)
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn) as c:
 q=c.cursor()
 for name in ['RRL_STOCK_QC_POLICY','RRL_STOCK_QC_GATE','RRL_STOCK_QC_SAMPLING','RRL_STOCK_QUALITY']:
  q.execute('select TYPE,TEXT from USER_SOURCE where NAME=:name order by TYPE,LINE',name=name);rows=q.fetchall()
  for kind in {r[0] for r in rows}:
   (out/(name+'_'+kind.replace(' ','_')+'.sql')).write_text('create or replace '+''.join(r[1] for r in rows if r[0]==kind)+'\n/\n',encoding='utf-8')
 q.execute("select TABLE_NAME,COLUMN_NAME,DATA_TYPE,DATA_LENGTH from USER_TAB_COLUMNS where TABLE_NAME in ('RRL_SBORKA_PALLETS','RRL_WARES','RRL_RECEIPT_WARE_SETTINGS','RRL_SUBWARES','RRL_CUSTOMER_ADDR','RRL_SKU') and (COLUMN_NAME like '%WARE%' or COLUMN_NAME like '%ADDR%' or COLUMN_NAME like '%QC%' or COLUMN_NAME like '%PROOV%' or COLUMN_NAME like '%MONO%') order by TABLE_NAME,COLUMN_ID");rows=q.fetchall();(out/'columns.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps(rows))
 q.execute("select NAME,TYPE from USER_DEPENDENCIES where REFERENCED_NAME='RRL_STOCK_QC_POLICY' order by NAME,TYPE");print('dependents',json.dumps(q.fetchall()))
