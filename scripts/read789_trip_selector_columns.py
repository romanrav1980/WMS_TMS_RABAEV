exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor()
 for table in ("RRL_ADDR","RRL_CUSTOMER_ORDER","RRL_TRANSPORT_TASK"):
  q.execute("select COLUMN_NAME,DATA_TYPE from USER_TAB_COLUMNS where TABLE_NAME=:t order by COLUMN_ID",t=table);print(table,q.fetchall())
 q.execute("select count(*)from RRL_ADDR where RAION is not null");print("DISTRICT_ROWS",q.fetchone()[0])
