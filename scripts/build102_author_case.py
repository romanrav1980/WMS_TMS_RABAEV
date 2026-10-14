from pathlib import Path
import json
s=Path("scripts/ni052_loading_case.py").read_text(encoding="utf-8-sig")
# Reuse the established original goods fixture; add tare before real shipment.
needle='  shipop="FULL.HU.SHIP:"+tag;'
assert needle in s
s=s.replace(needle,'''  tare_count=post("TARE_COUNT",{"owner_ware_id":ware,"pallet_type_id":1,"condition":"GOOD","observed_quantity":"1","expected_version":0,"reason":"Own booked cargo tare fixture","decision_reference":"TARE:"+tag},{})
  bookop="TARE.CARGO.BOOK:"+tag
  booked=post("TARE_BOOK",{"pallet_type_id":1,"expected_warehouse_id":ware},{"place_kind":"HU","place_id":top},bookop)
  assert booked["available_quantity"]=="0"
'''+needle,1)
needle='  state=loading.status(trip);'
assert needle in s
s=s.replace(needle,'''
  import httpx
  admin_client=httpx.Client(auth=("admin","admin123"),timeout=35)
  base_url="http://127.0.0.1:8088"
  def api(client,method,path,body=None,status=200):
   response=client.request(method,base_url+path,json=body)
   assert response.status_code==status,(response.status_code,response.text[:1800])
   return response.json()
  driver_user="QTBC"+tag;driver_group=driver_user.upper();driver_secret=uuid4().hex
  q.execute("insert into RUSERS(ID,PASS,NAME,USER_GROUP,DELETED,PRAVO_ADMIN_LOGIN)values(:id,:secret,'Own booked cargo driver',:grp,0,0)",id=driver_user,secret=driver_secret,grp=driver_group);conn.commit()
  api(admin_client,"POST","/api/admin/rights/groups",{"id":driver_group,"name":"Own booked cargo driver"})
  for right in ["driver_return_accept","tare_accept","tare_view"]:
   api(admin_client,"POST",f"/api/admin/rights/groups/{driver_group}/rights",{"right_name":right,"description":"Own booked cargo driver"})
  binding=api(admin_client,"GET",f"/api/transport/driver-bindings/{driver}")
  assert not binding.get("active"),"Do not replace an active driver binding"
  enabled=api(admin_client,"PUT",f"/api/transport/driver-bindings/{driver}",{"user_id":driver_user,"active":True,"expected_version":binding["binding_version"]})
  try:
   driver_client=httpx.Client(auth=(driver_user,driver_secret),timeout=35)
   available=api(admin_client,"GET",f"/api/inventory/tare/warehouses/{ware}/trips/{trip}/loaded-bookings")
   assert len(available)==1 and available[0]["operation_id"]==bookop
   offer={"operation_id":"TARE.CARGO.OFFER:"+tag,"task_id":trip,"owner_ware_id":ware,"pallet_type_id":1,"condition":"GOOD","from_kind":"WAREHOUSE","from_id":str(ware),"to_kind":"VEHICLE","to_id":str(vehicle),"quantity":"1","scan_vehicle":"QL"+tag,"booking_operation_ids":[bookop]}
   offered=api(admin_client,"POST","/api/inventory/tare/offer",offer)
   assert not offered["tare_balance_changed"]
   assert api(admin_client,"POST","/api/inventory/tare/offer",offer)==offered
   accepted={"operation_id":"TARE.CARGO.ACCEPT:"+tag,"offer_operation_id":offer["operation_id"],"accepted_quantity":"1","scan_vehicle":"QL"+tag}
   result=api(driver_client,"POST","/api/inventory/tare/accept",accepted)
   assert api(driver_client,"POST","/api/inventory/tare/accept",accepted)==result
   q.execute("select STATUS,CLOSED_OPERATION_ID from RRL_TARE_BOOK where OPERATION_ID=:op",op=bookop);assert q.fetchone()==("TRANSFERRED",accepted["operation_id"])
   q.execute("select CUSTODIAN_KIND,QUANTITY from RRL_TARE_BALANCE where OWNER_WARE_ID=:ware and PALLET_TYPE_ID=1",ware=ware);assert dict(q.fetchall())=={"WAREHOUSE":0,"VEHICLE":1}
   q.execute("select count(*) from RRL_EVENTS where OPERATION_ID=:op",op=accepted["operation_id"]);assert q.fetchone()==(0,)
   q.execute("select count(*) from RRL_TARE_OFFER_BOOK where OFFER_OPERATION_ID=:op and BOOK_OPERATION_ID=:book and LOAD_OPERATION_ID=:loadop",op=offer["operation_id"],book=bookop,loadop=shipop);assert q.fetchone()==(1,)
   print("PASS102 one outer PALLET booked/actual existing nested BOX+STOCK load/dedicated driver acceptance, bookTRANSFERRED and ware0/vehicle1, no second goods event; original offer/replay",flush=True)
  finally:
   api(admin_client,"PUT",f"/api/transport/driver-bindings/{driver}",{"user_id":driver_user,"active":False,"expected_version":enabled["binding_version"]})
   q.execute("update RUSERS set DELETED=1 where ID=:id",id=driver_user);conn.commit()
'''+needle,1)
begin=s.index('  state=loading.status(trip);');end=s.index('  from app.modules.inventory.infrastructure.warehouse_hu import WarehouseHu',begin)
s=s[:begin]+s[end:]
# The existing final cleanup touches only its own goods P/H through the same core.
print(json.dumps({"scripts/ni063_booked_cargo_case.py":s},ensure_ascii=True))
