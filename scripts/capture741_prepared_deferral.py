exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor()
 for table in("RRL_CUSTOMER_ORDER_FULFILLMENT","RRL_SHIPMENT_ALLOCATION"):
  q.execute("select COLUMN_NAME from USER_TAB_COLUMNS where TABLE_NAME=:t order by COLUMN_ID",t=table);print(table,q.fetchall())
 q.execute("select TEXT from USER_SOURCE where NAME='RRL_ST_DEFER_API'and TYPE='PACKAGE BODY'order by LINE");source="create or replace "+"".join(x[0]for x in q)+"/\n";Path("tmp/741_st_defer_before.sql").write_text(source,encoding="utf-8")
 q.execute("""select f.FULFILLMENT_ID,f.LEGACY_SBORKA_PALLET_ID,f.FACT_QTY,p.ST_NUMBER,p.TRANSTASK_ID
 from RRL_CUSTOMER_ORDER_FULFILLMENT f join RRL_SBORKA_PALLETS p on p.ID=f.LEGACY_SBORKA_PALLET_ID
 where f.STATUS='PICKED'and f.FACT_QTY>0 and p.TRANSTASK_ID>0
 and not exists(select 1 from RRL_TT_HU_LOAD_ST ls join RRL_TT_HU_LOAD_FACT l on l.LOAD_OPERATION_ID=ls.LOAD_OPERATION_ID where ls.SBORKA_PALLET_ID=p.ID and ls.ACTIVE_FLAG=1 and l.STATUS in('LOADED','DEPARTED'))
 fetch first 3 rows only""");print("PICKED_CANDIDATES",q.fetchall())
