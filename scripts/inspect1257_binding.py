exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor()
 q.execute("select distinct NAME from USER_SOURCE where TEXT like '%FULLPAL_SHIPMENT%'or TEXT like '%PICK_PALLET_BIND_SHIPMENT%'")
 print(json.dumps({"packages":q.fetchall()}))
 q.execute("select ID,PALLET_UID,ST_NUMBER,TRANSTASK_ID from RRL_SBORKA_PALLETS where PALLET_UID like 'SAP_2135%'")
 print(json.dumps({"prepared":q.fetchall()}))
 q.execute("select FULFILLMENT_ID,PALLET_UID,LEGACY_SBORKA_PALLET_ID,STATUS,FACT_QTY from RRL_CUSTOMER_ORDER_FULFILLMENT where CUSTOMER_ORDER_ID=2135")
 print(json.dumps({"fulfillment":q.fetchall()}))
 q.execute("""select SQL_ID,EXECUTIONS,round(ELAPSED_TIME/nullif(EXECUTIONS,0)/1000,3),round(BUFFER_GETS/nullif(EXECUTIONS,0),2),substr(SQL_TEXT,1,160)
 from V$SQL where PARSING_SCHEMA_NAME='RABAEV' and EXECUTIONS>0 and SQL_TEXT not like '%V$SQL%'
 and(SQL_TEXT like '%with cell_pallets as (%'or(SQL_TEXT like '%UNKNOWN_WEIGHTS%' and SQL_TEXT like '%RRL_RECEIPT_CELL_RULE%'))
 order by LAST_ACTIVE_TIME desc fetch first 5 rows only""")
 print(json.dumps({"placement_sql":q.fetchall()}))
