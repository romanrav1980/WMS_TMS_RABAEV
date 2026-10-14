import sys,json,hashlib
from pathlib import Path
import oracledb
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment();sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"api/wms_api_server"))
from app.config import get_settings
s=get_settings();out={};f="db/migrations/2026-10-11_ni052_unload/"
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor()
 packages=[("RRL_STOCK_POSTING_API","root"),("RRL_STOCK_BALANCE_CORE","balance"),("RRL_STOCK_RESERVE_CORE","reserve"),("RRL_STOCK_FULFILLMENT_FACT","fulfillment")]
 triggers=[("RRL_TT_HU_LOAD_FACT_GUARD","load_guard"),("RRL_TT_HU_LOAD_ST_GUARD","member_guard"),("RRL_QC_STAMP_GUARD","qc_guard"),("RRL_QC_SAMPLE_GUARD","sample_guard"),("RRL_TT_LOADED_ST_ASSIGN_GUARD","st_guard")]
 for name,stem in packages+triggers:
  parts=[]
  for kind in(("TRIGGER",)if(name,stem)in triggers else("PACKAGE","PACKAGE BODY")):
   q.execute("select TEXT from USER_SOURCE where NAME=:p_name and TYPE=:p_kind order by LINE",p_name=name,p_kind=kind)
   rows=q.fetchall();assert rows,(name,kind)
   parts.append("create or replace "+"".join(x[0]for x in rows).replace("\r\r\n","\n").replace("\r\n","\n").strip()+"\n/\n")
  out[f+"000_before_"+stem+".sql"]="\n".join(parts)
 q.execute("select CONSTRAINT_NAME,SEARCH_CONDITION_VC from USER_CONSTRAINTS where TABLE_NAME='RRL_TT_HU_LOAD_FACT'and CONSTRAINT_TYPE='C'and SEARCH_CONDITION_VC not like '%IS NOT NULL%'")
 out[f+"000_before_constraints.json"]=json.dumps(q.fetchall(),indent=2)
 q.execute("select COLUMN_NAME,DATA_TYPE from USER_TAB_COLUMNS where TABLE_NAME='RRL_CUSTOMER_ORDER_FULFILLMENT'order by COLUMN_ID")
 out[f+"000_before_fulfillment_columns.json"]=json.dumps(q.fetchall(),indent=2)
for p in("api/wms_api_server/app/modules/inventory/contracts_stock.py","api/wms_api_server/app/modules/transport/api/loading_routes.py","api/wms_api_server/app/modules/transport/infrastructure/loading.py","api/wms_api_server/app/modules/transport/contracts.py","db/migrations/2026-10-08_stock_posting_core/current_runtime_manifest.json"):
 out[f+"000_before_"+Path(p).name]=Path(p).read_text(encoding="utf-8")
out[f+"checkpoint.json"]=json.dumps({"migration_id":"2026-10-11-212-standalone-case-unload","sha256":{k:hashlib.sha256(v.encode()).hexdigest()for k,v in out.items()},"recovery":"Fresh exact root/stock owner/specACL/load/member/QC guards/application contract; additive immutable unloading journal and source status. Rollback only without unload history; after actual goods restoration use forward repair or explicit later physical load, no deleting movements/database copy."},indent=2)
print(json.dumps(out,ensure_ascii=True))
