import sys,json,hashlib
from pathlib import Path
import oracledb
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment();sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"api/wms_api_server"))
from app.config import get_settings
s=get_settings();out={};f="db/migrations/2026-10-11_ni042_small_final_weight/"
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor()
 for name,label in[("RRL_STOCK_QC_POLICY","policy"),("RRL_STOCK_QC_GATE","gate")]:
  parts=[]
  for kind in("PACKAGE","PACKAGE BODY"):
   q.execute("select TEXT from USER_SOURCE where NAME=:p_name and TYPE=:p_kind order by LINE",p_name=name,p_kind=kind)
   parts.append("create or replace "+"".join(x[0]for x in q.fetchall()).replace("\r\r\n","\n").replace("\r\n","\n").strip()+"\n/\n")
  out[f+"000_before_"+label+".sql"]="\n".join(parts)
for name,label in[("api/wms_api_server/app/schemas.py","schemas"),("api/wms_api_server/app/services/case_pick_service.py","service")]:
 out[f+"000_before_"+label+".py"]=Path(name).read_text(encoding="utf-8")
out[f+"checkpoint.json"]=json.dumps({"migration_id":"2026-10-11-202-small-box-final-weight","sha256":{k:hashlib.sha256(v.encode()).hexdigest()for k,v in out.items()},"recovery":"Fresh current QC contracts and legacy DTO/service preserved; additive defaultoff type flag, forward repair if history depends on it; no DB copy"},indent=2)
print(json.dumps(out,ensure_ascii=True))
