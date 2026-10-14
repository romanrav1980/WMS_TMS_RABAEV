import json,sys
from pathlib import Path
import oracledb
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment();sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"api/wms_api_server"))
from app.config import get_settings
s=get_settings();out={}
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor()
 for name,label in [("RRL_STOCK_REPL_CAPACITY","capacity"),("RRL_PICK_TOPOLOGY_API","topology")]:
  chunks=[]
  for kind in ("PACKAGE","PACKAGE BODY"):
   q.execute("select TEXT from USER_SOURCE where NAME=:name and TYPE=:kind order by LINE",name=name,kind=kind)
   chunks.append("create or replace "+"".join(row[0]for row in q.fetchall()).strip()+"\n/\n")
  out["db/migrations/2026-10-10_ni081_range_apply/000_before_"+label+".sql"]="\n".join(chunks)
print(json.dumps(out))
