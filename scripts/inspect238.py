exec(open("scripts/inspect226.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select TABLE_NAME,COLUMN_NAME,DATA_TYPE from USER_TAB_COLUMNS where TABLE_NAME in('RRL_INTERWARE_UNLOAD','RRL_INTERWARE_RECEIPT','RRL_INTERWARE_PLACEMENT','RRL_INTERWARE_ONWARD_BIND','RRL_TT_HU_LOAD_ST','RRL_TT_HU_LOAD_FACT','RRL_STOCK_OPERATION')and(DATA_TYPE like '%TIMESTAMP%'or DATA_TYPE='DATE'or COLUMN_NAME in('ST_ID','SBORKA_PALLET_ID','ST_IDENTIFIER','OPERATION_ID','RECEIPT_OPERATION_ID','PLAN_OPERATION_ID'))order by TABLE_NAME,COLUMN_ID")
 for row in q:print(row)
