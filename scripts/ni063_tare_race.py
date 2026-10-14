import sys
from pathlib import Path
from uuid import uuid4
from concurrent.futures import ThreadPoolExecutor
import httpx,oracledb
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment()
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"api/wms_api_server"))
from app.config import get_settings
s=get_settings();tag=uuid4().hex[:10];base="http://127.0.0.1:8088";p="/api/inventory/tare"
admin=httpx.Client(auth=("admin","admin123"),timeout=35)
def call(client,path,body=None,method=None):
 r=client.request(method or ("POST" if body else "GET"),base+path,json=body);assert r.status_code==200,(r.status_code,r.text[:1800]);return r.json()
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn) as c:
 q=c.cursor();q.execute("""
 select b.DRIVER_ID,b.USER_ID,u.PASS,b.BINDING_VERSION,t.TT_ID,t.VEHICLE_ID,t.VEHICLE_NUMBER
 from RRL_TRANSPORT_DRIVER_USER b join RUSERS u on u.ID=b.USER_ID join RRL_STORE_RETURN_TRANSPORT t on t.DRIVER_ID=b.DRIVER_ID
 join RRL_STORE_RETURN_APPROVAL a on a.OPERATION_ID=t.APPROVAL_OPERATION_ID
 where a.RECEIPT_OPERATION_ID='STORE.RECEIPT:bea258a7dd' and a.DISPOSITION='SUPPLIER'
 """);driver,user,password,version,trip,vehicle,plate=q.fetchone()
 assert user.startswith("QTD")
 q.execute("update RUSERS set DELETED=0 where ID=:actor",actor=user);c.commit();active_version=None
 try:
  active=call(admin,f"/api/transport/driver-bindings/{driver}",{"user_id":user,"active":True,"expected_version":version},"PUT");active_version=active["binding_version"]
  offers=[]
  for suffix in ("A","B"):
   body={"operation_id":"TARE.RACE.OFFER:"+tag+":"+suffix,"task_id":trip,"owner_ware_id":9104,"pallet_type_id":3,"condition":"GOOD","from_kind":"WAREHOUSE","from_id":"9104","to_kind":"VEHICLE","to_id":str(vehicle),"quantity":"4","scan_vehicle":plate}
   call(admin,p+"/offer",body);offers.append(body["operation_id"])
  def accept(idx):
   with httpx.Client(auth=(user,password),timeout=35) as client:
    body={"operation_id":"TARE.RACE.ACCEPT:"+tag+":"+str(idx),"offer_operation_id":offers[idx],"accepted_quantity":"4","scan_vehicle":plate}
    r=client.post(base+p+"/accept",json=body);return r.status_code,r.json()
  with ThreadPoolExecutor(max_workers=2) as pool:results=list(pool.map(accept,(0,1)))
  assert sorted(r[0] for r in results)==[200,409],results
  q.execute("select CUSTODIAN_KIND,QUANTITY from RRL_TARE_BALANCE where OWNER_WARE_ID=9104 and PALLET_TYPE_ID=3 and CONDITION_CODE='GOOD'")
  assert dict(q.fetchall())=={"WAREHOUSE":0,"VEHICLE":4,"STORE":2}
  rejected=next(r[1]["detail"]["operation_id"] for r in results if r[0]==409)
  q.execute("select count(*) from RRL_EVENT_OUTBOX where CORRELATION_ID=:op",op=rejected);assert q.fetchone()==(0,)
  with httpx.Client(auth=(user,password),timeout=35) as client:
   back={"operation_id":"TARE.RACE.BACK:"+tag,"task_id":trip,"owner_ware_id":9104,"pallet_type_id":3,"condition":"GOOD","from_kind":"VEHICLE","from_id":str(vehicle),"to_kind":"WAREHOUSE","to_id":"9104","quantity":"4","scan_vehicle":plate}
   call(client,p+"/offer",back)
  call(admin,p+"/accept",{"operation_id":"TARE.RACE.WARE:"+tag,"offer_operation_id":back["operation_id"],"accepted_quantity":"4","scan_vehicle":plate})
  context=call(admin,p+f"/trips/{trip}/context");assert context["trip"]["vehicle_id"]==vehicle and any(t["pallet_type_id"]==3 for t in context["types"])
  print("PASS098 concurrency4+4 over source4: one4/one409, no loser outbox; conserved6, source recovered4/store2; named trip/catalog context",flush=True)
 finally:
  if active_version is not None:call(admin,f"/api/transport/driver-bindings/{driver}",{"user_id":user,"active":False,"expected_version":active_version},"PUT")
  q.execute("update RUSERS set DELETED=1 where ID=:actor",actor=user);c.commit()
