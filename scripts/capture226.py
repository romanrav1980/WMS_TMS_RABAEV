from pathlib import Path
import json,hashlib,sys
import oracledb
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment();sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"api/wms_api_server"))
from app.config import get_settings
s=get_settings();out={};f="db/migrations/2026-10-11_ni061_marked_receive/"
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor()
 for name in["RRL_STOCK_POSTING_API","RRL_STOCK_UNIT_CORE","RRL_STOCK_INTERWARE_REC","RRL_INTERWARE_UNIT_SOURCE","RRL_STOCK_QC_MARK"]:
  parts=[]
  for kind in["PACKAGE","PACKAGE BODY"]:
   q.execute("select TEXT from USER_SOURCE where NAME=:n and TYPE=:t order by LINE",n=name,t=kind);rows=q.fetchall();assert rows
   parts.append("create or replace "+"".join(x[0]for x in rows).replace("\r\n","\n").strip()+"\n/\n")
  out[f+"000_before_"+name.lower()+".sql"]="\n".join(parts)
 q.execute("select TRIGGER_NAME from USER_TRIGGERS where TABLE_NAME='RRL_WMS_RECEIPT_UNIT'order by TRIGGER_NAME")
 for(name,)in q.fetchall():
  q.execute("select TEXT from USER_SOURCE where NAME=:n and TYPE='TRIGGER' order by LINE",n=name)
  out[f+"000_before_"+name.lower()+".sql"]="create or replace "+"".join(x[0]for x in q.fetchall()).replace("\r\n","\n").strip()+"\n/\n"
 q.execute("select distinct NAME,TYPE from USER_DEPENDENCIES where REFERENCED_NAME='RRL_STOCK_UNIT_CORE'order by NAME,TYPE");out[f+"000_unit_dependents.json"]=json.dumps(q.fetchall(),ensure_ascii=True)
for p in["api/wms_api_server/app/modules/inventory/api/interwarehouse_routes.py","api/wms_api_server/app/modules/inventory/contracts_interwarehouse.py","api/wms_api_server/app/modules/inventory/infrastructure/interwarehouse.py","wiki-raw/wms_admin_ui_reference/interwarehouse.js","db/migrations/2026-10-08_stock_posting_core/current_runtime_manifest.json"]:
 out[f+"000_before_"+Path(p).name]=Path(p).read_text(encoding="utf-8")
out[f+"checkpoint.json"]=json.dumps({"migration_id":"2026-10-11-226-original-marked-interwarehouse-receive","sha256":{k:hashlib.sha256(v.encode()).hexdigest()for k,v in out.items()},"recovery":"Fresh current UNIT/receipt/root/source proof owner and unit guards. Same original physical-unit identities restored at target receiving cell/no new codes/HARD; original ship/journal retained. Forward repair after actual marked receiving."},indent=2)
print(json.dumps(out,ensure_ascii=True))
