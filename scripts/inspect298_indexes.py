exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select TABLE_NAME,INDEX_NAME,COLUMN_NAME,COLUMN_POSITION from USER_IND_COLUMNS where TABLE_NAME in('RRL_INTERWARE_ONWARD_DISPATCH','RRL_STORE_RECEIPT_FACT','RRL_STORE_RECEIPT_LINE','RRL_INTERWARE_PLAN')order by TABLE_NAME,INDEX_NAME,COLUMN_POSITION");print(json.dumps(q.fetchall()))
