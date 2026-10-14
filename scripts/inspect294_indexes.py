exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select INDEX_NAME,COLUMN_NAME,COLUMN_POSITION from USER_IND_COLUMNS where TABLE_NAME in('RRL_WMS_RECEIPT_CODE','RRL_WMS_RECEIPT_UNIT')order by TABLE_NAME,INDEX_NAME,COLUMN_POSITION")
 print(json.dumps(q.fetchall()))
 q.execute("select CONSTRAINT_NAME,SEARCH_CONDITION_VC from USER_CONSTRAINTS where TABLE_NAME='RRL_WMS_RECEIPT_UNIT'and CONSTRAINT_TYPE='C'");print(json.dumps(q.fetchall()))
