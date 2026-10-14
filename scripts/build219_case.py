from pathlib import Path
import json
s=Path("scripts/ni063_fullpal_tare_case.py").read_text(encoding="utf-8")
# Original authoring fixture copied only through original single native load.
s=s[:s.index("  import httpx")]
s=s.replace('q.execute("select min(ID) from RRL_TR_VODITEL where ID>0");driver=q.fetchone()[0];assert driver','driver=seq("RRL_TR_VODITEL_SQ");meta("insert into RRL_TR_VODITEL(ID,F,I,O,DELETED)values(:id,\'Own219\',\'Driver\',:tag,0)",id=driver,tag=tag)')
s=s.replace('q.callproc("RRL_STOCK_POSTING_API.prepare_command",[inp,"admin",out,None])','q.callproc("RRL_STOCK_POSTING_API.prepare_command",[json.dumps(command),"admin",out,None])')
s+="""
  import httpx
  from concurrent.futures import ThreadPoolExecutor
  from app.modules.inventory.contracts_stock import StockCommand
  admin_api=httpx.Client(auth=("admin","admin123"),timeout=35);base="http://127.0.0.1:8088"
  def api(client,method,path,body=None,status=200):
   r=client.request(method,base+path,json=body);assert r.status_code==status,(r.status_code,r.text[:1900]);return r.json()
  sender="TC219"+tag;driver_user="TD219"+tag;pw=uuid4().hex;driver_pw=uuid4().hex
  for actor,secret,warehouse in[(sender,pw,ware),(driver_user,driver_pw,None)]:
   q.execute("insert into RUSERS(ID,PASS,NAME,USER_GROUP,WARE_ID,DELETED,PRAVO_ADMIN_LOGIN)values(:a,:p,'Own219',:g,:w,0,0)",a=actor,p=secret,g=actor.upper(),w=warehouse);conn.commit()
   api(admin_api,"POST","/api/admin/rights/groups",{"id":actor.upper(),"name":"Own219"})
   for right in(["tare_offer","tare_view","stock_posting_shipping"]if actor==sender else["driver_return_accept","tare_accept","tare_view","tare_offer"]):
    api(admin_api,"POST",f"/api/admin/rights/groups/{actor.upper()}/rights",{"right_name":right,"description":"Own219"})
  binding=api(admin_api,"GET",f"/api/transport/driver-bindings/{driver}");assert not binding.get("active")
  enabled=api(admin_api,"PUT",f"/api/transport/driver-bindings/{driver}",{"user_id":driver_user,"active":True,"expected_version":binding["binding_version"]})
  sender_api=httpx.Client(auth=(sender,pw),timeout=35);driver_api=httpx.Client(auth=(driver_user,driver_pw),timeout=35)
  offer={"operation_id":"TARE219.OFFER:"+tag,"task_id":trip,"owner_ware_id":ware,"pallet_type_id":1,"condition":"GOOD","from_kind":"WAREHOUSE","from_id":str(ware),"to_kind":"VEHICLE","to_id":str(vehicle),"quantity":"1","scan_vehicle":"QL"+tag,"booking_operation_ids":[bookop]}
  api(sender_api,"POST","/api/inventory/tare/offer",offer)
  api(sender_api,"POST","/api/inventory/tare/offer",{**offer,"operation_id":offer["operation_id"]+":DUP"},status=409)
  unload={"operation_id":"TARE219.UNLOAD:"+tag,"load_operation_id":shipop,"expected_version":preview["expected_version"],"scan_container":lot,"scan_cell":shipcell,"scan_vehicle":"QL"+tag,"scan_dock":dock,"reason":"Own219 before acceptance"}
  api(sender_api,"POST","/api/transport/loading/unload",unload,status=409)
  cancel={"operation_id":"TARE219.CANCEL:"+tag,"offer_operation_id":offer["operation_id"],"scan_vehicle":"QL"+tag,"reason":"Own219 original sender cancels before driver accepts"}
  canonical=StockCommand(operation_id=cancel["operation_id"],command_type="TARE_OFFER_CANCEL",actor=sender,source={"offer_operation_id":offer["operation_id"]},metadata={k:v for k,v in cancel.items()if k not in("operation_id","offer_operation_id")},lines=()).canonical_json();out=q.var(oracledb.DB_TYPE_CLOB)
  try:
   q.callproc("RRL_STOCK_POSTING_API.prepare_command",[canonical,sender,out,None]);assert out.getvalue()is None
   q.callproc("RRL_STOCK_POSTING_API.execute_prepared",[out])
   q.execute("select count(*)from RRL_TARE_OFFER_CANCEL where OFFER_OPERATION_ID=:p",p=offer["operation_id"]);assert q.fetchone()[0]==1
  finally:conn.rollback();q.callproc("RRL_STOCK_POSTING_API.reset_connection")
  q.execute("select count(*)from RRL_TARE_OFFER_CANCEL where OFFER_OPERATION_ID=:p",p=offer["operation_id"]);assert q.fetchone()[0]==0
  with ThreadPoolExecutor(2)as pool:rs=list(pool.map(lambda b:sender_api.post(base+"/api/inventory/tare/offer-cancel",json=b),[cancel,{**cancel,"operation_id":cancel["operation_id"]+":OTHER"}]))
  assert sorted(r.status_code for r in rs)==[200,409],[(r.status_code,r.text[:1500])for r in rs]
  result=next(r.json()for r in rs if r.status_code==200);cancel["operation_id"]=result["operation_id"];assert api(sender_api,"POST","/api/inventory/tare/offer-cancel",cancel)==result
  q.execute("update RUSERS set WARE_ID=6667491 where ID=:p",p=sender);conn.commit()
  try:api(sender_api,"POST","/api/inventory/tare/offer-cancel",cancel,status=403)
  finally:q.execute("update RUSERS set WARE_ID=:w where ID=:p",w=ware,p=sender);conn.commit()
  old_accept={"operation_id":"TARE219.OLD.ACCEPT:"+tag,"offer_operation_id":offer["operation_id"],"accepted_quantity":"1","scan_vehicle":"QL"+tag}
  api(driver_api,"POST","/api/inventory/tare/accept",old_accept,status=409)
  q.execute("select STATUS from RRL_TARE_BOOK where OPERATION_ID=:p",p=bookop);assert q.fetchone()[0]=="HELD"
  q.execute("select QUANTITY from RRL_TARE_BALANCE where OWNER_WARE_ID=:w and CUSTODIAN_KIND='WAREHOUSE'",w=ware);assert q.fetchone()[0]==1
  # Native rollback proves cancelled association no longer blocks original unloading.
  doc=StockCommand(operation_id=unload["operation_id"],command_type="UNLOAD_SHIPMENT",actor=sender,source={"load_operation_id":shipop},metadata={k:v for k,v in unload.items()if k not in("operation_id","load_operation_id")},lines=()).canonical_json()
  try:
   q.callproc("RRL_STOCK_POSTING_API.prepare_command",[doc,sender,out,None]);q.callproc("RRL_STOCK_POSTING_API.execute_prepared",[out]);q.execute("select REMAIN,HARD_RESERVED_BASE from RRL_REMAINS where UID_POLETA=:u and CELL=:c",u=lot,c=shipcell);assert q.fetchone()==(3,3)
  finally:conn.rollback();q.callproc("RRL_STOCK_POSTING_API.reset_connection")
  # Existing sender can re-offer same HELD book after explicit cancellation.
  new_offer={**offer,"operation_id":"TARE219.REOFFER:"+tag};api(sender_api,"POST","/api/inventory/tare/offer",new_offer)
  accepted={**old_accept,"operation_id":"TARE219.ACCEPT:"+tag,"offer_operation_id":new_offer["operation_id"]};api(driver_api,"POST","/api/inventory/tare/accept",accepted)
  api(sender_api,"POST","/api/inventory/tare/offer-cancel",{**cancel,"operation_id":"TARE219.NO.CANCEL:"+tag,"offer_operation_id":new_offer["operation_id"]},status=409)
  history=api(sender_api,"GET",f"/api/inventory/tare/trips/{trip}/offers");assert any(r["operation_id"]==offer["operation_id"]and r["cancel_operation_id"]==cancel["operation_id"]for r in history)
  q.execute("select count(*)from RRL_EVENTS where OPERATION_ID=:p",p=cancel["operation_id"]);assert q.fetchone()[0]==0
  q.execute("select STATUS,CLOSED_OPERATION_ID from RRL_TARE_BOOK where OPERATION_ID=:p",p=bookop);assert q.fetchone()==("TRANSFERRED",accepted["operation_id"])
  print("PASS219 cancelled original pending handover preserves offer/book/balance; rollback/concurrent/replay/currentWARE403/no old accept/unload rollback3/3/reoffer actual accepted, transferred FULLPAL preserved for recovery",tag,ware,wave,lot,shipop,bookop,sender,driver_user,driver,trip,flush=True)
 finally:
  q.execute("select RESERVATION_ID from RRL_STOCK_RESERVATION where UID_PALLET=:u and BASE_QTY>0 and STATUS in('ACTIVE','ALLOCATED','PICKING')",u=other)
  for(rid,)in q.fetchall():post("RESERVATION_RELEASE",{"reason":"Own219 spare cleanup"},{"reservation_id":int(rid)})
  q.execute("select CELL,BASE_UOM,STOCK_VERSION from RRL_REMAINS where UID_POLETA=:u and REMAIN>0",u=other)
  counts=[{"uid":other,"cell":cell,"article":article,"unit":unit,"quantity":"0","expected_stock_version":int(v),"unit_keys":[]}for cell,unit,v in q.fetchall()]
  if counts:post("INVENTORY_COUNT",{"reason":"Own219 spare cleanup","counts":counts},{"revision_id":revision})
  q.execute("select sum(r.REMAIN),sum(r.HARD_RESERVED_BASE)from RRL_REMAINS r join RRL_CELLS c on c.CELL=r.CELL where c.WARE_ID=6667491");assert q.fetchone()==(20,20)
  print("Own219 spare0; shipped original primary3/P0H0 and transferred tare1 retained for actual next return/recovery; own dedicated driver binding active",flush=True)
"""
print(json.dumps({"scripts/ni063_pending_offer_cancel_case.py":s},ensure_ascii=True))
