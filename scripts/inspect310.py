exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor()
 for table in ["RRL_WMS_RECEIPT_AGG","RRL_CRPT_AGGREGATION","RRL_TRACE_MANIFEST_USE","RRL_SAP_TRACE_AGG"]:
  q.execute("select COLUMN_NAME,DATA_TYPE from USER_TAB_COLUMNS where TABLE_NAME=:table_name order by COLUMN_ID",table_name=table);print(table,q.fetchall())
 q.execute("select UID_PALLET,SYSTEM_CODE,PROFILE_CODE,AGG_LEVEL from RRL_WMS_RECEIPT_AGG where UID_PALLET like 'REUSE.%'or UID_PALLET in(select UID_PALLET from RRL_TRACE_MANIFEST_USE) fetch first 12 rows only")
 print("Existing aggregate pallets",q.fetchall())
