"""175 fresh native CASE12+8, unpack and same-cell CASE slot relocation; no fake terminal cleanup."""
import json,sys,httpx
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from uuid import uuid4
import oracledb
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment()
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"api/wms_api_server"))
from app.config import get_settings
from app.oracle_gateway import OracleGateway
from app.services.picking_service import PickingService
from app.schemas import PickingPlanCreateRequest,PickWaveCreateRequest,PickWaveAddPlanRequest,PickWaveActionRequest
from app.modules.fulfillment.infrastructure.execution_progress import OrderExecution
qc_actor="admin";cfg=get_settings();tag=uuid4().hex[:10];lot="FULL.QA:"+tag;other=lot+"O";src="QF"+tag;dst="QG"+tag;st_uid="FULL.ST:"+tag
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
  actor=qc_actor if kind=="OUTGOING_PALLET_CHECK" else "admin"
  command={"contract_version":2,"operation_id":op or "FULL.QA:"+uuid4().hex,"command_type":kind,"actor":actor,"source":source,"lines":[],"units":[],"metadata":body}
  inp,out=q.var(oracledb.DB_TYPE_CLOB),q.var(oracledb.DB_TYPE_CLOB);inp.setvalue(0,json.dumps(command))
  try:
   q.callproc("RRL_STOCK_POSTING_API.prepare_command",[inp,actor,out,None])
   if out.getvalue() is None:q.callproc("RRL_STOCK_POSTING_API.execute_prepared",[out])
   result=out.getvalue();conn.commit();return json.loads(result.read() if hasattr(result,"read") else result)
  except BaseException:conn.rollback();raise
  finally:q.callproc("RRL_STOCK_POSTING_API.reset_connection")
 q.execute("select user,sys_context('USERENV','SERVICE_NAME') from dual");assert q.fetchone()==("RABAEV","orcl")

 q.execute("select ARTICUL from RRL_PALLETS where UID_PALLET='DS-BASE-B1'");base_article=q.fetchone()[0]
 article="QNATIVE"+tag.upper()
 meta("declare r RRL_ARTICULS%rowtype;begin select * into r from RRL_ARTICULS where ACTICUL=:old;r.ACTICUL:=:a;r.BARCODE_SHT:=:bc;r.ABC_GROUP:='A';insert into RRL_ARTICULS values r;end;",old=base_article,a=article,bc="QN"+tag)
 meta("insert into RRL_STOCK_UOM_CONVERSION(ARTICUL,INPUT_UOM,BASE_UOM,POLICY_VERSION,NUMERATOR,DENOMINATOR,BASE_SCALE,PROVENANCE) select :a,INPUT_UOM,BASE_UOM,POLICY_VERSION,NUMERATOR,DENOMINATOR,BASE_SCALE,'Native wave fixture' from RRL_STOCK_UOM_CONVERSION where ARTICUL=:old",a=article,old=base_article)
 meta("insert into RRL_STOCK_POLICY_GUARD(POLICY_KEY,LOCK_ID) select RRL_STOCK_LOCK_API.resource_key('SKU',:a),nvl(max(LOCK_ID),900000000)+1 from RRL_STOCK_POLICY_GUARD",a=article)
 q.execute("select min(CUSTOMER_ID) from RRL_CUSTOMER");customer=q.fetchone()[0]
 ware=100000+int(tag[:6],16)
 meta("insert into RRL_WARES(ID,NAME,PREFIX,SPIS_OTBOR_ON_SCAN_OPALL) values(:ware,:n,:p,1)",n="Own CASE QC "+tag,p="Q"+tag[:2])
 meta("insert into RRL_RECEIPT_WARE_SETTINGS(WARE_ID,OUTGOING_QC_MODE,OUTGOING_QC_INDEPENDENT) values(:ware,'BOTH',1)")
 for cell in (src,dst,"CPT_"+str(ware)):
  meta("insert into RRL_CELLS(CELL,WARE_ID,X,Y,Z,OTBOR,IS_SYSTEM) values(:c,:ware,0,0,0,:pick,:sys)",c=cell,pick=int(cell==dst),sys=int(cell.startswith("CPT_")))
  meta("insert into RRL_STOCK_POLICY_GUARD(POLICY_KEY,LOCK_ID) select RRL_STOCK_LOCK_API.resource_key('CELL',:c),nvl(max(LOCK_ID),900000000)+1 from RRL_STOCK_POLICY_GUARD",c=cell)
 face=seq("RRL_PICK_FACE_SQ")
 meta("insert into RRL_PICK_FACE(PICK_FACE_ID,WARE_ID,CELL_CODE,MAX_VOLUME,CREATED_BY) values(:id,:ware,:c,0.2,'admin')",id=face,c=dst)
 meta("insert into RRL_PICK_FACE_ARTICUL(PICK_FACE_ARTICUL_ID,PICK_FACE_ID,ARTICUL,BOX_VOLUME_M3,USE_ARTICUL_REPLENISH_RULE,REPLENISHMENT_QTY_MODE) values(RRL_PICK_FACE_ARTICUL_SQ.nextval,:id,:a,0.24,0,'FULL_PALLET')",id=face,a=article)
 revision=int(q.callfunc("REVIZION.create_revizion",oracledb.DB_TYPE_NUMBER,[ware,"admin"]));conn.commit()
 orders=[];plans=[];wave=None;service=PickingService();bookings=[];tare_types=set()
 try:
  post("INVENTORY_REGISTER_LOT",{"uid":lot,"cell":src,"article":article,"quantity":"20","expiry_date":"2030-01-01","price":0,"reason":"Native complete warehouse flow"},{"revision_id":revision})
  for qty in (12,8):
   order=seq("RRL_CUSTOMER_ORDER_SQ");orders.append(order)
   meta("insert into RRL_CUSTOMER_ORDER(CUSTOMER_ORDER_ID,ORDER_NO,CUSTOMER_ID,WARE_ID) values(:id,:no,:c,:ware)",id=order,no=lot+str(qty),c=customer)
   meta("insert into RRL_CUSTOMER_ORDER_ROW(CUSTOMER_ORDER_ROW_ID,CUSTOMER_ORDER_ID,LINE_NO,ARTICUL,ORDER_QTY,UNIT_CODE) values(RRL_CUSTOMER_ORDER_ROW_SQ.nextval,:o,1,:a,:qty,'EA')",o=order,a=article,qty=qty)
   plan=service.create_plan(PickingPlanCreateRequest(customer_order_id=order,created_by="admin"));plans.append(plan)
   q.execute("select TASK_TYPE,QTY,TARGET_CELL_CODE from RRL_PICK_TASK where PICK_PLAN_ID=:p",p=plan)
   assert q.fetchone()==("CASE_PICK",qty,dst),"Free portion of a shared physical pallet classified FULL"
  wave=service.create_wave(PickWaveCreateRequest(wave_code=lot,ware_id=ware,created_by="admin"))
  for plan in plans:service.add_wave_plan(wave,PickWaveAddPlanRequest(pick_plan_id=plan,created_by="admin"))
  service.preview_wave(wave,PickWaveActionRequest(updated_by="admin"))
  launch=PickWaveActionRequest(updated_by="admin",operation_id="NATIVE.LAUNCH:"+tag)
  service.launch_wave(wave,launch)
  q.execute("select sum(BASE_QTY) from RRL_STOCK_RESERVATION where SOURCE_DOC_TYPE='PICK_WAVE' and SOURCE_DOC_ID=:w and RESERVATION_DOMAIN='PICKING' and STATUS='ACTIVE'",w=wave);assert q.fetchone()==(20,)
  q.execute("select TASK_ID,UID_PALLET,FROM_CELL,TO_CELL,QTY from RRL_WAREHOUSE_TASK where TASK_SOURCE='WAVE' and SOURCE_DOC_ID=:w and TASK_TYPE='REPLENISHMENT' and STATUS not in('DONE','CANCELLED')",w=wave)
  tasks=q.fetchall();assert len(tasks)==1,tasks
  task,uid,from_cell,to_cell,qty=tasks[0];assert qty==20
  q.execute("select PICK_TASK_ID from RRL_PICK_TASK where PICK_PLAN_ID=:p",p=plans[1]);other_pick=int(q.fetchone()[0])
  meta("update RRL_PICK_TASK set TARGET_CELL_CODE=:c where PICK_TASK_ID=:p",c=src,p=other_pick)
  try:
   post("TASK_COMPLETE",{"fact_qty":"20","scanned_pallet":uid,"scanned_from_cell":from_cell,"scanned_to_cell":to_cell},{"task_id":int(task)})
   raise AssertionError("Shared pallet moved another owner's stock to a different picking destination")
  except oracledb.DatabaseError as exc:
   assert "WHOLE_REPLENISHMENT_OTHER_DESTINATION_OR_OWNER" in str(exc),str(exc)
  q.execute("select REMAIN,HARD_RESERVED_BASE from RRL_REMAINS where UID_POLETA=:u and CELL=:c",u=lot,c=src)
  assert q.fetchone()==(20,20)
  meta("update RRL_PICK_TASK set TARGET_CELL_CODE=:c where PICK_TASK_ID=:p",c=dst,p=other_pick)
  post("TASK_COMPLETE",{"fact_qty":"20","scanned_pallet":uid,"scanned_from_cell":from_cell,"scanned_to_cell":to_cell},{"task_id":int(task)})
  q.execute("select REMAIN,HARD_RESERVED_BASE from RRL_REMAINS where UID_POLETA=:u and CELL=:c",u=lot,c=dst);assert q.fetchone()==(20,20)
  released=post("WAVE_PICK_RELEASE",{},{"wave_id":wave})
  assert released["released_at"] is not None
  q.execute("select ct.CASE_PICK_TASK_ID,cl.CASE_PICK_LINE_ID,ct.SSCC,cl.PLANNED_QTY,cl.CELL_CODE from RRL_CASE_PICK_TASK ct join RRL_CASE_PICK_LINE cl on cl.CASE_PICK_TASK_ID=ct.CASE_PICK_TASK_ID where ct.PICK_WAVE_ID=:w order by ct.CUSTOMER_ORDER_ID",w=wave)
  lines=q.fetchall();assert len(lines)==2,lines
  from app.services.case_pick_service import CasePickService
  from app.schemas import CasePickTaskActionRequest
  cases=CasePickService()
  api175=httpx.Client(auth=("admin","admin123"),timeout=60)
  def tare_call(path,body):
   response=api175.post("http://127.0.0.1:8088/api/inventory/tare/"+path,json=body)
   assert response.status_code==200,(response.status_code,response.text[:1800]);return response.json()
  def tare_count(tare_type,quantity):
   response=api175.get(f"http://127.0.0.1:8088/api/inventory/tare/warehouses/{ware}/availability")
   assert response.status_code==200
   current=next(x for x in response.json()if x["pallet_type_id"]==tare_type)
   operation="QA175.TARE:"+uuid4().hex
   tare_call("count",{"operation_id":operation,"owner_ware_id":ware,"pallet_type_id":tare_type,"condition":"GOOD","observed_quantity":quantity,"expected_version":current["balance_version"]or 0,"reason":"Owned175 synthetic assembly container fixture","decision_reference":operation})
  for ct,cl,carrier,qty,cell in lines:
   q.execute("select PALLET_TYPE_ID from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=:p_id",p_id=int(ct));tare_type=q.fetchone()[0]
   if tare_type not in tare_types:tare_count(tare_type,"2");tare_types.add(tare_type)
   booking="QA175.TARE.BOOK:"+str(ct)
   tare_call("book",{"operation_id":booking,"place_kind":"CASE","place_id":str(ct)});bookings.append(booking)
   cases.claim_task(int(ct),CasePickTaskActionRequest(actor="admin"))
   cases.start_task(int(ct),CasePickTaskActionRequest(actor="admin"))
   op="NATIVE.CASE:"+tag+":"+str(ct)
   body={"fact_qty":str(int(qty)),"scan_cell":cell,"scan_container":carrier,"scan_product":article,"offline_event_id":op}
   result=post("CASE_PICK_CONFIRM",body,{"case_task_id":int(ct),"case_line_id":int(cl)},op)
   assert post("CASE_PICK_CONFIRM",body,{"case_task_id":int(ct),"case_line_id":int(cl)},op)==result
   cases.close_task(int(ct),CasePickTaskActionRequest(actor="admin"))

  from app.modules.inventory.infrastructure.case_shipment_binding import bind_case_shipment
  shipments={}
  for order,(ct,cl,carrier,qty,cell) in zip(orders,lines):
   sid=seq("RRL_SBORKA_PALLETS_SQ");ff=seq("RRL_CUSTOMER_ORDER_FULF_SQ");identifier="CASE.QC.ST:"+tag+":"+str(ct)
   meta("insert into RRL_SBORKA_PALLETS(ID,PALLET_UID,ST_NUMBER,WARE_ID,CONDITION,ADDR) values(:sid,:u,:u,:ware,0,'Own existing CASE QC ST')",sid=sid,u=identifier)
   meta("insert into RRL_SBORKA_PALLET_ROWS(ID,PALLET_UID,ARTICUL,EI,QUANTITY) values(RRL_SBORKA_PALLET_ROWS_SQ.nextval,:u,:a,'EA',:qty)",u=identifier,a=article,qty=qty)
   meta("insert into RRL_CUSTOMER_ORDER_FULFILLMENT(FULFILLMENT_ID,CUSTOMER_ORDER_ID,LEGACY_SBORKA_PALLET_ID,PALLET_UID,STATUS,FACT_QTY) values(:ff,:o,:sid,:u,'PLANNED',0)",ff=ff,o=order,sid=sid,u=identifier)
   q.execute("select CONTENT_VERSION from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=:id",id=ct);version=q.fetchone()[0]
   bind_case_shipment(OracleGateway(),int(ct),identifier,carrier,int(version),"admin");shipments[int(ct)]=identifier
  meta("insert into RRL_RECEIPT_SKU_RULE(WARE_ID,ARTICUL,PICK_CELL,QC_BASE_WEIGHT_KG,QC_BOX_WEIGHT_KG,QC_WEIGHT_BASE_UOM,QC_WEIGHT_VERSION) values(:ware,:a,:c,1,10,'EA',1)",a=article,c=dst)
  controller="QCC"+tag;group="QCG"+tag
  meta("insert into USER_GROUP(ID,NAME) values(:g,'Own CASE QC role')",g=group)
  meta("insert into RUSERS(ID,NAME,PASS,USER_GROUP,DELETED) values(:u,'Own CASE controller','qa-test-only',:g,0)",u=controller,g=group)
  meta("insert into RIGHTS(ID,RIGHT1,USER_GROUP,DESCR) select nvl(max(ID),0)+1,'outgoing_pallet_check',:g,'Own CASE QC role' from RIGHTS",g=group)
  qc_actor=controller
  parent="HU.CASE:"+tag;hu_dst="QH"+tag;case_transit="CPT_"+str(ware);case_stage="QI"+tag
  for cell,system in ((hu_dst,0),(case_stage,1)):
   meta("insert into RRL_CELLS(CELL,WARE_ID,X,Y,Z,OTBOR,IS_SYSTEM,LIMIT_WEIGHT,LIMIT_HEIGHT) values(:c,:ware,0,0,0,0,:system,0,0)",c=cell,system=system)
   meta("insert into RRL_STOCK_POLICY_GUARD(POLICY_KEY,LOCK_ID) select RRL_STOCK_LOCK_API.resource_key('CELL',:c),nvl(max(LOCK_ID),900000000)+1 from RRL_STOCK_POLICY_GUARD",c=cell)
  post("HU_CREATE",{"cell":case_transit,"warehouse":ware,"container_type":"ROLL_CAGE","tare_weight_kg":1,"scan_container":parent,"scan_cell":case_transit},{"uid":parent})
  def hu_tree():
   q.execute("select RRL_STOCK_HU_READ.snapshot_json(:u) from dual",u=parent);raw=q.fetchone()[0];return json.loads(raw.read() if hasattr(raw,"read") else raw)
  for ct,cl,carrier,qty,cell in lines:
   q.execute("select CONTENT_VERSION from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=:id",id=int(ct));version=int(q.fetchone()[0])
   post("HU_ATTACH",{"retained_tare_booking_operation_id":"QA175.TARE.BOOK:"+str(ct),"child_case_task_id":int(ct),"expected_version":hu_tree()["nodes"][0]["version"],"expected_child_version":version,"scan_container":parent,"scan_child":carrier},{"uid":parent})
  topo=seq("RRL_WH_TOPOLOGY_SQ");tc=seq("RRL_TOPOLOGY_CELL_SQ");slots=[]
  meta("insert into RRL_WAREHOUSE_TOPOLOGY(TOPOLOGY_ID,WARE_ID,TOPOLOGY_CODE,STATUS) values(:id,:ware,:code,'PUBLISHED')",id=topo,code=parent)
  meta("insert into RRL_TOPOLOGY_CELL(TOPOLOGY_CELL_ID,TOPOLOGY_ID,WARE_ID,CELL_CODE,LEGACY_CELL_CODE,SLOT_LAYER_KIND,MAX_WEIGHT_KG,MAX_VOLUME_M3) values(:id,:t,:ware,:c,:c,'STORAGE_SLOT',100,4)",id=tc,t=topo,c=hu_dst)
  for index in range(3):
   sid=seq("RRL_TOPO_CELL_SLOT_SQ");code="CASE:"+tag+":"+str(index)
   meta("insert into RRL_TOPOLOGY_CELL_SLOT(CELL_SLOT_ID,TOPOLOGY_ID,TOPOLOGY_CELL_ID,PARENT_SLOT_LAYER_KIND,SLOT_KIND,SLOT_CODE,CAPACITY_QTY,CAPACITY_WEIGHT_KG,CAPACITY_VOLUME_M3,WIDTH_M,DEPTH_M,HEIGHT_M,SUB_COLUMN_NO) values(:id,:t,:c,'STORAGE_SLOT','STORAGE_SLOT',:code,1,100,3,1.2,1.2,2,:i)",id=sid,t=topo,c=tc,code=code,i=index)
   slots.append((sid,code))
  def measures(version,mass):
   return {"origin":"MANUAL_CONFIRMED","content_version":version,"gross_weight_kg":str(mass),"width_m":"0.5","depth_m":"1","height_m":"1.5"}
  move={"expected_version":hu_tree()["nodes"][0]["version"],"target_cell":hu_dst,"target_slot_id":slots[0][0],"measurements":measures(hu_tree()["nodes"][0]["version"],30),"scan_container":parent,"scanned_from_cell":case_transit,"scanned_to_cell":hu_dst}
  planned=post("HU_PLAN_MOVE",move,{"uid":parent});task=int(planned["task_id"])
  from app.services.warehouse_task_service import WarehouseTaskService
  from app.schemas import WarehouseTaskStatusRequest
  service=WarehouseTaskService();service.assign_task(task,WarehouseTaskStatusRequest(updated_by="admin",assigned_to="admin"));service.start_task(task,WarehouseTaskStatusRequest(updated_by="admin"))
  service.complete_task(task,WarehouseTaskStatusRequest(operation_id="CASE.PLACE:"+tag,updated_by="admin",fact_qty="1",scanned_pallet=parent,scanned_from_cell=case_transit,scanned_to_cell=hu_dst,scanned_to_slot_code=slots[0][1]),"admin")
  ct,cl,carrier,qty,cell=lines[0];ct=int(ct)
  q.execute("select CONTENT_VERSION from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=:id",id=ct);version=int(q.fetchone()[0])
  split={"child_case_task_id":ct,"expected_version":hu_tree()["nodes"][0]["version"],"expected_child_version":version,"scan_container":parent,"scan_child":carrier,"scan_cell":hu_dst,"scan_parent_slot":slots[0][1],"scan_child_slot":slots[1][1],"child_slot_id":slots[1][0],"reason":"Own CASE separate physical slot","parent_measurements":measures(hu_tree()["nodes"][0]["version"],15),"child_measurements":measures(version,15)}
  op="CASE.SLOT.UNPACK:"+tag;r=post("HU_UNPACK",split,{"uid":parent},op);assert post("HU_UNPACK",split,{"uid":parent},op)==r
  assert r["child"]["case_task_id"]==ct and r["child"]["top_place_count"]==1 and r["parent"]["leaf_count"]==1
  q.execute("select UID_PALLET,HU_CASE_TASK_ID,CELL_SLOT_ID,HU_COMPOSITION_VERSION from RRL_RECEIPT_SLOT_CLAIM where HU_CASE_TASK_ID=:id",id=ct);assert q.fetchone()==("CASE:"+str(ct),ct,slots[1][0],version+1)
  q.execute("select count(*) from RRL_PALLETS where UID_PALLET=:u",u="CASE:"+str(ct));assert q.fetchone()==(0,)
  q.execute("select sum(REMAIN),sum(HARD_RESERVED_BASE) from RRL_REMAINS where CELL=:c",c=hu_dst);assert q.fetchone()==(20,20)
  q.execute("select count(*) from RRL_EVENTS where OPERATION_ID=:op",op=op);assert q.fetchone()==(0,)
  q.execute("select count(*),sum(HU_GROSS_WEIGHT_KG) from RRL_RECEIPT_SLOT_CLAIM where CELL=:c",c=hu_dst);assert q.fetchone()==(2,30)
  q.execute("select CONTENT_VERSION from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=:p_id",p_id=ct);relversion=int(q.fetchone()[0])
  relocation={"case_task_id":ct,"expected_version":relversion,"target_slot_id":slots[2][0],"scan_container":carrier,"scan_cell":hu_dst,"scan_from_slot":slots[1][1],"scan_to_slot":slots[2][1],"measurements":measures(relversion,15),"reason":"Owned175 physical CASE slot relocation"}
  op175="CASE.RELOCATE175:"+tag
  command={"contract_version":2,"operation_id":op175+".ROLLBACK","command_type":"HU_RELOCATE_SLOT","actor":"admin","source":{"uid":"CASE:"+str(ct)},"lines":[],"units":[],"metadata":relocation}
  inp,out=q.var(oracledb.DB_TYPE_CLOB),q.var(oracledb.DB_TYPE_CLOB);inp.setvalue(0,json.dumps(command))
  try:
   q.callproc("RRL_STOCK_POSTING_API.prepare_command",[inp,"admin",out,None]);q.callproc("RRL_STOCK_POSTING_API.execute_prepared",[out])
   q.execute("select CELL_SLOT_ID from RRL_RECEIPT_SLOT_CLAIM where HU_CASE_TASK_ID=:p_id",p_id=ct);assert q.fetchone()==(slots[2][0],)
  finally:conn.rollback();q.callproc("RRL_STOCK_POSTING_API.reset_connection")
  q.execute("select CELL_SLOT_ID,HU_COMPOSITION_VERSION from RRL_RECEIPT_SLOT_CLAIM where HU_CASE_TASK_ID=:p_id",p_id=ct);assert q.fetchone()==(slots[1][0],relversion)
  q.execute("select count(*)from RRL_STOCK_OPERATION where OPERATION_ID=:p_op",p_op=command["operation_id"]);assert q.fetchone()==(0,)
  body175={"operation_id":op175,"identifier":"CASE:"+str(ct),**relocation}
  url175="http://127.0.0.1:8088/api/warehouse-hus/relocate-slot"
  with httpx.Client(auth=("admin","admin123"),timeout=60)as client:
   denied=client.post(url175,json={**body175,"operation_id":op175+".BADSCAN","scan_from_slot":"Wrong175"})
   assert denied.status_code==409,(denied.status_code,denied.text[:1800])
  def relocate():
   with httpx.Client(auth=("admin","admin123"),timeout=60)as client:
    response=client.post(url175,json=body175);assert response.status_code==200,(response.status_code,response.text[:1800]);return response.json()
  with ThreadPoolExecutor(max_workers=2)as pool:replies=list(pool.map(lambda _:relocate(),range(2)))
  assert replies[0]==replies[1]and replies[0]["quantity_unchanged"]
  q.execute("select CELL_SLOT_ID,HU_COMPOSITION_VERSION from RRL_RECEIPT_SLOT_CLAIM where HU_CASE_TASK_ID=:p_id",p_id=ct);assert q.fetchone()==(slots[2][0],relversion+1)
  q.execute("select sum(REMAIN),sum(HARD_RESERVED_BASE)from RRL_REMAINS where CELL=:p_cell",p_cell=hu_dst);assert q.fetchone()==(20,20)
  q.execute("select count(*),sum(HU_GROSS_WEIGHT_KG)from RRL_RECEIPT_SLOT_CLAIM where CELL=:p_cell",p_cell=hu_dst);assert q.fetchone()==(2,30)
  q.execute("select count(*)from RRL_EVENTS where OPERATION_ID=:p_op",p_op=op175);assert q.fetchone()==(0,)
  with httpx.Client(auth=("admin","admin123"),timeout=60)as client:
   assert client.post(url175,json={**body175,"reason":"Other physical decision"}).status_code==409
  version=relversion
  print("PASS175 CASE12 slot1->slot2/native rollback/concurrent same receipt once/badscan409/changed409/P20H20/no quantity journal/two claims30kg",flush=True)
  move_case={"target_cell":case_stage,"expected_content_version":version+1,"scan_container":carrier,"scanned_to_cell":case_stage}
  op="CASE.SLOT.MOVE:"+tag;moved=post("CASE_CARRIER_MOVE",move_case,{"case_task_id":ct},op);assert post("CASE_CARRIER_MOVE",move_case,{"case_task_id":ct},op)==moved
  q.execute("select count(*) from RRL_RECEIPT_SLOT_CLAIM where HU_CASE_TASK_ID=:id",id=ct);assert q.fetchone()==(0,)
  q.execute("select sum(r.REMAIN),sum(r.HARD_RESERVED_BASE) from RRL_REMAINS r join RRL_CASE_CARRIER_LOT l on l.LOT_UID=r.UID_POLETA where l.CASE_PICK_TASK_ID=:id and r.CELL=:c",id=ct,c=case_stage);assert q.fetchone()==(12,12)
  print("PASS native CASE12+8 top task placement -> direct CASE12 slot unpack/two measured claims P20/H20 unchanged/no fake PP/no quantity journal/replay -> existing CASE move P12/H12 frees slot",flush=True)

 finally:
  if wave is not None:
   if "parent" in locals():
    q.execute("select count(*) from RRL_RECEIPT_SLOT_CLAIM where UID_PALLET=:u",u=parent)
    if q.fetchone()[0]:
     cleanup="QCL"+tag
     meta("insert into RRL_CELLS(CELL,WARE_ID,X,Y,Z,OTBOR,IS_SYSTEM,LIMIT_WEIGHT,LIMIT_HEIGHT) values(:c,:ware,0,0,0,0,0,0,0)",c=cleanup)
     meta("insert into RRL_STOCK_POLICY_GUARD(POLICY_KEY,LOCK_ID) select RRL_STOCK_LOCK_API.resource_key('CELL',:c),nvl(max(LOCK_ID),900000000)+1 from RRL_STOCK_POLICY_GUARD",c=cleanup)
     post("HU_MOVE",{"expected_version":hu_tree()["nodes"][0]["version"],"target_cell":cleanup,"scan_container":parent,"scanned_from_cell":hu_tree()["cell"],"scanned_to_cell":cleanup},{"uid":parent})
    q.execute("select CHILD_CASE_TASK_ID from RRL_WMS_HU_LINK where PARENT_UID=:u and ACTIVE_FLAG=1",u=parent)
    for (caseid,) in q.fetchall():
     q.execute("select CONTENT_VERSION,SSCC from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=:id",id=int(caseid));version,carrier=q.fetchone()
     post("HU_DETACH",{"child_case_task_id":int(caseid),"expected_version":hu_tree()["nodes"][0]["version"],"expected_child_version":int(version),"scan_container":parent,"scan_child":carrier,"reason":"Private cleanup after failed case"},{"uid":parent})
   q.execute("select CASE_PICK_TASK_ID,SSCC,CONTENT_VERSION from RRL_CASE_PICK_TASK where PICK_WAVE_ID=:w",w=wave)
   for ct,carrier,version in q.fetchall():
    q.execute("select LOT_UID from RRL_CASE_CARRIER_LOT where CASE_PICK_TASK_ID=:id",id=ct);lots=[r[0] for r in q.fetchall()]
    if lots:post("CASE_CARRIER_RETURN",{"destinations":{u:dst for u in lots},"scan_container":carrier,"expected_content_version":int(version),"reason":"End native wave fixture"},{"case_task_id":int(ct)})
   q.execute("select RESERVATION_ID from RRL_STOCK_RESERVATION where SOURCE_DOC_TYPE='PICK_WAVE' and SOURCE_DOC_ID=:w and STATUS in('ACTIVE','ALLOCATED','PICKING') and BASE_QTY>0",w=wave)
   for (rid,) in q.fetchall():post("RESERVATION_RELEASE",{"reason":"End native fixture"},{"reservation_id":int(rid)})
   # Pending tasks remain for their existing native owner.
   # No raw cancellation of physical tasks.
   for booking in bookings:
    tare_call("book-cancel",{"operation_id":booking+".CANCEL","booking_operation_id":booking})
   for tare_type in tare_types:tare_count(tare_type,"0")
   if bookings:
    post("WAVE_EXECUTION_FINISH",{"disposition":"RETURNED_TO_PLANNING","reason":"Owned175 CASE returned, booked tare released; original demand retained"},{"wave_id":wave},"QA175.WAVE.DEFER:"+str(wave))
   print("Owned wave completed only by native deferred decision when eligible",wave,flush=True)
  q.execute("select s.UID_POLETA,s.CELL,s.BASE_UOM,s.STOCK_VERSION from RRL_REMAINS s join RRL_PALLETS p on p.UID_PALLET=s.UID_POLETA where p.ARTICUL=:a and s.REMAIN>0",a=article)
  counts=[{"uid":u,"cell":cell,"article":article,"unit":unit,"quantity":"0","expected_stock_version":int(version),"unit_keys":[]} for u,cell,unit,version in q.fetchall()]
  if counts:post("INVENTORY_COUNT",{"reason":"End private native warehouse case","counts":counts},{"revision_id":revision})
  # Native CASE return/reservation owner performs reservation release.
  if "controller" in locals():meta("update RUSERS set DELETED=1 where ID=:u",u=controller)
  print("Own P/H restored; native document and movement evidence retained",flush=True)
