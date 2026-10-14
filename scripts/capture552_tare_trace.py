exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
import hashlib
folder="db/migrations/2026-10-12_ni063_damage_custody/"
out={}
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor()
 q.execute("select USER,sys_context('USERENV','SERVICE_NAME')from dual");target=q.fetchone();assert target[0]=="RABAEV",target
 q.execute("select OBJECT_NAME,OBJECT_TYPE from USER_OBJECTS where STATUS='INVALID'and OBJECT_NAME not like 'BIN$%'");assert not q.fetchall()
 for name,stem in [("RRL_STOCK_TARE_CMD","tare"),("RRL_STOCK_TARE_RESOLVE","resolve"),("RRL_STOCK_TARE_LOSS","loss")]:
  parts=[]
  for kind in ["PACKAGE","PACKAGE BODY"]:
   q.execute("select TEXT from USER_SOURCE where NAME=:name and TYPE=:kind order by LINE",name=name,kind=kind)
   rows=q.fetchall();assert rows
   parts.append("create or replace "+"".join(row[0]for row in rows).replace("\r","").strip()+"\n/\n")
  out[folder+"000_before_"+stem+".sql"]="\n".join(parts)
 for name in ["RRL_TARE_ASSERT_WRITE"]:
  q.execute("select TEXT from USER_SOURCE where NAME=:name order by LINE",name=name)
  out[folder+"000_"+name.lower()+".sql"]="".join(row[0]for row in q.fetchall()).replace("\r","")
out[folder+"checkpoint.json"]=json.dumps({"migration_id":"2026-10-12-552-tare-damage-custody","target":target,"source_sha256":{k:hashlib.sha256(v.encode()).hexdigest()for k,v in out.items()},"recovery":"Additive provenance only for new DAMAGE; current native source saved. Rollback only before origin/move/writeoff facts; after use forward repair, do not delete stock history."},indent=2)
print(json.dumps(out))
