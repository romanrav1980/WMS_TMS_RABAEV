exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor()
 q.execute("select DATA_DEFAULT from USER_TAB_COLUMNS where TABLE_NAME='RRL_TRANSPORT_TASK'and COLUMN_NAME='CONDITION'");print("TT_STATUS_DEFAULT",q.fetchone())
 q.execute("select INDEX_NAME,COLUMN_EXPRESSION from USER_IND_EXPRESSIONS where TABLE_NAME='RRL_EVENT_OUTBOX'order by INDEX_NAME,COLUMN_POSITION");print("EVENT_EXPRESSIONS",q.fetchall())
 q.execute("select INDEX_NAME,COLUMN_NAME from USER_IND_COLUMNS where TABLE_NAME='RRL_EVENT_OUTBOX'order by INDEX_NAME,COLUMN_POSITION");print("EVENT_INDEXES",q.fetchall())
