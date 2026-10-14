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
cfg=get_settings()
if Path("tmp/context622.json").exists()or Path("tmp/source622_progress.json").exists():raise SystemExit("Source622 already created; continue exact retained context")
tag=uuid4().hex[:10];lot="FULL.QA:"+tag;other=lot+"O";src="QF"+tag;dst="QG"+tag;st_uid="FULL.ST:"+tag
lot_prefix=str(50000000000000000+int(tag,16))
lot=lot_prefix+str((10-sum(int(n)*(3 if i%2==0 else 1)for i,n in enumerate(reversed(lot_prefix)))%10)%10)
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
 old_article=article;article="QIW622"+tag.upper()
 barcode_prefix="046"+str(int(tag,16)%10000000000).zfill(10);gtin=barcode_prefix+str((10-sum(int(n)*(3 if i%2==0 else 1)for i,n in enumerate(reversed(barcode_prefix)))%10)%10)
 meta("declare x RRL_ARTICULS%rowtype;begin select *into x from RRL_ARTICULS where ACTICUL=:old;x.ACTICUL:=:a;x.BARCODE_SHT:=:bc;insert into RRL_ARTICULS values x;end;",old=old_article,a=article,bc=gtin)
 meta("insert into RRL_STOCK_UOM_CONVERSION(ARTICUL,INPUT_UOM,BASE_UOM,POLICY_VERSION,NUMERATOR,DENOMINATOR,BASE_SCALE,PROVENANCE)select :a,INPUT_UOM,BASE_UOM,POLICY_VERSION,NUMERATOR,DENOMINATOR,BASE_SCALE,'Own622 marked fullpal'from RRL_STOCK_UOM_CONVERSION where ARTICUL=:old",a=article,old=old_article)
 meta("insert into RRL_SKU_RECEIPT_POLICY(ARTICUL,POLICY_VERSION,MARKING_REQUIRED,UPDATED_BY)values(:a,1,1,'admin')",a=article)
 for system,profile in[("CRPT","TOBACCO"),("EGAIS","ALCOHOL")]:
  meta("insert into RRL_SKU_RECEIPT_PROFILE(ARTICUL,SYSTEM_CODE,PROFILE_CODE,PROFILE_VERSION,SCAN_MODE)values(:a,:s,:p,'QR1','UNIT_OR_AGGREGATION')",a=article,s=system,p=profile)
 box_prefix="047"+str(int(tag,16)%10000000000).zfill(10);box_gtin=box_prefix+str((10-sum(int(n)*(3 if i%2==0 else 1)for i,n in enumerate(reversed(box_prefix)))%10)%10)
 meta("insert into RRL_STOCK_POLICY_GUARD(POLICY_KEY,LOCK_ID)select RRL_STOCK_LOCK_API.resource_key('SKU',:a),nvl(max(LOCK_ID),900000000)+1 from RRL_STOCK_POLICY_GUARD",a=article)
 import httpx
 from datetime import datetime,timedelta,timezone
 admin_api=httpx.Client(auth=("admin","admin123"),timeout=35);base="http://127.0.0.1:8088"
 def api(method,path,body=None,status=200):
  r=admin_api.request(method,base+path,json=body);assert r.status_code==status,(r.status_code,r.text[:2200]);return r.json()
 units=[{"unit_id":str(i),"quantity":"1","codes":[{"system_code":"CRPT","profile_code":"TOBACCO","code":gtin+tag[:5]+str(i).zfill(2)},{"system_code":"EGAIS","profile_code":"ALCOHOL","code":("QA"+tag+str(i)).ljust(68,"X")}]}for i in range(1,4)]
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
 meta("insert into RRL_SBORKA_PALLET_ROWS(ID,PALLET_UID,ARTICUL,EI,QUANTITY) values(RRL_SBORKA_PALLET_ROWS_SQ.nextval,:u,:a,'BOX',1)",u=st_uid,a=article)
 meta("insert into RRL_CUSTOMER_ORDER_FULFILLMENT(FULFILLMENT_ID,CUSTOMER_ORDER_ID,LEGACY_SBORKA_PALLET_ID,PALLET_UID,STATUS,FACT_QTY) values(:id,:o,:st,:u,'PLANNED',0)",id=ff,o=order,st=st,u=st_uid)
 q.execute("select TRANSPORTTYPE from RRL_TRANSPORT_TYPE where TRANSPORTTYPE='15'");trtype=q.fetchone()[0]
 driver=seq("RRL_TR_VODITEL_SQ");meta("insert into RRL_TR_VODITEL(ID,F,I,O,DELETED)values(:id,'Own622','Driver',:tag,0)",id=driver,tag=tag)
 vehicle=int(q.callfunc("RRL_TR_VEHICLE_ADD",oracledb.DB_TYPE_NUMBER,["QL"+tag,trtype,100,1,0,None]));conn.commit()
 trip=seq("RRL_TRANSPORT_TASK_SQ");dock="QD"+tag;pending_st=seq("RRL_SBORKA_PALLETS_SQ")
 meta("insert into RRL_TT_DOCK(DOCK,WARE_ID,DOCK_IS_BLOCKED) values(:dock,:ware,0)",dock=dock)
 meta("insert into RRL_TRANSPORT_TASK(ID,TRANSPORT,TRANSTYPE,CONDITION,SHIPMENT_DATE,VODITEL_ID,DOCK,DELETED) values(:id,:plate,:typ,'Спланирован',trunc(sysdate),:driver,:dock,0)",id=trip,plate="QL"+tag,typ=trtype,driver=driver,dock=dock)
 meta("update RRL_TR_VEHICLE set WORKING_NOW=1,BLOCKED=0,DELETED=0 where ID=:id",id=vehicle)
 meta("update RRL_SBORKA_PALLETS set TRANSTASK_ID=:tt where ID=:id",tt=trip,id=st)
 Path("tmp/source622_progress.json").write_text(json.dumps({"tag":tag,"article":article,"lot":lot,"warehouse":ware,"src":src,"dst":dst,"shipcell":shipcell,"task":task,"st":st,"st_uid":st_uid,"order":order,"wave":wave,"revision":revision,"trip":trip,"vehicle":vehicle,"dock":dock,"barcode":gtin,"units":units,"plan":plan,"pl":pl,"pt":pt,"ff":ff,"customer":customer,"driver":driver,"trtype":trtype},indent=2),encoding="utf-8")
 import xml.etree.ElementTree as ET
 idoc=ET.Element("ARTMAS10");doc=ET.SubElement(idoc,"IDOC");ctrl=ET.SubElement(doc,"EDI_DC40")
 def fields(node,values):
  for k,v in values.items():ET.SubElement(node,k).text=str(v)
 fields(ctrl,dict(MESTYP="ARTMAS",IDOCTYP="ARTMAS10",DOCNUM=str(4000000000000000+int(tag,16)),SNDPRN="OWN.QA.SAP",CREDAT="20261012",CRETIM="001500"))
 for segment,values in [("E1BPE1MATHEAD",{}),("E1BPE1MARART",dict(BASE_UOM="EA",EAN_UPC=gtin)),("E1BPE1MAKTRT",dict(LANGU_ISO="EN",MATL_DESC="Own622 SAP aggregation")),("E1BPE1MARMRT",dict(ALT_UNIT="EA",NUMERATOR="1",DENOMINATR="1",EAN_UPC=gtin)),("E1BPE1MARMRT",dict(ALT_UNIT="BOX",NUMERATOR="3",DENOMINATR="1",EAN_UPC=box_gtin))]:
  fields(ET.SubElement(doc,segment),dict(MATERIAL=article,**values))
 r=admin_api.post(base+"/api/integrations/sap/artmas",content=ET.tostring(idoc,encoding="utf-8"),headers={"Content-Type":"application/xml"});assert r.status_code==202,r.text
 try:
  import xml.etree.ElementTree as ET
  receive="QR622"+tag;pick="QK622"+tag
  for cell,is_pick in [(receive,0),(pick,1)]:
   meta("insert into RRL_CELLS(CELL,WARE_ID,X,Y,Z,OTBOR,IS_SYSTEM,LIMIT_WEIGHT,LIMIT_HEIGHT)values(:c,:ware,0,0,0,:pick,0,0,0)",c=cell,pick=is_pick)
   meta("insert into RRL_STOCK_POLICY_GUARD(POLICY_KEY,LOCK_ID)select RRL_STOCK_LOCK_API.resource_key('CELL',:c),nvl(max(LOCK_ID),900000000)+1 from RRL_STOCK_POLICY_GUARD",c=cell)
  meta("update RRL_WARES set DEFAULT_RECEIVE_CELL=:cell where ID=:ware",cell=receive)
  meta("insert into RRL_RECEIPT_SKU_RULE(WARE_ID,ARTICUL,PICK_CELL,MIN_SHELF_DAYS,SOURCE_PICK_MODE)values(:ware,:a,:cell,0,'AFTER_PUTAWAY')",a=article,cell=pick)
  sscc_prefix="100"+str(int(tag,16)).zfill(14)
  sscc=sscc_prefix+str((10-sum(int(n)*(3 if i%2==0 else 1)for i,n in enumerate(reversed(sscc_prefix)))%10)%10)
  scan_aggregations=[dict(system_code="CRPT",profile_code="TOBACCO",level="PALLET",code=lot),dict(system_code="EGAIS",profile_code="ALCOHOL",level="BOX",code="EGAIS.B:"+tag)]
  supply=ET.Element("WarehouseSupplyOrder",version="1")
  def fields(node,values):
   for key,value in values.items():ET.SubElement(node,key).text=str(value)
  fields(supply,dict(Sender="OWN.QA.SAP",MessageId="IW622.SUPPLY:"+tag,OrderNumber="IW622:"+tag,Revision=1,WarehouseId=ware,ReceiveCell=receive,Supplier="Own622 exact SAP source"))
  line=ET.SubElement(ET.SubElement(supply,"Lines"),"Line");fields(line,dict(LineNumber="1",Material=article));ET.SubElement(line,"Quantity",unit="EA").text="3"
  containers=ET.SubElement(supply,"Aggregations")
  for aggregation in scan_aggregations:
   item=ET.SubElement(containers,"Aggregation")
   fields(item,dict(LineNumber="1",System=aggregation["system_code"],Profile=aggregation["profile_code"],Level=aggregation["level"],Code=aggregation["code"]))
   members=ET.SubElement(item,"Units")
   for unit in units:
    code=next(code["code"]for code in unit["codes"]if code["system_code"]==aggregation["system_code"])
    fields(ET.SubElement(members,"Unit"),dict(UnitId=unit["unit_id"],Quantity="1",Code=code))
  imported=admin_api.post(base+"/api/integrations/sap/supply-orders",content=ET.tostring(supply,encoding="utf-8"),headers={"Content-Type":"application/xml"});assert imported.status_code==202,imported.text
  order_id=imported.json()["order_id"];manifest_op=None
  born=api("POST","/api/receiving/supply-orders/"+order_id+"/pallets",dict(operation_id="IW622.BIRTH:"+tag,line_number="1",sscc=lot,quantity="3",supplier_batch="PB622:"+tag,expiry_date="2030-01-01",gross_weight="3",units=[],aggregations=scan_aggregations),status=201)
  assert born["putaway_cell"]==src,born
  api("POST","/api/receiving/putaway/"+str(born["task_id"])+"/complete",dict(scanned_pallet=lot,scanned_from_cell=receive,scanned_to_cell=src))

  post("RESERVATION_CREATE",{"uid_pallet":lot,"cell":src,"articul":article,"qty":"3","unit_code":"EA","ware_id":ware,"reservation_kind":"HARD","reservation_scope":"PALLET","reservation_domain":"PICKING","source_doc_type":"PICK_WAVE","source_doc_id":wave,"source_line_id":pt,"customer_order_id":order,"customer_id":customer,"pick_plan_id":plan,"pick_plan_line_id":pl},{"type":"PICK_WAVE","id":wave})
  post("WAVE_PICK_RELEASE",{},{"wave_id":wave})
  before=OrderExecution(OracleGateway()).get(order);assert before["lines"][0]["picked_quantity"]=="0"
  completed=post("TASK_COMPLETE",{"fact_qty":"3","scanned_pallet":lot,"scanned_from_cell":src,"scanned_to_cell":dst},{"task_id":task})
  preview=FullPalletShipment(OracleGateway()).preview(task)
  assert preview["pallet_identifier"]==lot and preview["quantity"]=="3"
  body={"shipment_identifier":st_uid,"scanned_pallet":lot,"expected_stock_version":int(preview["stock_version"])}
  op="FULL.BIND:"+tag;bound=post("PICK_PALLET_BIND_SHIPMENT",body,{"task_id":task},op)
  assert post("PICK_PALLET_BIND_SHIPMENT",body,{"task_id":task},op)==bound
  q.execute("select STATUS,FACT_QTY,FACT_UOM,PICKED_WAREHOUSE_TASK_ID,PICKED_PALLET_UID from RRL_CUSTOMER_ORDER_FULFILLMENT where FULFILLMENT_ID=:id",id=ff)
  assert q.fetchone()==("PICKED",3,"EA",task,lot)
  assert OrderExecution(OracleGateway()).get(order)["lines"][0]["picked_quantity"]=="3"
  post("INTERNAL_MOVE",{"uid":lot,"source_cell":dst,"target_cell":shipcell,"quantity":"0","unit":"EA"},{})
  from app.transport_composition import build_transport_loading
  loading=build_transport_loading();preview=loading.preview_single(st_uid)
  assert preview["root"]==lot and preview["snapshot"]["nodes"][0]["kind"]=="STOCK"
  from app.modules.inventory.infrastructure.outgoing_quality import OutgoingQuality
  qc=OutgoingQuality(OracleGateway());quality=qc.status(st_uid,"admin")
  scans=[code for unit in units for code in unit["codes"]]
  api("POST","/api/outgoing-quality/"+st_uid+"/scan",{"operation_id":"IW622.QC:"+tag,"expected_composition_signature":quality["composition_signature"],"error_count":0,"scans":scans})
  assert qc.status(st_uid,"admin")["ready"]
  loading_context={"transport_task_id":trip,"scan_vehicle":"QL"+tag,"scan_dock":dock,"measurements":{"origin":"MANUAL_CONFIRMED","content_version":preview["expected_version"],"gross_weight_kg":"10","width_m":"1","depth_m":"1","height_m":"1.5"}}
  ship_body={"expected_version":preview["expected_version"],"expected_composition_signature":preview["composition_signature"],"scan_container":lot,"scan_cell":shipcell,"loading_context":loading_context}
  shipop="IW622.LOAD:"+tag;shipped=loading.load_single(shipop,st_uid,ship_body,"admin")
  assert loading.load_single(shipop,st_uid,ship_body,"admin")==shipped and shipped["physical_places"]==1
  q.execute("select TT_ID,ROOT_UID,VEHICLE_ID,VEHICLE_NUMBER,DOCK,STATUS from RRL_TT_HU_LOAD_FACT where LOAD_OPERATION_ID=:op",op=shipop);assert q.fetchone()==(trip,lot,vehicle,"QL"+tag,dock,"LOADED")


  from app.modules.platform.public import read_oracle_json
  profile=read_oracle_json(q.callfunc("RRL_VEHICLE_PROFILE_API.describe_profile",oracledb.DB_TYPE_CLOB,[vehicle]))
  profile_body=dict(operation_id="VEH.RETURN622:"+tag,vehicle_id=vehicle,vehicle_size_class="DEV.RETURN622",
     cargo_length_mm=3000,cargo_width_mm=2000,cargo_height_mm=2200,expected_version=0,
     expected_source_hash=profile["base_hash"],reason="Synthetic isolated return source vehicle profile",
     evidence_reference="DEV622:"+tag)
  profile_result=q.var(oracledb.DB_TYPE_CLOB)
  q.callproc("RRL_VEHICLE_PROFILE_API.configure",[json.dumps(profile_body),"admin",profile_result]);conn.commit()
  departed=loading.depart("IW622.DEPART:"+tag,trip,"admin")
  q.execute("select STATUS from RRL_TT_HU_LOAD_FACT where LOAD_OPERATION_ID=:p",p=shipop);assert q.fetchone()[0]=="DEPARTED"
  q.execute("select count(*),sum(BASE_QTY)from RRL_WMS_RECEIPT_UNIT where CURRENT_UID=:u and STOCK_STATUS='ISSUED'and HARD_RESERVATION_ID is null",u=lot);assert q.fetchone()==(3,3)
  q.execute("select BARCODE_KOR from RRL_ARTICULS where ACTICUL=:article",article=article);assert q.fetchone()[0]==box_gtin
  context={"tag":tag,"article":article,"lot":lot,"warehouse":ware,"source_load":shipop,"source_trip":trip,"barcode":gtin,"box_barcode":box_gtin,"source_quantity":"3","units":units,"aggregations":scan_aggregations,"sap_order_id":order_id,"order":order,"st":st,"st_uid":st_uid,"receive":receive,"pick":pick,"src":src,"dst":dst,"shipcell":shipcell,"vehicle":vehicle,"plate":"QL"+tag,"driver":driver,"supplier_batch":"PB622:"+tag,"expiry":"2030-01-01"}
  Path("tmp/context622.json").write_text(json.dumps(context,indent=2),encoding="utf-8")
  print("SOURCE622 new isolated actualSAP3EA/oneBOX3/customboxEAN/verifiedbatch/same3keys6codes/existing fullpalshipment/depart/sourceP0")

 finally:
  conn.rollback();q.callproc("RRL_STOCK_POSTING_API.reset_connection")

