import sys,json,hashlib
from pathlib import Path
import oracledb
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment();sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"api/wms_api_server"))
from app.config import get_settings
s=get_settings();out={};f="db/migrations/2026-10-11_ni042_small_hu/"
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor()
 for name,stem in [("RRL_STOCK_QC_GATE","gate"),("RRL_WH_FINAL_SCALE_ADMISSION","admission"),("RRL_STOCK_HU_CMD","hu"),("RRL_STOCK_HU_READ","read"),("RRL_STOCK_LOAD_BOX_CORE","load_boxes")]:
  parts=[]
  for kind in("PACKAGE","PACKAGE BODY"):
   q.execute("select TEXT from USER_SOURCE where NAME=:name and TYPE=:kind order by LINE",name=name,kind=kind)
   parts.append("create or replace "+"".join(x[0]for x in q.fetchall()).replace("\r\r\n","\n").replace("\r\n","\n").strip()+"\n/\n")
  out[f+"000_before_"+stem+".sql"]="\n".join(parts)
p="db/migrations/2026-10-08_stock_posting_core/current_runtime_manifest.json";out[f+"000_before_manifest.json"]=Path(p).read_text(encoding="utf-8")
out[f+"checkpoint.json"]=json.dumps({"migration_id":"2026-10-11-206-small-case-hu-control","sha256":{k:hashlib.sha256(v.encode()).hexdigest()for k,v in out.items()},"recovery":"Fresh gate/admission/HU owner/read/loadbox sources, same existing archive and stock owner; source paired rollback only without v3 small proofs, otherwise preserve history/forward repair; no DB copy"},indent=2)
print(json.dumps(out,ensure_ascii=True))
