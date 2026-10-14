exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor()
 q.execute("select ARTICUL,TEMP_MIN,TEMP_MAX from RRL_RECEIPT_SKU_RULE where WARE_ID=9807 and ARTICUL like 'QAUTOc0c2a00c0b%'");print(json.dumps({"thermal":q.fetchall()}))
 q.execute("select DOCK,WARE_ID,DOCK_IS_BLOCKED from RRL_TT_DOCK where WARE_ID=9807");print(json.dumps({"docks":q.fetchall()}))
 q.execute("select COLUMN_NAME from USER_TAB_COLUMNS where TABLE_NAME='RRL_TR_VODITEL'order by COLUMN_ID");print(json.dumps({"driver_columns":q.fetchall()}))
 q.execute("select ID,NAME,CODE from RRL_PALLET_TYPE where ACTIVE=1 fetch first 6 rows only");print(json.dumps({"types":q.fetchall()}))
