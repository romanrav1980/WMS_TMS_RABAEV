exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
saved=json.loads(Path('tmp/context406.json').read_text(encoding='utf-8'))
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.callproc('RRL_STOCK_CONFIG_API.begin_change',['admin','warehouse_settings_edit'])
 try:
  q.execute("insert into RRL_RECEIPT_WARE_SETTINGS(WARE_ID,OUTGOING_QC_MODE,OUTGOING_QC_INDEPENDENT,HU_CELL_HEIGHT_UNIT)values(:ware,'NONE',0,'M')",ware=saved['group_plan']['target_warehouse_id'])
  q.execute('update RRL_CELLS set LIMIT_HEIGHT=3,LIMIT_WEIGHT=100 where CELL=:cell and WARE_ID=:ware',cell=saved['group_put_cell'],ware=saved['group_plan']['target_warehouse_id']);c.commit()
 finally:q.callproc('RRL_STOCK_CONFIG_API.end_change')
print('Own422 target explicit3M/100KG/defaultunits known')
