exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select COLUMN_NAME from USER_TAB_COLUMNS where TABLE_NAME='RRL_SAP_PALLET_RECEIPT'order by COLUMN_ID");print("SAP receipt columns",[r[0]for r in q])
 q.execute("select o.COMMAND_TYPE,count(*)from RRL_SAP_PALLET_RECEIPT r join RRL_STOCK_OPERATION o on o.OPERATION_ID=r.OPERATION_ID group by o.COMMAND_TYPE");print("Native SAP receipts",q.fetchall())
 q.execute("select r.UID_PALLET,r.ORDER_ID,r.LINE_NUMBER,p.ARTICUL,count(*)from RRL_SAP_PALLET_RECEIPT r join RRL_WMS_RECEIPT_AGG agg on agg.UID_PALLET=r.UID_PALLET join RRL_PALLETS p on p.UID_PALLET=r.UID_PALLET group by r.UID_PALLET,r.ORDER_ID,r.LINE_NUMBER,p.ARTICUL fetch first 8rows only");print("SAP aggregate origin",q.fetchall())
