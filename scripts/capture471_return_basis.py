import json
from pathlib import Path
exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
out={}
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor()
 q.execute("select trigger_name from user_triggers where table_name in('RRL_STORE_RETURN_APPROVAL','RRL_STORE_RETURN_UNIT')")
 objects=[(r[0],"TRIGGER")for r in q.fetchall()]+[("RRL_STOCK_STORE_RETURN_CMD","PACKAGE BODY"),("RRL_STORE_RETURN_UNIT_CORE","PACKAGE"),("RRL_STORE_RETURN_UNIT_CORE","PACKAGE BODY")]
 for name,kind in objects:
  q.execute("select text from user_source where name=:n and type=:t order by line",n=name,t=kind)
  text="create or replace "+"".join(r[0]for r in q).replace("\r","")+"\n/\n"
  out["tmp/return471_"+name.lower()+"_"+kind.replace(" ","_").lower()+".sql"]=text
print(json.dumps(out))
