"""167 already-shipped1030 must stay shipped; exact close command replay/no stock."""
import sys,json
from pathlib import Path
from uuid import uuid4
from concurrent.futures import ThreadPoolExecutor
import httpx,oracledb
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment();sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"api/wms_api_server"))
from app.config import get_settings
s=get_settings();op="CASE.CLOSE167:"+uuid4().hex[:10];base="http://127.0.0.1:8088/api/case-pick"
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select STATUS,CLOSED_AT,CONTENT_VERSION,SHIPPED_OPERATION from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=1030");before=q.fetchone();assert before[0]=="SHIPPED"
 body={"operation_id":op,"expected_content_version":int(before[2]),"reason":"Own167 acknowledgement preserves original shipped state"}
 def call():
  with httpx.Client(auth=("admin","admin123"),timeout=25)as client:
   r=client.post(base+"/tasks/1030/close-pallet",json=body)
   assert r.status_code==200,(r.status_code,r.text[:1500])
   return r.json()
 with ThreadPoolExecutor(max_workers=2)as pool:results=list(pool.map(lambda _:call(),range(2)))
 assert results[0]==results[1] and results[0]["status"]=="SHIPPED" and results[0]["already_closed"]is True
 q.execute("select STATUS,CLOSED_AT,CONTENT_VERSION,SHIPPED_OPERATION from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=1030");assert q.fetchone()==before
 q.execute("select count(*)from RRL_CASE_PICK_EVENT where OFFLINE_EVENT_ID=:op",op=op);assert q.fetchone()[0]==1
 with httpx.Client(auth=("admin","admin123"),timeout=25)as client:
  r=client.post(base+"/tasks/1030/close-pallet",json={**body,"reason":"Changed command body"});assert r.status_code==409 and "CASE_CLOSE_CONTENT_CONFLICT"in r.text
  r=client.post(base+"/tasks/1031/close-pallet",json={"operation_id":op+".OPEN","expected_content_version":0})
  assert r.status_code==409 and "CASE_OPEN_LINES_REMAIN"in r.text,(r.status_code,r.text[:1500])
  q.execute("select count(*)from RRL_CASE_PICK_EVENT where OFFLINE_EVENT_ID=:op",op=op+".OPEN");assert q.fetchone()[0]==0
  q.execute("select PASS,WARE_ID from RUSERS where ID='Q1341a19738325'");secret,ware=q.fetchone()
  denied=client.post(base+"/tasks/1030/close-pallet",auth=("Q1341a19738325",secret),json=body);assert denied.status_code==403,(denied.status_code,denied.text[:1000])
 q.execute("select sum(r.REMAIN),sum(r.HARD_RESERVED_BASE)from RRL_REMAINS r join RRL_CELLS x on x.CELL=r.CELL where x.WARE_ID=6667491");assert q.fetchone()==(20,20)
 print("PASS167 original SHIPPED1030 currentstatus/timestamp/version/source retained; concurrent same closeop once/exact; changedbody409/openlines1031noevent/foreign403/P20H20")
