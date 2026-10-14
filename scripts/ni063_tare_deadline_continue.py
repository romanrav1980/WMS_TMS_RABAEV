import sys
from pathlib import Path
import httpx,oracledb
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment()
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"api/wms_api_server"))
from app.config import get_settings
s=get_settings();base="http://127.0.0.1:8088";p="/api/inventory/tare";admin=httpx.Client(auth=("admin","admin123"),timeout=35)
def call(client,path,body=None,method=None):
 r=client.request(method or ("POST" if body else "GET"),base+path,json=body);assert r.status_code==200,(r.status_code,r.text[:1700]);return r.json()
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn) as c:
 q=c.cursor();q.execute("select OPERATION_ID,TT_ID,VEHICLE_ID,VEHICLE_NUMBER,TO_ID from RRL_TARE_OFFER where OPERATION_ID like 'TARE.DEAD.OFFER:%:STORE' order by OFFERED_AT desc fetch first 1 row only")
 pending_offer,trip,vehicle,plate,store=q.fetchone();tag=pending_offer.split(":")[1]
 # IDs use TARE.DEAD.OFFER:<tag>:STORE.
 tag=pending_offer.split(":")[1]
 q.execute("select a.ACCEPTED_BY,u.PASS from RRL_TARE_OFFER o join RRL_TARE_ACCEPT a on a.OFFER_OPERATION_ID=o.OPERATION_ID join RUSERS u on u.ID=a.ACCEPTED_BY where o.TO_KIND='STORE' and a.ACCEPTED_BY like 'QTS%' order by a.ACCEPTED_AT fetch first 1 row only")
 store_user,store_password=q.fetchone()
 q.execute("select b.DRIVER_ID,b.USER_ID,u.PASS,b.BINDING_VERSION from RRL_TRANSPORT_DRIVER_USER b join RUSERS u on u.ID=b.USER_ID join RRL_TRANSPORT_TASK tt on tt.VODITEL_ID=b.DRIVER_ID where tt.ID=:trip",trip=trip)
 driver,driver_user,driver_password,version=q.fetchone()
 assert store_user.startswith("QTS") and driver_user.startswith("QTD")
 q.execute("update RUSERS set DELETED=0 where ID in(:a,:b)",a=store_user,b=driver_user);c.commit();active_version=None
 try:
  active=call(admin,f"/api/transport/driver-bindings/{driver}",{"user_id":driver_user,"active":True,"expected_version":version},"PUT");active_version=active["binding_version"]
  with httpx.Client(auth=(driver_user,driver_password),timeout=35) as drv,httpx.Client(auth=(store_user,store_password),timeout=35) as shop:
   delivered={"operation_id":pending_offer.replace("TARE.DEAD.OFFER:","TARE.DEAD.ACCEPT:"),"offer_operation_id":pending_offer,"accepted_quantity":"2","scan_vehicle":plate}
   result=call(shop,p+"/accept",delivered);assert call(shop,p+"/accept",delivered)==result
   q.execute("select RETURN_MODE,POLICY_VERSION,TIMEZONE_REGION,to_char(DUE_AT,'YYYY-MM-DD HH24:MI:SS TZH:TZM') from RRL_TARE_DELIVERY_POLICY where ACCEPT_OPERATION_ID=:op",op=delivered["operation_id"])
   mode,policy_version,timezone,due=q.fetchone();assert(mode,policy_version,timezone)==("SAME_DAY",1,"Europe/Moscow") and due is not None
   policy=call(admin,p+"/return-policy?scope_kind=STORE&scope_key="+store)
   if policy["policy_version"]==1:
    call(admin,p+"/return-policy",{"scope_kind":"STORE","scope_key":store,"return_mode":"DAYS","return_days":3,"timezone_region":"Europe/Moscow","expected_version":1},"PUT")
   assert call(shop,p+"/accept",delivered)==result
   def transfer(sender,receiver,fk,fi,tk,ti,suffix):
    offer={"operation_id":"TARE.DEAD.OFFER:"+tag+":"+suffix,"task_id":trip,"owner_ware_id":9104,"pallet_type_id":3,"condition":"GOOD","from_kind":fk,"from_id":str(fi),"to_kind":tk,"to_id":str(ti),"quantity":"2","scan_vehicle":plate}
    call(sender,p+"/offer",offer)
    accepted={"operation_id":"TARE.DEAD.ACCEPT:"+tag+":"+suffix,"offer_operation_id":offer["operation_id"],"accepted_quantity":"2","scan_vehicle":plate}
    call(receiver,p+"/accept",accepted)
   transfer(shop,drv,"STORE",store,"VEHICLE",vehicle,"BACK")
   transfer(drv,admin,"VEHICLE",vehicle,"WAREHOUSE",9104,"WARE")
  debt=call(admin,p+"/warehouses/9104/store-debt");own=[r for r in debt if r["store_addr"]==store and r["pallet_type_id"]==3]
  assert len(own)==1 and own[0]["accept_operation_id"]==delivered["operation_id"] and own[0]["outstanding_quantity"]=="2" and own[0]["return_mode"]=="SAME_DAY",own
  q.execute("select CUSTODIAN_KIND,QUANTITY from RRL_TARE_BALANCE where OWNER_WARE_ID=9104 and PALLET_TYPE_ID=3 and CONDITION_CODE='GOOD'")
  assert dict(q.fetchall())=={"WAREHOUSE":4,"VEHICLE":0,"STORE":2}
  try:q.execute("update RRL_TARE_DELIVERY_POLICY set POLICY_VERSION=999 where ACCEPT_OPERATION_ID=:op",op=delivered["operation_id"]);c.commit();raise AssertionError("Policy snapshot changed")
  except oracledb.DatabaseError as exc:c.rollback();assert "TARE_DELIVERY_POLICY_HISTORY_IMMUTABLE" in str(exc)
  print("PASS099 actual SAME_DAY snapshot1; laterDAYS3 config cannot change deadline/replay; FIFO returned2 settles old legacy2, new debt2; warehouse4/store2 conserved/immutable",flush=True)
 finally:
  if active_version is not None:call(admin,f"/api/transport/driver-bindings/{driver}",{"user_id":driver_user,"active":False,"expected_version":active_version},"PUT")
  q.execute("update RUSERS set DELETED=1 where ID in(:a,:b)",a=store_user,b=driver_user);c.commit()
