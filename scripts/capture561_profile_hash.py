exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
import hashlib
folder=Path("db/migrations/2026-10-12_ni071_vehicle_source");out={}
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select count(*)from RRL_VEHICLE_PROFILE_HIST");assert q.fetchone()==(0,),"Earlier profile facts need legacy replay handling"
 parts=[]
 for kind in ["PACKAGE","PACKAGE BODY"]:
  q.execute("select TEXT from USER_SOURCE where NAME='RRL_VEHICLE_PROFILE_API'and TYPE=:kind order by LINE",kind=kind)
  parts.append("create or replace "+"".join(r[0]for r in q.fetchall()).replace("\r","").strip()+"\n/\n")
 out[str(folder/"000_before_source_hash.sql")]="\n".join(parts)
out[str(folder/"008_source_hash.sql")]=(folder/"002_profile_api.sql").read_text(encoding="utf-8")
p=folder/"checkpoint.json";m=json.loads(p.read_text(encoding="utf-8"));m["applied"]="55913/0/native VALID, no old trip inference"
m["hash_patch_sha256"]={k:hashlib.sha256(v.encode()).hexdigest()for k,v in out.items()}
out[str(p)]=json.dumps(m,indent=2)+"\n"
print(json.dumps(out))
