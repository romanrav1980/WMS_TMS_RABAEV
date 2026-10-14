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
 orders=[];plans=[];wave=None;service=PickingService()
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
  for ct,cl,carrier,qty,cell in lines:
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
  parent="HU.CASE:"+tag;hu_dst="QH"+tag;case_transit="CPT_"+str(ware)
  meta("insert into RRL_CELLS(CELL,WARE_ID,X,Y,Z,OTBOR,IS_SYSTEM,LIMIT_WEIGHT,LIMIT_HEIGHT) values(:c,:ware,0,0,0,0,0,0,0)",c=hu_dst)
  meta("insert into RRL_STOCK_POLICY_GUARD(POLICY_KEY,LOCK_ID) select RRL_STOCK_LOCK_API.resource_key('CELL',:c),nvl(max(LOCK_ID),900000000)+1 from RRL_STOCK_POLICY_GUARD",c=hu_dst)
  post("HU_CREATE",{"cell":case_transit,"warehouse":ware,"container_type":"ROLL_CAGE","tare_weight_kg":1,"scan_container":parent,"scan_cell":case_transit},{"uid":parent})
  def hu_tree():
   q.execute("select RRL_STOCK_HU_READ.snapshot_json(:u) from dual",u=parent);raw=q.fetchone()[0];return json.loads(raw.read() if hasattr(raw,"read") else raw)
  for ct,cl,carrier,qty,cell in lines:
   q.execute("select CONTENT_VERSION from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=:id",id=int(ct));version=int(q.fetchone()[0])
   body={"child_case_task_id":int(ct),"expected_version":hu_tree()["nodes"][0]["version"],"expected_child_version":version,"scan_container":parent,"scan_child":carrier}
   op="HU.CASE.PACK:"+tag+":"+str(ct);packed=post("HU_ATTACH",body,{"uid":parent},op);assert post("HU_ATTACH",body,{"uid":parent},op)==packed
  state=hu_tree();assert state["leaf_count"]==2 and state["top_place_count"]==1 and len(state["nodes"])==5
  meta("update RRL_CELLS set IS_SYSTEM=1 where CELL=:c",c=hu_dst)
  for ct,cl,carrier,qty,cell in lines:
   q.execute("select CONTENT_VERSION from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=:id",id=int(ct));version=int(q.fetchone()[0])
   try:post("CASE_CARRIER_MOVE",{"target_cell":hu_dst,"expected_content_version":version,"scan_container":carrier,"scanned_to_cell":hu_dst},{"case_task_id":int(ct)});raise AssertionError("Nested CASE moved alone")
   except oracledb.DatabaseError as exc:assert "NESTED_HU_REQUIRES_TOP_MOVE_OR_EXPLICIT_UNPACK" in str(exc),str(exc)
  move={"expected_version":state["nodes"][0]["version"],"target_cell":hu_dst,"scan_container":parent,"scanned_from_cell":case_transit,"scanned_to_cell":hu_dst}
  op="HU.CASE.MOVE:"+tag;moved=post("HU_MOVE",move,{"uid":parent},op);assert post("HU_MOVE",move,{"uid":parent},op)==moved
  assert moved["cell"]==hu_dst and moved["leaf_count"]==2
  from app.modules.inventory.infrastructure.warehouse_hu import WarehouseHu
  hus=WarehouseHu(OracleGateway());api_view=hus.preview(parent,"admin")
  assert api_view["quantities"]==[{"article":article,"base_uom":"EA","quantity":"20"}]
  assert api_view["gross_weight_kg"] is None and api_view["unknown_tare_containers"]==2
  case_view=hus.preview(lines[0][2]);assert case_view["case_task_id"]==int(lines[0][0]) and case_view["top_place_count"]==0
  assert case_view["quantities"][0]["quantity"]=="12"

  from app.modules.inventory.infrastructure.outgoing_quality import OutgoingQuality
  admission=OutgoingQuality(OracleGateway())
  for ct,cl,carrier,qty,cell in lines:
   identifier=shipments[int(ct)];status=admission.status(identifier);assert status["case_status"]=="WAIT_CONTROL"
   version_before=int(status.get("document_id"))
   plan_body={"quality_kind":"PLAN","expected_composition_signature":status["composition_signature"]}
   plan_op="CASE.QC.PLAN:"+tag+":"+str(ct)
   planned=post("OUTGOING_PALLET_CHECK",plan_body,{"pallet_identifier":identifier},plan_op);assert planned["plan_assigned"]
   q.execute("select STATUS,CONTENT_VERSION from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=:id",id=ct);state_before,version=q.fetchone();assert state_before=="CONTROL_IN_PROGRESS"
   scan={"quality_kind":"SCAN","error_count":0,"expected_composition_signature":status["composition_signature"],
    "item_scans":[{"scan_id":"CASE.QCI:"+tag+":"+str(ct)+":"+str(i),"barcode":"QN"+tag,"quantity":"1"} for i in range(int(qty))]}
   checked=post("OUTGOING_PALLET_CHECK",scan,{"pallet_identifier":identifier});assert checked["verified"]==1 and not checked["ready"] and checked["shipped"]==0
   weight={"quality_kind":"WEIGHT2","gross_weight":str(int(qty)),"wood_weight":"0","expected_composition_signature":status["composition_signature"]}
   op="CASE.QC.WEIGHT:"+tag+":"+str(ct)
   weighed=post("OUTGOING_PALLET_CHECK",weight,{"pallet_identifier":identifier},op)
   assert weighed["verified"]==1 and weighed["ready"] and weighed["whole_hu_shipment_required"] and weighed["shipped"]==0,(weighed,admission.status(identifier))
   assert post("OUTGOING_PALLET_CHECK",weight,{"pallet_identifier":identifier},op)==weighed
   q.execute("select STATUS,CONTENT_VERSION from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=:id",id=ct);assert q.fetchone()==("CONTROLLED",version)
   failed=post("OUTGOING_PALLET_CHECK",{**weight,"gross_weight":str(int(qty)+6)},{"pallet_identifier":identifier})
   assert failed["verified"]==0 and not failed["ready"]
   q.execute("select STATUS from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=:id",id=ct);assert q.fetchone()==("WAIT_CONTROL",)
   post("OUTGOING_PALLET_CHECK",scan,{"pallet_identifier":identifier})
   again=post("OUTGOING_PALLET_CHECK",weight,{"pallet_identifier":identifier});assert again["ready"] and again["shipped"]==0
   q.execute("select count(*) from RRL_CASE_PICK_EVENT where CASE_PICK_TASK_ID=:id and EVENT_TYPE='CONTROL_PASSED'",id=ct);assert q.fetchone()[0]>=2
  print("PASS CASE12+8 native close/bind/HU -> PLAN pending -> independent scan/weight CONTROLLED; failed weight WAIT_CONTROL; composition version stable; nested auto deferred/replay, P/H20 retained",flush=True)
  q.execute("select sum(r.REMAIN),sum(r.HARD_RESERVED_BASE) from RRL_REMAINS r join RRL_CASE_CARRIER_LOT h on h.LOT_UID=r.UID_POLETA where h.CASE_PICK_TASK_ID in(:a,:b) and r.CELL=:c",a=int(lines[0][0]),b=int(lines[1][0]),c=hu_dst);assert q.fetchone()==(20,20)
  for ct,cl,carrier,qty,cell in lines:
   q.execute("select CONTENT_VERSION,CURRENT_CELL from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=:id",id=int(ct));version,currentcell=q.fetchone();assert currentcell==hu_dst
   post("HU_DETACH",{"child_case_task_id":int(ct),"expected_version":hu_tree()["nodes"][0]["version"],"expected_child_version":int(version),"scan_container":parent,"scan_child":carrier,"reason":"End private HU CASE evidence"},{"uid":parent})
  for ct,cl,carrier,qty,cell in lines:
   q.execute("select STATUS from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=:id",id=ct);assert q.fetchone()==("WAIT_CONTROL",)
   state=admission.status(shipments[int(ct)]);assert not state["ready"] and not state["scan_matches"] and not state["weight_matches"]
  print("PASS unpack revokes both CASE admissions and all prior signatures; own stock unchanged",flush=True)
  print("PASS existing CASE12+8 packed into one HU -> whole system staging20/H20 -> CASE locations/owners retained/replay -> explicit unpack",flush=True)
  for order,qty in zip(orders,(12,8)):
   assert OrderExecution(OracleGateway()).get(order)["lines"][0]["picked_quantity"]==str(qty)
  q.execute("select REMAIN,HARD_RESERVED_BASE from RRL_REMAINS where UID_POLETA=:u and CELL=:c",u=lot,c=dst);assert q.fetchone()==(0,0)
  print("PASS native create_plan12+8 on physical20 -> both CASE; existing wave/launch -> one whole replenishment with two owners -> coverage/release -> physical CASE12+8/replay",flush=True)
 finally:
  if wave is not None:
   if "parent" in locals():
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
   meta("update RRL_WAREHOUSE_TASK set STATUS='CANCELLED' where TASK_SOURCE='WAVE' and SOURCE_DOC_ID=:w and STATUS not in('DONE','CANCELLED')",w=wave)
   meta("update RRL_PICK_WAVE_REPLENISH_TASK set STATUS='CANCELLED' where PICK_WAVE_ID=:w and STATUS not in('DONE','CANCELLED')",w=wave)
   meta("update RRL_PICK_WAVE set STATUS='DONE' where PICK_WAVE_ID=:w",w=wave)
  q.execute("select s.UID_POLETA,s.CELL,s.BASE_UOM,s.STOCK_VERSION from RRL_REMAINS s join RRL_PALLETS p on p.UID_PALLET=s.UID_POLETA where p.ARTICUL=:a and s.REMAIN>0",a=article)
  counts=[{"uid":u,"cell":cell,"article":article,"unit":unit,"quantity":"0","expected_stock_version":int(version),"unit_keys":[]} for u,cell,unit,version in q.fetchall()]
  if counts:post("INVENTORY_COUNT",{"reason":"End private native warehouse case","counts":counts},{"revision_id":revision})
  for plan in plans:meta("update RRL_PICK_RESERVATION set RESERVATION_STATUS='RELEASED' where PICK_PLAN_ID=:p and RESERVATION_STATUS='ACTIVE'",p=plan)
  if "controller" in locals():meta("update RUSERS set DELETED=1 where ID=:u",u=controller)
  print("Own P/H restored; native document and movement evidence retained",flush=True)
