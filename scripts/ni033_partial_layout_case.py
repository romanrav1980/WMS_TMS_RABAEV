"""One real CASE shortage -> inventory -> replenishment -> resumed pick."""
import json,sys
from pathlib import Path
from uuid import uuid4
import oracledb
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment()
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"api/wms_api_server"))
from app.config import get_settings
from app.oracle_gateway import OracleGateway
from app.resource_composition import assign_warehouse
from app.services.case_pick_service import CasePickService
from app.schemas import CasePickLineShortRequest
from app.modules.inventory.infrastructure.recovery_worker import ShortRecoveryWorker
from fastapi import HTTPException
auditor_mode="--auditor" in sys.argv
chunk_mode="--chunks" in sys.argv
case_resource_mode="--case-resource" in sys.argv
reach_mode="--reachtruck" in sys.argv
cfg=get_settings();tag=uuid4().hex[:10];cell="QP"+tag;store="QW"+tag
lots=["NSHORT-P-"+tag,"NSHORT-S-"+tag];carrier="NSHORT-C-"+tag
with oracledb.connect(user=cfg.oracle_user,password=cfg.oracle_password,dsn=cfg.oracle_dsn) as conn:
 conn.call_timeout=15000;q=conn.cursor()
 def meta(sql,**b):
  q.callproc("RRL_STOCK_CONFIG_API.begin_change",["admin","warehouse_settings_edit"])
  try:q.execute(sql,b);conn.commit()
  except BaseException:conn.rollback();raise
  finally:q.callproc("RRL_STOCK_CONFIG_API.end_change")
 def seq(name):
  q.execute("select "+name+".nextval from dual");return int(q.fetchone()[0])
 def post(kind,body,source,op=None,actor="admin"):
  d={"contract_version":2,"operation_id":op or "SHORT.QA:"+uuid4().hex,"command_type":kind,"actor":actor,"source":source,"lines":[],"units":[],"metadata":body}
  inp,out=q.var(oracledb.DB_TYPE_CLOB),q.var(oracledb.DB_TYPE_CLOB);inp.setvalue(0,json.dumps(d))
  try:
   q.callproc("RRL_STOCK_POSTING_API.prepare_command",[inp,actor,out,None])
   if out.getvalue() is None:q.callproc("RRL_STOCK_POSTING_API.execute_prepared",[out])
   r=out.getvalue();r=json.loads(r.read() if hasattr(r,"read") else r);conn.commit();return r
  except BaseException:conn.rollback();raise
  finally:q.callproc("RRL_STOCK_POSTING_API.reset_connection")
 q.execute("select user,sys_context('USERENV','SERVICE_NAME') from dual");assert q.fetchone()==("RABAEV","orcl")
 q.execute("select ARTICUL from RRL_PALLETS where UID_PALLET='DS-BASE-B1'");article=q.fetchone()[0]
 for c,pick in ((cell,1),(store,0)):
  meta("insert into RRL_CELLS(CELL,WARE_ID,X,Y,Z,OTBOR,IS_SYSTEM) values(:c,1,0,0,0,:p,0)",c=c,p=pick)
  meta("insert into RRL_STOCK_POLICY_GUARD(POLICY_KEY,LOCK_ID) select RRL_STOCK_LOCK_API.resource_key('CELL',:c),nvl(max(LOCK_ID),900000000)+1 from RRL_STOCK_POLICY_GUARD",c=c)
 face=seq("RRL_PICK_FACE_SQ")
 meta("insert into RRL_PICK_FACE(PICK_FACE_ID,WARE_ID,CELL_CODE,CREATED_BY) values(:id,1,:c,'admin')",id=face,c=cell)
 meta("insert into RRL_PICK_FACE_ARTICUL(PICK_FACE_ARTICUL_ID,PICK_FACE_ID,ARTICUL,REPLENISHMENT_QTY_MODE) values(RRL_PICK_FACE_ARTICUL_SQ.nextval,:f,:a,'FILL_TO_VOLUME')",f=face,a=article)
 if chunk_mode:
  from decimal import Decimal
  q.execute("select NUMERATOR,DENOMINATOR from RRL_STOCK_UOM_CONVERSION where ARTICUL=:a and INPUT_UOM='BOX' order by POLICY_VERSION desc fetch first 1 row only",a=article)
  num,den=q.fetchone();box_volume=Decimal(str(num))/Decimal(str(den))*Decimal("0.01")
  meta("update RRL_PICK_FACE set MAX_VOLUME=0.01 where PICK_FACE_ID=:id",id=face)
  meta("update RRL_PICK_FACE_ARTICUL set BOX_VOLUME_M3=:v,USE_ARTICUL_REPLENISH_RULE=0 where PICK_FACE_ID=:id and ARTICUL=:a",id=face,a=article,v=box_volume)
 rev=int(q.callfunc("REVIZION.create_revizion",oracledb.DB_TYPE_NUMBER,[1,"admin"]));conn.commit()
 q.execute("select min(CUSTOMER_ID) from RRL_CUSTOMER");customer=q.fetchone()[0]
 order,row,plan,pl,pt,wave,wt,ct,cl=[seq(n) for n in ("RRL_CUSTOMER_ORDER_SQ","RRL_CUSTOMER_ORDER_ROW_SQ","RRL_PICK_PLAN_SQ","RRL_PICK_PLAN_LINE_SQ","RRL_PICK_TASK_SQ","RRL_PICK_WAVE_SQ","RRL_PICK_WAVE_TASK_SQ","RRL_CASE_PICK_TASK_SQ","RRL_CASE_PICK_LINE_SQ")]
 meta("insert into RRL_CUSTOMER_ORDER(CUSTOMER_ORDER_ID,ORDER_NO,CUSTOMER_ID,WARE_ID) values(:id,:no,:customer,1)",id=order,no=carrier,customer=customer)
 meta("insert into RRL_CUSTOMER_ORDER_ROW(CUSTOMER_ORDER_ROW_ID,CUSTOMER_ORDER_ID,LINE_NO,ARTICUL,ORDER_QTY) values(:id,:o,1,:a,3)",id=row,o=order,a=article)
 meta("insert into RRL_PICK_PLAN(PICK_PLAN_ID,CUSTOMER_ORDER_ID,CUSTOMER_ID,WARE_ID,STATUS,TOTAL_ORDER_QTY,TOTAL_PLANNED_QTY) values(:id,:o,:customer,1,'RELEASED',3,3)",id=plan,o=order,customer=customer)
 meta("insert into RRL_PICK_PLAN_LINE(PICK_PLAN_LINE_ID,PICK_PLAN_ID,CUSTOMER_ORDER_ROW_ID,ARTICUL,REQUESTED_QTY,PLANNED_QTY,CASE_PICK_QTY,STATUS) values(:id,:p,:r,:a,3,3,3,'PLANNED_FULL')",id=pl,p=plan,r=row,a=article)
 meta("insert into RRL_PICK_TASK(PICK_TASK_ID,PICK_PLAN_ID,PICK_PLAN_LINE_ID,CUSTOMER_ORDER_ID,CUSTOMER_ID,TASK_TYPE,STATUS,ARTICUL,SOURCE_CELL_CODE,QTY,PICK_SEQUENCE) values(:id,:p,:pl,:o,:customer,'CASE_PICK','IN_PROGRESS',:a,:c,3,1)",id=pt,p=plan,pl=pl,o=order,customer=customer,a=article,c=cell)
 meta("insert into RRL_PICK_WAVE(PICK_WAVE_ID,WAVE_CODE,WARE_ID,STATUS,CREATED_BY) values(:id,:code,1,'LAUNCHED','admin')",id=wave,code=carrier)
 meta("insert into RRL_PICK_WAVE_TASK(PICK_WAVE_TASK_ID,PICK_WAVE_ID,PICK_TASK_ID,TASK_TYPE,STATUS,ARTICUL,QTY,SOURCE_CELL_CODE) values(:id,:w,:p,'CASE_PICK','IN_PROGRESS',:a,3,:c)",id=wt,w=wave,p=pt,a=article,c=cell)
 meta("insert into RRL_CASE_PICK_TASK(CASE_PICK_TASK_ID,PICK_WAVE_ID,PICK_PLAN_ID,CUSTOMER_ORDER_ID,CUSTOMER_ID,SSCC,STATUS,WARE_ID,TOTAL_LINES,PLANNED_QTY,ASSIGNED_TO,CREATED_BY) values(:id,:w,:p,:o,:customer,:carrier,'IN_PROGRESS',1,1,3,'admin','admin')",id=ct,w=wave,p=plan,o=order,customer=customer,carrier=carrier)
 meta("insert into RRL_CASE_PICK_LINE(CASE_PICK_LINE_ID,CASE_PICK_TASK_ID,PICK_WAVE_ID,PICK_WAVE_TASK_ID,PICK_TASK_ID,PICK_PLAN_LINE_ID,CUSTOMER_ORDER_ID,CUSTOMER_ID,ARTICUL,CELL_CODE,PICK_FACE_ID,PICK_SEQUENCE,PLANNED_QTY,STATUS,CREATED_BY) values(:id,:ct,:w,:wt,:pt,:pl,:o,:customer,:a,:c,:f,1,3,'ACTIVE','admin')",id=cl,ct=ct,w=wave,wt=wt,pt=pt,pl=pl,o=order,customer=customer,a=article,c=cell,f=face)
 print(json.dumps({"tag":tag,"case_task":ct,"line":cl,"wave":wave,"revision":rev,"cell":cell,"store":store,"lots":lots,"carrier":carrier,"article":article}),flush=True)
 audit_session=None;audit_resource=None;auditor="admin"
 picker="admin";picker_session=None;picker_resource=None;second_picker=None;second_session=None;second_resource=None
 reach_user="admin";reach_resource=None;reach_session=None;reach_equipment=None
 bound=False;fulfillment=None;progress=None
 try:
  post("INVENTORY_REGISTER_LOT",{"uid":lots[0],"cell":cell,"article":article,"quantity":"3","expiry_date":"2030-01-01","price":0,"reason":"Physical fulfillment case"},{"revision_id":rev})
  post("RESERVATION_CREATE",{"uid_pallet":lots[0],"cell":cell,"articul":article,"qty":"3","unit_code":"EA","ware_id":1,"reservation_kind":"HARD","reservation_scope":"QTY","reservation_domain":"PICKING","source_doc_type":"PICK_WAVE","source_doc_id":wave,"source_line_id":pt,"customer_order_id":order,"customer_id":customer,"pick_plan_id":plan,"pick_plan_line_id":pl},{"type":"PICK_WAVE","id":wave})

  from app.modules.inventory.infrastructure.wave_pick_release import WavePickRelease
  admission=WavePickRelease(OracleGateway())
  before=admission.preview(wave)
  assert before["ready"] is True and before["released_at"] is None
  try:
   post("CASE_PICK_CONFIRM",{"fact_qty":"1","scan_cell":cell,"scan_container":carrier,"scan_product":article,"offline_event_id":"BLOCKED.PICK:"+tag},{"case_task_id":ct,"case_line_id":cl})
   raise AssertionError("Unreleased wave permitted physical picking")
  except oracledb.DatabaseError as exc:
   assert "WAVE_PICK_RELEASE_REQUIRED" in str(exc),str(exc)
  gateop="PICK.RELEASE:"+tag
  released=post("WAVE_PICK_RELEASE",{},{"wave_id":wave},gateop)
  assert released["released_at"] is not None
  assert post("WAVE_PICK_RELEASE",{},{"wave_id":wave},gateop)==released
  meta("update RRL_CUSTOMER_ORDER_ROW set UNIT_CODE='EA' where CUSTOMER_ORDER_ROW_ID=:id",id=row)
  from app.modules.fulfillment.infrastructure.execution_progress import OrderExecution
  progress=OrderExecution(OracleGateway())
  assert progress.get(order)["lines"][0]["picked_quantity"]=="0"
  shipment_uid="QFULFILL-"+tag;shipment=seq("RRL_SBORKA_PALLETS_SQ");fulfillment=seq("RRL_CUSTOMER_ORDER_FULF_SQ")
  meta("insert into RRL_SBORKA_PALLETS(ID,PALLET_UID,ST_NUMBER,WARE_ID,CONDITION,ADDR) values(:id,:p_uid,:p_uid,1,0,'NI033 own fixture')",id=shipment,p_uid=shipment_uid)
  meta("insert into RRL_SBORKA_PALLET_ROWS(ID,PALLET_UID,ARTICUL,EI,QUANTITY) values(RRL_SBORKA_PALLET_ROWS_SQ.nextval,:p_uid,:a,'EA',3)",p_uid=shipment_uid,a=article)
  meta("insert into RRL_CUSTOMER_ORDER_FULFILLMENT(FULFILLMENT_ID,CUSTOMER_ORDER_ID,LEGACY_SBORKA_PALLET_ID,PALLET_UID,STATUS,FACT_QTY) values(:id,:o,:sid,:p_uid,'PLANNED',0)",id=fulfillment,o=order,sid=shipment,p_uid=shipment_uid)
  meta("update RRL_SBORKA_PALLET_ROWS set PACK_COUNT=3,ORDER_WEIGHT=3 where PALLET_UID=:p_uid",p_uid=shipment_uid)
  from app.modules.inventory.infrastructure.case_shipment_binding import bind_case_shipment
  try:bind_case_shipment(OracleGateway(),ct,shipment_uid,carrier,1,"admin");raise AssertionError("Prepared ST became PICKED without physical carrier")
  except ValueError:pass
  q.execute("select STATUS,FACT_QTY from RRL_CUSTOMER_ORDER_FULFILLMENT where FULFILLMENT_ID=:id",id=fulfillment);assert q.fetchone()==("PLANNED",0)
  post("CASE_PICK_CONFIRM",{"fact_qty":"1","scan_cell":cell,"scan_container":carrier,"scan_product":article,"offline_event_id":"FUL.PICK:"+tag},{"case_task_id":ct,"case_line_id":cl},"FUL.QA.PICK:"+tag)
  from app.schemas import CasePickLineShortRequest,CasePickTaskActionRequest
  reported=CasePickService().short_line(ct,cl,CasePickLineShortRequest(picked_qty="1",short_qty="2",
      reason_text="Approved partial shipment",offline_event_id="PART.SHORT:"+tag,actor="admin"))
  post("CASE_SHORT_APPROVE",{"decision":"ACCEPT_SHORT","reason":"Ship confirmed quantity and retain original demand"},
       {"short_id":reported["case_pick_short_id"]},"PART.APPROVE:"+tag)
  assert q.callfunc("RRL_STOCK_ELIGIBILITY.reason",str,[lots[0],cell,1,0,None,None,"ALLOCATE",None,article])=="SOURCE_INVENTORY_PENDING"
  CasePickService().close_task(ct,CasePickTaskActionRequest(actor="admin"))
  from app.modules.inventory.infrastructure.partial_shipment_layout import PartialShipmentLayout
  from app.modules.inventory.api.partial_shipment_routes import PartialLayoutRequest
  layout=PartialShipmentLayout(OracleGateway())
  proposal=layout.preview(ct,shipment_uid)
  request=PartialLayoutRequest(operation_id="PART.LAYOUT:"+tag,pallet_identifier=shipment_uid,scan_container=carrier,
      expected_content_version=proposal["content_version"],expected_physical_signature=proposal["physical_signature"],
      expected_layout_signature=proposal["layout_signature"],reason="Approved shortage, ship physical contents").model_dump(mode="json")
  prepared=layout.prepare(ct,request,"admin")
  assert layout.prepare(ct,request,"admin")["idempotent"]
  try:layout.prepare(ct,{**request,"reason":"changed"},"admin");raise AssertionError("Changed partial layout replay accepted")
  except ValueError:pass
  q.execute("select QUANTITY,ORIGINAL_QUANTITY,PACK_COUNT,ORDER_WEIGHT from RRL_SBORKA_PALLET_ROWS where PALLET_UID=:p_uid",p_uid=shipment_uid)
  assert q.fetchone()==(1,3,1,1)
  q.execute("select ORDER_QTY from RRL_CUSTOMER_ORDER_ROW where CUSTOMER_ORDER_ROW_ID=:id",id=row);assert q.fetchone()==(3,)
  q.execute("select count(*) from RRL_CASE_PICK_EVENT where CASE_PICK_TASK_ID=:id and EVENT_TYPE='SHIPMENT_LAYOUT_ADJUSTED'",id=ct);assert q.fetchone()==(1,)
  status=progress.get(order)["lines"][0]
  assert (status["picked_quantity"],status["remaining_quantity"],status["status"])==("1","2","PARTIAL_REFUSED"),status
  q.execute("select CONTENT_VERSION from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=:id",id=ct);content_version=int(q.fetchone()[0])
  result=bind_case_shipment(OracleGateway(),ct,shipment_uid,carrier,content_version,"admin")
  bound=True
  replay=bind_case_shipment(OracleGateway(),ct,shipment_uid,carrier,content_version,"admin")
  assert result["fulfillment_status"]=="PICKED" and replay["idempotent"]
  q.execute("select STATUS,FACT_QTY,FACT_UOM,PICKED_CASE_TASK_ID,PICKED_CONTENT_VERSION from RRL_CUSTOMER_ORDER_FULFILLMENT where FULFILLMENT_ID=:id",id=fulfillment);assert q.fetchone()==("PICKED",1,"EA",ct,content_version)
  try:bind_case_shipment(OracleGateway(),ct,shipment_uid,carrier,content_version+1,"admin");raise AssertionError("Changed binding version replay accepted")
  except ValueError:pass
  q.execute("select count(*) from RRL_CASE_PICK_EVENT where CASE_PICK_TASK_ID=:id and EVENT_TYPE='SHIPMENT_BOUND'",id=ct);assert q.fetchone()==(1,)
  print("PASS partial CASE1 + approved shortage2 -> original order3 unchanged, existing ST1 with original3/weight/package history + replay, bind physical1; reported source unavailable until linked recount",flush=True)
 finally:
  q.execute("select h.LOT_UID,t.CONTENT_VERSION from RRL_CASE_CARRIER_LOT h join RRL_CASE_PICK_TASK t on t.CASE_PICK_TASK_ID=h.CASE_PICK_TASK_ID where h.CASE_PICK_TASK_ID=:id",id=ct);packed=q.fetchall()
  if packed:
   post("CASE_CARRIER_RETURN",{"destinations":{u:cell for u,_ in packed},"expected_content_version":int(packed[0][1]),"scan_container":carrier,"reason":"End bounded QA case"},{"case_task_id":ct})
  q.execute("select RESERVATION_ID from RRL_STOCK_RESERVATION where SOURCE_DOC_TYPE='PICK_WAVE' and SOURCE_DOC_ID=:w and STATUS in('ACTIVE','ALLOCATED','PICKING') and BASE_QTY>0",w=wave)
  for (rid,) in q.fetchall():post("RESERVATION_RELEASE",{"reason":"End QA"}, {"reservation_id":int(rid)})
  q.execute("select r.UID_POLETA,r.CELL,r.BASE_UOM,r.STOCK_VERSION from RRL_REMAINS r join RRL_PALLETS p on p.UID_PALLET=r.UID_POLETA where r.REMAIN>0 and (p.UID_PALLET in(:a,:b) or p.STOCK_ORIGIN_UID in(:a,:b))",a=lots[0],b=lots[1])
  counts=[{"uid":u,"cell":c,"article":article,"unit":base,"quantity":"0","expected_stock_version":int(v),"unit_keys":[]} for u,c,base,v in q.fetchall()]
  if counts:post("INVENTORY_COUNT",{"reason":"End bounded QA fixture","counts":counts},{"revision_id":rev})
  meta("update RRL_WAREHOUSE_TASK set STATUS='CANCELLED' where TASK_SOURCE='WAVE' and SOURCE_DOC_ID=:id and STATUS not in('DONE','CANCELLED')",id=wave)
  meta("update RRL_INVENTORY_TASK set STATUS='CANCELLED' where SOURCE_DOC_TYPE='CASE_PICK_SHORT' and SOURCE_DOC_ID in(select CASE_PICK_SHORT_ID from RRL_CASE_PICK_SHORT where CASE_PICK_TASK_ID=:id) and STATUS!='DONE'",id=ct)
  meta("update RRL_PICK_WAVE set STATUS='CANCELLED' where PICK_WAVE_ID=:id",id=wave)
  meta("update RRL_CASE_PICK_SHORT set RECOVERY_STATE='FAILED',RECOVERY_LAST_ERROR='QA fixture closed' where CASE_PICK_TASK_ID=:id and RECOVERY_STATE not in('RESUMED','FAILED')",id=ct)
  if audit_session is not None:
   meta("update RRL_RESOURCE_SESSION set STATUS='CLOSED',LOGOUT_AT=systimestamp,CURRENT_INVENTORY_TASK_ID=null where SESSION_ID=:id",id=audit_session)
   meta("update RRL_RESOURCE set ACTIVE=0,STATUS='CLOSED' where RESOURCE_ID=:id",id=audit_resource)
   meta("update RUSERS set DELETED=1 where ID=:id",id=auditor)
  if case_resource_mode:
   for user,resource,session in ((picker if picker_session==second_session else "QCP1"+tag,picker_resource,picker_session),(second_picker,second_resource,second_session)):
    if session is not None:meta("update RRL_RESOURCE_SESSION set STATUS='CLOSED',LOGOUT_AT=systimestamp where SESSION_ID=:id",id=session)
    if resource is not None:meta("update RRL_RESOURCE set ACTIVE=0,STATUS='CLOSED' where RESOURCE_ID=:id",id=resource)
    if user is not None:meta("update RUSERS set DELETED=1 where ID=:id",id=user)
  if reach_mode:
   if reach_session is not None:meta("update RRL_RESOURCE_SESSION set STATUS='CLOSED',LOGOUT_AT=systimestamp,CURRENT_TASK_ID=null where SESSION_ID=:id",id=reach_session)
   if reach_resource is not None:meta("update RRL_RESOURCE set ACTIVE=0,STATUS='CLOSED' where RESOURCE_ID=:id",id=reach_resource)
   if reach_equipment is not None:meta("update RRL_RESOURCE_EQUIPMENT set ACTIVE=0 where EQUIPMENT_ID=:id",id=reach_equipment)
   meta("update RUSERS set DELETED=1 where ID=:id",id=reach_user)
  q.execute("select STATUS,FACT_QTY,PICKED_CASE_TASK_ID from RRL_CUSTOMER_ORDER_FULFILLMENT where FULFILLMENT_ID=:id",id=fulfillment)
  remaining=q.fetchone();assert remaining is None or remaining==("PLANNED",0,None)
  q.execute("select count(*) from RRL_CASE_PICK_EVENT where CASE_PICK_TASK_ID=:id and EVENT_TYPE='SHIPMENT_BOUND'",id=ct);assert q.fetchone()==(1 if bound else 0,)
  if bound:assert progress.get(order)["lines"][0]["picked_quantity"]=="0"
  print("PASS root carrier return resets current fulfillment to PLANNED; immutable physical binding evidence retained; own stock restored",flush=True)
