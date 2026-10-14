exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("""select TABLE_NAME,COLUMN_NAME,DATA_LENGTH,CHAR_LENGTH,CHAR_USED from USER_TAB_COLUMNS
 where TABLE_NAME in('RRL_PALLETS','RRL_SAP_PALLET_RECEIPT','RRL_RECEIPT_SLOT_CLAIM','RRL_WMS_RECEIPT_UNIT','RRL_WAREHOUSE_TASK')
 and COLUMN_NAME in('UID_PALLET','CURRENT_UID','SSCC')order by TABLE_NAME,COLUMN_NAME""")
 print(json.dumps(q.fetchall()))
