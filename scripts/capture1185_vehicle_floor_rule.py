exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
f={};root="db/migrations/2026-10-14_ni022_vehicle_floor_rule/"
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("set transaction read only")
 for name in("RRL_VEHICLE_PROFILE_API","RRL_TRANSPORT_PLAN_RULES"):
  for typ,suffix in(("PACKAGE","spec"),("PACKAGE BODY","body")):
   q.execute("select TEXT from USER_SOURCE where NAME=:name and TYPE=:typ order by LINE",name=name,typ=typ)
   source="".join(x[0]for x in q).replace("\r\n","\n").replace("\r","");assert source.strip()
   f[root+"000_"+name.lower()+"_"+suffix+".sql"]="create or replace "+source.rstrip()+"\n/\n"
 f[root+"checkpoint.json"]=json.dumps({"migration_id":"2026-10-14-1185-vehicle-floor-rule","target":"RABAEV/orcl","state":"PREPARED_NOT_APPLIED","captured_sources":list(f)},indent=2)
print(json.dumps(f))
