from pathlib import Path
import json,hashlib,sys
import oracledb
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment();sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"api/wms_api_server"))
from app.config import get_settings
s=get_settings();out={};f="db/migrations/2026-10-11_ni052_single_load_scope/"
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor()
 for name in["RRL_STOCK_POSTING_API","RRL_STOCK_LOADING_READ"]:
  parts=[]
  for kind in["PACKAGE","PACKAGE BODY"]:
   q.execute("select TEXT from USER_SOURCE where NAME=:n and TYPE=:t order by LINE",n=name,t=kind);rows=q.fetchall();assert rows
   parts.append("create or replace "+"".join(x[0]for x in rows).replace("\r\n","\n").strip()+"\n/\n")
  out[f+"000_before_"+name.lower()+".sql"]="\n".join(parts)
for p in["api/wms_api_server/app/modules/transport/contracts.py","api/wms_api_server/app/modules/transport/api/loading_routes.py","api/wms_api_server/app/modules/transport/infrastructure/loading.py","db/migrations/2026-10-08_stock_posting_core/current_runtime_manifest.json"]:
 out[f+"000_before_"+Path(p).name]=Path(p).read_text(encoding="utf-8")
out[f+"checkpoint.json"]=json.dumps({"migration_id":"2026-10-11-224-single-loading-current-warehouse","sha256":{k:hashlib.sha256(v.encode()).hexdigest()for k,v in out.items()},"recovery":"Fresh root/loading read and exact API/public port/adapter. Read/authorization-only; no quantity/schema migration. Current warehouse before committed replay and after actual waits; native selected source rules unchanged."},indent=2)
print(json.dumps(out,ensure_ascii=True))
