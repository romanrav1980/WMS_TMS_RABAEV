exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor()
 for name in ("RRL_ST_DEFER_PHYSICAL","RRL_STOCK_WAITING_TASK","RRL_STOCK_HU_TASK","RRL_STOCK_WAITING_PLAN"):
  for typ in ("PACKAGE","PACKAGE BODY"):
   q.execute("select TEXT from USER_SOURCE where NAME=:n and TYPE=:t order by LINE",n=name,t=typ)
   text=''.join(row[0]for row in q)
   if text:Path("tmp/948_"+name.lower()+"_"+typ.lower().replace(" ","_")+".sql").write_text("create or replace "+text+"\n/\n",encoding="utf-8");print(name,typ,len(text))
 q.execute("select COLUMN_NAME,DATA_TYPE,DATA_LENGTH from USER_TAB_COLUMNS where TABLE_NAME='RRL_WAREHOUSE_TASK'and COLUMN_NAME in('UID_PALLET','SOURCE_DOC_TYPE','SOURCE_DOC_ID','QTY_MODE')")
 print("TASK_CONTRACT",q.fetchall())
