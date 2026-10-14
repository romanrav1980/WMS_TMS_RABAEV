exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
out={};folder="db/migrations/2026-10-12_ni071_vehicle_source/"
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();parts=[]
 for kind in ["PACKAGE","PACKAGE BODY"]:
  q.execute("select TEXT from USER_SOURCE where NAME='RRL_STOCK_CONFIG_API'and TYPE=:kind order by LINE",kind=kind)
  parts.append("create or replace "+"".join(row[0]for row in q.fetchall()).replace("\r","").strip()+"\n/\n")
 out[folder+"000_before_config_fleet.sql"]="\n".join(parts)
print(json.dumps(out))
