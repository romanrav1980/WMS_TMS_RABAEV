exec(open('scripts/ni063_slow_queries.py',encoding='utf-8').read().split('with oracledb.connect',1)[0])
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn) as c:
 q=c.cursor();q.execute('select ID,PARENT_WARE_ID from RRL_WARES where ID in(9807,6667491,31217707,9104)');print(json.dumps(q.fetchall()))
 q.execute("select NAME,LINE,TEXT from USER_ERRORS where NAME in('RRL_QC_SCOPE_READ','RRL_STOCK_QC_POLICY','RRL_STOCK_QC_GATE','RRL_STOCK_SHIPPING_CORE','RRL_STOCK_PALLET_QC_CMD') order by NAME,LINE");print(json.dumps(q.fetchall()))
