from pathlib import Path
import json,sys,hashlib
import oracledb
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment();sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"api/wms_api_server"))
from app.config import get_settings
s=get_settings();out={};f="db/migrations/2026-10-11_ni061_dispatch_decision/"
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select TRIGGER_NAME from USER_TRIGGERS where TABLE_NAME='RRL_INTERWARE_ONWARD_BIND'")
 for(name,)in q.fetchall():
  q.execute("select TEXT from USER_SOURCE where NAME=:n and TYPE='TRIGGER'order by LINE",n=name);out[f+"000_before_"+name.lower()+".sql"]="create or replace "+"".join(x[0]for x in q.fetchall()).strip()+"\n/\n"
for path in["api/wms_api_server/app/modules/inventory/infrastructure/interwarehouse_onward.py","api/wms_api_server/app/modules/inventory/infrastructure/interwarehouse_queue.sql","api/wms_api_server/app/modules/inventory/api/interwarehouse_routes.py","api/wms_api_server/app/modules/inventory/contracts_interwarehouse.py","api/wms_api_server/app/modules/inventory/infrastructure/interwarehouse.py","wiki-raw/wms_admin_ui_reference/interwarehouse.html","wiki-raw/wms_admin_ui_reference/interwarehouse.js"]:
 p=Path(path);out[f+"000_before_"+p.name]=p.read_text(encoding="utf-8")
print(json.dumps(out,ensure_ascii=True))
