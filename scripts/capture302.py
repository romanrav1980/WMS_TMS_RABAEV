exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
d=Path("db/migrations/2026-10-11_ni061_recovery_redelivery");d.mkdir(exist_ok=True)
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor()
 for name in ["RRL_STOCK_INTERWARE_NEXT"]:
  for kind in ["PACKAGE","PACKAGE BODY"]:
   q.execute("select TEXT from USER_SOURCE where NAME=:pkg and TYPE=:kind order by LINE",pkg=name,kind=kind)
   source="".join(r[0]for r in q).replace(chr(13)," ").strip();assert source
   (d/("000_before_"+name.lower()+"_"+kind.lower().replace(" ","_")+".sql")).write_text("create or replace "+source+"\n/\n",encoding="utf-8")
 for table in ["RRL_INTERWARE_ONWARD_BIND","RRL_INTERWARE_ONWARD_DISPATCH"]:
  q.execute("select COLUMN_NAME,DATA_TYPE,DATA_LENGTH,CHAR_LENGTH,CHAR_USED,NULLABLE from USER_TAB_COLUMNS where TABLE_NAME=:tab order by COLUMN_ID",tab=table);print(table,q.fetchall())
print("Captured302 currentNEXT only")
