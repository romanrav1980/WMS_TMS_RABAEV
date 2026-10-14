"""One own ordinary tare circulation; no goods-stock mutation."""
import sys
from pathlib import Path
from uuid import uuid4
from concurrent.futures import ThreadPoolExecutor
import httpx,oracledb
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment()
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"api/wms_api_server"))
from app.config import get_settings
cfg=get_settings();tag=uuid4().hex[:10];base="http://127.0.0.1:8088"
admin=httpx.Client(auth=("admin","admin123"),timeout=35)
users=[("QTS"+tag,"QTS"+tag.upper(),uuid4().hex),("QTD"+tag,"QTD"+tag.upper(),uuid4().hex)]
def call(client,path,body=None,status=200,method=None):
 r=client.request(method or ("POST" if body is not None else "GET"),base+path,json=body)
 assert r.status_code==status,(r.status_code,r.text[:2000]);return r.json()
with oracledb.connect(user=cfg.oracle_user,password=cfg.oracle_password,dsn=cfg.oracle_dsn) as c:
 q=c.cursor();q.execute("""
 select t.TT_ID,t.DRIVER_ID,t.VEHICLE_ID,t.VEHICLE_NUMBER,t.STORE_ADDR
 from RRL_STORE_RETURN_TRANSPORT t join RRL_STORE_RETURN_APPROVAL a on a.OPERATION_ID=t.APPROVAL_OPERATION_ID
 where a.RECEIPT_OPERATION_ID='STORE.RECEIPT:bea258a7dd' and a.DISPOSITION='SUPPLIER'
 """);trip,driver,vehicle,plate,store=q.fetchone()
 for username,group,password in users:
  q.execute("insert into RUSERS(ID,PASS,NAME,USER_GROUP,DELETED,PRAVO_ADMIN_LOGIN)values(:id,:secret,'Own tare actor',:grp,0,0)",id=username,secret=password,grp=group)
 c.commit();binding_version=None
 try:
  for idx,(username,group,password) in enumerate(users):
   call(admin,"/api/admin/rights/groups",{"id":group,"name":"Own tare circulation"})
   for right in ["tare_view","tare_offer","tare_accept"]+(["store_receipt_confirm"] if idx==0 else ["driver_return_accept"]):
    call(admin,f"/api/admin/rights/groups/{group}/rights",{"right_name":right,"description":"Own tare author role"})
  store_client=httpx.Client(auth=(users[0][0],users[0][2]),timeout=35);driver_client=httpx.Client(auth=(users[1][0],users[1][2]),timeout=35)
  call(admin,"/api/delivery/store-receipts/receivers",{"store_address":store,"username":users[0][0]})
  binding=call(admin,f"/api/transport/driver-bindings/{driver}")
  configured=call(admin,f"/api/transport/driver-bindings/{driver}",{"user_id":users[1][0],"active":True,"expected_version":binding["binding_version"]},method="PUT")
  binding_version=configured["binding_version"]
  p="/api/inventory/tare"
  q.execute("select QUANTITY,BALANCE_VERSION from RRL_TARE_BALANCE where OWNER_WARE_ID=9104 and PALLET_TYPE_ID=3 and CONDITION_CODE='GOOD' and CUSTODIAN_KIND='WAREHOUSE' and CUSTODIAN_ID='9104'")
  existing=q.fetchone();assert existing is None,"One-time circulation already seeded"
  count={"operation_id":"TARE.COUNT:"+tag,"owner_ware_id":9104,"pallet_type_id":3,"condition":"GOOD","observed_quantity":"6","expected_version":0,"reason":"Own initial physical count six trolleys","decision_reference":"AUTHOR:"+tag}
  result=call(admin,p+"/count",count);assert result["destination_quantity"]=="6"
  assert call(admin,p+"/count",count)==result
  def offer(source_client,from_kind,from_id,to_kind,to_id,qty,suffix):
   body={"operation_id":"TARE.OFFER:"+tag+":"+suffix,"task_id":trip,"owner_ware_id":9104,"pallet_type_id":3,"condition":"GOOD","from_kind":from_kind,"from_id":str(from_id),"to_kind":to_kind,"to_id":str(to_id),"quantity":str(qty),"scan_vehicle":plate}
   result=call(source_client,p+"/offer",body);assert result["status"]=="WAITING_OTHER_PARTICIPANT" and not result["tare_balance_changed"]
   assert call(source_client,p+"/offer",body)==result
   return body
  def accept(target_client,body,qty,suffix):
   command={"operation_id":"TARE.ACCEPT:"+tag+":"+suffix,"offer_operation_id":body["operation_id"],"accepted_quantity":str(qty),"scan_vehicle":plate}
   result=call(target_client,p+"/accept",command);assert result["status"]=="POSTED" and not result["goods_stock_changed"]
   assert call(target_client,p+"/accept",command)==result
   return result
  outbound=offer(admin,"WAREHOUSE",9104,"VEHICLE",vehicle,6,"OUT")
  command={"operation_id":"TARE.ACCEPT.BAD:"+tag,"offer_operation_id":outbound["operation_id"],"accepted_quantity":"6","scan_vehicle":plate}
  call(admin,p+"/accept",command,403)
  accept(driver_client,outbound,6,"OUT")
  delivery=offer(driver_client,"VEHICLE",vehicle,"STORE",store,6,"STORE")
  accept(store_client,delivery,6,"STORE")
  back=offer(store_client,"STORE",store,"VEHICLE",vehicle,4,"BACK")
  accept(driver_client,back,4,"BACK")
  q.execute("select QUANTITY from RRL_TARE_BALANCE where OWNER_WARE_ID=9104 and PALLET_TYPE_ID=3 and CUSTODIAN_KIND='WAREHOUSE'");assert q.fetchone()==(0,)
  to_warehouse=offer(driver_client,"VEHICLE",vehicle,"WAREHOUSE",9104,4,"WARE")
  accept(admin,to_warehouse,4,"WARE")
  balances=call(admin,p+"/warehouses/9104/balances")
  own=[r for r in balances if r["pallet_type_id"]==3 and r["condition_code"]=="GOOD"]
  assert {r["custodian_kind"]:r["quantity"] for r in own}=={"WAREHOUSE":"4","VEHICLE":"0","STORE":"2"},own
  assert len(call(driver_client,p+f"/trips/{trip}/offers"))>=4
  q.execute("select count(*) from RRL_EVENTS where OPERATION_ID like :prefix",prefix="TARE.%"+tag+"%");assert q.fetchone()==(0,)
  q.execute("select count(*) from RRL_TARE_JOURNAL where OPERATION_ID like :prefix",prefix="TARE.%"+tag+"%");assert q.fetchone()==(5,)
  try:q.execute("delete from RRL_TARE_JOURNAL where OPERATION_ID=:op",op=count["operation_id"]);c.commit();raise AssertionError("Tare journal deleted")
  except oracledb.DatabaseError as exc:c.rollback();assert "TARE_HISTORY_IMMUTABLE" in str(exc)
  print("PASS098 actual6 issued/6 store/4 returned/4 warehouse, warehouse4+store2+vehicle0; current dedicated driver/store actors, root replay, goods events0/immutable journal5",flush=True)
 finally:
  if binding_version is not None:
   call(admin,f"/api/transport/driver-bindings/{driver}",{"user_id":users[1][0],"active":False,"expected_version":binding_version},method="PUT")
  q.execute("update RUSERS set DELETED=1 where ID in(:a,:b)",a=users[0][0],b=users[1][0]);c.commit()
