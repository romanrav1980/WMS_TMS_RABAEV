from pathlib import Path
import json,sys,hashlib
import oracledb
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment();sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"api/wms_api_server"))
from app.config import get_settings
s=get_settings();out={};f="db/migrations/2026-10-11_ni053_marked_recipient/"
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor()
 for name in["RRL_STOCK_POSTING_API","RRL_STOCK_STORE_RECEIPT_CMD","RRL_STOCK_STORE_RECEIPT_READ","RRL_STOCK_STORE_DISPOSITION","RRL_STOCK_STORE_WEIGHT_CORE"]:
  parts=[]
  for kind in["PACKAGE","PACKAGE BODY"]:
   q.execute("select TEXT from USER_SOURCE where NAME=:n and TYPE=:t order by LINE",n=name,t=kind);rows=q.fetchall();assert rows,name;parts.append("create or replace "+"".join(x[0]for x in rows).strip()+"\n/\n")
  out[f+"000_before_"+name.lower()+".sql"]="\n".join(parts)
 q.execute("select COLUMN_NAME,DATA_TYPE from USER_TAB_COLUMNS where TABLE_NAME='RRL_STORE_RECEIPT_FACT'order by COLUMN_ID");out[f+"000_receipt_columns.json"]=json.dumps(q.fetchall())
for path in["db/migrations/2026-10-08_stock_posting_core/current_runtime_manifest.json","api/wms_api_server/app/modules/delivery/api/store_receipt_routes.py","api/wms_api_server/app/modules/delivery/infrastructure/store_receipt.py"]:
 p=Path(path)
 if p.exists():out[f+"000_before_"+p.name]=p.read_text(encoding="utf-8")
out[f+"checkpoint.json"]=json.dumps({"migration_id":"2026-10-11-229-original-marked-store-recipient","sha256":{k:hashlib.sha256(v.encode()).hexdigest()for k,v in out.items()}},indent=2)
print(json.dumps(out,ensure_ascii=True))
