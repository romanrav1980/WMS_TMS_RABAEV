import sys,json,hashlib
from pathlib import Path
import oracledb
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment();sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"api/wms_api_server"))
from app.config import get_settings
s=get_settings();out={};f="db/migrations/2026-10-11_ni052_unload_slot/"
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor()
 for name,stem in [("RRL_STOCK_UNLOAD_CMD","unload"),("RRL_STOCK_HU_SLOT","slot"),("RRL_STOCK_HU_PLACEMENT_CORE","placement")]:
  parts=[]
  for kind in ["PACKAGE","PACKAGE BODY"]:
   q.execute("select TEXT from USER_SOURCE where NAME=:p_name and TYPE=:p_kind order by LINE",p_name=name,p_kind=kind);rows=q.fetchall();assert rows,(name,kind)
   parts.append("create or replace "+"".join(x[0]for x in rows).replace("\r\r\n","\n").replace("\r\n","\n").strip()+"\n/\n")
  out[f+"000_before_"+stem+".sql"]="\n".join(parts)
 q.execute("select TRIGGER_NAME,TABLE_NAME from USER_TRIGGERS where TABLE_NAME in('RRL_WAREHOUSE_TASK','RRL_RECEIPT_SLOT_CLAIM','RRL_WAREHOUSE_TASK_SYNC')order by TRIGGER_NAME")
 triggers=q.fetchall();out[f+"000_trigger_inventory.json"]=json.dumps(triggers,indent=2)
 for name,table in triggers:
  q.execute("select TEXT from USER_SOURCE where NAME=:p_name and TYPE='TRIGGER'order by LINE",p_name=name);rows=q.fetchall()
  out[f+"000_before_"+name.lower()+".sql"]="create or replace "+"".join(x[0]for x in rows).replace("\r\r\n","\n").replace("\r\n","\n").strip()+"\n/\n"
for p in ["api/wms_api_server/app/modules/transport/api/unloading_routes.py","wiki-raw/wms_admin_ui_reference/transport-unloading.js","wiki-raw/wms_admin_ui_reference/transport-loading.html","db/migrations/2026-10-08_stock_posting_core/current_runtime_manifest.json"]:
 out[f+"000_before_"+Path(p).name]=Path(p).read_text(encoding="utf-8")
out[f+"checkpoint.json"]=json.dumps({"migration_id":"2026-10-11-215-unload-current-storage-slot","sha256":{k:hashlib.sha256(v.encode()).hexdigest()for k,v in out.items()},"recovery":"Exact owner/guards/API/UI checkpoint; reuse native target_json/record_place with CELL_X and SLOT locks; forward repair after actual placed unload history."},indent=2)
print(json.dumps(out,ensure_ascii=True))
