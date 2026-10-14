import sys,json,hashlib
from pathlib import Path
import oracledb
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment();sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"api/wms_api_server"))
from app.config import get_settings
s=get_settings();out={};f="db/migrations/2026-10-11_ni042_weight_choice_demand/"
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();parts=[]
 for kind in("PACKAGE","PACKAGE BODY"):
  q.execute("select TEXT from USER_SOURCE where NAME='RRL_STOCK_POOL_READ'and TYPE=:p_kind order by LINE",p_kind=kind)
  parts.append("create or replace "+"".join(x[0]for x in q.fetchall()).replace("\r\r\n","\n").replace("\r\n","\n").strip()+"\n/\n")
 out[f+"000_before_pool.sql"]="\n".join(parts)
out[f+"checkpoint.json"]=json.dumps({"migration_id":"2026-10-11-198-weight-choice-demand","sha256":{k:hashlib.sha256(v.encode()).hexdigest()for k,v in out.items()},"recovery":"Pure pool reader only, fresh before source retained, no physical facts rewritten"},indent=2)
print(json.dumps(out,ensure_ascii=True))
