import sys,json,hashlib
from pathlib import Path
import oracledb
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment();sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"api/wms_api_server"))
from app.config import get_settings
s=get_settings();out={};f="db/migrations/2026-10-11_ni042_case_mass/"
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor()
 for name,stem,types in [("RRL_STOCK_HU_READ","read",("PACKAGE","PACKAGE BODY")),("RRL_WH_FINAL_SCALE_ADMISSION","admission",("PACKAGE","PACKAGE BODY")),("RRL_STOCK_LOAD_BOX_CORE","boxes",("PACKAGE","PACKAGE BODY")),("RRL_STOCK_HU_LOAD_CORE","load",("PACKAGE","PACKAGE BODY")),("RRL_STOCK_STORE_RECEIPT_READ","store",("PACKAGE","PACKAGE BODY")),("RRL_TT_LOAD_BOX_WEIGHT_GUARD","guard",("TRIGGER",))]:
  parts=[]
  for kind in types:
   q.execute("select TEXT from USER_SOURCE where NAME=:name and TYPE=:kind order by LINE",name=name,kind=kind)
   parts.append("create or replace "+"".join(x[0]for x in q.fetchall()).replace("\r\r\n","\n").replace("\r\n","\n").strip()+"\n/\n")
  out[f+"000_before_"+stem+".sql"]="\n".join(parts)
 q.execute("select COLUMN_NAME,DATA_TYPE,NULLABLE from USER_TAB_COLUMNS where TABLE_NAME='RRL_TT_LOAD_BOX_WEIGHT'order by COLUMN_ID")
 out[f+"000_before_columns.json"]=json.dumps(q.fetchall(),indent=2)
 q.execute("select CONSTRAINT_NAME,CONSTRAINT_TYPE,SEARCH_CONDITION_VC,R_CONSTRAINT_NAME from USER_CONSTRAINTS where TABLE_NAME='RRL_TT_LOAD_BOX_WEIGHT'")
 out[f+"000_before_constraints.json"]=json.dumps(q.fetchall(),indent=2)
for path in("api/wms_api_server/app/modules/inventory/infrastructure/warehouse_hu.py","db/migrations/2026-10-08_stock_posting_core/current_runtime_manifest.json"):
 out[f+"000_before_"+Path(path).name]=Path(path).read_text(encoding="utf-8")
out[f+"checkpoint.json"]=json.dumps({"migration_id":"2026-10-11-207-case-measured-mass-manifest","sha256":{k:hashlib.sha256(v.encode()).hexdigest()for k,v in out.items()},"recovery":"Fresh existing HU/read/load/box/store/guard and exact constraints. Existing ordinary box identities retained, new CASE FK plus virtual ordinary FK, no historical fact rewrite/no second physical box; paired rollback before CASE load records, otherwise forward repair. No DB copy."},indent=2)
print(json.dumps(out,ensure_ascii=True))
