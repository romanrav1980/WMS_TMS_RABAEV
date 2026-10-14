"""Actual full-pallet move -> existing ST binding -> pinned shipment; clean only own P/H through root."""
import json,sys
from pathlib import Path
from uuid import uuid4
import oracledb
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment()
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"api/wms_api_server"))
from app.config import get_settings
from app.oracle_gateway import OracleGateway
from app.modules.inventory.infrastructure.fullpal_shipment import FullPalletShipment
from app.modules.fulfillment.infrastructure.execution_progress import OrderExecution
cfg=get_settings();tag=uuid4().hex[:10];lot="FULL.QA:"+tag;other=lot+"O";src="QF"+tag;dst="QG"+tag;st_uid="FULL.ST:"+tag
with oracledb.connect(user=cfg.oracle_user,password=cfg.oracle_password,dsn=cfg.oracle_dsn) as conn:
 conn.call_timeout=15000;q=conn.cursor()
 def meta(sql,**b):
  if ":ware" in sql:b["ware"]=ware
  q.callproc("RRL_STOCK_CONFIG_API.begin_change",["admin","warehouse_settings_edit"])
  try:q.execute(sql,b);conn.commit()
  except BaseException:conn.rollback();raise
  finally:q.callproc("RRL_STOCK_CONFIG_API.end_change")
 def seq(name):
  q.execute("select "+name+".nextval from dual");return int(q.fetchone()[0])
 def post(kind,body,source,op=None):
  command={"contract_version":2,"operation_id":op or "FULL.QA:"+uuid4().hex,"command_type":kind,"actor":"admin","source":source,"lines":[],"units":[],"metadata":body}
  inp,out=q.var(oracledb.DB_TYPE_CLOB),q.var(oracledb.DB_TYPE_CLOB);inp.setvalue(0,json.dumps(command))
  try:
   q.callproc("RRL_STOCK_POSTING_API.prepare_command",[json.dumps(command),"admin",out,None])
   if out.getvalue() is None:q.callproc("RRL_STOCK_POSTING_API.execute_prepared",[out])
   result=out.getvalue();conn.commit();return json.loads(result.read() if hasattr(result,"read") else result)
  except BaseException:conn.rollback();raise
  finally:q.callproc("RRL_STOCK_POSTING_API.reset_connection")
 q.execute("select user,sys_context('USERENV','SERVICE_NAME') from dual");assert q.fetchone()==("RABAEV","orcl")
 q.execute("select ARTICUL from RRL_PALLETS where UID_PALLET='DS-BASE-B1'");article=q.fetchone()[0]
 q.execute("select min(CUSTOMER_ID) from RRL_CUSTOMER");customer=q.fetchone()[0]
 ware=100000+int(tag[:6],16);shipcell="QH"+tag;top="HU.FULL:"+tag;box="HU.FULL.BOX:"+tag
 meta("insert into RRL_WARES(ID,NAME,PREFIX) values(:ware,:n,:p)",n="Own FULLPAL HU "+tag,p="Q"+tag[:2])
 meta("insert into RRL_RECEIPT_WARE_SETTINGS(WARE_ID,OUTGOING_QC_MODE,OUTGOING_QC_INDEPENDENT) values(:ware,'NONE',0)")
 for cell in (src,dst,shipcell):
  meta("insert into RRL_CELLS(CELL,WARE_ID,X,Y,Z,OTBOR,IS_SYSTEM,LIMIT_WEIGHT,LIMIT_HEIGHT) values(:c,:ware,0,0,0,0,0,0,0)",c=cell)
  meta("insert into RRL_STOCK_POLICY_GUARD(POLICY_KEY,LOCK_ID) select RRL_STOCK_LOCK_API.resource_key('CELL',:c),nvl(max(LOCK_ID),900000000)+1 from RRL_STOCK_POLICY_GUARD",c=cell)
 revision=int(q.callfunc("REVIZION.create_revizion",oracledb.DB_TYPE_NUMBER,[ware,"admin"]));conn.commit()
 order,row,plan,pl,pt,wave,wt,task,st,ff=[seq(n) for n in ("RRL_CUSTOMER_ORDER_SQ","RRL_CUSTOMER_ORDER_ROW_SQ","RRL_PICK_PLAN_SQ","RRL_PICK_PLAN_LINE_SQ","RRL_PICK_TASK_SQ","RRL_PICK_WAVE_SQ","RRL_PICK_WAVE_TASK_SQ","RRL_WAREHOUSE_TASK_SQ","RRL_SBORKA_PALLETS_SQ","RRL_CUSTOMER_ORDER_FULF_SQ")]
 meta("insert into RRL_CUSTOMER_ORDER(CUSTOMER_ORDER_ID,ORDER_NO,CUSTOMER_ID,WARE_ID) values(:id,:no,:c,:ware)",id=order,no=lot,c=customer)
 meta("insert into RRL_CUSTOMER_ORDER_ROW(CUSTOMER_ORDER_ROW_ID,CUSTOMER_ORDER_ID,LINE_NO,ARTICUL,ORDER_QTY,UNIT_CODE) values(:id,:o,1,:a,3,'EA')",id=row,o=order,a=article)
 meta("insert into RRL_PICK_PLAN(PICK_PLAN_ID,CUSTOMER_ORDER_ID,CUSTOMER_ID,WARE_ID,STATUS) values(:id,:o,:c,:ware,'RELEASED')",id=plan,o=order,c=customer)
 meta("insert into RRL_PICK_PLAN_LINE(PICK_PLAN_LINE_ID,PICK_PLAN_ID,CUSTOMER_ORDER_ROW_ID,ARTICUL,REQUESTED_QTY,PLANNED_QTY,STATUS) values(:id,:p,:r,:a,3,3,'PLANNED_FULL')",id=pl,p=plan,r=row,a=article)
 meta("insert into RRL_PICK_TASK(PICK_TASK_ID,PICK_PLAN_ID,PICK_PLAN_LINE_ID,CUSTOMER_ORDER_ID,CUSTOMER_ID,TASK_TYPE,STATUS,ARTICUL,PALLET_UID,SOURCE_CELL_CODE,TARGET_CELL_CODE,QTY) values(:id,:p,:pl,:o,:c,'FULL_PALLET','NEW',:a,:u,:src,:dst,3)",id=pt,p=plan,pl=pl,o=order,c=customer,a=article,u=lot,src=src,dst=dst)
 meta("insert into RRL_PICK_WAVE(PICK_WAVE_ID,WAVE_CODE,WARE_ID,STATUS,CREATED_BY) values(:id,:code,:ware,'LAUNCHED','admin')",id=wave,code=lot)
 meta("insert into RRL_PICK_WAVE_TASK(PICK_WAVE_TASK_ID,PICK_WAVE_ID,PICK_TASK_ID,TASK_TYPE,STATUS,ARTICUL,PALLET_UID,QTY,SOURCE_CELL_CODE,TARGET_CELL_CODE) values(:id,:w,:p,'FULL_PALLET','NEW',:a,:u,3,:src,:dst)",id=wt,w=wave,p=pt,a=article,u=lot,src=src,dst=dst)
 meta("insert into RRL_WAREHOUSE_TASK(TASK_ID,TASK_TYPE,TASK_SOURCE,SOURCE_TASK_ID,SOURCE_DOC_TYPE,SOURCE_DOC_ID,UID_PALLET,FROM_CELL,TO_CELL,FROM_WARE_ID,TO_WARE_ID,QTY,UNIT_CODE,QTY_MODE,STATUS,ASSIGNED_TO,CREATED_BY) values(:id,'PICKING_MOVE','WAVE',:wt,'PICK_WAVE',:w,:u,:src,:dst,:ware,:ware,3,'EA','PALLET','ASSIGNED','admin','admin')",id=task,wt=wt,w=wave,u=lot,src=src,dst=dst)
 meta("insert into RRL_SBORKA_PALLETS(ID,PALLET_UID,ST_NUMBER,WARE_ID,CONDITION,ADDR) values(:id,:u,:u,:ware,0,'Own full-pallet ST')",id=st,u=st_uid)
 meta("insert into RRL_SBORKA_PALLET_ROWS(ID,PALLET_UID,ARTICUL,EI,QUANTITY) values(RRL_SBORKA_PALLET_ROWS_SQ.nextval,:u,:a,'BOX',0.125)",u=st_uid,a=article)
 meta("insert into RRL_CUSTOMER_ORDER_FULFILLMENT(FULFILLMENT_ID,CUSTOMER_ORDER_ID,LEGACY_SBORKA_PALLET_ID,PALLET_UID,STATUS,FACT_QTY) values(:id,:o,:st,:u,'PLANNED',0)",id=ff,o=order,st=st,u=st_uid)
 q.execute("select min(TRANSPORTTYPE) from RRL_TRANSPORT_TYPE");trtype=q.fetchone()[0]
 driver=seq("RRL_TR_VODITEL_SQ");meta("insert into RRL_TR_VODITEL(ID,F,I,O,DELETED)values(:id,'Own219','Driver',:tag,0)",id=driver,tag=tag)
 vehicle=int(q.callfunc("RRL_TR_VEHICLE_ADD",oracledb.DB_TYPE_NUMBER,["QL"+tag,trtype,100,1,0,None]));conn.commit()
 trip=seq("RRL_TRANSPORT_TASK_SQ");dock="QD"+tag;pending_st=seq("RRL_SBORKA_PALLETS_SQ")
 meta("insert into RRL_TT_DOCK(DOCK,WARE_ID,DOCK_IS_BLOCKED) values(:dock,:ware,0)",dock=dock)
 meta("insert into RRL_TRANSPORT_TASK(ID,TRANSPORT,TRANSTYPE,CONDITION,SHIPMENT_DATE,VODITEL_ID,DOCK,DELETED) values(:id,:plate,:typ,'Спланирован',trunc(sysdate),:driver,:dock,0)",id=trip,plate="QL"+tag,typ=trtype,driver=driver,dock=dock)
 meta("update RRL_TR_VEHICLE set WORKING_NOW=1,BLOCKED=0,DELETED=0 where ID=:id",id=vehicle)
 meta("update RRL_SBORKA_PALLETS set TRANSTASK_ID=:tt where ID=:id",tt=trip,id=st)
 meta("insert into RRL_SBORKA_PALLETS(ID,PALLET_UID,ST_NUMBER,WARE_ID,CONDITION,TRANSTASK_ID) values(:id,:u,:u,:ware,0,:tt)",id=pending_st,u="TT.PENDING:"+tag,tt=trip)
 try:
  for u,cell in ((lot,src),(other,dst)):
   post("INVENTORY_REGISTER_LOT",{"uid":u,"cell":cell,"article":article,"quantity":"3","expiry_date":"2030-01-01","price":0,"reason":"Full-pallet binding fixture"},{"revision_id":revision})
   post("RESERVATION_CREATE",{"uid_pallet":u,"cell":cell,"articul":article,"qty":"3","unit_code":"EA","ware_id":ware,"reservation_kind":"HARD","reservation_scope":"PALLET","reservation_domain":"PICKING","source_doc_type":"PICK_WAVE","source_doc_id":wave,"source_line_id":pt,"customer_order_id":order,"customer_id":customer,"pick_plan_id":plan,"pick_plan_line_id":pl},{"type":"PICK_WAVE","id":wave})
  post("TARE_COUNT",{"owner_ware_id":ware,"pallet_type_id":1,"condition":"GOOD","observed_quantity":"1","expected_version":0,"reason":"Own standalone tare","decision_reference":"TARE:"+tag},{})
  bookop="TARE.FULL.BOOK:"+tag
  booked=post("TARE_BOOK",{"pallet_type_id":1,"expected_warehouse_id":ware},{"place_kind":"HU","place_id":lot},bookop)
  assert booked["available_quantity"]=="0"
  assert post("TARE_BOOK",{"pallet_type_id":1,"expected_warehouse_id":ware},{"place_kind":"HU","place_id":lot},bookop)==booked
  try:post("TARE_BOOK_CANCEL",{},{"booking_operation_id":bookop})
  except oracledb.DatabaseError as exc:assert "EMPTY_PLACE_REQUIRED" in str(exc),str(exc)
  else:raise AssertionError("Goods pallet was cancelled as empty")
  post("WAVE_PICK_RELEASE",{},{"wave_id":wave})
  before=OrderExecution(OracleGateway()).get(order);assert before["lines"][0]["picked_quantity"]=="0"
  try:post("PICK_PALLET_BIND_SHIPMENT",{"shipment_identifier":st_uid,"scanned_pallet":lot,"expected_stock_version":0},{"task_id":task});raise AssertionError("Unperformed task bound")
  except oracledb.DatabaseError as exc:assert "FULLPAL_CONFIRMED_MOVE_REQUIRED" in str(exc),str(exc)
  completed=post("TASK_COMPLETE",{"fact_qty":"3","scanned_pallet":lot,"scanned_from_cell":src,"scanned_to_cell":dst},{"task_id":task})
  preview=FullPalletShipment(OracleGateway()).preview(task)
  assert preview["pallet_identifier"]==lot and preview["quantity"]=="3"
  body={"shipment_identifier":st_uid,"scanned_pallet":lot,"expected_stock_version":int(preview["stock_version"])}
  try:post("SHIP_PALLET",{},{"pallet_identifier":st_uid});raise AssertionError("Unbound physical pallet shipped")
  except oracledb.DatabaseError as exc:assert "FULLPAL_PHYSICAL_SHIPMENT_BIND_REQUIRED" in str(exc),str(exc)
  op="FULL.BIND:"+tag;bound=post("PICK_PALLET_BIND_SHIPMENT",body,{"task_id":task},op)
  assert post("PICK_PALLET_BIND_SHIPMENT",body,{"task_id":task},op)==bound
  q.execute("select STATUS,FACT_QTY,FACT_UOM,PICKED_WAREHOUSE_TASK_ID,PICKED_PALLET_UID from RRL_CUSTOMER_ORDER_FULFILLMENT where FULFILLMENT_ID=:id",id=ff)
  assert q.fetchone()==("PICKED",3,"EA",task,lot)
  assert OrderExecution(OracleGateway()).get(order)["lines"][0]["picked_quantity"]=="3"
  meta("update RRL_SBORKA_PALLET_ROWS set EI='EA',QUANTITY=1 where PALLET_UID=:u",u=st_uid)
  try:post("SHIP_PALLET",{},{"pallet_identifier":st_uid});raise AssertionError("Bound whole pallet partially shipped after ST edit")
  except oracledb.DatabaseError as exc:assert "FULLPAL_BOUND_WHOLE_COMPOSITION_REQUIRED" in str(exc),str(exc)
  q.execute("select REMAIN,HARD_RESERVED_BASE from RRL_REMAINS where UID_POLETA=:u and CELL=:c",u=lot,c=dst);assert q.fetchone()==(3,3)
  meta("update RRL_SBORKA_PALLET_ROWS set EI='BOX',QUANTITY=0.125 where PALLET_UID=:u",u=st_uid)
  post("INTERNAL_MOVE",{"uid":lot,"source_cell":dst,"target_cell":shipcell,"quantity":"0","unit":"EA"},{})
  from app.transport_composition import build_transport_loading
  loading=build_transport_loading();preview=loading.preview_single(st_uid)
  assert preview["root"]==lot and preview["snapshot"]["nodes"][0]["kind"]=="STOCK"
  loading_context={"transport_task_id":trip,"scan_vehicle":"QL"+tag,"scan_dock":dock,"measurements":{"origin":"MANUAL_CONFIRMED","content_version":preview["expected_version"],"gross_weight_kg":"10","width_m":"1","depth_m":"1","height_m":"1.5"}}
  ship_body={"expected_version":preview["expected_version"],"expected_composition_signature":preview["composition_signature"],"scan_container":lot,"scan_cell":shipcell,"loading_context":loading_context}
  for bad,reason in (({**ship_body,"scan_container":"OTHER"},"SINGLE_LOAD_PLACE_CELL_SCAN_REQUIRED"),({**ship_body,"loading_context":{**loading_context,"scan_vehicle":"OTHER"}},"LOAD_VEHICLE_DOCK_SCAN_REQUIRED")):
   try:post("LOAD_SHIPMENT",bad,{"pallet_identifier":st_uid})
   except oracledb.DatabaseError as exc:assert reason in str(exc),str(exc)
   else:raise AssertionError("Invalid standalone load accepted")
  shipop="SINGLE.FULL.LOAD:"+tag;shipped=loading.load_single(shipop,st_uid,ship_body,"admin")
  assert loading.load_single(shipop,st_uid,ship_body,"admin")==shipped and shipped["physical_places"]==1
  q.execute("select TT_ID,ROOT_UID,VEHICLE_ID,VEHICLE_NUMBER,DOCK,STATUS from RRL_TT_HU_LOAD_FACT where LOAD_OPERATION_ID=:op",op=shipop);assert q.fetchone()==(trip,lot,vehicle,"QL"+tag,dock,"LOADED")

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
