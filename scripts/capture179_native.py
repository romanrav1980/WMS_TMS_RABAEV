import sys,json
from pathlib import Path
import oracledb
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment();sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"api/wms_api_server"))
from app.config import get_settings
s=get_settings();out={}
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select user,sys_context('USERENV','SERVICE_NAME')from dual");assert q.fetchone()==("RABAEV","orcl")
 for short,name in [("unit","RRL_STOCK_UNIT_CORE"),("root","RRL_STOCK_POSTING_API")]:
  chunks=[]
  for kind in ("PACKAGE","PACKAGE BODY"):
   q.execute("select TEXT from USER_SOURCE where NAME=:p_name and TYPE=:p_kind order by LINE",p_name=name,p_kind=kind)
   chunks.append("create or replace "+"".join(row[0]for row in q.fetchall()).replace("\r\r\n","\n").replace("\r\n","\n").strip()+"\n/\n")
  out["db/migrations/2026-10-11_ni042_weight_box_capture/000_before_"+short+".sql"]="\n".join(chunks)
print(json.dumps(out))
