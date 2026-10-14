import sys,json
from pathlib import Path
import oracledb
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment();sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"api/wms_api_server"))
from app.config import get_settings
s=get_settings();out={}
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select user,sys_context('USERENV','SERVICE_NAME')from dual");assert q.fetchone()==("RABAEV","orcl")
 packages=[("hu","RRL_STOCK_HU_CMD"),("slot","RRL_STOCK_HU_SLOT"),("placement","RRL_STOCK_HU_PLACEMENT_CORE"),("reserve","RRL_STOCK_RESERVE_CORE"),("root","RRL_STOCK_POSTING_API")]
 for short,name in packages:
  chunks=[]
  for kind in ("PACKAGE","PACKAGE BODY"):
   q.execute("select TEXT from USER_SOURCE where NAME=:p_name and TYPE=:p_kind order by LINE",p_name=name,p_kind=kind)
   chunks.append("create or replace "+"".join(row[0]for row in q.fetchall()).replace("\r\r\n","\n").replace("\r\n","\n").strip()+"\n/\n")
  out["db/migrations/2026-10-11_ni041_slot_repack/000_before_"+short+".sql"]="\n".join(chunks)
 for name in ("RRL_HU_TASK_PLAN_GUARD","RRL_HU_CLAIM_MEASURE_GUARD","RRL_HU_LINK_WRITE_GUARD","RRL_HU_CONTAINER_GUARD","RRL_HU_TARE_LINK_GUARD"):
  q.execute("select TEXT from USER_SOURCE where NAME=:p_name and TYPE='TRIGGER'order by LINE",p_name=name)
  out["db/migrations/2026-10-11_ni041_slot_repack/000_before_"+name.lower()+".sql"]="create or replace "+"".join(row[0]for row in q.fetchall()).replace("\r\r\n","\n").replace("\r\n","\n").strip()+"\n/\n"
print(json.dumps(out))
