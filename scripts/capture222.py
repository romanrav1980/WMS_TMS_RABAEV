from pathlib import Path
import json,hashlib,sys
import oracledb
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment();sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"api/wms_api_server"))
from app.config import get_settings
s=get_settings();out={};f="db/migrations/2026-10-11_ni052_unload_all_slots/"
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor()
 for name in["RRL_STOCK_UNLOAD_CMD","RRL_STOCK_HU_PLACEMENT_CORE","RRL_STOCK_HU_SLOT"]:
  parts=[]
  for kind in["PACKAGE","PACKAGE BODY"]:
   q.execute("select TEXT from USER_SOURCE where NAME=:n and TYPE=:t order by LINE",n=name,t=kind);rows=q.fetchall();assert rows
   parts.append("create or replace "+"".join(x[0]for x in rows).replace("\r\n","\n").strip()+"\n/\n")
  out[f+"000_before_"+name.lower()+".sql"]="\n".join(parts)
p=Path("db/migrations/2026-10-08_stock_posting_core/current_runtime_manifest.json");out[f+"000_before_manifest.json"]=p.read_text(encoding="utf-8")
out[f+"checkpoint.json"]=json.dumps({"migration_id":"2026-10-11-222-current-slots-all-unload-roots","sha256":{k:hashlib.sha256(v.encode()).hexdigest()for k,v in out.items()},"recovery":"Fresh unloaded admission owner and existing native slot/placement implementation. No quantity migration. Forward repair after new stock-root slot placement history."},indent=2)
print(json.dumps(out,ensure_ascii=True))
