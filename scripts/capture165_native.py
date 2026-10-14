import json,sys
from pathlib import Path
import oracledb
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment();sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"api/wms_api_server"))
from app.config import get_settings
s=get_settings();out={}
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor()
 q.execute("select sys_context('USERENV','SESSION_USER'),sys_context('USERENV','SERVICE_NAME')from dual")
 user,service=q.fetchone();assert user=="RABAEV"and service.lower()=="orcl"
 q.execute("select count(*)from USER_OBJECTS where OBJECT_NAME='RRL_CASE_TASK_ACCESS'");assert q.fetchone()[0]==0
 for name,label in [("RRL_CASE_RESOURCE_POLICY","policy"),("RRL_STOCK_POSTING_API","root")]:
  q.execute("select count(*)from USER_OBJECTS where OBJECT_NAME=:name and STATUS!='VALID'",name=name);assert q.fetchone()[0]==0
  chunks=[]
  for kind in ("PACKAGE","PACKAGE BODY"):
   q.execute("select TEXT from USER_SOURCE where NAME=:name and TYPE=:kind order by LINE",name=name,kind=kind)
   chunks.append("create or replace "+"".join(row[0]for row in q.fetchall()).strip()+"\n/\n")
  out["db/migrations/2026-10-10_ni033_case_scope/000_before_"+label+".sql"]="\n".join(chunks)
print(json.dumps(out,ensure_ascii=True))
