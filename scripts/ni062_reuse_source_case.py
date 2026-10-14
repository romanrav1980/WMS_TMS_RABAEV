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
   q.callproc("RRL_STOCK_POSTING_API.prepare_command",[inp,"admin",out,None])
   if out.getvalue() is None:q.callproc("RRL_STOCK_POSTING_API.execute_prepared",[out])
   result=out.getvalue();conn.commit();return json.loads(result.read() if hasattr(result,"read") else result)
  except BaseException:conn.rollback();raise
  finally:q.callproc("RRL_STOCK_POSTING_API.reset_connection")
 q.execute("select user,sys_context('USERENV','SERVICE_NAME') from dual");assert q.fetchone()==("RABAEV","orcl")
 import httpx,xml.etree.ElementTree as ET
 client=httpx.Client(auth=("admin","admin123"),timeout=35);base="http://127.0.0.1:8088"
 def fullapi(method,path,body=None,status=200,raw=None):
  response=client.request(method,base+path,**({"content":raw,"headers":{"Content-Type":"application/xml"}}if raw is not None else {"json":body}))
  assert response.status_code==status,(response.status_code,response.text[:1800]);return response.json()
 article="REUSE.QA:"+tag;barcode="REUSE.EA:"+tag;box_barcode="REUSE.BOX:"+tag;batch="REUSE.BATCH:"+tag
 prefix=str(30000000000000000+int(tag[:8],16));digit=(10-sum(int(n)*(3 if i%2==0 else 1)for i,n in enumerate(reversed(prefix)))%10)%10;lot=prefix+str(digit)
 idoc=ET.Element("ARTMAS10");document=ET.SubElement(idoc,"IDOC");control=ET.SubElement(document,"EDI_DC40")
 def fields(node,values):
  for name,value in values.items():ET.SubElement(node,name).text=str(value)
 fields(control,{"MESTYP":"ARTMAS","IDOCTYP":"ARTMAS10","DOCNUM":str(1000000000000000+int(tag[:8],16)),"SNDPRN":"OWN.QA.SAP","CREDAT":"20261010","CRETIM":"090000"})
 for segment,values in [("E1BPE1MATHEAD",{}),("E1BPE1MARART",{"BASE_UOM":"EA","EAN_UPC":barcode}),("E1BPE1MAKTRT",{"LANGU_ISO":"EN","MATL_DESC":"Own full box reuse "+tag}),("E1BPE1MARMRT",{"ALT_UNIT":"EA","NUMERATOR":"1","DENOMINATR":"1","EAN_UPC":barcode}),("E1BPE1MARMRT",{"ALT_UNIT":"BOX","NUMERATOR":"24","DENOMINATR":"1","EAN_UPC":box_barcode})]:
  fields(ET.SubElement(document,segment),{"MATERIAL":article,**values})
 fullapi("POST","/api/integrations/sap/artmas",status=202,raw=ET.tostring(idoc,encoding="utf-8"))
 q.callproc("RRL_STOCK_CONFIG_API.begin_change",["admin","finished_goods_edit"])
 try:q.execute("insert into RRL_SKU_RECEIPT_POLICY(ARTICUL,POLICY_VERSION,MARKING_REQUIRED,UPDATED_BY)values(:article,1,0,'admin')",article=article);conn.commit()
 finally:q.callproc("RRL_STOCK_CONFIG_API.end_change")

 q.execute("select min(CUSTOMER_ID) from RRL_CUSTOMER");customer=q.fetchone()[0]
 ware=100000+int(tag[:6],16);shipcell="QH"+tag;top="HU.FULL:"+tag;box="HU.FULL.BOX:"+tag
 meta("insert into RRL_WARES(ID,NAME,PREFIX) values(:ware,:n,:p)",n="Own FULLPAL HU "+tag,p="Q"+tag[:2])
 meta("insert into RRL_RECEIPT_WARE_SETTINGS(WARE_ID,OUTGOING_QC_MODE,OUTGOING_QC_INDEPENDENT) values(:ware,'NONE',0)")
 for cell in (src,dst,shipcell):
  meta("insert into RRL_CELLS(CELL,WARE_ID,X,Y,Z,OTBOR,IS_SYSTEM,LIMIT_WEIGHT,LIMIT_HEIGHT) values(:c,:ware,0,0,0,0,0,0,0)",c=cell)
  meta("insert into RRL_STOCK_POLICY_GUARD(POLICY_KEY,LOCK_ID) select RRL_STOCK_LOCK_API.resource_key('CELL',:c),nvl(max(LOCK_ID),900000000)+1 from RRL_STOCK_POLICY_GUARD",c=cell)
 receive_cell="QIN"+tag;pick_cell="QIP"+tag
 for cell,pick in [(receive_cell,0),(pick_cell,1)]:
  meta("insert into RRL_CELLS(CELL,WARE_ID,X,Y,Z,OTBOR,IS_SYSTEM,LIMIT_WEIGHT,LIMIT_HEIGHT)values(:cell,:ware,0,0,0,:pick,0,0,0)",cell=cell,pick=pick)
  meta("insert into RRL_STOCK_POLICY_GUARD(POLICY_KEY,LOCK_ID)select RRL_STOCK_LOCK_API.resource_key('CELL',:cell),nvl(max(LOCK_ID),900000000)+1 from RRL_STOCK_POLICY_GUARD",cell=cell)
 meta("update RRL_WARES set DEFAULT_RECEIVE_CELL=:cell where ID=:ware",cell=receive_cell)
 meta("insert into RRL_RECEIPT_SKU_RULE(WARE_ID,ARTICUL,PICK_CELL,MIN_SHELF_DAYS,ALLOW_PICK_BATCH_MIX)values(:ware,:article,:cell,0,0)",article=article,cell=pick_cell)
 supply=ET.Element("WarehouseSupplyOrder",version="1")
 fields(supply,{"Sender":"OWN.QA.SAP","MessageId":"REUSE.SUPPLY:"+tag,"OrderNumber":"REUSE:"+tag,"Revision":"1","WarehouseId":ware,"ReceiveCell":receive_cell,"Supplier":"Own software fixture"})
 line_node=ET.SubElement(ET.SubElement(supply,"Lines"),"Line");fields(line_node,{"LineNumber":"1","Material":article});ET.SubElement(line_node,"Quantity",unit="EA").text="24"
 imported=fullapi("POST","/api/integrations/sap/supply-orders",status=202,raw=ET.tostring(supply,encoding="utf-8"));supply_id=imported["order_id"]
 revision=int(q.callfunc("REVIZION.create_revizion",oracledb.DB_TYPE_NUMBER,[ware,"admin"]));conn.commit()
 order,row,plan,pl,pt,wave,wt,task,st,ff=[seq(n) for n in ("RRL_CUSTOMER_ORDER_SQ","RRL_CUSTOMER_ORDER_ROW_SQ","RRL_PICK_PLAN_SQ","RRL_PICK_PLAN_LINE_SQ","RRL_PICK_TASK_SQ","RRL_PICK_WAVE_SQ","RRL_PICK_WAVE_TASK_SQ","RRL_WAREHOUSE_TASK_SQ","RRL_SBORKA_PALLETS_SQ","RRL_CUSTOMER_ORDER_FULF_SQ")]
 meta("insert into RRL_CUSTOMER_ORDER(CUSTOMER_ORDER_ID,ORDER_NO,CUSTOMER_ID,WARE_ID) values(:id,:no,:c,:ware)",id=order,no=lot,c=customer)
 meta("insert into RRL_CUSTOMER_ORDER_ROW(CUSTOMER_ORDER_ROW_ID,CUSTOMER_ORDER_ID,LINE_NO,ARTICUL,ORDER_QTY,UNIT_CODE) values(:id,:o,1,:a,24,'EA')",id=row,o=order,a=article)
 meta("insert into RRL_PICK_PLAN(PICK_PLAN_ID,CUSTOMER_ORDER_ID,CUSTOMER_ID,WARE_ID,STATUS) values(:id,:o,:c,:ware,'RELEASED')",id=plan,o=order,c=customer)
 meta("insert into RRL_PICK_PLAN_LINE(PICK_PLAN_LINE_ID,PICK_PLAN_ID,CUSTOMER_ORDER_ROW_ID,ARTICUL,REQUESTED_QTY,PLANNED_QTY,STATUS) values(:id,:p,:r,:a,24,24,'PLANNED_FULL')",id=pl,p=plan,r=row,a=article)
 meta("insert into RRL_PICK_TASK(PICK_TASK_ID,PICK_PLAN_ID,PICK_PLAN_LINE_ID,CUSTOMER_ORDER_ID,CUSTOMER_ID,TASK_TYPE,STATUS,ARTICUL,PALLET_UID,SOURCE_CELL_CODE,TARGET_CELL_CODE,QTY) values(:id,:p,:pl,:o,:c,'FULL_PALLET','NEW',:a,:u,:src,:dst,24)",id=pt,p=plan,pl=pl,o=order,c=customer,a=article,u=lot,src=src,dst=dst)
 meta("insert into RRL_PICK_WAVE(PICK_WAVE_ID,WAVE_CODE,WARE_ID,STATUS,CREATED_BY) values(:id,:code,:ware,'LAUNCHED','admin')",id=wave,code=lot)
 meta("insert into RRL_PICK_WAVE_TASK(PICK_WAVE_TASK_ID,PICK_WAVE_ID,PICK_TASK_ID,TASK_TYPE,STATUS,ARTICUL,PALLET_UID,QTY,SOURCE_CELL_CODE,TARGET_CELL_CODE) values(:id,:w,:p,'FULL_PALLET','NEW',:a,:u,24,:src,:dst)",id=wt,w=wave,p=pt,a=article,u=lot,src=src,dst=dst)
 meta("insert into RRL_WAREHOUSE_TASK(TASK_ID,TASK_TYPE,TASK_SOURCE,SOURCE_TASK_ID,SOURCE_DOC_TYPE,SOURCE_DOC_ID,UID_PALLET,FROM_CELL,TO_CELL,FROM_WARE_ID,TO_WARE_ID,QTY,UNIT_CODE,QTY_MODE,STATUS,ASSIGNED_TO,CREATED_BY) values(:id,'PICKING_MOVE','WAVE',:wt,'PICK_WAVE',:w,:u,:src,:dst,:ware,:ware,24,'EA','PALLET','ASSIGNED','admin','admin')",id=task,wt=wt,w=wave,u=lot,src=src,dst=dst)
 meta("insert into RRL_SBORKA_PALLETS(ID,PALLET_UID,ST_NUMBER,WARE_ID,CONDITION,ADDR) values(:id,:u,:u,:ware,0,'Own full-pallet ST')",id=st,u=st_uid)
 meta("insert into RRL_SBORKA_PALLET_ROWS(ID,PALLET_UID,ARTICUL,EI,QUANTITY) values(RRL_SBORKA_PALLET_ROWS_SQ.nextval,:u,:a,'BOX',1)",u=st_uid,a=article)
 meta("insert into RRL_CUSTOMER_ORDER_FULFILLMENT(FULFILLMENT_ID,CUSTOMER_ORDER_ID,LEGACY_SBORKA_PALLET_ID,PALLET_UID,STATUS,FACT_QTY) values(:id,:o,:st,:u,'PLANNED',0)",id=ff,o=order,st=st,u=st_uid)
 q.execute("select min(TRANSPORTTYPE) from RRL_TRANSPORT_TYPE");trtype=q.fetchone()[0]
 q.execute("select min(ID) from RRL_TR_VODITEL where ID>0");driver=q.fetchone()[0];assert driver
 vehicle=int(q.callfunc("RRL_TR_VEHICLE_ADD",oracledb.DB_TYPE_NUMBER,["QL"+tag,trtype,100,1,0,None]));conn.commit()
 trip=seq("RRL_TRANSPORT_TASK_SQ");dock="QD"+tag;pending_st=seq("RRL_SBORKA_PALLETS_SQ")
 meta("insert into RRL_TT_DOCK(DOCK,WARE_ID,DOCK_IS_BLOCKED) values(:dock,:ware,0)",dock=dock)
 meta("insert into RRL_TRANSPORT_TASK(ID,TRANSPORT,TRANSTYPE,CONDITION,SHIPMENT_DATE,VODITEL_ID,DOCK,DELETED) values(:id,:plate,:typ,'Спланирован',trunc(sysdate),:driver,:dock,0)",id=trip,plate="QL"+tag,typ=trtype,driver=driver,dock=dock)
 meta("update RRL_TR_VEHICLE set WORKING_NOW=1,BLOCKED=0,DELETED=0 where ID=:id",id=vehicle)
 meta("update RRL_SBORKA_PALLETS set TRANSTASK_ID=:tt where ID=:id",tt=trip,id=st)
 meta("insert into RRL_SBORKA_PALLETS(ID,PALLET_UID,ST_NUMBER,WARE_ID,CONDITION,TRANSTASK_ID) values(:id,:u,:u,:ware,0,:tt)",id=pending_st,u="TT.PENDING:"+tag,tt=trip)
 store_addr="STORE.QA:"+tag;foreign_addr="STORE.OTHER:"+tag
 q.execute("select min(ADDR) from RRL_ADDR");template_addr=q.fetchone()[0];assert template_addr
 for address in (store_addr,foreign_addr):
  meta("insert into RRL_ADDR(ADDR) values(:addr)",addr=address)
 meta("update RRL_SBORKA_PALLETS set ADDR=:addr where ID=:id",addr=store_addr,id=st)
 import httpx
 client=httpx.Client(auth=("admin","admin123"),timeout=35)
 def http(method,path,body=None,expected=200):
  response=client.request(method,"http://127.0.0.1:8088/api/delivery/store-receipts"+path,json=body)
  assert response.status_code==expected,(response.status_code,response.text[:1200])
  return response.json()
 for address in (store_addr,foreign_addr):
  http("PUT","/policy",{"store_address":address,"mode":"BARCODE","expected_version":0})
 try:
  for u,cell in ((lot,src),(other,dst)):
   if u==lot:
    payload={"operation_id":"REUSE.SAP.RECEIVE:"+tag,"line_number":"1","sscc":lot,"quantity":"24","product_barcode":box_barcode,"supplier_batch":batch,"expiry_date":"2030-01-01","gross_weight":"10","units":[],"aggregations":[]}
    incoming=fullapi("POST",f"/api/receiving/supply-orders/{supply_id}/pallets",payload,201)
    assert incoming["putaway_cell"]==src,incoming
    fullapi("POST",f"/api/receiving/putaway/{incoming['task_id']}/complete",{"scanned_pallet":lot,"scanned_from_cell":receive_cell,"scanned_to_cell":src})
   else:post("INVENTORY_REGISTER_LOT",{"uid":u,"cell":cell,"article":article,"quantity":"24","expiry_date":"2030-01-01","price":0,"reason":"Full-pallet binding fixture"},{"revision_id":revision})
   post("RESERVATION_CREATE",{"uid_pallet":u,"cell":cell,"articul":article,"qty":"24","unit_code":"EA","ware_id":ware,"reservation_kind":"HARD","reservation_scope":"PALLET","reservation_domain":"PICKING","source_doc_type":"PICK_WAVE","source_doc_id":wave,"source_line_id":pt,"customer_order_id":order,"customer_id":customer,"pick_plan_id":plan,"pick_plan_line_id":pl},{"type":"PICK_WAVE","id":wave})
  post("WAVE_PICK_RELEASE",{},{"wave_id":wave})
  before=OrderExecution(OracleGateway()).get(order);assert before["lines"][0]["picked_quantity"]=="0"
  try:post("PICK_PALLET_BIND_SHIPMENT",{"shipment_identifier":st_uid,"scanned_pallet":lot,"expected_stock_version":0},{"task_id":task});raise AssertionError("Unperformed task bound")
  except oracledb.DatabaseError as exc:assert "FULLPAL_CONFIRMED_MOVE_REQUIRED" in str(exc),str(exc)
  completed=post("TASK_COMPLETE",{"fact_qty":"24","scanned_pallet":lot,"scanned_from_cell":src,"scanned_to_cell":dst},{"task_id":task})
  preview=FullPalletShipment(OracleGateway()).preview(task)
  assert preview["pallet_identifier"]==lot and preview["quantity"]=="24"
  body={"shipment_identifier":st_uid,"scanned_pallet":lot,"expected_stock_version":int(preview["stock_version"])}
  try:post("SHIP_PALLET",{},{"pallet_identifier":st_uid});raise AssertionError("Unbound physical pallet shipped")
  except oracledb.DatabaseError as exc:assert "FULLPAL_PHYSICAL_SHIPMENT_BIND_REQUIRED" in str(exc),str(exc)
  op="FULL.BIND:"+tag;bound=post("PICK_PALLET_BIND_SHIPMENT",body,{"task_id":task},op)
  assert post("PICK_PALLET_BIND_SHIPMENT",body,{"task_id":task},op)==bound
  q.execute("select STATUS,FACT_QTY,FACT_UOM,PICKED_WAREHOUSE_TASK_ID,PICKED_PALLET_UID from RRL_CUSTOMER_ORDER_FULFILLMENT where FULFILLMENT_ID=:id",id=ff)
  assert q.fetchone()==("PICKED",24,"EA",task,lot)
  assert OrderExecution(OracleGateway()).get(order)["lines"][0]["picked_quantity"]=="24"
  meta("update RRL_SBORKA_PALLET_ROWS set EI='EA',QUANTITY=1 where PALLET_UID=:u",u=st_uid)
  try:post("SHIP_PALLET",{},{"pallet_identifier":st_uid});raise AssertionError("Bound whole pallet partially shipped after ST edit")
  except oracledb.DatabaseError as exc:assert "FULLPAL_BOUND_WHOLE_COMPOSITION_REQUIRED" in str(exc),str(exc)
  q.execute("select REMAIN,HARD_RESERVED_BASE from RRL_REMAINS where UID_POLETA=:u and CELL=:c",u=lot,c=dst);assert q.fetchone()==(24,24)
  meta("update RRL_SBORKA_PALLET_ROWS set EI='BOX',QUANTITY=1 where PALLET_UID=:u",u=st_uid)
  def tree(uid):
   q.execute("select RRL_STOCK_HU_READ.snapshot_json(:u) from dual",u=uid);raw=q.fetchone()[0];return json.loads(raw.read() if hasattr(raw,"read") else raw)
  def link(parent,child):
   post("HU_ATTACH",{"child_uid":child,"expected_version":tree(parent)["nodes"][0]["version"],"expected_child_version":tree(child)["nodes"][0]["version"],"scan_container":parent,"scan_child":child},{"uid":parent})
  for uid,kind in ((top,"PALLET"),(box,"BOX")):
   post("HU_CREATE",{"cell":dst,"warehouse":ware,"container_type":kind,"tare_weight_kg":1,"scan_container":uid,"scan_cell":dst},{"uid":uid})
  link(box,lot);link(top,box)
  moved=post("HU_MOVE",{"expected_version":tree(top)["nodes"][0]["version"],"target_cell":shipcell,"scan_container":top,"scanned_from_cell":dst,"scanned_to_cell":shipcell},{"uid":top})
  q.execute("select STOCK_VERSION from RRL_REMAINS where UID_POLETA=:u and CELL=:c",u=lot,c=shipcell);current_version=int(q.fetchone()[0])
  q.execute("select REMAIN,HARD_RESERVED_BASE from RRL_REMAINS where UID_POLETA=:u and CELL=:c",u=lot,c=dst);assert q.fetchone()==(0,0)
  try:post("SHIP_PALLET",{},{"pallet_identifier":st_uid})
  except oracledb.DatabaseError as exc:assert "SHIPMENT_WHOLE_HU_REQUIRED" in str(exc),str(exc)
  else:raise AssertionError("Nested FULLPAL shipped separately")
  from app.transport_composition import build_transport_loading
  loading=build_transport_loading()
  loading_context={"transport_task_id":trip,"scan_vehicle":"QL"+tag,"scan_dock":dock,"measurements":{"origin":"MANUAL_CONFIRMED","content_version":tree(top)["nodes"][0]["version"],"gross_weight_kg":"10","width_m":"1","depth_m":"1","height_m":"1.5"}}
  ship_body={"expected_version":tree(top)["nodes"][0]["version"],"scan_container":top,"scan_cell":shipcell}
  try:post("HU_SHIP",{**ship_body,"scan_cell":dst},{"uid":top})
  except oracledb.DatabaseError as exc:assert "HU_SHIP_CONTAINER_CELL_SCAN_REQUIRED" in str(exc),str(exc)
  else:raise AssertionError("Wrong physical loading cell accepted")
  ship_body["loading_context"]=loading_context
  for bad,reason in (({**loading_context,"scan_vehicle":"OTHER"},"LOAD_VEHICLE_DOCK_SCAN_REQUIRED"),({**loading_context,"measurements":{**loading_context["measurements"],"gross_weight_kg":"101"}},"LOAD_VEHICLE_PHYSICAL_CAPACITY_EXCEEDED")):
   try:post("HU_SHIP",{**ship_body,"loading_context":bad},{"uid":top})
   except oracledb.DatabaseError as exc:assert reason in str(exc),str(exc)
   else:raise AssertionError("Invalid physical loading accepted")
   q.execute("select REMAIN,HARD_RESERVED_BASE from RRL_REMAINS where UID_POLETA=:u and CELL=:c",u=lot,c=shipcell);assert q.fetchone()==(24,24)
  shipop="FULL.HU.SHIP:"+tag;shipped=post("HU_SHIP",ship_body,{"uid":top},shipop)
  assert post("HU_SHIP",ship_body,{"uid":top},shipop)==shipped and len(shipped["shipments"])==1
  q.execute("select TT_ID,ROOT_UID,VEHICLE_ID,VEHICLE_NUMBER,DOCK,STATUS from RRL_TT_HU_LOAD_FACT where LOAD_OPERATION_ID=:op",op=shipop);assert q.fetchone()==(trip,top,vehicle,"QL"+tag,dock,"LOADED")
  state=loading.status(trip);assert state["loaded_place_count"]==1 and state["pending_st_ids"]==[pending_st]
  try:loading.depart("TT.BAD.DEPART:"+tag,trip,"admin")
  except Exception as exc:assert "DEPART_WAITING_FOR_ACTUAL_LOADED_STS" in str(exc),str(exc)
  else:raise AssertionError("Trip with missing physical place departed")
  try:
   q.execute("update RRL_TRANSPORT_TASK set TRANSPORT='OTHER' where ID=:id",id=trip);conn.commit()
  except oracledb.DatabaseError as exc:conn.rollback();assert "UNLOADING_REQUIRED" in str(exc) or "EXPLICIT_TRIP_MEMBERSHIP_WRITER_REQUIRED" in str(exc),str(exc)
  else:raise AssertionError("Loaded vehicle changed silently")
  try:
   q.execute("update RRL_SBORKA_PALLETS set TRANSTASK_ID=0 where ID=:id",id=st);conn.commit()
  except oracledb.DatabaseError as exc:conn.rollback();assert "UNLOADING_REQUIRED" in str(exc) or "EXPLICIT_TRIP_MEMBERSHIP_WRITER_REQUIRED" in str(exc),str(exc)
  else:raise AssertionError("Loaded ST changed trip silently")
  meta("update RRL_SBORKA_PALLETS set TRANSTASK_ID=0 where ID=:id",id=pending_st)
  op="TT.DEPART:"+tag;departed=loading.depart(op,trip,"admin");assert loading.depart(op,trip,"admin")==departed
  assert departed["physical_places"]==1 and not departed["stock_consumed_again"]
  q.execute("select count(*) from RRL_EVENTS where OPERATION_ID=:op",op=op);assert q.fetchone()==(0,)
  q.execute("select STATUS,DEPARTURE_OPERATION_ID from RRL_TT_HU_LOAD_FACT where LOAD_OPERATION_ID=:op",op=shipop);assert q.fetchone()==("DEPARTED",op)
  q.execute("select CONDITION from RRL_TRANSPORT_TASK where ID=:id",id=trip);assert q.fetchone()==("Отгружен",)
  print("PASS actual FULLPAL upper HU load -> one physical place/same existing TT/vehicle/dock+P/H0/replay; wrong scan/weight denied; pending ST blocks departure; loaded reassignment denied; separate departure/replay no quantity journal",flush=True)
  # Frozen loading address is the destination authority, not a later ST edit.
  q.execute("select DESTINATION_ADDR from RRL_TT_HU_LOAD_ST where LOAD_OPERATION_ID=:op and SBORKA_PALLET_ID=:st",op=shipop,st=st)
  assert q.fetchone()==(store_addr,)
  try:
   q.execute("update RRL_SBORKA_PALLETS set ADDR=:addr where ID=:id",addr=foreign_addr,id=st);conn.commit()
  except oracledb.DatabaseError as exc:conn.rollback();assert "LOADED_ST_CONFIRMED_UNLOADING_REQUIRED" in str(exc),str(exc)
  else:raise AssertionError("Departed destination changed")
  places=http("GET",f"/trips/{trip}/places?store_address={store_addr}")
  assert len(places)==1 and places[0]["load_operation_id"]==shipop
  preview=http("GET",f"/preview?load_operation_id={shipop}&store_address={store_addr}")
  assert preview["mode"]=="BARCODE" and not preview["requires_marked_recipient_flow"]
  receipt={"operation_id":"STORE.RECEIPT:"+tag,"load_operation_id":shipop,"store_address":store_addr,
   "scan_place":top,"expected_composition_signature":preview["composition_signature"],"before_cameras":True}
  accepted=http("POST","/confirm",receipt)
  assert accepted["status"]=="ACCEPTED" and accepted["accepted_lines"][0]["accepted_quantity"]=="24"
  assert not accepted["warehouse_stock_consumed_again"] and not accepted["government_ack_created"]
  assert http("POST","/confirm",receipt)==accepted
  print("PASS107 fresh assumed ARTMAS/warehouse SAP receipt BOX24/original verified batch -> existing whole picking/ST/nested load/departure/store acceptance24; tag="+tag,flush=True)
 finally:
  q.execute("select PARENT_UID,CHILD_PALLET_UID from RRL_WMS_HU_LINK where PARENT_UID in(:a,:b) and ACTIVE_FLAG=1 order by HU_LINK_ID",a=top,b=box)
  for parent,child in q.fetchall():
   post("HU_DETACH",{"child_uid":child,"expected_version":tree(parent)["nodes"][0]["version"],"expected_child_version":tree(child)["nodes"][0]["version"],"scan_container":parent,"scan_child":child,"reason":"End own FULLPAL HU"},{"uid":parent})
  q.execute("select RESERVATION_ID from RRL_STOCK_RESERVATION where SOURCE_DOC_TYPE='PICK_WAVE' and SOURCE_DOC_ID=:w and STATUS in('ACTIVE','ALLOCATED','PICKING') and BASE_QTY>0",w=wave)
  for (rid,) in q.fetchall():post("RESERVATION_RELEASE",{"reason":"End private full-pallet fixture"},{"reservation_id":int(rid)})
  q.execute("select UID_POLETA,CELL,BASE_UOM,STOCK_VERSION from RRL_REMAINS where UID_POLETA in(:a,:b) and REMAIN>0",a=lot,b=other)
  counts=[{"uid":u,"cell":cell,"article":article,"unit":unit,"quantity":"0","expected_stock_version":int(version),"unit_keys":[]} for u,cell,unit,version in q.fetchall()]
  if counts:post("INVENTORY_COUNT",{"reason":"End private full-pallet fixture","counts":counts},{"revision_id":revision})
  meta("update RRL_WAREHOUSE_TASK set STATUS='CANCELLED' where TASK_ID=:id and STATUS!='DONE'",id=task)
  meta("update RRL_PICK_WAVE set STATUS='DONE' where PICK_WAVE_ID=:w",w=wave)
  print("Own P/H restored; immutable operation and fulfillment history retained",flush=True)
