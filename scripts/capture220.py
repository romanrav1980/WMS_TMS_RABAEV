from pathlib import Path
import json,hashlib,sys
import oracledb
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment();sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"api/wms_api_server"))
from app.config import get_settings
s=get_settings();out={};f="db/migrations/2026-10-11_ni063_hu_load_recovery/"
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor()
 for name in["RRL_TARE_LOAD_RECOVERY_API","RRL_STOCK_TARE_BOOK_CMD"]:
  parts=[]
  for kind in["PACKAGE","PACKAGE BODY"]:
   q.execute("select TEXT from USER_SOURCE where NAME=:n and TYPE=:t order by LINE",n=name,t=kind);rows=q.fetchall();assert rows
   parts.append("create or replace "+"".join(x[0]for x in rows).replace("\r\n","\n").strip()+"\n/\n")
  out[f+"000_before_"+name.lower()+".sql"]="\n".join(parts)
 q.execute("select text from user_source where name='RRL_TARE_LOAD_RECOVERY_GUARD' and type='TRIGGER'order by line")
 out[f+"000_before_guard.sql"]="create or replace "+"".join(x[0]for x in q.fetchall()).replace("\r\n","\n").strip()+"\n/\n"
 q.execute("select TABLE_NAME,COLUMN_NAME,NULLABLE from user_tab_columns where TABLE_NAME='RRL_TARE_LOAD_RECOVERY' order by COLUMN_ID");out[f+"000_before_columns.json"]=json.dumps(q.fetchall(),ensure_ascii=True)
for p in["api/wms_api_server/app/modules/inventory/infrastructure/tare_load_recovery.py","wiki-raw/wms_admin_ui_reference/tare-load-recovery.js","db/migrations/2026-10-08_stock_posting_core/current_runtime_manifest.json"]:
 out[f+"000_before_"+Path(p).name]=Path(p).read_text(encoding="utf-8")
out[f+"checkpoint.json"]=json.dumps({"migration_id":"2026-10-11-220-hu-fullpal-tare-recovery","sha256":{k:hashlib.sha256(v.encode()).hexdigest()for k,v in out.items()},"recovery":"Fresh native owners and existing recovery guard. Add nullable ROOT_UID with exclusive CASE/HU key; existing historical CASE proofs remain intact. Refuse rollback after any HU recovery."},indent=2)
print(json.dumps(out,ensure_ascii=True))
