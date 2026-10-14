"""169 fresh owned returned401: two HTTP commands yield one durable decision."""
import sys
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import httpx,oracledb
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment();sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"api/wms_api_server"))
from app.config import get_settings
s=get_settings();op="WAVE.DEFER169:401";body={"operation_id":op,"disposition":"RETURNED_TO_PLANNING","reason":"Returned own CASE1036; preserve original order demand"}
def call():
 with httpx.Client(auth=("admin","admin123"),timeout=60)as client:
  r=client.post("http://127.0.0.1:8088/api/picking/waves/401/finish-execution",json=body)
  assert r.status_code==200,(r.status_code,r.text[:1200]);return r.json()
with ThreadPoolExecutor(max_workers=2)as pool:results=list(pool.map(lambda _:call(),range(2)))
assert results[0]==results[1]and results[0]["completion_outcome"]=="UNFULFILLED_RETURNED_TO_PLANNING"
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select count(*)from RRL_STOCK_OPERATION where OPERATION_ID=:p_op",p_op=op);assert q.fetchone()[0]==1
 q.execute("select STATUS,PICKED_QTY from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=1036");assert q.fetchone()==("CANCELLED",1)
 q.execute("select sum(r.REMAIN),sum(r.HARD_RESERVED_BASE)from RRL_REMAINS r join RRL_CELLS x on x.CELL=r.CELL where x.WARE_ID=6667491");assert q.fetchone()==(20,20)
print("PASS169 concurrent fresh401 creates one decision/exact responses; historical CASE1 remains; P20H20 unchanged")
