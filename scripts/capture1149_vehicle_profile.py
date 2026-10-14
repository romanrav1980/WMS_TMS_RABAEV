exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
files={};prefix="db/migrations/2026-10-14_ni022_vehicle_temperature/"
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 c.call_timeout=5000;q=c.cursor();q.execute("set transaction read only")
 q.execute("select sys_context('USERENV','CURRENT_SCHEMA'),sys_context('USERENV','DB_NAME')from dual");target=q.fetchone();assert target[0]=="RABAEV",target
 for typ,name,file in(("PACKAGE","RRL_VEHICLE_PROFILE_API","000_before_spec.sql"),("PACKAGE BODY","RRL_VEHICLE_PROFILE_API","000_before_body.sql")):
  q.execute("select TEXT from USER_SOURCE where NAME=:n and TYPE=:t order by LINE",n=name,t=typ)
  source="".join(x[0] for x in q).replace("\r\n","\n").replace("\r","")
  assert source.strip(),name;files[prefix+file]="create or replace "+source.rstrip()+"\n/\n"
 q.execute("select OBJECT_NAME,OBJECT_TYPE from USER_OBJECTS where STATUS='INVALID'order by OBJECT_NAME,OBJECT_TYPE");invalid=[list(x)for x in q]
 files[prefix+"checkpoint.json"]=json.dumps({"migration_id":"2026-10-14-1149-vehicle-temperature-profile","target":list(target),"captured_sources":["000_before_spec.sql","000_before_body.sql"],"invalid_baseline":invalid},indent=2)
 print(json.dumps(files))
