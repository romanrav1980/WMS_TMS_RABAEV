exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select INDEX_NAME,UNIQUENESS from USER_INDEXES where TABLE_NAME='RRL_PRIHOD_NAKLAD_ROWS'");print("INDEXES",q.fetchall())
 q.execute("select LINE,TEXT from USER_SOURCE where NAME='RRL_STOCK_RECEIPT_CORE'and TYPE='PACKAGE BODY'order by LINE");print(''.join(row[1]for row in q.fetchall())[:14500])
