exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split('with oracledb.connect',1)[0])
d=Path("db/migrations/2026-10-11_ni061_recurrent_loss");d.mkdir(exist_ok=True)
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor()
 for table in ["RRL_INTERWARE_SHORTAGE_UNIT","RRL_INTERWARE_RECOVERY_UNIT"]:
  q.execute("select CONSTRAINT_NAME,INDEX_NAME from USER_CONSTRAINTS where TABLE_NAME=:tab and CONSTRAINT_TYPE='P'",tab=table);key=q.fetchone()
  q.execute("select CONSTRAINT_NAME,TABLE_NAME from USER_CONSTRAINTS where R_CONSTRAINT_NAME=:key_name",key_name=key[0]);references=q.fetchall();assert not references,references
  print(table,key,"externalFKs",references)
  q.execute("select count(*),sum(BASE_QTY)from "+table);print("retained",q.fetchone())
 for name,kind in [("RRL_STOCK_INTERWARE_SHORT_CMD","PACKAGE"),("RRL_STOCK_INTERWARE_SHORT_CMD","PACKAGE BODY"),("RRL_IW_SHORT_UNIT_GUARD","TRIGGER")]:
  q.execute("select TEXT from USER_SOURCE where NAME=:pkg and TYPE=:kind order by LINE",pkg=name,kind=kind)
  source="".join(r[0]for r in q).replace(chr(13)," ").strip()
  if source:(d/("000_before_"+name.lower()+"_"+kind.lower().replace(" ","_")+".sql")).write_text("create or replace "+source+"\n/\n",encoding="utf-8")
  else:print("No source",name)
print("Captured304 current source and actual loss/recovery PK dependencies")
