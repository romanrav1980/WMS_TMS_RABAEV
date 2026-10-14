exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
out={};root="db/migrations/2026-10-14_ni052_loading_temperature/"
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 c.call_timeout=5000;q=c.cursor();q.execute("set transaction read only")
 q.execute("select user,sys_context('USERENV','SERVICE_NAME')from dual");target=q.fetchone();assert target==("RABAEV","orcl"),target
 for name in("RRL_STOCK_HU_LOAD_CORE","RRL_STOCK_TRIP_DEPART_CMD"):
  for typ,suffix in(("PACKAGE","spec"),("PACKAGE BODY","body")):
   q.execute("select TEXT from USER_SOURCE where NAME=:n and TYPE=:t order by LINE",n=name,t=typ)
   source="".join(x[0] for x in q).replace("\r\n","\n").replace("\r","");assert source.strip(),(name,typ)
   out[root+"000_"+name.lower()+"_"+suffix+".sql"]="create or replace "+source.rstrip()+"\n/\n"
 q.execute("select COLUMN_NAME,DATA_TYPE from USER_TAB_COLUMNS where TABLE_NAME='RRL_STOCK_OPERATION'order by COLUMN_ID");columns=[list(x)for x in q]
 q.execute("select OBJECT_NAME,OBJECT_TYPE from USER_OBJECTS where STATUS='INVALID'order by OBJECT_NAME,OBJECT_TYPE");invalid=[list(x)for x in q]
 out[root+"checkpoint.json"]=json.dumps({"migration_id":"2026-10-14-1160-loading-temperature","target":list(target),"captured_sources":list(out),"operation_columns":columns,"invalid_baseline":invalid,"state":"CAPTURED_NOT_IMPLEMENTED"},indent=2)
 print(json.dumps(out))
