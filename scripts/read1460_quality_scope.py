exec(open('scripts/ni063_slow_queries.py',encoding='utf-8').read().split('with oracledb.connect',1)[0])
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn) as c:
 q=c.cursor();q.execute('select ID,ADDR,PALLET_UID,WARE_ID from RRL_SBORKA_PALLETS where ID=641492');row=q.fetchone();print(json.dumps(row));Path('tmp/qc1460_scope.json').write_text(json.dumps({'document_id':row[0],'store_addr':row[1],'shipment':row[2],'warehouse':row[3]}),encoding='utf-8')
