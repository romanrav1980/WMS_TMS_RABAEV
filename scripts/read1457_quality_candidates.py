exec(open('scripts/ni063_slow_queries.py',encoding='utf-8').read().split('with oracledb.connect',1)[0])
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn) as c:
 q=c.cursor();q.execute("""select r.UID_PALLET,r.POSTED_BASE_QTY,r.STOCK_BASE_UOM,p.STOCK_COMPOSITION_VERSION,
 json_value(r.RESULT_JSON,'$.warehouse_id'),p.PROD_BATCH_ID,json_value(r.RESULT_JSON,'$.supplier_batch'),
 (select sum(REMAIN) from RRL_REMAINS b where b.UID_POLETA=r.UID_PALLET) QTY
 from (select * from RRL_SAP_PALLET_RECEIPT order by RECEIVED_AT desc fetch first 50 rows only)r
 join RRL_PALLETS p on p.UID_PALLET=r.UID_PALLET where p.STOCK_COMPOSITION_VERSION=1
 order by r.RECEIVED_AT desc fetch first 10 rows only""");rows=q.fetchall();print(json.dumps(rows));Path('tmp/qc1457_candidates.json').write_text(json.dumps(rows,indent=2),encoding='utf-8')
