exec(open('scripts/ni063_slow_queries.py',encoding='utf-8').read().split('with oracledb.connect',1)[0])
x=json.loads(Path('tmp/context671.json').read_text(encoding='utf-8'));w=x['group_plan']['target_warehouse_id'];target=x['group_plan']['outbound_dock']
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.callproc('RRL_STOCK_CONFIG_API.begin_change',['admin','warehouse_settings_edit'])
 try:
  q.execute("insert into RRL_RECEIPT_WARE_SETTINGS(WARE_ID,HU_CELL_HEIGHT_UNIT,UPDATED_BY)values(:ware,'M','admin')",ware=w)
  q.execute('update RRL_CELLS set LIMIT_HEIGHT=2.5,LIMIT_WEIGHT=100 where CELL=:cell and WARE_ID=:ware',cell=target,ware=w);assert q.rowcount==1;c.commit()
 finally:q.callproc('RRL_STOCK_CONFIG_API.end_change')
print('707 private target explicit 2.5M/100KG; measured group1.5M/7KG; no stock writes')
