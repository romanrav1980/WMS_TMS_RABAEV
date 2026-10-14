import sys,json,hashlib
from pathlib import Path
import oracledb
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment();sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"api/wms_api_server"))
from app.config import get_settings
out={};f="db/migrations/2026-10-11_ni042_case_sscc/"
s=get_settings()
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();chunks=[]
 for kind in("PACKAGE","PACKAGE BODY"):
  q.execute("select TEXT from USER_SOURCE where NAME='RRL_STOCK_CASE_PICK_CMD'and TYPE=:p_kind order by LINE",p_kind=kind)
  chunks.append("create or replace "+"".join(x[0]for x in q.fetchall()).replace("\r\r\n","\n").replace("\r\n","\n").strip()+"\n/\n")
 out[f+"000_before_case.sql"]="\n".join(chunks)
out[f+"000_before_labels.py"]=Path("api/wms_api_server/app/modules/inventory/infrastructure/labels.py").read_text(encoding="utf-8")
out[f+"checkpoint.json"]=json.dumps({"migration_id":"2026-10-11-203-case-logistic-sscc","sha256":{k:hashlib.sha256(v.encode()).hexdigest()for k,v in out.items()},"recovery":"Fresh root CASE and receipt label source preserved; defaultoff old carriers unaffected; immutable label history prevents destructive rollback; no DB copy"},indent=2)
print(json.dumps(out,ensure_ascii=True))
