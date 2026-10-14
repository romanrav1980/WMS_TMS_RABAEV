from pathlib import Path
import json,sys
import oracledb
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment();sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"api/wms_api_server"))
from app.config import get_settings
s=get_settings();out={};f="db/migrations/2026-10-11_ni061_task_replan/"
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor()
 for name in["RRL_STOCK_INTERWARE_PUT","RRL_STOCK_POSTING_API"]:
  parts=[]
  for kind in["PACKAGE","PACKAGE BODY"]:
   q.execute("select TEXT from USER_SOURCE where NAME=:n and TYPE=:t order by LINE",n=name,t=kind);rows=q.fetchall();assert rows,name;parts.append("create or replace "+"".join(x[0]for x in rows).strip()+"\n/\n")
  out[f+"000_before_"+name.lower()+".sql"]="\n".join(parts)
 q.execute("select TRIGGER_NAME from USER_TRIGGERS where TABLE_NAME='RRL_WAREHOUSE_TASK'")
 for(name,)in q.fetchall():
  q.execute("select TEXT from USER_SOURCE where NAME=:n and TYPE='TRIGGER'order by LINE",n=name);out[f+"000_before_"+name.lower()+".sql"]="create or replace "+"".join(x[0]for x in q.fetchall()).strip()+"\n/\n"
out[f+"000_manifest.json"]=Path("db/migrations/2026-10-08_stock_posting_core/current_runtime_manifest.json").read_text(encoding="utf-8")
for path in["api/wms_api_server/app/modules/inventory/api/interwarehouse_routes.py","api/wms_api_server/app/modules/inventory/infrastructure/interwarehouse.py","api/wms_api_server/app/modules/inventory/contracts_interwarehouse.py","api/wms_api_server/app/modules/inventory/infrastructure/interwarehouse_queue.sql","wiki-raw/wms_admin_ui_reference/interwarehouse.js","wiki-raw/wms_admin_ui_reference/interwarehouse.html"]:
 p=Path(path);out[f+"000_before_"+p.name]=p.read_text(encoding="utf-8")
print(json.dumps(out,ensure_ascii=True))
