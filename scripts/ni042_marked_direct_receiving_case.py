"""180 original file-gateway XML contract to native weighted pallet receipt."""
import sys,json,xml.etree.ElementTree as ET
from pathlib import Path
from uuid import uuid4
from decimal import Decimal
import httpx,oracledb
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment();sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"api/wms_api_server"))
from app.config import get_settings
s=get_settings();tag=sys.argv[1]if len(sys.argv)>1 else uuid4().hex[:8];article="QPB201"+tag.upper();ware=30000000+int(tag[:6],16);receive="Q201R"+tag;pick="Q201P"+tag;storage="Q201S"+tag
prefix=str(50000000000000000+int(tag,16));sscc=prefix+str((10-sum(int(n)*(3 if i%2==0 else 1)for i,n in enumerate(reversed(prefix)))%10)%10)
digits="0401234567890";gtin=digits+str((10-sum(int(n)*(3 if i%2==0 else 1)for i,n in enumerate(digits))%10)%10)
scan="(01)"+gtin+"(3103)009800(21)"+tag
api=httpx.Client(auth=("admin","admin123"),timeout=35);base="http://127.0.0.1:8088";born=False;task=None;revision=None
def call(method,path,body=None,status=200,raw=None):
 r=api.request(method,base+path,**({"content":raw,"headers":{"Content-Type":"application/xml"}}if raw is not None else {"json":body}))
 assert r.status_code==status,(r.status_code,r.text[:2000]);return r.json()
def fields(node,values):
 for key,value in values.items():ET.SubElement(node,key).text=str(value)
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();c.call_timeout=15000
 def meta(sql,**binds):
  q.callproc("RRL_STOCK_CONFIG_API.begin_change",["admin","warehouse_settings_edit"])
  try:q.execute(sql,binds);c.commit()
  except BaseException:c.rollback();raise
  finally:q.callproc("RRL_STOCK_CONFIG_API.end_change")
 idoc=ET.Element("ARTMAS10");doc=ET.SubElement(idoc,"IDOC");control=ET.SubElement(doc,"EDI_DC40")
 fields(control,{"MESTYP":"ARTMAS","IDOCTYP":"ARTMAS10","DOCNUM":str(2000000000000000+int(tag,16)),"SNDPRN":"OWN.QA.SAP","CREDAT":"20261011","CRETIM":"020000"})
 for segment,values in [("E1BPE1MATHEAD",{}),("E1BPE1MARART",{"BASE_UOM":"EA","EAN_UPC":gtin}),("E1BPE1MAKTRT",{"LANGU_ISO":"EN","MATL_DESC":"Own weighted box "+tag}),("E1BPE1MARMRT",{"ALT_UNIT":"EA","NUMERATOR":"1","DENOMINATR":"1","EAN_UPC":gtin})]:
  fields(ET.SubElement(doc,segment),{"MATERIAL":article,**values})
 call("POST","/api/integrations/sap/artmas",status=202,raw=ET.tostring(idoc,encoding="utf-8"))
 meta("update RRL_ARTICULS set TYPE_W=0 where ACTICUL=:p_a",p_a=article)
 call("PUT",f"/api/finished-goods/skus/{article}/receiving-policy",{"expected_version":0,"marking_required":True,"serialized_weight_boxes":False,"profiles":[{"system_code":"CRPT","profile_code":"TOBACCO","profile_version":"DIR1","scan_mode":"UNIT"},{"system_code":"EGAIS","profile_code":"ALCOHOL","profile_version":"DIR1","scan_mode":"UNIT"}]})
 meta("insert into RRL_WARES(ID,NAME,PREFIX,DEFAULT_RECEIVE_CELL)values(:p_ware,:p_name,'QW',:p_receive)",p_ware=ware,p_name="Own180 "+tag,p_receive=receive)
 meta("insert into RRL_RECEIPT_WARE_SETTINGS(WARE_ID,OUTGOING_QC_MODE,OUTGOING_QC_INDEPENDENT)values(:p_ware,'NONE',0)",p_ware=ware)
 for cell,is_pick in [(receive,0),(pick,1),(storage,0),("CPT_"+str(ware),0)]:
  meta("insert into RRL_CELLS(CELL,WARE_ID,X,Y,Z,OTBOR,IS_SYSTEM,LIMIT_WEIGHT,LIMIT_HEIGHT)values(:p_cell,:p_ware,0,0,0,:p_pick,:p_system,0,0)",p_cell=cell,p_ware=ware,p_pick=is_pick,p_system=int(cell.startswith("CPT_")))
  meta("insert into RRL_STOCK_POLICY_GUARD(POLICY_KEY,LOCK_ID)select RRL_STOCK_LOCK_API.resource_key('CELL',:p_cell),nvl(max(LOCK_ID),900000000)+1 from RRL_STOCK_POLICY_GUARD",p_cell=cell)
 meta("insert into RRL_RECEIPT_SKU_RULE(WARE_ID,ARTICUL,PICK_CELL,MIN_SHELF_DAYS,ALLOW_PICK_BATCH_MIX,SOURCE_PICK_MODE)values(:p_ware,:p_a,:p_pick,0,0,'DIRECT')",p_ware=ware,p_a=article,p_pick=pick)
 supply=ET.Element("WarehouseSupplyOrder",version="1")
 fields(supply,{"Sender":"OWN.QA.SAP","MessageId":"DIRECT201.SUPPLY:"+tag,"OrderNumber":"D201:"+tag,"Revision":1,"WarehouseId":ware,"ReceiveCell":receive,"Supplier":"Own180 software fixture"})
 line=ET.SubElement(ET.SubElement(supply,"Lines"),"Line");fields(line,{"LineNumber":"1","Material":article});ET.SubElement(line,"Quantity",unit="EA").text="12"
 imported=call("POST","/api/integrations/sap/supply-orders",status=202,raw=ET.tostring(supply,encoding="utf-8"))
 revision=int(q.callfunc("REVIZION.create_revizion",oracledb.DB_TYPE_NUMBER,[ware,"admin"]));c.commit()
 body={"operation_id":"DIRECT201.RECEIVE:"+tag,"line_number":"1","sscc":sscc,"quantity":"12","product_barcode":gtin,"supplier_batch":"PB:"+tag,"expiry_date":"2030-01-01","gross_weight":"12"}
 units=[{"unit_id":str(i),"quantity":"1","codes":[
   {"system_code":"CRPT","profile_code":"TOBACCO","code":gtin+tag[:5]+str(i).zfill(2)},
   {"system_code":"EGAIS","profile_code":"ALCOHOL","code":("QA"+tag+str(i)).ljust(68,"X")}]}for i in range(1,13)]
 body["units"]=units;body.pop("product_barcode",None)
 from app.services.picking_service import PickingService
 from app.schemas import PickingPlanCreateRequest,PickWaveCreateRequest,PickWaveAddPlanRequest,PickWaveActionRequest
 from app.modules.inventory.contracts_stock import StockCommand
 from app.modules.inventory.infrastructure.stock_posting_uow import StockPosting
 from app.modules.platform.public import read_oracle_json
 from app.oracle_gateway import OracleGateway
 picking=PickingService();orders=[];plans=[];wave=None;bookings=[];case_types=set()
 def post(kind,source,metadata,op=None):
  return StockPosting().post(StockCommand(operation_id=op or "DIRECT201:"+uuid4().hex,command_type=kind,actor="admin",source=source,metadata=metadata,lines=()))
 def seq(name):q.execute("select "+name+".nextval from dual");return int(q.fetchone()[0])
 q.execute("select min(CUSTOMER_ID),max(CUSTOMER_ID)from RRL_CUSTOMER");customers=q.fetchone()
 for customer,quantity in zip(customers,(5,7)):
  order=seq("RRL_CUSTOMER_ORDER_SQ");orders.append(order)
  meta("insert into RRL_CUSTOMER_ORDER(CUSTOMER_ORDER_ID,ORDER_NO,CUSTOMER_ID,WARE_ID)values(:p_id,:p_no,:p_customer,:p_ware)",p_id=order,p_no="DIRECT201:"+tag+":"+str(quantity),p_customer=customer,p_ware=ware)
  meta("insert into RRL_CUSTOMER_ORDER_ROW(CUSTOMER_ORDER_ROW_ID,CUSTOMER_ORDER_ID,LINE_NO,ARTICUL,ORDER_QTY,UNIT_CODE)values(RRL_CUSTOMER_ORDER_ROW_SQ.nextval,:p_order,1,:p_article,:p_qty,'EA')",p_order=order,p_article=article,p_qty=quantity)
  empty=picking.create_plan(PickingPlanCreateRequest(customer_order_id=order,created_by="admin"))
  q.execute("select p.STATUS,(select nvl(sum(l.PLANNED_QTY),0)from RRL_PICK_PLAN_LINE l where l.PICK_PLAN_ID=p.PICK_PLAN_ID)from RRL_PICK_PLAN p where p.PICK_PLAN_ID=:p_id",p_id=empty);assert q.fetchone()==("NO_STOCK",0)
  picking.cancel_plan(empty,"admin")
 try:
  result=call("POST",f"/api/receiving/supply-orders/{imported['order_id']}/pallets",body,201);born=True
  task=result["task_id"];assert result["marking_units"]==12
  q.execute("select count(*),sum(BASE_QTY)from RRL_WMS_RECEIPT_UNIT where UID_PALLET=:p_uid",p_uid=sscc);assert q.fetchone()==(12,12)
  q.execute("select count(*)from RRL_WMS_RECEIPT_CODE where UID_PALLET=:p_uid",p_uid=sscc);assert q.fetchone()[0]==24

  assert call("POST",f"/api/receiving/supply-orders/{imported['order_id']}/pallets",body,201)==result
  # An in-progress physical putaway must block DIRECT admission.
  meta("update RRL_WAREHOUSE_TASK set STATUS='IN_PROGRESS'where TASK_ID=:p_task",p_task=task)
  from fastapi import HTTPException
  try:
   empty=picking.create_plan(PickingPlanCreateRequest(customer_order_id=orders[0],created_by="admin"))
   q.execute("select p.STATUS,(select nvl(sum(l.PLANNED_QTY),0)from RRL_PICK_PLAN_LINE l where l.PICK_PLAN_ID=p.PICK_PLAN_ID)from RRL_PICK_PLAN p where p.PICK_PLAN_ID=:p_id",p_id=empty);assert q.fetchone()==("NO_STOCK",0)
   picking.cancel_plan(empty,"admin")
  finally:meta("update RRL_WAREHOUSE_TASK set STATUS='PLANNED'where TASK_ID=:p_task",p_task=task)
  for order in orders:
   plan=picking.create_plan(PickingPlanCreateRequest(customer_order_id=order,created_by="admin"));plans.append(plan)
   q.execute("select TASK_TYPE,SOURCE_CELL_CODE,TARGET_CELL_CODE from RRL_PICK_TASK where PICK_PLAN_ID=:p_plan",p_plan=plan);assert q.fetchone()==("CASE_PICK",receive,None)
  wave=picking.create_wave(PickWaveCreateRequest(wave_code="DIRECT201:"+tag,ware_id=ware,created_by="admin"))
  for plan in plans:picking.add_wave_plan(wave,PickWaveAddPlanRequest(pick_plan_id=plan,created_by="admin"))
  picking.preview_wave(wave,PickWaveActionRequest(updated_by="admin"))
  wire=StockCommand(operation_id="DIRECT201.LAUNCH:"+tag,command_type="WAVE_LAUNCH",actor="admin",source={"wave_id":wave},metadata={},lines=()).canonical_json()
  inp,out=q.var(oracledb.DB_TYPE_CLOB),q.var(oracledb.DB_TYPE_CLOB);inp.setvalue(0,wire)
  try:
   q.callproc("RRL_STOCK_POSTING_API.prepare_command",[inp,"admin",out,None]);assert out.getvalue()is None
   q.callproc("RRL_STOCK_POSTING_API.execute_prepared",[out])
   q.execute("select STATUS from RRL_WAREHOUSE_TASK where TASK_ID=:p_task",p_task=task);assert q.fetchone()[0]=="CANCELLED"
   q.execute("select HARD_RESERVED_BASE from RRL_REMAINS where UID_POLETA=:p_uid and CELL=:p_cell",p_uid=sscc,p_cell=receive);assert q.fetchone()[0]==12
  finally:c.rollback();q.callproc("RRL_STOCK_POSTING_API.reset_connection")
  q.execute("select STATUS from RRL_WAREHOUSE_TASK where TASK_ID=:p_task",p_task=task);assert q.fetchone()[0]=="PLANNED"
  q.execute("select HARD_RESERVED_BASE from RRL_REMAINS where UID_POLETA=:p_uid and CELL=:p_cell",p_uid=sscc,p_cell=receive);assert q.fetchone()[0]==0
  print("PASS201 outer rollback restores original placement and source HARD0",flush=True)
  picking.launch_wave(wave,PickWaveActionRequest(updated_by="admin",operation_id="DIRECT201.LAUNCH:"+tag))
  q.execute("select STATUS,LAST_ERROR,QTY from RRL_WAREHOUSE_TASK where TASK_ID=:p_task",p_task=task);state,reason,qty=q.fetchone()
  assert state=="CANCELLED"and reason=="DIRECT_PICK_BY_LINE:DIRECT201.LAUNCH:"+tag and qty==12
  q.execute("select count(*)from RRL_PICK_WAVE_REPLENISH_TASK where PICK_WAVE_ID=:p_wave",p_wave=wave);assert q.fetchone()[0]==0
  q.execute("select count(*)from RRL_RECEIPT_SLOT_CLAIM where TASK_ID=:p_task",p_task=task);assert q.fetchone()[0]==0
  post("WAVE_PICK_RELEASE",{"wave_id":wave},{})
  q.execute("select t.CASE_PICK_TASK_ID,l.CASE_PICK_LINE_ID,t.SSCC,l.CELL_CODE,l.PLANNED_QTY,t.PALLET_TYPE_ID from RRL_CASE_PICK_TASK t join RRL_CASE_PICK_LINE l on l.CASE_PICK_TASK_ID=t.CASE_PICK_TASK_ID where t.PICK_WAVE_ID=:p_wave order by t.CUSTOMER_ORDER_ID",p_wave=wave)
  rows=q.fetchall();assert sorted(r[4]for r in rows)==[5,7]
  tare="/api/inventory/tare"
  for case,line,carrier,cell,quantity,case_type in rows:
   assert cell==receive;case_types.add(case_type)
   available=call("GET",tare+f"/warehouses/{ware}/availability")
   current=next(x for x in available if x["pallet_type_id"]==case_type)
   call("POST",tare+"/count",{"operation_id":"DIRECT201.TARE.COUNT:"+str(case),"owner_ware_id":ware,"pallet_type_id":case_type,"condition":"GOOD","observed_quantity":"2","expected_version":current["balance_version"]or 0,"reason":"Own201 software container fixture","decision_reference":"DIRECT201:"+tag})
   book="DIRECT201.TARE.BOOK:"+str(case);call("POST",tare+"/book",{"operation_id":book,"place_kind":"CASE","place_id":str(case)});bookings.append(book)
   call("POST",f"/api/case-pick/tasks/{case}/claim",{});call("POST",f"/api/case-pick/tasks/{case}/start",{})
   payload={"operation_id":"DIRECT201.PICK:"+str(case),"fact_qty":str(quantity),"scan_cell":receive,"scan_product":gtin,"scan_container":carrier}
   q.execute("select u.UNIT_ID,u.PHYSICAL_UNIT_KEY from RRL_WMS_RECEIPT_UNIT u join RRL_STOCK_RESERVATION r on r.RESERVATION_ID=u.HARD_RESERVATION_ID where r.SOURCE_DOC_TYPE='PICK_WAVE'and r.SOURCE_DOC_ID=:p_wave and r.SOURCE_LINE_ID=(select PICK_TASK_ID from RRL_CASE_PICK_LINE where CASE_PICK_LINE_ID=:p_line)and r.BASE_QTY>0 order by u.PHYSICAL_UNIT_KEY",p_wave=wave,p_line=line)
   selected=q.fetchall();assert len(selected)==int(quantity)
   scans=[code for unit_id,_ in selected for code in units[int(unit_id)-1]["codes"]]
   payload["unit_scans"]=scans
   path=f"/api/case-pick/tasks/{case}/lines/{line}/confirm"
   denied=api.post(base+path,json={**payload,"operation_id":payload["operation_id"]+":EAN","unit_scans":[]});assert denied.status_code==409,(denied.status_code,denied.text)
   from app.services.case_pick_service import CasePickService
   from app.schemas import CasePickLineConfirmRequest
   try:picked=call("POST",path,payload)
   except AssertionError:
    try:CasePickService().confirm_line(int(case),int(line),CasePickLineConfirmRequest(**payload,actor="admin"))
    except HTTPException as exc:print("Native201 reason",str(exc.__cause__.__cause__)[:2200],flush=True)
    raise
   assert call("POST",path,payload)==picked
  q.execute("select REMAIN,HARD_RESERVED_BASE from RRL_REMAINS where UID_POLETA=:p_uid and CELL=:p_cell",p_uid=sscc,p_cell=receive);assert q.fetchone()==(0,0)
  q.execute("select sum(PICKED_QTY)from RRL_CASE_PICK_LINE where PICK_WAVE_ID=:p_wave",p_wave=wave);assert q.fetchone()[0]==12
  q.execute("select count(*)from RRL_WMS_RECEIPT_UNIT u join RRL_CASE_CARRIER_LOT lot on lot.LOT_UID=u.CURRENT_UID join RRL_CASE_PICK_TASK ct on ct.CASE_PICK_TASK_ID=lot.CASE_PICK_TASK_ID where ct.PICK_WAVE_ID=:p_wave",p_wave=wave);assert q.fetchone()[0]==12
  q.execute("select l.CUSTOMER_ORDER_ID,count(*),sum(u.BASE_QTY)from RRL_CASE_CARRIER_LOT lot join RRL_CASE_PICK_LINE l on l.CASE_PICK_LINE_ID=lot.CASE_PICK_LINE_ID join RRL_WMS_RECEIPT_UNIT u on u.CURRENT_UID=lot.LOT_UID where l.PICK_WAVE_ID=:p_wave group by l.CUSTOMER_ORDER_ID order by l.CUSTOMER_ORDER_ID",p_wave=wave);allocated=q.fetchall();assert [tuple(x[1:])for x in allocated]==[(5,5),(7,7)],allocated
  print("PASS201 real SAP12 physical units/24 codes/two WMS profiles/current DIRECT/original stores5+7/exact sourceHARD/unit QR required/EAN-only409/no replenishment/no unit assigned twice/source0/CASE12/replay/no legalACK",article,wave,flush=True)

 finally:
  if wave is not None:
   q.execute("select CASE_PICK_TASK_ID,SSCC,CONTENT_VERSION from RRL_CASE_PICK_TASK where PICK_WAVE_ID=:p_wave",p_wave=wave)
   for case,carrier,version in q.fetchall():
    q.execute("select h.LOT_UID from RRL_CASE_CARRIER_LOT h join RRL_REMAINS r on r.UID_POLETA=h.LOT_UID where h.CASE_PICK_TASK_ID=:p_case and r.REMAIN>0",p_case=case)
    lots=[x[0]for x in q.fetchall()]
    post("CASE_CARRIER_RETURN",{"case_task_id":int(case)},{"scan_container":carrier,"expected_content_version":int(version),"allow_empty":not bool(lots),"destinations":{uid:receive for uid in lots},"reason":"Own201 native direct CASE return"})
   q.execute("select RESERVATION_ID from RRL_STOCK_RESERVATION where SOURCE_DOC_TYPE='PICK_WAVE'and SOURCE_DOC_ID=:p_wave and STATUS in('ACTIVE','ALLOCATED','PICKING')and BASE_QTY>0",p_wave=wave)
   for(rid,)in q.fetchall():post("RESERVATION_RELEASE",{"reservation_id":int(rid)},{"reason":"Own201 release"})
  for book in bookings:call("POST","/api/inventory/tare/book-cancel",{"operation_id":"DIRECT201.BOOK.CANCEL:"+book,"booking_operation_id":book})
  if wave is not None:
   q.execute("select STATUS from RRL_PICK_WAVE where PICK_WAVE_ID=:p_wave",p_wave=wave)
   if q.fetchone()[0]=="LAUNCHED":post("WAVE_EXECUTION_FINISH",{"wave_id":wave},{"disposition":"RETURNED_TO_PLANNING","reason":"Own201 returned demands remain"})
   else:post("WAVE_CANCEL",{"document_type":"PICK_WAVE","document_id":wave},{"reason":"Own201 unlaunched cleanup"})
  else:
   for plan in plans:picking.cancel_plan(plan,"admin")
  if born:
   from app.modules.inventory.infrastructure.receiving import Receiving
   Receiving(OracleGateway()).cancel(task,"Owned201 fixture cleanup","admin")
   q.execute("select r.UID_POLETA,r.CELL,r.BASE_UOM,r.STOCK_VERSION from RRL_REMAINS r join RRL_PALLETS p on p.UID_PALLET=r.UID_POLETA where p.ARTICUL=:p_a and r.REMAIN>0",p_a=article)
   stock_rows=q.fetchall();counts=[]
   for uid,cell,unit,v in stock_rows:
    q.execute("select PHYSICAL_UNIT_KEY from RRL_WMS_RECEIPT_UNIT where CURRENT_UID=:p_uid and CURRENT_CELL=:p_cell and STOCK_STATUS='AVAILABLE'",p_uid=uid,p_cell=cell)
    counts.append({"uid":uid,"cell":cell,"article":article,"unit":unit,"quantity":"0","expected_stock_version":int(v),"unit_keys":[x[0]for x in q.fetchall()]})
   if counts:post("INVENTORY_COUNT",{"revision_id":revision},{"reason":"Own201 native cleanup","counts":counts})
  q.execute("select nvl(sum(r.REMAIN),0),nvl(sum(r.HARD_RESERVED_BASE),0)from RRL_REMAINS r join RRL_CELLS c on c.CELL=r.CELL where c.WARE_ID=:p_ware",p_ware=ware);assert q.fetchone()==(0,0)
  q.execute("select sum(r.REMAIN),sum(r.HARD_RESERVED_BASE)from RRL_REMAINS r join RRL_CELLS c on c.CELL=r.CELL where c.WARE_ID=6667491");assert q.fetchone()==(20,20)
  print("Own201 native return/release/count completed; original135 P20H20 unchanged",flush=True)
