import sys,json,hashlib
from pathlib import Path
import oracledb
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment();sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"api/wms_api_server"))
from app.config import get_settings
out={};f="db/migrations/2026-10-11_ni042_final_scale/"
s=get_settings()
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor()
 for package,name in [("RRL_WH_SCALE_API","archive"),("RRL_CASE_SCALE_ADMISSION","admission"),("RRL_STOCK_PALLET_QC_CMD","qc")]:
  chunks=[]
  for kind in("PACKAGE","PACKAGE BODY"):
   q.execute("select TEXT from USER_SOURCE where NAME=:name and TYPE=:kind order by LINE",name=package,kind=kind)
   chunks.append("create or replace "+"".join(x[0]for x in q.fetchall()).replace("\r\r\n","\n").replace("\r\n","\n").strip()+"\n/\n")
  out[f+"000_before_"+name+".sql"]="\n".join(chunks)
 for name in("RRL_WH_SCALE_CAPTURE","RRL_WH_SCALE_DEVICE"):
  q.execute("select COLUMN_NAME,DATA_TYPE,NULLABLE from USER_TAB_COLUMNS where TABLE_NAME=:name order by COLUMN_ID",name=name)
  out[f+"000_before_"+name.lower()+".json"]=json.dumps(q.fetchall(),indent=2)
for path in("api/wms_api_server/app/modules/inventory/contracts_warehouse_scale.py","api/wms_api_server/app/modules/inventory/infrastructure/warehouse_scales.py","api/wms_api_server/app/modules/inventory/api/warehouse_scale_routes.py","db/migrations/2026-10-08_stock_posting_core/current_runtime_manifest.json"):
 out[f+"000_before_"+Path(path).name]=Path(path).read_text(encoding="utf-8")
out[f+"checkpoint.json"]=json.dumps({"migration_id":"2026-10-11-204-final-scale-archive","sha256":{k:hashlib.sha256(v.encode()).hexdigest()for k,v in out.items()},"recovery":"Fresh addressed archive/admission/QC and schema captured; same existing archive/device/validator extended by explicit purpose; paired rollback only while no final captures, otherwise forward repair; no DB copy"},indent=2)
print(json.dumps(out,ensure_ascii=True))
