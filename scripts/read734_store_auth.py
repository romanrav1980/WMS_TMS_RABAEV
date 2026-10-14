exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select NAME,TYPE,TEXT from USER_SOURCE where NAME in('RRL_STOCK_STORE_RECEIPT_READ','RRL_STOCK_STORE_RECEIPT_SRC')and TYPE='PACKAGE'order by NAME,LINE")
 for row in q:print(row[0],row[2].strip())
