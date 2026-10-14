import sys,json,hashlib
from pathlib import Path
import oracledb
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment();sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"api/wms_api_server"))
from app.config import get_settings
s=get_settings();out={};f="db/migrations/2026-10-11_ni052_unload_units/"
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor()
 for name,stem in [("RRL_STOCK_UNLOAD_CMD","unload"),("RRL_STOCK_UNIT_CORE","unit")]:
  parts=[]
  for kind in ["PACKAGE","PACKAGE BODY"]:
   q.execute("select TEXT from USER_SOURCE where NAME=:p_name and TYPE=:p_kind order by LINE",p_name=name,p_kind=kind);rows=q.fetchall();assert rows
   parts.append("create or replace "+"".join(x[0]for x in rows).replace("\r\r\n","\n").replace("\r\n","\n").strip()+"\n/\n")
  out[f+"000_before_"+stem+".sql"]="\n".join(parts)
out[f+"000_before_manifest.json"]=Path("db/migrations/2026-10-08_stock_posting_core/current_runtime_manifest.json").read_text(encoding="utf-8")
out[f+"checkpoint.json"]=json.dumps({"migration_id":"2026-10-11-213-unload-original-units","sha256":{k:hashlib.sha256(v.encode()).hexdigest()for k,v in out.items()},"recovery":"Fresh native owner snapshot. Restore only without actual marked unload history; otherwise forward repair preserving original issued and recovery journal."},indent=2)
print(json.dumps(out,ensure_ascii=True))
