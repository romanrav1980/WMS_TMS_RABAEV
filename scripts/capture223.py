from pathlib import Path
import json,hashlib,sys
import oracledb
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment();sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"api/wms_api_server"))
from app.config import get_settings
s=get_settings();out={};f="db/migrations/2026-10-11_ni052_single_load_slot_release/"
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor()
 for name in["RRL_STOCK_SINGLE_LOAD_CMD","RRL_STOCK_HU_PLACEMENT_CORE","RRL_STOCK_HU_SHIP_CMD"]:
  parts=[]
  for kind in["PACKAGE","PACKAGE BODY"]:
   q.execute("select TEXT from USER_SOURCE where NAME=:n and TYPE=:t order by LINE",n=name,t=kind);rows=q.fetchall();assert rows
   parts.append("create or replace "+"".join(x[0]for x in rows).replace("\r\n","\n").strip()+"\n/\n")
  out[f+"000_before_"+name.lower()+".sql"]="\n".join(parts)
 q.execute("select TEXT from USER_SOURCE where NAME='RRL_HU_CLAIM_IDENTITY_GUARD' and TYPE='TRIGGER' order by LINE");out[f+"000_before_guard.sql"]="create or replace "+"".join(x[0]for x in q.fetchall()).replace("\r\n","\n").strip()+"\n/\n"
p=Path("db/migrations/2026-10-08_stock_posting_core/current_runtime_manifest.json");out[f+"000_before_manifest.json"]=p.read_text(encoding="utf-8")
out[f+"checkpoint.json"]=json.dumps({"migration_id":"2026-10-11-223-single-fullpal-load-slot-release","sha256":{k:hashlib.sha256(v.encode()).hexdigest()for k,v in out.items()},"recovery":"Fresh existing SINGLE loading, native placement owner and current identity guard; no schema migration. Release existing source occupancy through same quantity transaction; forward repair after newly supported completed load."},indent=2)
print(json.dumps(out,ensure_ascii=True))
