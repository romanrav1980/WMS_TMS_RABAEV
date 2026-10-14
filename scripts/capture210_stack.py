import sys,json,hashlib
from pathlib import Path
import oracledb
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment();sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"api/wms_api_server"))
from app.config import get_settings
s=get_settings();out={};f="db/migrations/2026-10-11_ni042_stack_stage/"
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();parts=[]
 for kind in("PACKAGE","PACKAGE BODY"):
  q.execute("select TEXT from USER_SOURCE where NAME='RRL_CASE_ROUTE_ADMISSION'and TYPE=:p_kind order by LINE",p_kind=kind)
  parts.append("create or replace "+"".join(x[0]for x in q.fetchall()).replace("\r\r\n","\n").replace("\r\n","\n").strip()+"\n/\n")
 out[f+"000_before_route.sql"]="\n".join(parts)
for p in("api/wms_api_server/app/modules/master_data/contracts.py","api/wms_api_server/app/modules/master_data/infrastructure/receipt_policy.py","db/migrations/2026-10-08_stock_posting_core/current_runtime_manifest.json"):
 out[f+"000_before_"+Path(p).name]=Path(p).read_text(encoding="utf-8")
out[f+"checkpoint.json"]=json.dumps({"migration_id":"2026-10-11-210-case-stacking-stage","sha256":{k:hashlib.sha256(v.encode()).hexdigest()for k,v in out.items()},"recovery":"Additive stage columns and small metadata guard; fresh route/contracts/repository sources. Rollback only without explicit staged policies/issued rows; otherwise forward repair, no stock delete or database copy."},indent=2)
print(json.dumps(out,ensure_ascii=True))
