import sys,json
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import oracledb,httpx
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment();sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"api/wms_api_server"))
from app.config import get_settings
s=get_settings();receipt="STORE229.RECEIVE:13508027ed0";load="IW228.LOAD:13508027ed";path="http://127.0.0.1:8088/api/delivery/store-receipts/load-custody/release"
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();c.call_timeout=15000
 command={"contract_version":2,"operation_id":"STORE232.ROLLBACK:13508027ed","command_type":"STORE_CUSTODY_RELEASE","actor":"admin","source":{"receipt_operation_id":receipt},"lines":[],"units":[],"metadata":{}}
 out=q.var(oracledb.DB_TYPE_CLOB)
 q.execute("select CUSTODY_RELEASED_AT from RRL_TT_HU_LOAD_FACT where LOAD_OPERATION_ID=:p",p=load);before=q.fetchone()[0]
 if before is None:
  try:
   q.callproc("RRL_STOCK_POSTING_API.prepare_command",[json.dumps(command),"admin",out,None])
   if out.getvalue()is None:q.callproc("RRL_STOCK_POSTING_API.execute_prepared",[out])
   q.execute("select count(*)from RRL_STORE_LOAD_CUSTODY where OPERATION_ID=:p",p=command["operation_id"]);assert q.fetchone()[0]==1
  finally:c.rollback();q.callproc("RRL_STOCK_POSTING_API.reset_connection")
  q.execute("select CUSTODY_RELEASED_AT from RRL_TT_HU_LOAD_FACT where LOAD_OPERATION_ID=:p",p=load);assert q.fetchone()[0]is None
  def run(i):
   body={"operation_id":"STORE232.RELEASE:13508027ed"+str(i),"receipt_operation_id":receipt}
   with httpx.Client(auth=("admin","admin123"),timeout=40)as h:return h.post(path,json=body),body
  with ThreadPoolExecutor(max_workers=2)as pool:results=list(pool.map(run,[0,1]))
  assert sorted(r.status_code for r,b in results)==[200,409],[(r.status_code,r.text[:3000])for r,b in results]
  saved,body=next((r.json(),b)for r,b in results if r.status_code==200)
 else:
  q.execute("select OPERATION_ID from RRL_STORE_LOAD_CUSTODY where RECEIPT_OPERATION_ID=:p",p=receipt);body={"operation_id":q.fetchone()[0],"receipt_operation_id":receipt};saved=None
 with httpx.Client(auth=("admin","admin123"),timeout=40)as h:
  r=h.post(path,json=body);assert r.status_code==200,(r.status_code,r.text)
  if saved is not None:assert r.json()==saved
  assert r.json()["stock_changed"]is False
  r=h.post(path,json={"operation_id":"STORE232.PARTIAL:d76ea1c478","receipt_operation_id":"STORE230.RECEIVE:d76ea1c4780"});assert r.status_code==409,(r.status_code,r.text)
 q.execute("select l.STATUS,l.CUSTODY_RELEASE_OPERATION_ID,count(p.OPERATION_ID)from RRL_TT_HU_LOAD_FACT l left join RRL_STORE_LOAD_CUSTODY p on p.LOAD_OPERATION_ID=l.LOAD_OPERATION_ID where l.LOAD_OPERATION_ID=:p group by l.STATUS,l.CUSTODY_RELEASE_OPERATION_ID",p=load);assert q.fetchone()==("DEPARTED",body["operation_id"],1)
 q.execute("select CUSTODY_RELEASED_AT from RRL_TT_HU_LOAD_FACT where LOAD_OPERATION_ID='IW230.LOAD:d76ea1c478'");assert q.fetchone()[0]is None
 q.execute("select count(*)from RRL_EVENTS where OPERATION_ID=:p",p=body["operation_id"]);assert q.fetchone()[0]==0
 q.execute("select sum(r.REMAIN),sum(r.HARD_RESERVED_BASE)from RRL_REMAINS r join RRL_CELLS x on x.CELL=r.CELL where x.WARE_ID=6667491");assert q.fetchone()==(20,20)
 print("PASS232 full accepted custody released/original departure retained/rollback/concurrent winner/replay/partial retains custody/no stock events/protected20/20",body["operation_id"],flush=True)
