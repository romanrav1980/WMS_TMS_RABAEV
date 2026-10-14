exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select COLUMN_NAME from USER_TAB_COLUMNS where TABLE_NAME='RRL_SAP_SUPPLY_LINE'order by COLUMN_ID");print(q.fetchall())
 q.execute("select o.ORDER_ID,o.WARE_ID,o.CLOSED_AT,h.CONDITION,settings.COMPANY_PREFIX from RRL_SAP_SUPPLY_ORDER o join RRL_PRIHOD_NAKLAD h on h.ID=o.NAKLAD_ID left join RRL_RECEIPT_WARE_SETTINGS settings on settings.WARE_ID=o.WARE_ID where o.ORDER_ID in('SAP_2046',(select ORDER_ID from RRL_SAP_PALLET_RECEIPT where UID_PALLET like 'LEGACY.SAP.688:%'))");print(q.fetchall())
