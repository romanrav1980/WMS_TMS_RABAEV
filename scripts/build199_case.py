from pathlib import Path
import json
s=Path("scripts/ni042_weight_box_sap_case.py").read_text(encoding="utf-8")
s=s.replace("tag=uuid4().hex[:8]","tag=sys.argv[1]if len(sys.argv)>1 else uuid4().hex[:8]")
s=s.replace("QW180","QPB199").replace("Q180","Q199").replace("WEIGHT180","DIRECT199").replace("W180:","D199:")
s=s.replace('"KG"','"EA"').replace("TYPE_W=3","TYPE_W=0").replace('"serialized_weight_boxes":True','"serialized_weight_boxes":False')
s=s.replace('[(receive,0),(pick,1),(storage,0)]','[(receive,0),(pick,1),(storage,0),("CPT_"+str(ware),0)]')
s=s.replace("MIN_SHELF_DAYS,ALLOW_PICK_BATCH_MIX)values(:p_ware,:p_a,:p_pick,0,0)","MIN_SHELF_DAYS,ALLOW_PICK_BATCH_MIX,SOURCE_PICK_MODE)values(:p_ware,:p_a,:p_pick,0,0,'DIRECT')")
s=s.replace('.text="9.8"','.text="20"')
start=s.index(' body={"operation_id"')
end=s.index(' try:',start)
s=s[:start]+''' body={"operation_id":"DIRECT199.RECEIVE:"+tag,"line_number":"1","sscc":sscc,"quantity":"20","product_barcode":gtin,"supplier_batch":"PB:"+tag,"expiry_date":"2030-01-01","gross_weight":"20"}
 from app.services.picking_service import PickingService
 from app.schemas import PickingPlanCreateRequest,PickWaveCreateRequest,PickWaveAddPlanRequest,PickWaveActionRequest
 from app.modules.inventory.contracts_stock import StockCommand
 from app.modules.inventory.infrastructure.stock_posting_uow import StockPosting
 from app.modules.platform.public import read_oracle_json
 from app.oracle_gateway import OracleGateway
 picking=PickingService();orders=[];plans=[];wave=None;bookings=[];case_types=set()
 def post(kind,source,metadata,op=None):
  return StockPosting().post(StockCommand(operation_id=op or "DIRECT199:"+uuid4().hex,command_type=kind,actor="admin",source=source,metadata=metadata,lines=()))
 def seq(name):q.execute("select "+name+".nextval from dual");return int(q.fetchone()[0])
 q.execute("select min(CUSTOMER_ID),max(CUSTOMER_ID)from RRL_CUSTOMER");customers=q.fetchone()
 for customer,quantity in zip(customers,(12,8)):
  order=seq("RRL_CUSTOMER_ORDER_SQ");orders.append(order)
  meta("insert into RRL_CUSTOMER_ORDER(CUSTOMER_ORDER_ID,ORDER_NO,CUSTOMER_ID,WARE_ID)values(:p_id,:p_no,:p_customer,:p_ware)",p_id=order,p_no="DIRECT199:"+tag+":"+str(quantity),p_customer=customer,p_ware=ware)
  meta("insert into RRL_CUSTOMER_ORDER_ROW(CUSTOMER_ORDER_ROW_ID,CUSTOMER_ORDER_ID,LINE_NO,ARTICUL,ORDER_QTY,UNIT_CODE)values(RRL_CUSTOMER_ORDER_ROW_SQ.nextval,:p_order,1,:p_article,:p_qty,'EA')",p_order=order,p_article=article,p_qty=quantity)
  empty=picking.create_plan(PickingPlanCreateRequest(customer_order_id=order,created_by="admin"))
  q.execute("select STATUS,PLANNED_QTY from RRL_PICK_PLAN where PICK_PLAN_ID=:p_id",p_id=empty);assert q.fetchone()==("NO_STOCK",0)
  picking.cancel_plan(empty,"admin")
''' +s[end:]
start=s.index('  task=result["task_id"]')
end=s.index('\n finally:',start)
s=s[:start]+'''  task=result["task_id"];assert result["marking_units"]==0
  assert call("POST",f"/api/receiving/supply-orders/{imported['order_id']}/pallets",body,201)==result
  # An in-progress physical putaway must block DIRECT admission.
  meta("update RRL_WAREHOUSE_TASK set STATUS='IN_PROGRESS'where TASK_ID=:p_task",p_task=task)
  from fastapi import HTTPException
  try:
   empty=picking.create_plan(PickingPlanCreateRequest(customer_order_id=orders[0],created_by="admin"))
   q.execute("select STATUS,PLANNED_QTY from RRL_PICK_PLAN where PICK_PLAN_ID=:p_id",p_id=empty);assert q.fetchone()==("NO_STOCK",0)
   picking.cancel_plan(empty,"admin")
  finally:meta("update RRL_WAREHOUSE_TASK set STATUS='PLANNED'where TASK_ID=:p_task",p_task=task)
  for order in orders:
   plan=picking.create_plan(PickingPlanCreateRequest(customer_order_id=order,created_by="admin"));plans.append(plan)
   q.execute("select TASK_TYPE,SOURCE_CELL_CODE,TARGET_CELL_CODE from RRL_PICK_TASK where PICK_PLAN_ID=:p_plan",p_plan=plan);assert q.fetchone()==("CASE_PICK",receive,None)
  wave=picking.create_wave(PickWaveCreateRequest(wave_code="DIRECT199:"+tag,ware_id=ware,created_by="admin"))
  for plan in plans:picking.add_wave_plan(wave,PickWaveAddPlanRequest(pick_plan_id=plan,created_by="admin"))
  picking.preview_wave(wave,PickWaveActionRequest(updated_by="admin"))
  picking.launch_wave(wave,PickWaveActionRequest(updated_by="admin",operation_id="DIRECT199.LAUNCH:"+tag))
  q.execute("select STATUS,LAST_ERROR,QTY from RRL_WAREHOUSE_TASK where TASK_ID=:p_task",p_task=task);state,reason,qty=q.fetchone()
  assert state=="CANCELLED"and reason=="DIRECT_PICK_BY_LINE:DIRECT199.LAUNCH:"+tag and qty==20
  q.execute("select count(*)from RRL_PICK_WAVE_REPLENISH_TASK where PICK_WAVE_ID=:p_wave",p_wave=wave);assert q.fetchone()[0]==0
  q.execute("select count(*)from RRL_RECEIPT_SLOT_CLAIM where TASK_ID=:p_task",p_task=task);assert q.fetchone()[0]==0
  post("WAVE_PICK_RELEASE",{"wave_id":wave},{})
  q.execute("select t.CASE_PICK_TASK_ID,l.CASE_PICK_LINE_ID,t.SSCC,l.CELL_CODE,l.PLANNED_QTY,t.PALLET_TYPE_ID from RRL_CASE_PICK_TASK t join RRL_CASE_PICK_LINE l on l.CASE_PICK_TASK_ID=t.CASE_PICK_TASK_ID where t.PICK_WAVE_ID=:p_wave order by t.CUSTOMER_ORDER_ID",p_wave=wave)
  rows=q.fetchall();assert sorted(r[4]for r in rows)==[8,12]
  tare="/api/inventory/tare"
  for case,line,carrier,cell,quantity,case_type in rows:
   assert cell==receive;case_types.add(case_type)
   available=call("GET",tare+f"/warehouses/{ware}/availability")
   current=next(x for x in available if x["pallet_type_id"]==case_type)
   call("POST",tare+"/count",{"operation_id":"DIRECT199.TARE.COUNT:"+str(case),"owner_ware_id":ware,"pallet_type_id":case_type,"condition":"GOOD","observed_quantity":"2","expected_version":current["balance_version"]or 0,"reason":"Own199 software container fixture","decision_reference":"DIRECT199:"+tag})
   book="DIRECT199.TARE.BOOK:"+str(case);call("POST",tare+"/book",{"operation_id":book,"place_kind":"CASE","place_id":str(case)});bookings.append(book)
   call("POST",f"/api/case-pick/tasks/{case}/claim",{});call("POST",f"/api/case-pick/tasks/{case}/start",{})
   payload={"operation_id":"DIRECT199.PICK:"+str(case),"fact_qty":str(quantity),"scan_cell":receive,"scan_product":gtin,"scan_container":carrier}
   path=f"/api/case-pick/tasks/{case}/lines/{line}/confirm"
   picked=call("POST",path,payload);assert call("POST",path,payload)==picked
  q.execute("select REMAIN,HARD_RESERVED_BASE from RRL_REMAINS where UID_POLETA=:p_uid and CELL=:p_cell",p_uid=sscc,p_cell=receive);assert q.fetchone()==(0,0)
  q.execute("select sum(PICKED_QTY)from RRL_CASE_PICK_LINE where PICK_WAVE_ID=:p_wave",p_wave=wave);assert q.fetchone()[0]==20
  print("PASS199 actual SAP EA20/current DIRECT/awaiting before receipt/two original stores12+8/no rack target/no replenishment/source HARD20/existing CASE picks20/replay/putaway cancelled with originalQTY20 retained/no double path",article,wave,flush=True)
''' +s[end:]
start=s.index('\n finally:')
s=s[:start]+'''
 finally:
  if wave is not None:
   q.execute("select CASE_PICK_TASK_ID,SSCC,CONTENT_VERSION from RRL_CASE_PICK_TASK where PICK_WAVE_ID=:p_wave",p_wave=wave)
   for case,carrier,version in q.fetchall():
    q.execute("select h.LOT_UID from RRL_CASE_CARRIER_LOT h join RRL_REMAINS r on r.UID_POLETA=h.LOT_UID where h.CASE_PICK_TASK_ID=:p_case and r.REMAIN>0",p_case=case)
    lots=[x[0]for x in q.fetchall()]
    post("CASE_CARRIER_RETURN",{"case_task_id":int(case)},{"scan_container":carrier,"expected_content_version":int(version),"allow_empty":not bool(lots),"destinations":{uid:receive for uid in lots},"reason":"Own199 native direct CASE return"})
   q.execute("select RESERVATION_ID from RRL_STOCK_RESERVATION where SOURCE_DOC_TYPE='PICK_WAVE'and SOURCE_DOC_ID=:p_wave and STATUS in('ACTIVE','ALLOCATED','PICKING')and BASE_QTY>0",p_wave=wave)
   for(rid,)in q.fetchall():post("RESERVATION_RELEASE",{"reservation_id":int(rid)},{"reason":"Own199 release"})
  for book in bookings:call("POST","/api/inventory/tare/book-cancel",{"operation_id":"DIRECT199.BOOK.CANCEL:"+book,"booking_operation_id":book})
  if wave is not None:
   q.execute("select STATUS from RRL_PICK_WAVE where PICK_WAVE_ID=:p_wave",p_wave=wave)
   if q.fetchone()[0]=="LAUNCHED":post("WAVE_EXECUTION_FINISH",{"wave_id":wave},{"disposition":"RETURNED_TO_PLANNING","reason":"Own199 returned demands remain"})
   else:post("WAVE_CANCEL",{"document_type":"PICK_WAVE","document_id":wave},{"reason":"Own199 unlaunched cleanup"})
  else:
   for plan in plans:picking.cancel_plan(plan,"admin")
  if born:
   from app.modules.inventory.infrastructure.receiving import Receiving
   Receiving(OracleGateway()).cancel(task,"Owned199 fixture cleanup","admin")
   q.execute("select r.UID_POLETA,r.CELL,r.BASE_UOM,r.STOCK_VERSION from RRL_REMAINS r join RRL_PALLETS p on p.UID_PALLET=r.UID_POLETA where p.ARTICUL=:p_a and r.REMAIN>0",p_a=article)
   counts=[{"uid":uid,"cell":cell,"article":article,"unit":unit,"quantity":"0","expected_stock_version":int(v),"unit_keys":[]}for uid,cell,unit,v in q.fetchall()]
   if counts:post("INVENTORY_COUNT",{"revision_id":revision},{"reason":"Own199 native cleanup","counts":counts})
  q.execute("select nvl(sum(r.REMAIN),0),nvl(sum(r.HARD_RESERVED_BASE),0)from RRL_REMAINS r join RRL_CELLS c on c.CELL=r.CELL where c.WARE_ID=:p_ware",p_ware=ware);assert q.fetchone()==(0,0)
  q.execute("select sum(r.REMAIN),sum(r.HARD_RESERVED_BASE)from RRL_REMAINS r join RRL_CELLS c on c.CELL=r.CELL where c.WARE_ID=6667491");assert q.fetchone()==(20,20)
  print("Own199 native return/release/count completed; original135 P20H20 unchanged",flush=True)
'''
print(json.dumps({"scripts/ni042_direct_receiving_case.py":s},ensure_ascii=True))
