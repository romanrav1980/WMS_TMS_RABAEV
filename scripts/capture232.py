from pathlib import Path
import json,sys,hashlib
import oracledb
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment();sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"api/wms_api_server"))
from app.config import get_settings
s=get_settings();out={};f="db/migrations/2026-10-11_ni053_final_custody/"
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor()
 for name in["RRL_STOCK_STORE_RECEIPT_CMD","RRL_STOCK_INTERWARE_CUSTODY","RRL_STOCK_STORE_RETURN_TR_CMD","RRL_STOCK_STORE_RETURN_CUST_CMD","RRL_STOCK_POSTING_API"]:
  parts=[]
  for kind in["PACKAGE","PACKAGE BODY"]:
   q.execute("select TEXT from USER_SOURCE where NAME=:n and TYPE=:t order by LINE",n=name,t=kind);rows=q.fetchall();assert rows,name;parts.append("create or replace "+"".join(x[0]for x in rows).strip()+"\n/\n")
  out[f+"000_before_"+name.lower()+".sql"]="\n".join(parts)
 q.execute("select TRIGGER_NAME from USER_TRIGGERS where TABLE_NAME='RRL_TT_HU_LOAD_FACT'order by TRIGGER_NAME")
 for(name,)in q.fetchall():
  q.execute("select TEXT from USER_SOURCE where NAME=:n and TYPE='TRIGGER'order by LINE",n=name)
  out[f+"000_before_"+name.lower()+".sql"]="create or replace "+"".join(x[0]for x in q.fetchall()).strip()+"\n/\n"
 q.execute("select COLUMN_NAME,DATA_TYPE from USER_TAB_COLUMNS where TABLE_NAME='RRL_TT_HU_LOAD_FACT'order by COLUMN_ID");out[f+"000_load_columns.json"]=json.dumps(q.fetchall())
out[f+"000_manifest.json"]=Path("db/migrations/2026-10-08_stock_posting_core/current_runtime_manifest.json").read_text(encoding="utf-8")
out[f+"checkpoint.json"]=json.dumps({"migration_id":"2026-10-11-232-final-store-custody-release","sha256":{k:hashlib.sha256(v.encode()).hexdigest()for k,v in out.items()}},indent=2)
print(json.dumps(out,ensure_ascii=True))
