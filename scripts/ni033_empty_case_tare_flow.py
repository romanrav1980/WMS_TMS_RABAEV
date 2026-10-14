"""170 owned CASE1034: empty cancellation -> existing tare release -> deferred wave."""
import sys,json
from pathlib import Path
import httpx,oracledb
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment();sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"api/wms_api_server"))
from app.config import get_settings
s=get_settings();ware=20052672;task=1034;wave=399;root="http://127.0.0.1:8088/api"
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c,httpx.Client(auth=("admin","admin123"),timeout=60)as client:
 q=c.cursor();q.execute("select STATUS,SSCC,CONTENT_VERSION,PALLET_TYPE_ID from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=:p_task",p_task=task);status,carrier,version,tare_type=q.fetchone()
 def post(path,body):
  r=client.post(root+path,json=body);assert r.status_code==200,(r.status_code,r.text[:1600]);return r.json()
 def availability():
  r=client.get(root+f"/inventory/tare/warehouses/{ware}/availability");assert r.status_code==200
  return next(x for x in r.json()if x["pallet_type_id"]==tare_type)
 def count(qty,operation):
  current=availability()
  return post("/inventory/tare/count",{"operation_id":operation,"owner_ware_id":ware,"pallet_type_id":tare_type,"condition":"GOOD","observed_quantity":qty,"expected_version":current["balance_version"]or 0,"reason":"Own170 existing emptyCASE/tare lifecycle","decision_reference":operation})
 book="QA170.TARE.BOOK:1034"
 try:
  if status=="NEW":
   count("1","QA170.TARE.OPEN:1034")
   post("/inventory/tare/book",{"operation_id":book,"place_kind":"CASE","place_id":str(task)})
   result=post(f"/case-pick/tasks/{task}/return-carrier",{"operation_id":"CASE.EMPTY170:1034","scan_container":carrier,"expected_content_version":int(version),"destinations":{},"allow_empty":True,"reason":"Unused owned CASE; preserve demand and release booked tare"})
   assert result["status"]=="CANCELLED_EMPTY"
   decision={"operation_id":"WAVE.DEFER170:399.BOOKED","disposition":"RETURNED_TO_PLANNING","reason":"Try before existing tare release"}
   blocked=client.post(root+f"/picking/waves/{wave}/finish-execution",json=decision)
   assert blocked.status_code==409 and "WAVE_DEFER_TARE_BOOK_REMAINS"in blocked.text,(blocked.status_code,blocked.text[:1400])
  q.execute("select STATUS from RRL_TARE_BOOK where OPERATION_ID=:p_op",p_op=book);row=q.fetchone()
  if row and row[0]=="HELD":post("/inventory/tare/book-cancel",{"operation_id":"QA170.TARE.CANCEL:1034","booking_operation_id":book})
  result=post(f"/picking/waves/{wave}/finish-execution",{"operation_id":"WAVE.DEFER170:399","disposition":"RETURNED_TO_PLANNING","reason":"Empty cancelledCASE; existing tare booking released; original order remains open"})
  assert result["completion_outcome"]=="UNFULFILLED_RETURNED_TO_PLANNING"and not result["order_fulfilled"]
 finally:
  q.execute("select STATUS from RRL_TARE_BOOK where OPERATION_ID=:p_op",p_op=book);row=q.fetchone()
  if row and row[0]=="HELD":post("/inventory/tare/book-cancel",{"operation_id":"QA170.TARE.CANCEL:1034","booking_operation_id":book})
  q.execute("select count(*)from RRL_STOCK_OPERATION where OPERATION_ID='QA170.TARE.ZERO:1034'")
  if q.fetchone()[0]==0:count("0","QA170.TARE.ZERO:1034")
 q.execute("select sum(r.REMAIN),sum(r.HARD_RESERVED_BASE)from RRL_REMAINS r join RRL_CELLS x on x.CELL=r.CELL where x.WARE_ID=6667491");assert q.fetchone()==(20,20)
print("PASS170 " + ("new HTTP emptyCASE1034/HELD refusal/tare release/wave399 completion" if status=="NEW" else "existing1034/399 receipts replay only; initial HELD refusal not repeated") + "; own goodtare0, original P20H20 unchanged")
