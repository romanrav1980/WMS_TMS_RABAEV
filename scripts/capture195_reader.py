import sys,json,hashlib
from pathlib import Path
import oracledb
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment();sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"api/wms_api_server"))
from app.config import get_settings
s=get_settings();chunks=[]
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select user,sys_context('USERENV','SERVICE_NAME')from dual");assert q.fetchone()==("RABAEV","orcl")
 for kind in ("PACKAGE","PACKAGE BODY"):
  q.execute("select TEXT from USER_SOURCE where NAME='RRL_WEIGHT_BOX_PLANNING_READ'and TYPE=:p_kind order by LINE",p_kind=kind)
  chunks.append("create or replace "+"".join(r[0]for r in q.fetchall()).replace("\r\r\n","\n").replace("\r\n","\n").strip()+"\n/\n")
old="\n".join(chunks);f="db/migrations/2026-10-11_ni042_weight_box_choice/"
print(json.dumps({f+"000_before_reader.sql":old,f+"checkpoint.json":json.dumps({"migration_id":"2026-10-11-195-approved-weight-box-choice","before_sha256":hashlib.sha256(old.encode()).hexdigest(),"recovery":"Fresh original pure reader; additive approved choice archive/context/guards; history-protected rollback; no DB copy"},indent=2)},ensure_ascii=True))
