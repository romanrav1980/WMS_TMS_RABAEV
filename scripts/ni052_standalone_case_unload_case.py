"""180 original file-gateway XML contract to native weighted pallet receipt."""
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime,timezone,timedelta
import sys,json,xml.etree.ElementTree as ET
from pathlib import Path
from uuid import uuid4
from decimal import Decimal
import httpx,oracledb
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment();sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"api/wms_api_server"))
from app.config import get_settings
s=get_settings();tag=sys.argv[1]if len(sys.argv)>1 else uuid4().hex[:8];article="QPB212"+tag.upper();ware=30000000+int(tag[:6],16);receive="Q212R"+tag;pick="Q212P"+tag;storage="Q212S"+tag
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
 fields(control,{"MESTYP":"ARTMAS","IDOCTYP":"ARTMAS10","DOCNUM":str(2000000000000000+int(tag,16)),"SNDPRN":"OWN.QA.SAP","CREDAT":"21261011","CRETIM":"020000"})
 for segment,values in [("E1BPE1MATHEAD",{}),("E1BPE1MARART",{"BASE_UOM":"EA","EAN_UPC":gtin}),("E1BPE1MAKTRT",{"LANGU_ISO":"EN","MATL_DESC":"Own weighted box "+tag}),("E1BPE1MARMRT",{"ALT_UNIT":"EA","NUMERATOR":"1","DENOMINATR":"1","EAN_UPC":gtin})]:
  fields(ET.SubElement(doc,segment),{"MATERIAL":article,**values})
 call("POST","/api/integrations/sap/artmas",status=202,raw=ET.tostring(idoc,encoding="utf-8"))
 meta("update RRL_ARTICULS set TYPE_W=0 where ACTICUL=:p_a",p_a=article)
 call("PUT",f"/api/finished-goods/skus/{article}/receiving-policy",{"expected_version":0,"marking_required":False,"serialized_weight_boxes":False,"profiles":[]})
 meta("insert into RRL_WARES(ID,NAME,PREFIX,DEFAULT_RECEIVE_CELL)values(:p_ware,:p_name,'QW',:p_receive)",p_ware=ware,p_name="Own180 "+tag,p_receive=receive)
 meta("insert into RRL_RECEIPT_WARE_SETTINGS(WARE_ID,OUTGOING_QC_MODE,OUTGOING_QC_INDEPENDENT)values(:p_ware,'NONE',0)",p_ware=ware)
 meta("update RRL_RECEIPT_WARE_SETTINGS set COMPANY_PREFIX='900000',EXTENSION_DIGIT=0 where WARE_ID=:p_ware",p_ware=ware)
 for cell,is_pick in [(receive,0),(pick,1),(storage,0),("CPT_"+str(ware),0)]:
  meta("insert into RRL_CELLS(CELL,WARE_ID,X,Y,Z,OTBOR,IS_SYSTEM,LIMIT_WEIGHT,LIMIT_HEIGHT)values(:p_cell,:p_ware,0,0,0,:p_pick,:p_system,0,0)",p_cell=cell,p_ware=ware,p_pick=is_pick,p_system=int(cell.startswith("CPT_")))
  meta("insert into RRL_STOCK_POLICY_GUARD(POLICY_KEY,LOCK_ID)select RRL_STOCK_LOCK_API.resource_key('CELL',:p_cell),nvl(max(LOCK_ID),900000000)+1 from RRL_STOCK_POLICY_GUARD",p_cell=cell)
 meta("insert into RRL_RECEIPT_SKU_RULE(WARE_ID,ARTICUL,PICK_CELL,MIN_SHELF_DAYS,ALLOW_PICK_BATCH_MIX,SOURCE_PICK_MODE)values(:p_ware,:p_a,:p_pick,0,0,'DIRECT')",p_ware=ware,p_a=article,p_pick=pick)
 supply=ET.Element("WarehouseSupplyOrder",version="1")
 fields(supply,{"Sender":"OWN.QA.SAP","MessageId":"DIRECT212.SUPPLY:"+tag,"OrderNumber":"D212:"+tag,"Revision":1,"WarehouseId":ware,"ReceiveCell":receive,"Supplier":"Own180 software fixture"})
 line=ET.SubElement(ET.SubElement(supply,"Lines"),"Line");fields(line,{"LineNumber":"1","Material":article});ET.SubElement(line,"Quantity",unit="EA").text="20"
 imported=call("POST","/api/integrations/sap/supply-orders",status=202,raw=ET.tostring(supply,encoding="utf-8"))
 revision=int(q.callfunc("REVIZION.create_revizion",oracledb.DB_TYPE_NUMBER,[ware,"admin"]));c.commit()
 body={"operation_id":"DIRECT212.RECEIVE:"+tag,"line_number":"1","sscc":sscc,"quantity":"20","product_barcode":gtin,"supplier_batch":"PB:"+tag,"expiry_date":"2120-01-01","gross_weight":"20"}
 from app.services.picking_service import PickingService
 from app.schemas import PickingPlanCreateRequest,PickWaveCreateRequest,PickWaveAddPlanRequest,PickWaveActionRequest
 from app.modules.inventory.contracts_stock import StockCommand
 from app.modules.inventory.infrastructure.stock_posting_uow import StockPosting
 from app.modules.platform.public import read_oracle_json
 from app.oracle_gateway import OracleGateway
 picking=PickingService();orders=[];plans=[];wave=None;bookings=[];case_types=set();sender=None;controller=None;parent=None;shipped=False
 def post(kind,source,metadata,op=None):
  return StockPosting().post(StockCommand(operation_id=op or "DIRECT212:"+uuid4().hex,command_type=kind,actor="admin",source=source,metadata=metadata,lines=()))
 def seq(name):q.execute("select "+name+".nextval from dual");return int(q.fetchone()[0])
 q.execute("select min(CUSTOMER_ID),max(CUSTOMER_ID)from RRL_CUSTOMER");customers=q.fetchone()
 customer_id=700000000+int(tag,16)
 meta("declare x RRL_CUSTOMER%rowtype;begin select *into x from RRL_CUSTOMER where CUSTOMER_ID=:p_template;x.CUSTOMER_ID:=:p_id;x.CUSTOMER_CODE:=:p_code;insert into RRL_CUSTOMER values x;end;",p_template=customers[0],p_id=customer_id,p_code="QSC212"+tag)
 customers=(customer_id,)
 type_body={"pallet_type_code":"SMALL212."+tag,"pallet_type_name":"Own212 final weighing small box","load_unit_class":"CONTAINER","default_volume_m3":"0.001","default_weight_kg":"0.1","final_weight_required":True,"expected_version":0}
 created_type=call("POST","/api/case-pick/pallet-types",type_body);small_type=created_type["pallet_type_id"]
 types=call("GET","/api/case-pick/pallet-types");current_type=next(x for x in types if x["pallet_type_id"]==small_type)
 assert current_type["final_weight_required"]==1 and current_type["type_version"]==1
 # Old client omission preserves the new safety requirement.
 old_client={**type_body,"pallet_type_id":small_type,"expected_version":1};old_client.pop("final_weight_required")
 call("POST","/api/case-pick/pallet-types",old_client)
 conflict=api.post(base+"/api/case-pick/pallet-types",json={**type_body,"pallet_type_id":small_type,"expected_version":1});assert conflict.status_code==409
 try:q.execute("update RRL_PALLET_TYPE set FINAL_WEIGHT_REQUIRED=0 where PALLET_TYPE_ID=:p_id",p_id=small_type);raise AssertionError("Final weight bypassed by raw write")
 except oracledb.DatabaseError as exc:c.rollback();assert exc.args[0].code==20863
 meta("insert into RRL_CUSTOMER_PALLET_TYPE_RULE(CUSTOMER_PALLET_TYPE_RULE_ID,CUSTOMER_ID,PALLET_TYPE_ID,IS_DEFAULT,ACTIVE,CREATED_BY)select nvl(max(CUSTOMER_PALLET_TYPE_RULE_ID),0)+1,:p_customer,:p_type,1,1,'admin'from RRL_CUSTOMER_PALLET_TYPE_RULE",p_customer=customer_id,p_type=small_type)
 for customer,quantity in zip(customers,(6,)):
  order=seq("RRL_CUSTOMER_ORDER_SQ");orders.append(order)
  meta("insert into RRL_CUSTOMER_ORDER(CUSTOMER_ORDER_ID,ORDER_NO,CUSTOMER_ID,WARE_ID)values(:p_id,:p_no,:p_customer,:p_ware)",p_id=order,p_no="DIRECT212:"+tag+":"+str(quantity),p_customer=customer,p_ware=ware)
  meta("insert into RRL_CUSTOMER_ORDER_ROW(CUSTOMER_ORDER_ROW_ID,CUSTOMER_ORDER_ID,LINE_NO,ARTICUL,ORDER_QTY,UNIT_CODE)values(RRL_CUSTOMER_ORDER_ROW_SQ.nextval,:p_order,1,:p_article,:p_qty,'EA')",p_order=order,p_article=article,p_qty=quantity)
  empty=picking.create_plan(PickingPlanCreateRequest(customer_order_id=order,created_by="admin"))
  q.execute("select p.STATUS,(select nvl(sum(l.PLANNED_QTY),0)from RRL_PICK_PLAN_LINE l where l.PICK_PLAN_ID=p.PICK_PLAN_ID)from RRL_PICK_PLAN p where p.PICK_PLAN_ID=:p_id",p_id=empty);assert q.fetchone()==("NO_STOCK",0)
  picking.cancel_plan(empty,"admin")
 try:
  result=call("POST",f"/api/receiving/supply-orders/{imported['order_id']}/pallets",body,201);born=True
  task=result["task_id"];assert result["marking_units"]==0
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
  wave=picking.create_wave(PickWaveCreateRequest(wave_code="DIRECT212:"+tag,ware_id=ware,created_by="admin"))
  for plan in plans:picking.add_wave_plan(wave,PickWaveAddPlanRequest(pick_plan_id=plan,created_by="admin"))
  picking.preview_wave(wave,PickWaveActionRequest(updated_by="admin"))
  wire=StockCommand(operation_id="DIRECT212.LAUNCH:"+tag,command_type="WAVE_LAUNCH",actor="admin",source={"wave_id":wave},metadata={},lines=()).canonical_json()
  inp,out=q.var(oracledb.DB_TYPE_CLOB),q.var(oracledb.DB_TYPE_CLOB);inp.setvalue(0,wire)
  try:
   q.callproc("RRL_STOCK_POSTING_API.prepare_command",[inp,"admin",out,None]);assert out.getvalue()is None
   q.callproc("RRL_STOCK_POSTING_API.execute_prepared",[out])
   q.execute("select STATUS from RRL_WAREHOUSE_TASK where TASK_ID=:p_task",p_task=task);assert q.fetchone()[0]=="CANCELLED"
   q.execute("select HARD_RESERVED_BASE from RRL_REMAINS where UID_POLETA=:p_uid and CELL=:p_cell",p_uid=sscc,p_cell=receive);assert q.fetchone()[0]==6
  finally:c.rollback();q.callproc("RRL_STOCK_POSTING_API.reset_connection")
  q.execute("select STATUS from RRL_WAREHOUSE_TASK where TASK_ID=:p_task",p_task=task);assert q.fetchone()[0]=="PLANNED"
  q.execute("select HARD_RESERVED_BASE from RRL_REMAINS where UID_POLETA=:p_uid and CELL=:p_cell",p_uid=sscc,p_cell=receive);assert q.fetchone()[0]==0
  print("PASS212 outer rollback restores original placement and source HARD0",flush=True)
  picking.launch_wave(wave,PickWaveActionRequest(updated_by="admin",operation_id="DIRECT212.LAUNCH:"+tag))
  q.execute("select STATUS,LAST_ERROR,QTY from RRL_WAREHOUSE_TASK where TASK_ID=:p_task",p_task=task);state,reason,qty=q.fetchone()
  assert state=="CANCELLED"and reason=="DIRECT_PICK_BY_LINE:DIRECT212.LAUNCH:"+tag and qty==20
  q.execute("select count(*)from RRL_PICK_WAVE_REPLENISH_TASK where PICK_WAVE_ID=:p_wave",p_wave=wave);assert q.fetchone()[0]==0
  q.execute("select count(*)from RRL_RECEIPT_SLOT_CLAIM where TASK_ID=:p_task",p_task=task);assert q.fetchone()[0]==0
  post("WAVE_PICK_RELEASE",{"wave_id":wave},{})
  q.execute("select t.CASE_PICK_TASK_ID,l.CASE_PICK_LINE_ID,t.SSCC,l.CELL_CODE,l.PLANNED_QTY,t.PALLET_TYPE_ID from RRL_CASE_PICK_TASK t join RRL_CASE_PICK_LINE l on l.CASE_PICK_TASK_ID=t.CASE_PICK_TASK_ID where t.PICK_WAVE_ID=:p_wave order by t.CUSTOMER_ORDER_ID",p_wave=wave)
  rows=q.fetchall();assert sorted(r[4]for r in rows)==[6]
  tare="/api/inventory/tare"
  for case,line,carrier,cell,quantity,case_type in rows:
   assert cell==receive and case_type==small_type;case_types.add(case_type)
   available=call("GET",tare+f"/warehouses/{ware}/availability")
   current=next(x for x in available if x["pallet_type_id"]==case_type)
   call("POST",tare+"/count",{"operation_id":"DIRECT212.TARE.COUNT:"+str(case),"owner_ware_id":ware,"pallet_type_id":case_type,"condition":"GOOD","observed_quantity":"2","expected_version":current["balance_version"]or 0,"reason":"Own212 software container fixture","decision_reference":"DIRECT212:"+tag})
   book="DIRECT212.TARE.BOOK:"+str(case);call("POST",tare+"/book",{"operation_id":book,"place_kind":"CASE","place_id":str(case)});bookings.append(book)
   label_path=f"/api/case-pick/tasks/{case}/sscc-label"
   q.execute("select CONTENT_VERSION from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=:p_case",p_case=case);empty_version=int(q.fetchone()[0])
   label_body={"operation_id":"SSCC212:"+tag,"scan_container":carrier,"expected_content_version":empty_version}
   # Native issue joins outer metadata transaction; rollback restores original identity/history.
   q.callproc("RRL_STOCK_METADATA_TX.begin_change",["admin","case_pick_execute"])
   native_result=q.var(oracledb.DB_TYPE_CLOB)
   try:
    q.callproc("RRL_CASE_SSCC_API.issue",[case,json.dumps(label_body,sort_keys=True,separators=(",",":")),"admin",native_result])
    q.execute("select SSCC from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=:p_case",p_case=case);assert q.fetchone()[0]!=carrier
   finally:c.rollback();q.callproc("RRL_STOCK_METADATA_TX.end_change")
   q.execute("select SSCC from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=:p_case",p_case=case);assert q.fetchone()[0]==carrier
   try:q.callproc("RRL_CASE_SSCC_API.assert_ready",[case]);raise AssertionError("Unlabelled small CASE admitted")
   except oracledb.DatabaseError as exc:c.rollback();assert exc.args[0].code==20887
   label=call("POST",label_path,label_body);assert call("POST",label_path,label_body)==label
   call("POST",label_path,{**label_body,"scan_container":carrier+"X"},status=409)
   from app.modules.inventory.domain.sscc_label import check_digit
   carrier=label["sscc"];assert len(carrier)==18 and carrier[-1]==check_digit(carrier[:-1])
   printed=api.get(base+label_path+"/document");assert printed.status_code==200 and "(00)"+carrier in printed.text and "<svg" in printed.text
   zpl=api.get(base+label_path+"/document?format=zpl");assert zpl.status_code==200 and ">;>800"+carrier in zpl.text
   call("POST",label_path+"/confirm",{"scan":"000000000000000000"},status=409)
   try:q.execute("delete from RRL_CASE_SSCC_LABEL where CASE_PICK_TASK_ID=:p_case",p_case=case);raise AssertionError("Label history deleted")
   except oracledb.DatabaseError as exc:c.rollback();assert exc.args[0].code==20863
   try:q.callproc("RRL_CASE_SSCC_API.assert_ready",[case]);raise AssertionError("Unconfirmed label admitted")
   except oracledb.DatabaseError as exc:c.rollback();assert exc.args[0].code==20887
   call("POST",label_path+"/confirm",{"scan":"(00)"+carrier})
   assert call("POST",label_path+"/confirm",{"scan":carrier})["confirmed"]
   print("PASS212 native label rollback/original CP retained/18-digit checksum/replay/body conflict/GS1 SVG+ZPL/scan confirm/immutable archive",carrier,flush=True)
   sender="QS212"+tag;group=sender.upper();secret=uuid4().hex;device="WH.FINAL212:"+tag
   q.execute("insert into RUSERS(ID,PASS,NAME,USER_GROUP,WARE_ID,DELETED,PRAVO_ADMIN_LOGIN)values(:id,:secret,'Own final scale gateway',:grp,:ware,0,0)",id=sender,secret=secret,grp=group,ware=ware);c.commit()
   call("POST","/api/admin/rights/groups",{"id":group,"name":"Own212 final scale sender"})
   call("POST",f"/api/admin/rights/groups/{group}/rights",{"right_name":"warehouse_scale_ingest","description":"Own software gateway"})
   def stamp(value):return value.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f+00:00")
   scale_base="/api/inventory/warehouse-scales";now=datetime.now(timezone.utc)
   policy={"warehouse_id":ware,"post_cell":receive,"sender_id":sender,"expected_version":0,"active":True,"device_mode":"TEST","basis":"GROSS","capacity_kg":"100","resolution_kg":"0.001","calibration_ref":"DEV212:"+tag,"calibrated_until":stamp(now+timedelta(days=1))}
   call("PUT",scale_base+"/devices/"+device,policy)
   scale_gateway=httpx.Client(auth=(sender,secret),timeout=35)
   def scale_call(packet,status=200):
    response=scale_gateway.post(base+scale_base+"/final-captures",json=packet);assert response.status_code==status,(response.status_code,response.text[:1800]);return response.json()
   def final_packet(purpose,weight,version,tare_key=None):
    now=datetime.now(timezone.utc)
    return {"device_id":device,"capture_id":purpose+"212:"+tag,"post_cell":receive,"case_task_id":case,
      "expected_content_version":version,"scan_container":carrier,"purpose":purpose,
      **({"tare_capture_key":tare_key}if tare_key else{}),
      "device_policy_version":1,"calibration_ref":policy["calibration_ref"],"unit":"KG","basis":"GROSS","preset_tare_kg":"0",
      "zero_confirmed":True,"zero_check_kg":"0","zero_check_at":stamp(now-timedelta(seconds=10)),"measured_at":stamp(now),
      "samples":[{"offset_ms":i*500,"weight_kg":weight}for i in range(5)]}
   minimal=json.dumps({"metadata":{},"source":{"case_task_id":case}})
   try:q.callproc("RRL_CASE_SCALE_ADMISSION.assert_capture",[minimal,0]);raise AssertionError("First fill without actual empty tare admitted")
   except oracledb.DatabaseError as exc:c.rollback();assert exc.args[0].code==20886
   tare_packet=final_packet("EMPTY_TARE","0.100",label["content_version"])
   scale_call({**tare_packet,"capture_id":"BAD212:"+tag,"samples":[*tare_packet["samples"][:-1],{"offset_ms":2000,"weight_kg":"0.110"}]},409)
   tare_capture=scale_call(tare_packet);assert scale_call(tare_packet)==tare_capture
   scale_call({**tare_packet,"zero_check_kg":"0.001"},409)
   call("POST",scale_base+"/final-captures",tare_packet,status=403)
   scale_call({**tare_packet,"capture_id":"BAD.GROSS212:"+tag,"purpose":"FINAL_GROSS"},409)
   print("PASS212 empty SSCC tare archive/stable exact.100/current sender/TEST/replay/changed-body/unstable/closed-source refusals",tare_capture["capture_key"],flush=True)
   call("POST",f"/api/case-pick/tasks/{case}/claim",{});call("POST",f"/api/case-pick/tasks/{case}/start",{})
   payload={"operation_id":"DIRECT212.PICK:"+str(case),"fact_qty":str(quantity),"scan_cell":receive,"scan_product":gtin,"scan_container":carrier}
   path=f"/api/case-pick/tasks/{case}/lines/{line}/confirm"
   from app.services.case_pick_service import CasePickService
   from app.schemas import CasePickLineConfirmRequest
   try:picked=call("POST",path,payload)
   except AssertionError:
    try:CasePickService().confirm_line(int(case),int(line),CasePickLineConfirmRequest(**payload,actor="admin"))
    except HTTPException as exc:print("Native212 reason",str(exc.__cause__.__cause__)[:2200],flush=True)
    raise
   assert call("POST",path,payload)==picked
  q.execute("select REMAIN,HARD_RESERVED_BASE from RRL_REMAINS where UID_POLETA=:p_uid and CELL=:p_cell",p_uid=sscc,p_cell=receive);assert q.fetchone()==(14,0)
  q.execute("select sum(PICKED_QTY)from RRL_CASE_PICK_LINE where PICK_WAVE_ID=:p_wave",p_wave=wave);assert q.fetchone()[0]==6
  q.execute("select CONTENT_VERSION from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=:p_case",p_case=case);version=int(q.fetchone()[0])
  call("POST",f"/api/case-pick/tasks/{case}/close-pallet",{"operation_id":"SMALL212.CLOSE:"+tag,"expected_content_version":version,"reason":"Complete current six-unit small box"})
  sid=seq("RRL_SBORKA_PALLETS_SQ");ff=seq("RRL_CUSTOMER_ORDER_FULF_SQ");identifier="SMALL212.ST:"+tag
  meta("insert into RRL_SBORKA_PALLETS(ID,PALLET_UID,ST_NUMBER,WARE_ID,CONDITION,ADDR)values(:p_id,:p_uid,:p_uid,:p_ware,0,'Own212 current small-box shipment')",p_id=sid,p_uid=identifier,p_ware=ware)
  meta("insert into RRL_SBORKA_PALLET_ROWS(ID,PALLET_UID,ARTICUL,EI,QUANTITY)values(RRL_SBORKA_PALLET_ROWS_SQ.nextval,:p_uid,:p_article,'EA',6)",p_uid=identifier,p_article=article)
  meta("insert into RRL_CUSTOMER_ORDER_FULFILLMENT(FULFILLMENT_ID,CUSTOMER_ORDER_ID,LEGACY_SBORKA_PALLET_ID,PALLET_UID,STATUS,FACT_QTY)values(:p_id,:p_order,:p_ship,:p_uid,'PLANNED',0)",p_id=ff,p_order=orders[0],p_ship=sid,p_uid=identifier)
  from app.modules.inventory.infrastructure.case_shipment_binding import bind_case_shipment
  bind_case_shipment(OracleGateway(),int(case),identifier,carrier,version,"admin")
  from app.modules.master_data.infrastructure.quality_weight_policy import QualityWeightPolicy
  from app.modules.master_data.contracts_quality_weight import WeightPolicyInput
  QualityWeightPolicy(OracleGateway()).set(ware,article,WeightPolicyInput(expected_version=0,base_uom="EA",base_weight_kg="0.05",box_weight_kg="0.05"),"admin")
  gross_packet=final_packet("FINAL_GROSS","0.400",version,tare_capture["capture_key"])
  scale_call({**gross_packet,"capture_id":"BAD.VERSION212:"+tag,"expected_content_version":version-1},409)
  scale_call({**gross_packet,"capture_id":"BAD.TARE212:"+tag,"tare_capture_key":"F"*64},409)
  final_capture=scale_call(gross_packet);assert scale_call(gross_packet)==final_capture
  assert final_capture["net_weight_kg"]=="0.3"and final_capture["tare_weight_kg"]=="0.1"
  final_list=call("GET",scale_base+f"/final-captures?task={case}")
  assert len(final_list["items"])==2
  old_list=call("GET",scale_base+f"/captures?task={case}&line={line}");assert old_list["items"]==[]
  assert call("GET",scale_base+"/captures/"+final_capture["capture_key"])==final_capture
  try:q.execute("update RRL_WH_SCALE_CAPTURE set WEIGHT_KG=1 where CAPTURE_KEY=:key",key=final_capture["capture_key"]);raise AssertionError("Final archive altered")
  except oracledb.DatabaseError as exc:c.rollback();assert exc.args[0].code==20863
  q.execute("select REMAIN,HARD_RESERVED_BASE from RRL_REMAINS where UID_POLETA=:p_uid and CELL=:p_cell",p_uid=sscc,p_cell=receive);assert q.fetchone()==(14,0)
  print("PASS212 closed whole CASE/current composition/final gross.400/measured tare.100/net.300/list separated/immutable/no P-H change",final_capture["capture_key"],flush=True)
  from app.modules.inventory.infrastructure.outgoing_quality import OutgoingQuality
  quality=OutgoingQuality(OracleGateway());before=quality.status(identifier)
  assert before["control_mode"]=="WEIGHT"and before["required"]and not before["ready"],before
  parent="SMALL212.HU:"+tag
  q.execute("select CURRENT_CELL from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=:p_id",p_id=case);case_cell=q.fetchone()[0]
  post("HU_CREATE",{"uid":parent},{"cell":case_cell,"warehouse":ware,"container_type":"ROLL_CAGE","tare_weight_kg":1,"scan_container":parent,"scan_cell":case_cell})
  def hu_tree():
   q.execute("select RRL_STOCK_HU_READ.snapshot_json(:p_uid)from dual",p_uid=parent);return read_oracle_json(q.fetchone()[0])
  def case_version():
   q.execute("select CONTENT_VERSION from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=:p_id",p_id=case);return int(q.fetchone()[0])
  def packing(kind,op):
   return post(kind,{"uid":parent},{"child_case_task_id":int(case),"expected_version":hu_tree()["nodes"][0]["version"],"expected_child_version":case_version(),"scan_container":parent,"scan_child":carrier,"retained_tare_booking_operation_id":book,"reason":"Own212 physical layout"},op)
  # A parent exemption cannot approve an unweighed child; old GROSS command version remains stale.
  packing("HU_ATTACH","SMALL212.UNCONTROLLED.PACK:"+tag)
  assert not quality.status(identifier)["ready"]
  packing("HU_DETACH","SMALL212.UNCONTROLLED.UNPACK:"+tag)
  assert not quality.status(identifier)["ready"]
  new_packet=final_packet("FINAL_GROSS","0.400",case_version(),tare_capture["capture_key"]);new_packet["capture_id"]="GROSS.AFTER.LAYOUT212:"+tag
  final_capture=scale_call(new_packet)
  assert final_capture["composition_signature_version"]==3
  before=quality.status(identifier)
  controller="QC212"+tag;control_group=controller.upper();control_secret=uuid4().hex
  q.execute("insert into RUSERS(ID,PASS,NAME,USER_GROUP,WARE_ID,DELETED,PRAVO_ADMIN_LOGIN)values(:id,:secret,'Own final controller',:grp,:ware,0,0)",id=controller,secret=control_secret,grp=control_group,ware=ware);c.commit()
  call("POST","/api/admin/rights/groups",{"id":control_group,"name":"Own212 independent final controller"})
  call("POST",f"/api/admin/rights/groups/{control_group}/rights",{"right_name":"outgoing_pallet_check","description":"Own final controller"})
  qc_gateway=httpx.Client(auth=(controller,control_secret),timeout=35)
  final_path="/api/outgoing-quality/"+identifier+"/final-weight"
  check={"operation_id":"SMALL212.QC:"+tag,"capture_key":final_capture["capture_key"],"expected_composition_signature":before["composition_signature"]}
  raw={"operation_id":"SMALL212.MANUAL:"+tag,"quality_kind":"WEIGHT","gross_weight":"0.400","wood_weight":"0.100","expected_composition_signature":before["composition_signature"]}
  call("POST","/api/outgoing-quality/"+identifier+"/weight",raw,status=409)
  bad=qc_gateway.post(base+final_path,json={**check,"gross_weight":"0.400"});assert bad.status_code==422
  q.execute("select count(*)from RRL_WH_FINAL_SCALE_USE where CAPTURE_KEY=:p_key",p_key=final_capture["capture_key"]);assert q.fetchone()[0]==0
  # Current native actor WARE is checked even for a saved APPLIED result.
  q.execute("update RUSERS set WARE_ID=6667491 where ID=:p_actor",p_actor=controller);c.commit()
  refused=qc_gateway.post(base+final_path,json=check);assert refused.status_code==403
  q.execute("update RUSERS set WARE_ID=:p_ware where ID=:p_actor",p_ware=ware,p_actor=controller);c.commit()
  # One original native QC transaction: late rollback restores proof, approval, CASE and outbox.
  canonical=StockCommand(operation_id=check["operation_id"],command_type="OUTGOING_PALLET_CHECK",actor=controller,source={"pallet_identifier":identifier},lines=(),
      metadata={"quality_kind":"WEIGHT","gross_weight":final_capture["weight_kg"],"wood_weight":final_capture["tare_weight_kg"],"final_scale_capture":check["capture_key"],"expected_composition_signature":check["expected_composition_signature"]}).canonical_json()
  result=q.var(oracledb.DB_TYPE_CLOB)
  try:
   q.callproc("RRL_STOCK_POSTING_API.prepare_command",[canonical,controller,result,None]);assert result.getvalue()is None
   q.callproc("RRL_STOCK_POSTING_API.execute_prepared",[result])
   assert read_oracle_json(result.getvalue())["ready"]
   q.execute("select count(*)from RRL_WH_FINAL_SCALE_USE where CAPTURE_KEY=:p_key",p_key=check["capture_key"]);assert q.fetchone()[0]==1
  finally:c.rollback();q.callproc("RRL_STOCK_POSTING_API.reset_connection")
  q.execute("select count(*)from RRL_WH_FINAL_SCALE_USE where CAPTURE_KEY=:p_key",p_key=check["capture_key"]);assert q.fetchone()[0]==0
  q.execute("select count(*)from RRL_STOCK_OPERATION where OPERATION_ID=:p_op",p_op=check["operation_id"]);assert q.fetchone()[0]==0
  q.execute("select PROOVED,WEIGHT_QC_OPERATION_ID from RRL_SBORKA_PALLETS where ID=:p_id",p_id=sid);previous=q.fetchone();assert (previous[0]or 0)==0 and previous[1]is None
  q.execute("select STATUS from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=:p_id",p_id=case);assert q.fetchone()[0]=="WAIT_CONTROL"
  print("PASS212 late native QC rollback removes final-use/journal/approval and restores WAIT_CONTROL",flush=True)
  checks=[check,{**check,"operation_id":"SMALL212.QC.B:"+tag}]
  with ThreadPoolExecutor(max_workers=2)as pool:responses=list(pool.map(lambda payload:qc_gateway.post(base+final_path,json=payload),checks))
  assert sorted(r.status_code for r in responses)==[200,409],[(r.status_code,r.text[:1800])for r in responses]
  index=next(i for i,r in enumerate(responses)if r.status_code==200);check=checks[index];verified=responses[index].json()
  assert verified["verified"]==1 and verified["ready"]
  status_http=qc_gateway.get(base+"/api/outgoing-quality/"+identifier);assert status_http.status_code==200 and status_http.json()["final_scale_required"]and status_http.json()["case_task_id"]==case
  captures_http=qc_gateway.get(base+"/api/outgoing-quality/"+identifier+"/final-captures");assert captures_http.status_code==200 and captures_http.json()["use_by_capture"][check["capture_key"]]["operation_id"]==check["operation_id"]
  assert verified["final_scale_device_mode"]=="TEST"and verified["net_weight_kg"]=="0.3"
  replay=qc_gateway.post(base+final_path,json=check);assert replay.status_code==200 and replay.json()==verified
  q.execute("select count(*),max(STOCK_OPERATION_ID)from RRL_WH_FINAL_SCALE_USE where CAPTURE_KEY=:p_key",p_key=check["capture_key"]);assert q.fetchone()==(1,check["operation_id"])
  try:q.execute("delete from RRL_WH_FINAL_SCALE_USE where CAPTURE_KEY=:p_key",p_key=check["capture_key"]);raise AssertionError("Scale use deleted")
  except oracledb.DatabaseError as exc:c.rollback();assert exc.args[0].code==20863
  q.execute("update RUSERS set WARE_ID=6667491 where ID=:p_actor",p_actor=controller);c.commit()
  refused=qc_gateway.post(base+final_path,json=check);assert refused.status_code==403
  try:q.callproc("RRL_STOCK_POSTING_API.prepare_command",[StockCommand(operation_id=check["operation_id"],command_type="OUTGOING_PALLET_CHECK",actor=controller,source={"pallet_identifier":identifier},lines=(),metadata={"quality_kind":"WEIGHT","gross_weight":final_capture["weight_kg"],"wood_weight":final_capture["tare_weight_kg"],"final_scale_capture":check["capture_key"],"expected_composition_signature":check["expected_composition_signature"]}).canonical_json(),controller,result,None]);raise AssertionError("Foreign native QC replay admitted")
  except oracledb.DatabaseError as exc:c.rollback();assert exc.args[0].code==20882
  finally:q.callproc("RRL_STOCK_POSTING_API.reset_connection")
  q.execute("update RUSERS set WARE_ID=:p_ware where ID=:p_actor",p_ware=ware,p_actor=controller);c.commit()
  used=call("GET",scale_base+f"/final-captures?task={case}");assert used["use_by_capture"][check["capture_key"]]["operation_id"]==check["operation_id"]
  print("PASS212 native once-only final GROSS/current source/tare exactly once/independent actor/concurrent distinctOP1winner/replay/manual bypass refused/current WARE before saved replay/immutable use",check["operation_id"],flush=True)
  after=quality.status(identifier);assert after["ready"]and after["control_mode"]=="WEIGHT"
  q.execute("select TRIAL_WEIGHT,WOOD_WEIGHT from RRL_SBORKA_PALLETS where ID=:p_id",p_id=sid);gross,tare_weight=q.fetchone()
  assert Decimal(str(gross))==Decimal("0.400")and Decimal(str(tare_weight))==Decimal("0.100")
  signature=quality.status(identifier)["composition_signature"]
  packing("HU_ATTACH","SMALL212.CONTROLLED.PACK:"+tag)
  from app.modules.inventory.infrastructure.warehouse_hu import WarehouseHu
  warehouse_hus=WarehouseHu(OracleGateway())
  view=warehouse_hus.preview(parent,"admin")
  assert view["quantities"]==[{"article":article,"base_uom":"EA","quantity":"6"}]
  assert view["gross_weight_kg"]=="1.4"and view["unknown_tare_containers"]==0 and view["unknown_weight_leaves"]==0,view
  q.execute("select min(TRANSPORTTYPE)from RRL_TRANSPORT_TYPE");trtype=q.fetchone()[0]
  q.execute("select min(ID)from RRL_TR_VODITEL where ID>0");driver=q.fetchone()[0]
  plate="QV212"+tag;vehicle=int(q.callfunc("RRL_TR_VEHICLE_ADD",oracledb.DB_TYPE_NUMBER,[plate,trtype,100,1,0,None]));c.commit()
  trip=seq("RRL_TRANSPORT_TASK_SQ");dock="QD212"+tag;store="Own212 store "+tag
  meta("insert into RRL_TT_DOCK(DOCK,WARE_ID,DOCK_IS_BLOCKED)values(:p_dock,:p_ware,0)",p_dock=dock,p_ware=ware)
  meta("insert into RRL_TRANSPORT_TASK(ID,TRANSPORT,TRANSTYPE,CONDITION,SHIPMENT_DATE,VODITEL_ID,DOCK,DELETED)values(:p_id,:p_plate,:p_type,'Спланирован',trunc(sysdate),:p_driver,:p_dock,0)",p_id=trip,p_plate=plate,p_type=trtype,p_driver=driver,p_dock=dock)
  meta("update RRL_TR_VEHICLE set MAX_WEIGHT_KG=100,WORKING_NOW=1,BLOCKED=0 where ID=:p_id",p_id=vehicle)
  meta("update RRL_SBORKA_PALLETS set TRANSTASK_ID=:p_trip,ADDR=:p_store where ID=:p_id",p_trip=trip,p_store=store,p_id=sid)
  meta("insert into RRL_ADDR(ADDR)values(:p_addr)",p_addr=store)
  call("PUT","/api/delivery/store-receipts/policy",{"store_address":store,"mode":"WEIGHT_PHOTO","expected_version":0})
  packing("HU_DETACH","SMALL212.STANDALONE:"+tag)
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

 finally:
  if parent is not None and not shipped:
   q.execute("select CHILD_CASE_TASK_ID from RRL_WMS_HU_LINK where PARENT_UID=:p_uid and ACTIVE_FLAG=1",p_uid=parent)
   for (nested_case,)in q.fetchall():
    packing("HU_DETACH","SMALL212.CLEANUP.UNPACK:"+tag)
  if wave is not None and not shipped:
   q.execute("select CASE_PICK_TASK_ID,SSCC,CONTENT_VERSION from RRL_CASE_PICK_TASK where PICK_WAVE_ID=:p_wave",p_wave=wave)
   for case,carrier,version in q.fetchall():
    q.execute("select h.LOT_UID from RRL_CASE_CARRIER_LOT h join RRL_REMAINS r on r.UID_POLETA=h.LOT_UID where h.CASE_PICK_TASK_ID=:p_case and r.REMAIN>0",p_case=case)
    lots=[x[0]for x in q.fetchall()]
    post("CASE_CARRIER_RETURN",{"case_task_id":int(case)},{"scan_container":carrier,"expected_content_version":int(version),"allow_empty":not bool(lots),"destinations":{uid:receive for uid in lots},"reason":"Own212 native direct CASE return"})
   q.execute("select RESERVATION_ID from RRL_STOCK_RESERVATION where SOURCE_DOC_TYPE='PICK_WAVE'and SOURCE_DOC_ID=:p_wave and STATUS in('ACTIVE','ALLOCATED','PICKING')and BASE_QTY>0",p_wave=wave)
   for(rid,)in q.fetchall():post("RESERVATION_RELEASE",{"reservation_id":int(rid)},{"reason":"Own212 release"})
  for book in ([] if shipped else bookings):call("POST","/api/inventory/tare/book-cancel",{"operation_id":"DIRECT212.BOOK.CANCEL:"+book,"booking_operation_id":book})
  for case_type in ([] if shipped else case_types):
   available=call("GET",f"/api/inventory/tare/warehouses/{ware}/availability");current=next(x for x in available if x["pallet_type_id"]==case_type)
   call("POST","/api/inventory/tare/count",{"operation_id":"SMALL212.TARE.ZERO:"+str(ware),"owner_ware_id":ware,"pallet_type_id":case_type,"condition":"GOOD","observed_quantity":"0","expected_version":current["balance_version"]or 0,"reason":"Retire own empty software box","decision_reference":"SMALL212.END:"+tag})
  if wave is not None and not shipped:
   q.execute("select STATUS from RRL_PICK_WAVE where PICK_WAVE_ID=:p_wave",p_wave=wave)
   if q.fetchone()[0]=="LAUNCHED":post("WAVE_EXECUTION_FINISH",{"wave_id":wave},{"disposition":None if shipped else "RETURNED_TO_PLANNING","reason":"Own212 current physical shipment" if shipped else "Own212 returned demands remain"})
   else:post("WAVE_CANCEL",{"document_type":"PICK_WAVE","document_id":wave},{"reason":"Own212 unlaunched cleanup"})
  elif wave is None:
   for plan in plans:picking.cancel_plan(plan,"admin")
  if born:
   from app.modules.inventory.infrastructure.receiving import Receiving
   Receiving(OracleGateway()).cancel(task,"Owned212 fixture cleanup","admin")
   q.execute("select r.UID_POLETA,r.CELL,r.BASE_UOM,r.STOCK_VERSION from RRL_REMAINS r join RRL_PALLETS p on p.UID_PALLET=r.UID_POLETA where p.ARTICUL=:p_a and r.REMAIN>0",p_a=article)
   counts=[{"uid":uid,"cell":cell,"article":article,"unit":unit,"quantity":"0","expected_stock_version":int(v),"unit_keys":[]}for uid,cell,unit,v in q.fetchall()]
   if counts:post("INVENTORY_COUNT",{"revision_id":revision},{"reason":"Own212 native cleanup","counts":counts})
  q.execute("select nvl(sum(r.REMAIN),0),nvl(sum(r.HARD_RESERVED_BASE),0)from RRL_REMAINS r join RRL_CELLS c on c.CELL=r.CELL where c.WARE_ID=:p_ware",p_ware=ware);assert q.fetchone()==(0,0)
  q.execute("select sum(r.REMAIN),sum(r.HARD_RESERVED_BASE)from RRL_REMAINS r join RRL_CELLS c on c.CELL=r.CELL where c.WARE_ID=6667491");assert q.fetchone()==(20,20)
  if "unloader"in locals():q.execute("update RUSERS set DELETED=1 where ID=:p_actor",p_actor=unloader);c.commit()
  if controller is not None:q.execute("update RUSERS set DELETED=1 where ID=:p_actor",p_actor=controller);c.commit()
  if sender is not None:q.execute("update RUSERS set DELETED=1 where ID=:sender",sender=sender);c.commit()
  print("Own212 native return/release/count completed; original135 P20H20 unchanged",flush=True)

