import sys,json,hashlib
from pathlib import Path
import oracledb
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment();sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"api/wms_api_server"))
from app.config import get_settings
s=get_settings();out={};f="db/migrations/2026-10-11_ni042_weight_choice_plan/"
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select user,sys_context('USERENV','SERVICE_NAME')from dual");assert q.fetchone()==("RABAEV","orcl")
 for name,short in [("RRL_PICKING_API","picking"),("RRL_WEIGHT_BOX_CHOICE_API","choice")]:
  chunks=[]
  for kind in ("PACKAGE","PACKAGE BODY"):
   q.execute("select TEXT from USER_SOURCE where NAME=:p_name and TYPE=:p_kind order by LINE",p_name=name,p_kind=kind)
   chunks.append("create or replace "+"".join(r[0]for r in q.fetchall()).replace("\r\r\n","\n").replace("\r\n","\n").strip()+"\n/\n")
  out[f+"000_before_"+short+".sql"]="\n".join(chunks)
out[f+"000_before_guard.sql"]=Path("db/migrations/2026-10-11_ni042_weight_box_choice/004_guard.sql").read_text(encoding="utf-8")
out[f+"checkpoint.json"]=json.dumps({"migration_id":"2026-10-11-196-weight-choice-native-plan","sha256":{k:hashlib.sha256(v.encode()).hexdigest()for k,v in out.items()},"recovery":"Fresh existing planner/choice source and guard saved; pure/private metadata binder with native old plan/SOFT transaction; forward repair once USED history exists; no DB copy"},indent=2)
print(json.dumps(out,ensure_ascii=True))
