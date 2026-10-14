import sys,json,hashlib
from pathlib import Path
import oracledb
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment();sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"api/wms_api_server"))
from app.config import get_settings
s=get_settings();out={};f=Path("db/migrations/2026-10-11_ni042_small_hu")
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor()
 for name,stem,types in [("RRL_STOCK_PALLET_QC_CMD","qc",("PACKAGE","PACKAGE BODY")),("RRL_WH_SCALE_API","archive",("PACKAGE","PACKAGE BODY")),("RRL_WH_FINAL_SCALE_USE_GUARD","use_guard",("TRIGGER",))]:
  parts=[]
  for kind in types:
   q.execute("select TEXT from USER_SOURCE where NAME=:name and TYPE=:kind order by LINE",name=name,kind=kind)
   parts.append("create or replace "+"".join(x[0]for x in q.fetchall()).replace("\r\r\n","\n").replace("\r\n","\n").strip()+"\n/\n")
  out[str(f/("000_before_"+stem+".sql"))]="\n".join(parts)
p=f/"checkpoint.json";checkpoint=json.loads(p.read_text(encoding="utf-8"));checkpoint["sha256"].update({k:hashlib.sha256(v.encode()).hexdigest()for k,v in out.items()})
out[str(p)]=json.dumps(checkpoint,indent=2)
print(json.dumps(out,ensure_ascii=True))
