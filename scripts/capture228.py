from pathlib import Path
import json,sys,hashlib
import oracledb
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment();sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"api/wms_api_server"))
from app.config import get_settings
s=get_settings();out={};f="db/migrations/2026-10-11_ni061_marked_onward/"
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor()
 for name in["RRL_STOCK_POSTING_API","RRL_STOCK_INTERWARE_NEXT","RRL_STOCK_SHIPPING_CORE","RRL_STOCK_SINGLE_LOAD_CMD","RRL_STOCK_LOADING_READ","RRL_STOCK_INTERWARE_CUSTODY"]:
  parts=[]
  for kind in["PACKAGE","PACKAGE BODY"]:
   q.execute("select TEXT from USER_SOURCE where NAME=:n and TYPE=:t order by LINE",n=name,t=kind);parts.append("create or replace "+"".join(x[0]for x in q.fetchall()).strip()+"\n/\n")
  out[f+"000_before_"+name.lower()+".sql"]="\n".join(parts)
for path in["db/migrations/2026-10-08_stock_posting_core/current_runtime_manifest.json","api/wms_api_server/app/modules/inventory/infrastructure/interwarehouse_onward.py"]:out[f+"000_before_"+Path(path).name]=Path(path).read_text(encoding="utf-8")
out[f+"checkpoint.json"]=json.dumps({"migration_id":"2026-10-11-228-original-marked-interwarehouse-onward","sha256":{k:hashlib.sha256(v.encode()).hexdigest()for k,v in out.items()}},indent=2)
print(json.dumps(out,ensure_ascii=True))
