import sys,json,hashlib
from pathlib import Path
import oracledb
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment();sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"api/wms_api_server"))
from app.config import get_settings
s=get_settings();out={};f="db/migrations/2026-10-11_ni052_unload_fullpal/"
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor()
 for name,stem in [("RRL_STOCK_UNLOAD_CMD","unload"),("RRL_STOCK_FULFILLMENT_FACT","fulfillment")]:
  parts=[]
  for kind in["PACKAGE","PACKAGE BODY"]:
   q.execute("select TEXT from USER_SOURCE where NAME=:p_name and TYPE=:p_kind order by LINE",p_name=name,p_kind=kind);rows=q.fetchall();assert rows,(name,kind)
   parts.append("create or replace "+"".join(x[0]for x in rows).replace("\r\r\n","\n").replace("\r\n","\n").strip()+"\n/\n")
  out[f+"000_before_"+stem+".sql"]="\n".join(parts)
for p in["api/wms_api_server/app/modules/transport/infrastructure/loading.py","wiki-raw/wms_admin_ui_reference/transport-unloading.js","db/migrations/2026-10-08_stock_posting_core/current_runtime_manifest.json"]:
 out[f+"000_before_"+Path(p).name]=Path(p).read_text(encoding="utf-8")
out[f+"checkpoint.json"]=json.dumps({"migration_id":"2026-10-11-217-fullpal-original-unload","sha256":{k:hashlib.sha256(v.encode()).hexdigest()for k,v in out.items()},"recovery":"Fresh owner/checkpoint. Restore original positive P/H/units through same root; old full-pallet task and shipping history retained; current picked physical stock version refreshed in fulfillment. Forward repair after actual stock reversal."},indent=2)
print(json.dumps(out,ensure_ascii=True))
