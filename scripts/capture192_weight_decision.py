import sys,json,hashlib
from pathlib import Path
import oracledb
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment();sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"api/wms_api_server"))
from app.config import get_settings
s=get_settings();out={};f="db/migrations/2026-10-11_ni042_weight_decision/"
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select user,sys_context('USERENV','SERVICE_NAME')from dual");assert q.fetchone()==("RABAEV","orcl")
 for name,short in [("RRL_STOCK_CASE_SHORT_CMD","short"),("RRL_ORDER_WEIGHT_READ","read"),("RRL_STOCK_POOL_READ","pool")]:
  chunks=[]
  for kind in ("PACKAGE","PACKAGE BODY"):
   q.execute("select TEXT from USER_SOURCE where NAME=:p_name and TYPE=:p_kind order by LINE",p_name=name,p_kind=kind)
   chunks.append("create or replace "+"".join(r[0]for r in q.fetchall()).replace("\r\r\n","\n").replace("\r\n","\n").strip()+"\n/\n")
  out[f+"000_before_"+short+".sql"]="\n".join(chunks)
out[f+"checkpoint.json"]=json.dumps({"migration_id":"2026-10-11-192-weight-tolerance-decision","before_sha256":{k:hashlib.sha256(v.encode()).hexdigest()for k,v in out.items()},"recovery":"Fresh original short/read/pool contracts; additive nullable decision metadata and existing native writer; history-protected rollback; no DB copy"},indent=2)
print(json.dumps(out,ensure_ascii=True))
