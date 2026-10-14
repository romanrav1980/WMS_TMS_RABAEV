import sys
from pathlib import Path
from uuid import uuid4
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier
import httpx,oracledb
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment()
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"api/wms_api_server"))
from app.config import get_settings
cfg=get_settings();tag=uuid4().hex[:10];base="http://127.0.0.1:8088"
source="STORE.RECEIPT:04633c677f";barrier=Barrier(2)
def attempt(i):
 body={"operation_id":"RETURN.RACE:"+tag+":"+str(i),"line_no":1,"quantity":"2","disposition":"SUPPLIER","reason":"Own concurrency author case","decision_reference":"Own Supply Chain race "+tag,"complete_good_box":False}
 with httpx.Client(auth=("admin","admin123"),timeout=30) as c:
  barrier.wait();r=c.post(base+"/api/delivery/store-returns/"+source+"/approve",json=body)
  return body,r.status_code,r.json()
with ThreadPoolExecutor(max_workers=2) as pool:
 results=list(pool.map(attempt,[1,2]))
assert sorted(row[1] for row in results)==[200,409],results
with oracledb.connect(user=cfg.oracle_user,password=cfg.oracle_password,dsn=cfg.oracle_dsn) as c:
 q=c.cursor();q.execute("select sum(BASE_QTY),count(*) from RRL_STORE_RETURN_APPROVAL where RECEIPT_OPERATION_ID=:source",source=source);assert q.fetchone()==(2,1)
 for body,status,result in results:
  q.execute("select count(*) from RRL_EVENT_OUTBOX where CORRELATION_ID=:op",op=body["operation_id"]);assert q.fetchone()==(1 if status==200 else 0,)
print("PASS092 actual concurrent approvals2+2 over accepted3: one applied2/one definitive conflict, no overapproval/no loser outbox",flush=True)
