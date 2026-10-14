from pathlib import Path
import json
s=Path("scripts/ni052_slotted_hu_unload_case.py").read_text(encoding="utf-8").replace("215","216")
s=s.replace('  q.execute("select min(ID)from RRL_TR_VODITEL where ID>0");driver=q.fetchone()[0]','  driver=seq("RRL_TR_VODITEL_SQ")\n  meta("insert into RRL_TR_VODITEL(ID,F,I,O,DELETED)values(:p_id,\'Own216\',:p_tag,\'Driver\',0)",p_id=driver,p_tag=tag)')
anchor='  canonical=StockCommand(operation_id=body["operation_id"],command_type="UNLOAD_SHIPMENT"'
idx=s.index(anchor)
# Late capacity checks must run after returned tare proof, so move the complete existing refusal block too.
start=s.index('  no_slot={')
capacity=s[start:idx]
s=s[:start]+s[idx:];idx=s.index(anchor)
extra="""  driver_user="DR216"+tag;driver_group=driver_user.upper();driver_secret=uuid4().hex
  receiver="WR216"+tag;receiver_group=receiver.upper();receiver_secret=uuid4().hex
  for name,group,secret,warehouse in[(driver_user,driver_group,driver_secret,None),(receiver,receiver_group,receiver_secret,ware)]:
   q.execute("insert into RUSERS(ID,PASS,NAME,USER_GROUP,WARE_ID,DELETED,PRAVO_ADMIN_LOGIN)values(:p_id,:p_secret,'Own216 tare participant',:p_group,:p_ware,0,0)",p_id=name,p_secret=secret,p_group=group,p_ware=warehouse);c.commit()
   call("POST","/api/admin/rights/groups",{"id":group,"name":"Own216 tare custody"})
   for right in(["driver_return_accept","tare_offer","tare_accept","tare_view"]if warehouse is None else["tare_accept","tare_plan","tare_view"]):
    call("POST",f"/api/admin/rights/groups/{group}/rights",{"right_name":right,"description":"Own216 exact participant"})
  binding=call("GET",f"/api/transport/driver-bindings/{driver}");assert not binding.get("active")
  enabled=call("PUT",f"/api/transport/driver-bindings/{driver}",{"user_id":driver_user,"active":True,"expected_version":binding["binding_version"]})
  driver_api=httpx.Client(auth=(driver_user,driver_secret),timeout=35);receiver_api=httpx.Client(auth=(receiver,receiver_secret),timeout=35)
  def actor_call(client,path,payload,status=200):
   response=client.post(base+path,json=payload);assert response.status_code==status,(response.status_code,response.text[:2000]);return response.json()
  offer={"operation_id":"TARE216.OUT:"+tag,"task_id":trip,"owner_ware_id":ware,"pallet_type_id":small_type,"condition":"GOOD","from_kind":"WAREHOUSE","from_id":str(ware),"to_kind":"VEHICLE","to_id":str(vehicle),"quantity":"1","scan_vehicle":plate,"booking_operation_ids":[book]}
  call("POST","/api/inventory/tare/offer",offer)
  out_accept={"operation_id":"TARE216.OUT.ACCEPT:"+tag,"offer_operation_id":offer["operation_id"],"accepted_quantity":"1","scan_vehicle":plate}
  actor_call(driver_api,"/api/inventory/tare/accept",out_accept)
  q.execute("select STATUS,CLOSED_OPERATION_ID from RRL_TARE_BOOK where OPERATION_ID=:p_book",p_book=book);assert q.fetchone()==("TRANSFERRED",out_accept["operation_id"])
  blocked=unloading.post(base+uri,json=body);assert blocked.status_code==409 and "UNLOAD_TARE_HANDOVER_DECISION_REQUIRED"in blocked.text
  back={**offer,"operation_id":"TARE216.BACK:"+tag,"from_kind":"VEHICLE","from_id":str(vehicle),"to_kind":"WAREHOUSE","to_id":str(ware),"booking_operation_ids":[]}
  actor_call(driver_api,"/api/inventory/tare/offer",back)
  reclaim={"operation_id":"TARE216.RECOVERY:"+tag,"place_kind":"CASE","place_id":str(case),"pallet_type_id":small_type,"expected_warehouse_id":ware,"load_recovery":{"load_operation_id":load_id,"original_booking_operation_id":book,"return_offer_operation_id":back["operation_id"],"expected_load_version":load_version,"scan_place":carrier}}
  actor_call(receiver_api,"/api/inventory/tare/book",reclaim,409)
  back_accept={"operation_id":"TARE216.BACK.ACCEPT:"+tag,"offer_operation_id":back["operation_id"],"accepted_quantity":"1","scan_vehicle":plate}
  actor_call(receiver_api,"/api/inventory/tare/accept",back_accept)
  command=StockCommand(operation_id=reclaim["operation_id"],command_type="TARE_BOOK",actor=receiver,source={"place_kind":"CASE","place_id":str(case)},metadata={"pallet_type_id":small_type,"expected_warehouse_id":ware,"load_recovery":reclaim["load_recovery"]},lines=())
  outcome=q.var(oracledb.DB_TYPE_CLOB)
  try:
   q.callproc("RRL_STOCK_POSTING_API.prepare_command",[command.canonical_json(),receiver,outcome,None]);assert outcome.getvalue()is None
   q.callproc("RRL_STOCK_POSTING_API.execute_prepared",[outcome])
   q.execute("select count(*)from RRL_TARE_LOAD_RECOVERY where OPERATION_ID=:p_op",p_op=reclaim["operation_id"]);assert q.fetchone()[0]==1
  finally:c.rollback();q.callproc("RRL_STOCK_POSTING_API.reset_connection")
  q.execute("select count(*)from RRL_TARE_LOAD_RECOVERY where ORIGINAL_BOOK_OPERATION_ID=:p_book",p_book=book);assert q.fetchone()[0]==0
  with ThreadPoolExecutor(2)as pool:replies=list(pool.map(lambda b:receiver_api.post(base+"/api/inventory/tare/book",json=b),[reclaim,{**reclaim,"operation_id":reclaim["operation_id"]+":OTHER"}]))
  assert sorted(r.status_code for r in replies)==[200,409],[(r.status_code,r.text[:1800])for r in replies]
  recovered=next(r.json()for r in replies if r.status_code==200);reclaim["operation_id"]=recovered["operation_id"]
  assert receiver_api.post(base+"/api/inventory/tare/book",json=reclaim).json()==recovered
  q.execute("update RUSERS set WARE_ID=6667491 where ID=:p_actor",p_actor=receiver);c.commit()
  try:assert receiver_api.post(base+"/api/inventory/tare/book",json=reclaim).status_code==403
  finally:q.execute("update RUSERS set WARE_ID=:p_ware where ID=:p_actor",p_ware=ware,p_actor=receiver);c.commit()
  bookings=[reclaim["operation_id"]]
  q.execute("select CUSTODIAN_KIND,QUANTITY from RRL_TARE_BALANCE where OWNER_WARE_ID=:p_ware and PALLET_TYPE_ID=:p_type",p_ware=ware,p_type=small_type);assert dict(q.fetchall())=={"WAREHOUSE":1,"VEHICLE":0}
  q.execute("select STATUS,CLOSED_OPERATION_ID from RRL_TARE_BOOK where OPERATION_ID=:p_book",p_book=book);assert q.fetchone()==("TRANSFERRED",out_accept["operation_id"])
  print("PASS216 existing two-actor original nestedCASE tare accepted vehicle1→warehouse1/new originalCASE HELD recovery/original transferred history/late rollback/concurrent1winner/replay/currentWARE403/goods unchanged until unload",reclaim["operation_id"],flush=True)
"""
s=s[:idx]+extra+capacity+s[idx:]
# Retire only owned participants and binding; never modify a pre-existing driver.
anchor='  if "unloader"in locals():'
idx=s.index(anchor)
extra="""  if "enabled"in locals():call("PUT",f"/api/transport/driver-bindings/{driver}",{"user_id":driver_user,"active":False,"expected_version":enabled["binding_version"]})
  for actor in[locals().get("driver_user"),locals().get("receiver")]:
   if actor:q.execute("update RUSERS set DELETED=1 where ID=:p_actor",p_actor=actor);c.commit()
"""
s=s[:idx]+extra+s[idx:]
print(json.dumps({"scripts/ni063_load_tare_recovery_case.py":s},ensure_ascii=True))
