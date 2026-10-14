import sys,json,hashlib
from pathlib import Path
import oracledb
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment();sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"api/wms_api_server"))
from app.config import get_settings
s=get_settings();out={};f="db/migrations/2026-10-11_ni042_direct_receiving/"
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor()
 for name,label in[("RRL_PICKING_API","picking"),("RRL_STOCK_WAVE_LAUNCH_CMD","launch"),("RRL_STOCK_ELIGIBILITY","eligibility")]:
  chunks=[]
  for kind in("PACKAGE","PACKAGE BODY"):
   q.execute("select TEXT from USER_SOURCE where NAME=:p_name and TYPE=:p_kind order by LINE",p_name=name,p_kind=kind)
   chunks.append("create or replace "+"".join(x[0]for x in q.fetchall()).replace("\r\r\n","\n").replace("\r\n","\n").strip()+"\n/\n")
  out[f+"000_before_"+label+".sql"]="\n".join(chunks)
out[f+"checkpoint.json"]=json.dumps({"migration_id":"2026-10-11-199-direct-receiving-pick-plan","sha256":{k:hashlib.sha256(v.encode()).hexdigest()for k,v in out.items()},"recovery":"Fresh existing native planner/launch/eligibility saved; no database copy; original metadata history retained"},indent=2)
print(json.dumps(out,ensure_ascii=True))
