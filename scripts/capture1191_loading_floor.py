exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
f={};root="db/migrations/2026-10-14_ni052_loading_floor/"
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("set transaction read only")
 for name in("RRL_STOCK_HU_LOAD_CORE","RRL_STOCK_TRIP_DEPART_CMD","RRL_TRANSPORT_PLAN_RULES"):
  for typ,suffix in(("PACKAGE","spec"),("PACKAGE BODY","body")):
   q.execute("select TEXT from USER_SOURCE where NAME=:name and TYPE=:typ order by LINE",name=name,typ=typ)
   source="".join(x[0]for x in q).replace("\r\n","\n").replace("\r","");assert source.strip()
   f[root+"000_"+name.lower()+"_"+suffix+".sql"]="create or replace "+source.rstrip()+"\n/\n"
 q.execute("select OBJECT_NAME,OBJECT_TYPE from USER_OBJECTS where STATUS='INVALID'order by OBJECT_NAME,OBJECT_TYPE")
 f[root+"checkpoint.json"]=json.dumps({"migration_id":"2026-10-14-1191-loading-floor","target":"RABAEV/orcl","state":"PREPARED_NOT_APPLIED","captured_sources":list(f),"invalid_baseline":[list(x)for x in q]},indent=2)
print(json.dumps(f))
