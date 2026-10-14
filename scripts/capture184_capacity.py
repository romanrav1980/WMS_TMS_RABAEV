import sys,json
from pathlib import Path
import oracledb
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment();sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"api/wms_api_server"))
from app.config import get_settings
s=get_settings();chunks=[]
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select user,sys_context('USERENV','SERVICE_NAME')from dual");assert q.fetchone()==("RABAEV","orcl")
 for kind in ("PACKAGE","PACKAGE BODY"):
  q.execute("select TEXT from USER_SOURCE where NAME='RRL_STOCK_REPL_CAPACITY'and TYPE=:p_kind order by LINE",p_kind=kind)
  chunks.append("create or replace "+"".join(r[0]for r in q.fetchall()).replace("\r\r\n","\n").replace("\r\n","\n").strip()+"\n/\n")
print(json.dumps({"db/migrations/2026-10-11_ni042_box_capacity/000_before_capacity.sql":"\n".join(chunks)},ensure_ascii=True))
