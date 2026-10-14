exec(open('scripts/ni063_slow_queries.py',encoding='utf-8').read().split('with oracledb.connect',1)[0])
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn) as c:
 q=c.cursor();q.execute("""select r.UID_PALLET,r.POSTED_BASE_QTY,p.STOCK_COMPOSITION_VERSION,json_value(r.RESULT_JSON,'$.warehouse_id'),p.ARTICUL,
 (select count(*) from RRL_SKU_RECEIPT_PROFILE f where f.ARTICUL=p.ARTICUL),
 (select min(ID) from RRL_SBORKA_PALLETS sp where sp.WARE_ID=to_number(json_value(r.RESULT_JSON,'$.warehouse_id')))
 from (select * from RRL_SAP_PALLET_RECEIPT order by RECEIVED_AT desc fetch first 500 rows only)r
 join RRL_PALLETS p on p.UID_PALLET=r.UID_PALLET where p.STOCK_COMPOSITION_VERSION=1
 and r.POSTED_BASE_QTY=(select sum(REMAIN) from RRL_REMAINS b where b.UID_POLETA=r.UID_PALLET)
 order by r.RECEIVED_AT desc fetch first 12 rows only""");print(json.dumps(q.fetchall()))
