"""Actual separate store/driver authenticated handover; ordinary own return only."""
import sys
from pathlib import Path
from uuid import uuid4
import httpx,oracledb
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment()
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"api/wms_api_server"))
from app.config import get_settings
cfg=get_settings();tag=uuid4().hex[:10];base="http://127.0.0.1:8088"
admin=httpx.Client(auth=("admin","admin123"),timeout=30)
users=[("QRS"+tag,"QRS"+tag.upper(),uuid4().hex),("QRD"+tag,"QRD"+tag.upper(),uuid4().hex)]
def call(client,method,path,body=None,status=200):
 r=client.request(method,base+path,json=body);assert r.status_code==status,(r.status_code,r.text[:1800]);return r.json()
with oracledb.connect(user=cfg.oracle_user,password=cfg.oracle_password,dsn=cfg.oracle_dsn) as c:
 q=c.cursor();q.execute("""
 select t.OPERATION_ID,t.TT_ID,t.DRIVER_ID,t.VEHICLE_NUMBER,t.STORE_ADDR,a.BASE_UOM,to_char(a.BASE_QTY,'TM9','NLS_NUMERIC_CHARACTERS=''.,''')
 from RRL_STORE_RETURN_TRANSPORT t join RRL_STORE_RETURN_APPROVAL a on a.OPERATION_ID=t.APPROVAL_OPERATION_ID
 where a.RECEIPT_OPERATION_ID='STORE.RECEIPT:bea258a7dd' and a.DISPOSITION='SUPPLIER'
 """);transport,trip,driver,plate,store,uom,quantity=q.fetchone()
 for username,group,password in users:
  q.execute("insert into RUSERS(ID,PASS,NAME,USER_GROUP,DELETED,PRAVO_ADMIN_LOGIN)values(:id,:secret,'Own return custody actor',:grp,0,0)",id=username,secret=password,grp=group)
 c.commit()
 binding_version=None
 try:
  for idx,(username,group,password) in enumerate(users):
   call(admin,"POST","/api/admin/rights/groups",{"id":group,"name":"Own return custody"})
   rights=["store_receipt_confirm","store_return_handover"] if idx==0 else ["driver_return_accept"]
   for right in rights:call(admin,"POST",f"/api/admin/rights/groups/{group}/rights",{"right_name":right,"description":"Own custody author role"})
  store_client=httpx.Client(auth=(users[0][0],users[0][2]),timeout=30);driver_client=httpx.Client(auth=(users[1][0],users[1][2]),timeout=30)
  call(admin,"POST","/api/delivery/store-receipts/receivers",{"store_address":store,"username":users[0][0]})
  binding=call(admin,"GET","/api/transport/driver-bindings/"+str(driver))
  configured=call(admin,"PUT","/api/transport/driver-bindings/"+str(driver),{"user_id":users[1][0],"active":True,"expected_version":binding["binding_version"]})
  binding_version=configured["binding_version"]
  path="/api/delivery/store-return-custody"
  rows=call(store_client,"GET",path+"/store?store_address="+store);assert any(x["transport_operation_id"]==transport for x in rows)
  handed={"operation_id":"RETURN.HAND:"+tag,"transport_operation_id":transport,"pallet_identifier":"INTERNAL.RETURN:"+tag,"quantity":quantity,"base_uom":uom,"gross_weight_kg":"2","physical_places":1}
  bad=call(store_client,"POST",path+"/handover",{**handed,"operation_id":"RETURN.HAND.BADQ:"+tag,"quantity":"2"},409);assert "STORE_RETURN_FULL_APPROVED_QUANTITY_REQUIRED" in bad["detail"]["message"]
  bad=call(store_client,"POST",path+"/handover",{**handed,"operation_id":"RETURN.HAND.BADM:"+tag,"gross_weight_kg":"2.000000001"},409);assert "STORE_RETURN_PHYSICAL_PLACE_OR_PLAN_MISMATCH" in bad["detail"]["message"]
  done=call(store_client,"POST",path+"/handover",handed);assert done["custody"]=="STORE_PENDING_DRIVER" and not done["warehouse_stock_changed"]
  assert call(store_client,"POST",path+"/handover",handed)==done
  rows=call(driver_client,"GET",path+"/driver");assert any(x["handover_operation_id"]==handed["operation_id"] for x in rows)
  pickup={"operation_id":"RETURN.PICKUP:"+tag,"handover_operation_id":handed["operation_id"],"scan_vehicle":plate,"scan_pallet":handed["pallet_identifier"]}
  bad=call(admin,"POST",path+"/pickup",pickup,status=403);assert "STORE_RETURN_BOUND_DRIVER_AND_HANDOVER_REQUIRED" in bad["detail"]["message"]
  bad=call(driver_client,"POST",path+"/pickup",{**pickup,"operation_id":"RETURN.PICKUP.BADSCAN:"+tag,"scan_pallet":"FOREIGN"},409);assert "STORE_RETURN_DRIVER_VEHICLE_PALLET_SCAN_REQUIRED" in bad["detail"]["message"]
  result=call(driver_client,"POST",path+"/pickup",pickup);assert result["custody"]=="VEHICLE" and not result["warehouse_stock_changed"]
  assert call(driver_client,"POST",path+"/pickup",pickup)==result
  bad=call(driver_client,"POST",path+"/pickup",{**pickup,"operation_id":"RETURN.PICKUP.DUP:"+tag},409);assert "STORE_RETURN_ALREADY_PICKED_UP" in bad["detail"]["message"]
  for op in (handed["operation_id"],pickup["operation_id"]):
   q.execute("select count(*) from RRL_EVENTS where OPERATION_ID=:op",op=op);assert q.fetchone()==(0,)
   q.execute("select count(*) from RRL_EVENT_OUTBOX where CORRELATION_ID=:op",op=op);assert q.fetchone()==(1,)
  try:q.execute("delete from RRL_STORE_RETURN_PICKUP where OPERATION_ID=:op",op=pickup["operation_id"]);c.commit();raise AssertionError("Custody deleted")
  except oracledb.DatabaseError as exc:c.rollback();assert "STORE_RETURN_CUSTODY_HISTORY_IMMUTABLE" in str(exc)
  print("PASS095 actual store binding/separate dedicated authenticated driver/current trip/internal pallet scan/quantity+mass/retry/admin spoof/foreign scan/duplicate/immutable/outbox1/events0; custody vehicle, no stock birth",flush=True)
 finally:
  if binding_version is not None:
   call(admin,"PUT","/api/transport/driver-bindings/"+str(driver),{"user_id":users[1][0],"active":False,"expected_version":binding_version})
  q.execute("update RUSERS set DELETED=1 where ID in(:a,:b)",a=users[0][0],b=users[1][0]);c.commit()
