from pathlib import Path
import json,hashlib,sys
import oracledb
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment();sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"api/wms_api_server"))
from app.config import get_settings
s=get_settings();out={};f="db/migrations/2026-10-11_ni063_offer_cancel/"
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor()
 for name in["RRL_STOCK_POSTING_API","RRL_STOCK_TARE_CMD","RRL_STOCK_TARE_HANDOVER","RRL_STOCK_TARE_RESOLVE","RRL_TARE_PARTICIPANT","RRL_STOCK_UNLOAD_CMD"]:
  parts=[]
  for kind in["PACKAGE","PACKAGE BODY"]:
   q.execute("select TEXT from USER_SOURCE where NAME=:n and TYPE=:t order by LINE",n=name,t=kind);rows=q.fetchall();assert rows,(name,kind)
   parts.append("create or replace "+"".join(x[0]for x in rows).replace("\r\n","\n").strip()+"\n/\n")
  out[f+"000_before_"+name.lower()+".sql"]="\n".join(parts)
 q.execute("select trigger_name from user_triggers where table_name in('RRL_TARE_OFFER','RRL_TARE_OFFER_BOOK')")
 for(name,)in q.fetchall():
  q.execute("select TEXT from USER_SOURCE where NAME=:n and TYPE='TRIGGER' order by LINE",n=name)
  out[f+"000_before_"+name.lower()+".sql"]="create or replace "+"".join(x[0]for x in q.fetchall()).replace("\r\n","\n").strip()+"\n/\n"
for p in["db/migrations/2026-10-08_stock_posting_core/current_runtime_manifest.json","api/wms_api_server/app/modules/inventory/contracts_stock.py","api/wms_api_server/app/modules/inventory/api/tare_routes.py","api/wms_api_server/app/modules/inventory/infrastructure/tare.py","api/wms_api_server/app/modules/inventory/infrastructure/tare_assembly.py"]:
 out[f+"000_before_"+Path(p).name]=Path(p).read_text(encoding="utf-8")
out[f+"checkpoint.json"]=json.dumps({"migration_id":"2026-10-11-219-unaccepted-tare-offer-cancel","sha256":{k:hashlib.sha256(v.encode()).hexdigest()for k,v in out.items()},"recovery":"Fresh original command/participant/handover/unload owner and application sources. Additive cancellation fact; original offer and book associations never deleted. Forward repair after cancellation history."},indent=2)
print(json.dumps(out,ensure_ascii=True))
