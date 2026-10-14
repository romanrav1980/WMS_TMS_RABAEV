exec(open('scripts/ni063_slow_queries.py',encoding='utf-8').read().split('with oracledb.connect',1)[0])
x=json.loads(Path('tmp/context671.json').read_text(encoding='utf-8'));w=x['group_plan']['target_warehouse_id'];target=x['group_plan']['outbound_dock']
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute('select LIMIT_HEIGHT,LIMIT_WEIGHT from RRL_CELLS where CELL=:cell',cell=target);print('target limits',q.fetchone());q.execute('select count(*)from RRL_RECEIPT_WARE_SETTINGS where WARE_ID=:ware',ware=w);print('settings',q.fetchone());q.execute("select COLUMN_NAME,NULLABLE,DATA_DEFAULT from USER_TAB_COLUMNS where TABLE_NAME='RRL_RECEIPT_WARE_SETTINGS'");print(q.fetchall())
