exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
f={};root="db/migrations/2026-10-14_ni052_departure_temperature/"
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 c.call_timeout=5000;q=c.cursor();q.execute("set transaction read only")
 for name in("RRL_STOCK_LOAD_THERMAL","RRL_STOCK_TRIP_DEPART_CMD"):
  for typ,suffix in(("PACKAGE","spec"),("PACKAGE BODY","body")):
   q.execute("select TEXT from USER_SOURCE where NAME=:n and TYPE=:t order by LINE",n=name,t=typ)
   source="".join(x[0]for x in q).replace("\r\n","\n").replace("\r","");assert source.strip()
   f[root+"000_"+name.lower()+"_"+suffix+".sql"]="create or replace "+source.rstrip()+"\n/\n"
 print(json.dumps(f))
