exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor()
 q.execute("select TABLE_NAME,INDEX_NAME,COLUMN_NAME,COLUMN_POSITION from USER_IND_COLUMNS where TABLE_NAME in('RRL_TRANSPORT_TASK','RRL_SBORKA_PALLETS','RRL_CUSTOMER_STORE_MAP')order by TABLE_NAME,INDEX_NAME,COLUMN_POSITION")
 print("INDEXES",q.fetchall())
 q.execute("select NAME,LINE,TEXT from USER_SOURCE where TYPE='PACKAGE BODY'and NAME in('RRL_STOCK_POSTING_API','RRL_STOCK_COMMAND_EXEC','RRL_STOCK_DISPATCH_API')and(upper(TEXT)like '%OUTBOX%'or upper(TEXT)like '%FINISH_OPERATION%'or upper(TEXT)like '%EMIT%')order by NAME,LINE")
 print("ROOT_OUTBOX",[(n,l,t.strip())for n,l,t in q])
 q.execute("select PLAN_TABLE_OUTPUT from table(dbms_xplan.display_cursor('96k9jr9gp604m',null,'BASIC'))")
 print("SELECTOR_PLAN",[x[0]for x in q])
