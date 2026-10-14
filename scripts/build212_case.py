from pathlib import Path
import json
s=Path("scripts/ni042_case_mass_manifest_case.py").read_text(encoding="utf-8").replace("207","212")
s=s.replace('controller=None;','controller=None;')
start=s.index('  current_tree=hu_tree()',s.index('  call("PUT","/api/delivery/store-receipts/policy"'))
end=s.index('\n finally:',start)
s=s[:start]+'''  packing("HU_DETACH","SMALL212.STANDALONE:"+tag)
  from app.transport_composition import build_transport_loading
  loading=build_transport_loading();preview=loading.preview_single(identifier);tree=preview["snapshot"];load_version=preview["expected_version"]
  metadata={"expected_version":load_version,"expected_composition_signature":preview["composition_signature"],"scan_container":carrier,"scan_cell":tree["cell"],
   "loading_context":{"transport_task_id":trip,"scan_vehicle":plate,"scan_dock":dock,"measurements":{"origin":"MANUAL_CONFIRMED","content_version":load_version,"gross_weight_kg":"0.4","width_m":"0.5","depth_m":"0.5","height_m":"0.5"}}}
  load_id="SMALL212.LOAD:"+tag
  actual=loading.load_single(load_id,identifier,metadata,"admin");shipped=True
  assert loading.load_single(load_id,identifier,metadata,"admin")==actual
  q.execute("select sum(r.REMAIN),sum(r.HARD_RESERVED_BASE)from RRL_CASE_CARRIER_LOT h join RRL_REMAINS r on r.UID_POLETA=h.LOT_UID where h.CASE_PICK_TASK_ID=:p_case",p_case=case);assert q.fetchone()==(0,0)
  unloader="UL212"+tag;unload_group=unloader.upper();unload_secret=uuid4().hex
  q.execute("insert into RUSERS(ID,PASS,NAME,USER_GROUP,WARE_ID,DELETED,PRAVO_ADMIN_LOGIN)values(:p_actor,:p_secret,'Own212 expedition unloader',:p_group,:p_ware,0,0)",p_actor=unloader,p_secret=unload_secret,p_group=unload_group,p_ware=ware);c.commit()
  call("POST","/api/admin/rights/groups",{"id":unload_group,"name":"Own212 physical unloading"})
  call("POST",f"/api/admin/rights/groups/{unload_group}/rights",{"right_name":"stock_posting_shipping","description":"Own212 current warehouse expedition"})
  unloading=httpx.Client(auth=(unloader,unload_secret),timeout=35)
  body={"operation_id":"SMALL212.UNLOAD:"+tag,"load_operation_id":load_id,"expected_version":load_version,"scan_container":carrier,"scan_cell":tree["cell"],"scan_vehicle":plate,"scan_dock":dock,"reason":"Own212 physically unloaded before departure"}
  uri="/api/transport/loading/unload"
  refused=unloading.post(base+uri,json={**body,"scan_vehicle":"OTHER"});assert refused.status_code==409,(refused.status_code,refused.text[:1800])
  forbidden=unloading.post(base+uri,json={**body,"quantity":"100"});assert forbidden.status_code==422
  canonical=StockCommand(operation_id=body["operation_id"],command_type="UNLOAD_SHIPMENT",actor=unloader,source={"load_operation_id":load_id},metadata={k:v for k,v in body.items()if k not in("operation_id","load_operation_id")},lines=()).canonical_json()
  result=q.var(oracledb.DB_TYPE_CLOB)
  try:
   q.callproc("RRL_STOCK_POSTING_API.prepare_command",[canonical,unloader,result,None]);assert result.getvalue()is None
   q.callproc("RRL_STOCK_POSTING_API.execute_prepared",[result])
   q.execute("select sum(r.REMAIN),sum(r.HARD_RESERVED_BASE)from RRL_CASE_CARRIER_LOT h join RRL_REMAINS r on r.UID_POLETA=h.LOT_UID where h.CASE_PICK_TASK_ID=:p_case",p_case=case);assert q.fetchone()==(6,6)
   q.execute("select STATUS from RRL_TT_HU_LOAD_FACT where LOAD_OPERATION_ID=:p_op",p_op=load_id);assert q.fetchone()[0]=="UNLOADED"
  finally:c.rollback();q.callproc("RRL_STOCK_POSTING_API.reset_connection")
  q.execute("select count(*)from RRL_TT_UNLOAD_FACT where LOAD_OPERATION_ID=:p_op",p_op=load_id);assert q.fetchone()[0]==0
  q.execute("select STATUS from RRL_TT_HU_LOAD_FACT where LOAD_OPERATION_ID=:p_op",p_op=load_id);assert q.fetchone()[0]=="LOADED"
  q.execute("select sum(r.REMAIN),sum(r.HARD_RESERVED_BASE)from RRL_CASE_CARRIER_LOT h join RRL_REMAINS r on r.UID_POLETA=h.LOT_UID where h.CASE_PICK_TASK_ID=:p_case",p_case=case);assert q.fetchone()==(0,0)
  with ThreadPoolExecutor(2)as pool:
   responses=list(pool.map(lambda payload:unloading.post(base+uri,json=payload),[body,{**body,"operation_id":body["operation_id"]+":OTHER"}]))
  assert sorted(x.status_code for x in responses)==[200,409],[(x.status_code,x.text[:1800])for x in responses]
  winner=next(x.json()for x in responses if x.status_code==200);body["operation_id"]=winner["operation_id"];shipped=False
  assert unloading.post(base+uri,json=body).json()==winner
  q.execute("select sum(r.REMAIN),sum(r.HARD_RESERVED_BASE)from RRL_CASE_CARRIER_LOT h join RRL_REMAINS r on r.UID_POLETA=h.LOT_UID where h.CASE_PICK_TASK_ID=:p_case",p_case=case);assert q.fetchone()==(6,6)
  q.execute("select STATUS,SHIPPED_OPERATION_ID from RRL_CUSTOMER_ORDER_FULFILLMENT where LEGACY_SBORKA_PALLET_ID=:p_id",p_id=sid);assert q.fetchone()==("PICKED",None)
  q.execute("select count(*)from RRL_TT_HU_LOAD_ST where LOAD_OPERATION_ID=:p_op and ACTIVE_FLAG=1",p_op=load_id);assert q.fetchone()[0]==0
  q.execute("select sum(BASE_QTY)from RRL_EVENTS where OPERATION_ID=:p_op",p_op=load_id);assert q.fetchone()[0]==-6
  q.execute("select sum(BASE_QTY)from RRL_EVENTS where OPERATION_ID=:p_op",p_op=body["operation_id"]);assert q.fetchone()[0]==6
  q.execute("update RUSERS set WARE_ID=6667491 where ID=:p_actor",p_actor=unloader);c.commit()
  foreign=unloading.post(base+uri,json=body);assert foreign.status_code==403,(foreign.status_code,foreign.text[:1600])
  q.execute("update RUSERS set WARE_ID=:p_ware where ID=:p_actor",p_ware=ware,p_actor=unloader);c.commit()
  assert not quality.status(identifier)["ready"]
  try:q.execute("delete from RRL_TT_UNLOAD_FACT where LOAD_OPERATION_ID=:p_op",p_op=load_id);raise AssertionError("Unloading fact deleted")
  except oracledb.DatabaseError as exc:c.rollback();assert exc.args[0].code==20863
  print("PASS212 actual standaloneCASE6 loaded/P0H0 then separate physical unloading/native late rollback/concurrent1winner/exact replay/foreign saved replay403/P6H6/old journal-6 preserved/newjournal+6/fulfillmentPICKED/control revoked/old box mass history retained/no quantity override",article,load_id,winner["operation_id"],flush=True)
'''+s[end:]
# A failed post-load case remains active for repair; do not manufacture a completed wave.
s=s.replace('  if wave is not None:\n   q.execute("select STATUS from RRL_PICK_WAVE','  if wave is not None and not shipped:\n   q.execute("select STATUS from RRL_PICK_WAVE')
s=s.replace('  if controller is not None:q.execute','  if "unloader"in locals():q.execute("update RUSERS set DELETED=1 where ID=:p_actor",p_actor=unloader);c.commit()\n  if controller is not None:q.execute')
print(json.dumps({"scripts/ni052_standalone_case_unload_case.py":s},ensure_ascii=True))
