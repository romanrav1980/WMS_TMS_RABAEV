from pathlib import Path
import json,sys,hashlib
import oracledb
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment();sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"api/wms_api_server"))
from app.config import get_settings
s=get_settings();out={};f="db/migrations/2026-10-11_ni061_dispatch_decision/"
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor()
 for name in["RRL_STOCK_TRIP_DEPART_CMD","RRL_STOCK_INTERWARE_REC","RRL_STOCK_INTERWARE_PUT","RRL_STOCK_INTERWARE_NEXT","RRL_STOCK_METADATA_TX"]:
  parts=[]
  for kind in["PACKAGE","PACKAGE BODY"]:
   q.execute("select TEXT from USER_SOURCE where NAME=:n and TYPE=:t order by LINE",n=name,t=kind);rows=q.fetchall();assert rows,name;parts.append("create or replace "+"".join(x[0]for x in rows).strip()+"\n/\n")
  out[f+"000_before_"+name.lower()+".sql"]="\n".join(parts)
 q.execute("select TRIGGER_NAME from USER_TRIGGERS where TABLE_NAME='RRL_INTERWARE_PLAN'")
 for(name,)in q.fetchall():
  q.execute("select TEXT from USER_SOURCE where NAME=:n and TYPE='TRIGGER'order by LINE",n=name);out[f+"000_before_"+name.lower()+".sql"]="create or replace "+"".join(x[0]for x in q.fetchall()).strip()+"\n/\n"
 q.execute("select p.OPERATION_ID,p.SOURCE_LOAD_OPERATION_ID,p.TARGET_TT_ID,p.TARGET_WARE_ID from RRL_INTERWARE_PLAN p where not exists(select 1 from RRL_INTERWARE_RECEIPT r where r.PLAN_OPERATION_ID=p.OPERATION_ID)order by p.OPERATION_ID fetch first 5 rows only");out[f+"000_pending_plans.json"]=json.dumps(q.fetchall())
out[f+"000_manifest.json"]=Path("db/migrations/2026-10-08_stock_posting_core/current_runtime_manifest.json").read_text(encoding="utf-8")
out[f+"checkpoint.json"]=json.dumps({"migration_id":"2026-10-11-239-interwarehouse-dispatcher-delay-decision","sha256":{k:hashlib.sha256(v.encode()).hexdigest()for k,v in out.items()}},indent=2)
print(json.dumps(out,ensure_ascii=True))
