import sys,json,hashlib
from pathlib import Path
import oracledb
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment();sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"api/wms_api_server"))
from app.config import get_settings
s=get_settings();out={};f="db/migrations/2026-10-11_ni052_unload_hu/"
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();c.call_timeout=15000
 packages=[("RRL_STOCK_UNLOAD_CMD","unload"),("RRL_STOCK_FULFILLMENT_FACT","fulfillment"),("RRL_STOCK_RESERVE_CORE","reserve"),("RRL_STOCK_HU_READ","hu_read")]
 triggers=[("RRL_TT_UNLOAD_FACT_GUARD","unload_guard"),("RRL_TT_HU_LOAD_FACT_GUARD","load_guard"),("RRL_TT_HU_LOAD_ST_GUARD","member_guard"),("RRL_QC_SAMPLE_GUARD","sample_guard"),("RRL_HU_LINK_WRITE_GUARD","link_guard"),("RRL_HU_TARE_LINK_GUARD","tare_guard"),("RRL_HU_CONTAINER_GUARD","container_guard")]
 for name,stem in packages+triggers:
  parts=[]
  for kind in ["TRIGGER"]if(name,stem)in triggers else["PACKAGE","PACKAGE BODY"]:
   q.execute("select TEXT from USER_SOURCE where NAME=:p_name and TYPE=:p_kind order by LINE",p_name=name,p_kind=kind);rows=q.fetchall();assert rows,(name,kind)
   parts.append("create or replace "+"".join(x[0]for x in rows).replace("\r\r\n","\n").replace("\r\n","\n").strip()+"\n/\n")
  out[f+"000_before_"+stem+".sql"]="\n".join(parts)
 q.execute("select json_query(RESOLVED_PLAN_JSON,'$.domain' returning clob)from RRL_STOCK_OPERATION where OPERATION_ID='SMALL211.LOAD:8258e0ab'");row=q.fetchone();out[f+"000_sample_departed_hu_domain.json"]=row[0].read()
 for table in ["RRL_WMS_HU_LINK","RRL_PALLETS","RRL_STORAGE_SLOTS"]:
  q.execute("select COLUMN_NAME,DATA_TYPE from USER_TAB_COLUMNS where TABLE_NAME=:p_table order by COLUMN_ID",p_table=table)
  out[f+"000_"+table.lower()+"_columns.json"]=json.dumps(q.fetchall(),indent=2)
out[f+"000_before_manifest.json"]=Path("db/migrations/2026-10-08_stock_posting_core/current_runtime_manifest.json").read_text(encoding="utf-8")
out[f+"checkpoint.json"]=json.dumps({"migration_id":"2026-10-11-214-whole-case-hu-unload","sha256":{k:hashlib.sha256(v.encode()).hexdigest()for k,v in out.items()},"recovery":"Append fresh HU links; never reactivate/mutate original shipped link history. Native unloaded history retained, forward repair after any real recovery. Fresh owner/guard exact sources."},indent=2)
print(json.dumps(out,ensure_ascii=True))
