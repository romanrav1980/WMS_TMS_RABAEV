exec(open("scripts/ni063_slow_queries.py",encoding="utf-8").read().split("with oracledb.connect",1)[0])
import hashlib
folder="db/migrations/2026-10-12_ni071_vehicle_source/";out={}
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor()
 q.execute("select USER from dual");assert q.fetchone()==("RABAEV",)
 parts=[]
 for kind in ["PACKAGE","PACKAGE BODY"]:
  q.execute("select TEXT from USER_SOURCE where NAME='RRL_STOCK_TRIP_DEPART_CMD'and TYPE=:kind order by LINE",kind=kind)
  rows=q.fetchall();assert rows;parts.append("create or replace "+"".join(r[0]for r in rows).replace("\r","").strip()+"\n/\n")
 out[folder+"000_before_depart.sql"]="\n".join(parts)
 for table in ["RRL_TR_VEHICLE","RRL_TRANSPORT_TASK"]:
  q.execute("select COLUMN_NAME,DATA_TYPE from USER_TAB_COLUMNS where TABLE_NAME=:table_name order by COLUMN_ID",table_name=table)
  out[folder+"000_"+table.lower()+"_columns.json"]=json.dumps(q.fetchall(),indent=2)
out[folder+"checkpoint.json"]=json.dumps({"migration_id":"2026-10-12-559-vehicle-source-at-departure","prepared":True,"source_sha256":{k:hashlib.sha256(v.encode()).hexdigest()for k,v in out.items()},"recovery":"Additive vehicle physical profiles; immutable source on original departure; no old source inference or quantity writer. Restore captured native before live facts only, otherwise forward repair."},indent=2)
print(json.dumps(out))
