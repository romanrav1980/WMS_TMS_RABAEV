exec(open('scripts/ni063_slow_queries.py',encoding='utf-8').read().split('with oracledb.connect',1)[0])
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn) as c:
 q=c.cursor();q.execute("select COLUMN_NAME,DATA_TYPE from USER_TAB_COLUMNS where TABLE_NAME='RRL_SAP_PALLET_RECEIPT' order by COLUMN_ID");print(json.dumps(q.fetchall()))
 q.execute("select UID_PALLET,RESULT_JSON from RRL_SAP_PALLET_RECEIPT where UID_PALLET like 'B01.%' fetch first 1 rows only");row=q.fetchone();print(row[0],row[1].read() if hasattr(row[1],'read') else row[1])
 q.execute("select OBJECT_NAME from USER_OBJECTS where OBJECT_TYPE='PACKAGE' and OBJECT_NAME like '%RECEIPT%' order by OBJECT_NAME");print(json.dumps(q.fetchall()))
