exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor()
 q.execute("select text from user_source where name='RRL_STOCK_STORE_RETURN_REC_CMD'and type='PACKAGE BODY'order by line");lines=[r[0].strip()for r in q]
 for i,line in enumerate(lines):
  if "BATCH"in line.upper():print("\n".join(lines[max(0,i-2):i+2]))
 q.execute("select column_name from user_tab_columns where table_name='RRL_PALLETS'and(column_name like '%BATCH%'or column_name like '%EXPIR%'or column_name like '%PART%'or column_name like '%DATE%')")
 print("COLS",q.fetchall())
