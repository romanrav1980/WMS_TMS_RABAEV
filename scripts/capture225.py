from pathlib import Path
import json,hashlib,sys
import oracledb
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment();sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"api/wms_api_server"))
from app.config import get_settings
s=get_settings();out={};f="db/migrations/2026-10-11_ni061_marked_source/"
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor()
 for name in["RRL_INTERWARE_PLAN_GUARD","RRL_INTERWARE_HOP_LIMIT_GUARD"]:
  q.execute("select TEXT from USER_SOURCE where NAME=:n and TYPE='TRIGGER' order by LINE",n=name);rows=q.fetchall();assert rows
  out[f+"000_before_"+name.lower()+".sql"]="create or replace "+"".join(x[0]for x in rows).replace("\r\n","\n").strip()+"\n/\n"
 for name in["RRL_STOCK_INTERWARE_REC","RRL_STOCK_UNIT_CORE"]:
  parts=[]
  for kind in["PACKAGE","PACKAGE BODY"]:
   q.execute("select TEXT from USER_SOURCE where NAME=:n and TYPE=:t order by LINE",n=name,t=kind);rows=q.fetchall();assert rows
   parts.append("create or replace "+"".join(x[0]for x in rows).replace("\r\n","\n").strip()+"\n/\n")
  out[f+"000_before_"+name.lower()+".sql"]="\n".join(parts)
for p in["api/wms_api_server/app/modules/inventory/infrastructure/interwarehouse.py","db/migrations/2026-10-08_stock_posting_core/current_runtime_manifest.json"]:
 out[f+"000_before_"+Path(p).name]=Path(p).read_text(encoding="utf-8")
out[f+"checkpoint.json"]=json.dumps({"migration_id":"2026-10-11-225-marked-original-interwarehouse-source","sha256":{k:hashlib.sha256(v.encode()).hexdigest()for k,v in out.items()},"recovery":"Fresh original source plan/hop guard/unit and receipt owners. Metadata-only source plan extension; no goods birth until separate receiving command. Original exact physical unit fingerprint, current ISSUED set and multiple marking profiles retained; no government ACK fabricated."},indent=2)
print(json.dumps(out,ensure_ascii=True))
