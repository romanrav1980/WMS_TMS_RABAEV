from pathlib import Path
import json
s=Path("scripts/ni042_small_hu_control_case.py").read_text(encoding="utf-8").replace("206","207")
s=s.replace("parent=None","parent=None;shipped=False",1)
start=s.index('  signature=quality.status(identifier)["composition_signature"]')
end=s.index('  print("PASS207 own small type/',start)
new="""  signature=quality.status(identifier)["composition_signature"]
  packing("HU_ATTACH","SMALL207.CONTROLLED.PACK:"+tag)
  from app.modules.inventory.infrastructure.warehouse_hu import WarehouseHu
  warehouse_hus=WarehouseHu(OracleGateway())
  view=warehouse_hus.preview(parent,"admin")
  assert view["quantities"]==[{"article":article,"base_uom":"EA","quantity":"6"}]
  assert view["gross_weight_kg"]=="1.4"and view["unknown_tare_containers"]==0 and view["unknown_weight_leaves"]==0,view
  q.execute("select min(TRANSPORTTYPE)from RRL_TRANSPORT_TYPE");trtype=q.fetchone()[0]
  q.execute("select min(ID)from RRL_TR_VODITEL where ID>0");driver=q.fetchone()[0]
  plate="QV207"+tag;vehicle=int(q.callfunc("RRL_TR_VEHICLE_ADD",oracledb.DB_TYPE_NUMBER,[plate,trtype,100,1,0,None]));c.commit()
  trip=seq("RRL_TRANSPORT_TASK_SQ");dock="QD207"+tag;store="Own207 store "+tag
  meta("insert into RRL_TT_DOCK(DOCK,WARE_ID,DOCK_IS_BLOCKED)values(:p_dock,:p_ware,0)",p_dock=dock,p_ware=ware)
  meta("insert into RRL_TRANSPORT_TASK(ID,TRANSPORT,TRANSTYPE,CONDITION,SHIPMENT_DATE,VODITEL_ID,DOCK,DELETED)values(:p_id,:p_plate,:p_type,unistr('\\0421\\043F\\043B\\0430\\043D\\0438\\0440\\043E\\0432\\0430\\043D'),trunc(sysdate),:p_driver,:p_dock,0)",p_id=trip,p_plate=plate,p_type=trtype,p_driver=driver,p_dock=dock)
  meta("update RRL_TR_VEHICLE set MAX_WEIGHT_KG=100,WORKING_NOW=1,BLOCKED=0 where ID=:p_id",p_id=vehicle)
  meta("update RRL_SBORKA_PALLETS set TRANSTASK_ID=:p_trip,ADDR=:p_store where ID=:p_id",p_trip=trip,p_store=store,p_id=sid)
  call("PUT","/api/delivery/store-receipts/policy",{"store_address":store,"mode":"WEIGHT_PHOTO","expected_version":0})
  current_tree=hu_tree()
  context={"transport_task_id":trip,"scan_vehicle":plate,"scan_dock":dock,"measurements":{"origin":"MANUAL_CONFIRMED","content_version":current_tree["nodes"][0]["version"],"gross_weight_kg":"1.4","width_m":"0.5","depth_m":"0.5","height_m":"0.5"}}
  ship_body={"expected_version":current_tree["nodes"][0]["version"],"scan_container":parent,"scan_cell":current_tree["cell"],"loading_context":context}
  op="SMALL207.LOAD:"+tag
  # Explicit fake CASE measurement is rejected; the native compiler derives real .400.
  fake={"box_uid":"CASE:"+str(case),"content_version":case_version(),"scan_box":carrier,"gross_weight_kg":"1","origin":"MANUAL_CONFIRMED","measurement_ref":"fake"}
  try:post("HU_SHIP",{"uid":parent},{**ship_body,"loading_context":{**context,"physical_boxes":[fake]}},"SMALL207.FAKE:"+tag);raise AssertionError("Manual CASE mass accepted")
  except Exception as exc:assert "LOAD_CASE_BOX_SERVER_SOURCE_REQUIRED"in str(getattr(exc,"rule_reason",exc)),str(exc)
  # Native late rollback must restore stock and remove frozen box rows/load facts.
  canonical=StockCommand(operation_id=op,command_type="HU_SHIP",actor="admin",source={"uid":parent},metadata=ship_body,lines=()).canonical_json()
  result=q.var(oracledb.DB_TYPE_CLOB)
  try:
   q.callproc("RRL_STOCK_POSTING_API.prepare_command",[canonical,"admin",result,None]);assert result.getvalue()is None
   q.callproc("RRL_STOCK_POSTING_API.execute_prepared",[result])
   q.execute("select count(*)from RRL_TT_LOAD_BOX_WEIGHT where LOAD_OPERATION_ID=:p_op",p_op=op);assert q.fetchone()[0]==1
  finally:c.rollback();q.callproc("RRL_STOCK_POSTING_API.reset_connection")
  q.execute("select count(*)from RRL_TT_LOAD_BOX_WEIGHT where LOAD_OPERATION_ID=:p_op",p_op=op);assert q.fetchone()[0]==0
  q.execute("select sum(r.REMAIN),sum(r.HARD_RESERVED_BASE)from RRL_CASE_CARRIER_LOT h join RRL_REMAINS r on r.UID_POLETA=h.LOT_UID where h.CASE_PICK_TASK_ID=:p_case",p_case=case);assert q.fetchone()==(6,6)
  actual=post("HU_SHIP",{"uid":parent},ship_body,op);shipped=True
  assert post("HU_SHIP",{"uid":parent},ship_body,op)==actual
  q.execute("select BOX_UID,CASE_BOX_TASK_ID,PALLET_BOX_UID,GROSS_WEIGHT_KG,TARE_WEIGHT_KG,NET_WEIGHT_KG,DEVICE_MODE,WAREHOUSE_QC_OPERATION,FINAL_SCALE_CAPTURE,COVERAGE_COMPLETE from RRL_TT_LOAD_BOX_WEIGHT where LOAD_OPERATION_ID=:p_op",p_op=op)
  frozen=q.fetchone();assert frozen[:3]==("CASE:"+str(case),case,None)
  assert tuple(Decimal(str(x))for x in frozen[3:6])==(Decimal(".4"),Decimal(".1"),Decimal(".3"))
  assert frozen[6:]==("TEST",check["operation_id"],check["capture_key"],1)
  from app.transport_composition import build_transport_loading
  loading=build_transport_loading();depart=loading.depart("SMALL207.DEPART:"+tag,trip,"admin");assert not depart["stock_consumed_again"]
  preview=call("GET","/api/delivery/store-receipts/"+op+"/preview?store_address="+store.replace(" ","%20"))
  assert preview["shipping_gross_weight_kg"]=="1.4"and preview["shipping_weight_tolerance_kg"]=="0.2",preview
  box=preview["physical_boxes"][0]
  assert box["sscc"]==carrier and box["gross_weight_kg"]=="0.4"and box["tare_weight_kg"]=="0.1"and box["net_weight_kg"]=="0.3"
  assert box["origin"]=="WAREHOUSE_SCALE_QC"and box["device_mode"]=="TEST"and box["signature_version"]==3 and box["coverage_complete"]
  assert box["warehouse_qc_operation"]==check["operation_id"]and box["final_scale_capture"]==check["capture_key"]
  historical=warehouse_hus.preview(parent,"admin");assert historical["historical_composition"]and historical["gross_weight_kg"]=="1.4"
  print("PASS207 actual CASE measuredmass read/one .400 box+outer1.0=1.4/no duplicate6EA/fake mass refused/native late rollback/original HU load+departure/replay/frozen conditionalFK CASE/mass.400 tare.100 net.300 available tostore",article,op,flush=True)
"""
s=s[:start]+new+s[end:]
# Shipping has already consumed the CASE; do not return it or cancel handed-over physical tare booking.
s=s.replace("  if parent is not None:\n","  if parent is not None and not shipped:\n",1)
s=s.replace('  if wave is not None:\n   q.execute("select CASE_PICK_TASK_ID','  if wave is not None and not shipped:\n   q.execute("select CASE_PICK_TASK_ID',1)
# Tare transfer may be a pending handover for the physically loaded small box. Preserve that fact.
s=s.replace('  for book in bookings:call(', '  for book in ([] if shipped else bookings):call(',1)
# Do not zero booked/handed-over assets after real loading; source fixture goods are still cleaned natively.
s=s.replace('  for case_type in case_types:\n','  for case_type in ([] if shipped else case_types):\n',1)
s=s.replace('   if q.fetchone()[0]=="LAUNCHED":post("WAVE_EXECUTION_FINISH"', '   if q.fetchone()[0]=="LAUNCHED":post("WAVE_EXECUTION_FINISH"',1)
s=s.replace('{"disposition":"RETURNED_TO_PLANNING","reason":"Own207 returned demands remain"}','{"disposition":"NORMAL" if shipped else "RETURNED_TO_PLANNING","reason":"Own207 current physical shipment" if shipped else "Own207 returned demands remain"}')
print(json.dumps({"scripts/ni042_case_mass_manifest_case.py":s},ensure_ascii=True))
