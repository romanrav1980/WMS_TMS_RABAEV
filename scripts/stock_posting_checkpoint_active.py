"""Checkpoint a bounded corrective package replacement after the authorized cutover."""
import sys
from pathlib import Path
import oracledb
from stock_posting_environment import load_local_oracle_environment
ROOT=Path(__file__).resolve().parents[1]
load_local_oracle_environment()
sys.path.insert(0,str(ROOT/"api/wms_api_server"))
from app.config import get_settings
s=get_settings()
name=sys.argv[1]
assert name.startswith("RRL_STOCK_") and name.replace("_","").isalnum()
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn) as c:
 q=c.cursor()
 q.execute("select user,sys_context('USERENV','SERVICE_NAME') from dual")
 assert q.fetchone()==("RABAEV","orcl")
 chunks=[]
 for kind in ("PACKAGE","PACKAGE BODY"):
  q.execute("select TEXT from USER_SOURCE where NAME=:n and TYPE=:t order by LINE",n=name,t=kind)
  chunks.append("create or replace "+"".join(r[0] for r in q).rstrip()+"\n/\n")
 target=ROOT/"db/migrations/2026-10-08_stock_posting_core"/sys.argv[2]
 assert target.parent==ROOT/"db/migrations/2026-10-08_stock_posting_core" and target.suffix==".sql"
 target.write_text("\n".join(chunks),encoding="utf-8")
 print("Checkpoint saved: "+target.name)
