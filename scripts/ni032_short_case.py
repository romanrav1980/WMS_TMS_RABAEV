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
 try:
  if auditor_mode:
   from datetime import datetime,timedelta
   from app.services.resource_management_service import ResourceManagementService
   from app.schemas import ResourceCreateRequest,ResourceShiftCreateRequest,ResourceSessionLoginRequest
   from app.modules.resources.infrastructure.qualification_admin import QualificationAdmin
   group="QIG"+tag;auditor="QIA"+tag
   meta("insert into USER_GROUP(ID,NAME) values(:id,'NI03.2 auditor fixture')",id=group)
   meta("insert into RUSERS(ID,NAME,PASS,USER_GROUP,DELETED) values(:id,'QA auditor','qa-test-only',:g,0)",id=auditor,g=group)
   for right in ("inventory_task_execute","inventory_task_view","stock_inventory_count"):
    meta("insert into RIGHTS(ID,RIGHT1,USER_GROUP,DESCR) select nvl(max(ID),0)+1,:right,:g,'NI03.2 QA' from RIGHTS",right=right,g=group)
   rs=ResourceManagementService();admin=QualificationAdmin(OracleGateway())
   audit_resource=rs.create_resource(ResourceCreateRequest(resource_code=carrier,resource_name="QA auditor",resource_type="INVENTORY",ware_id=1,user_id=auditor,created_by="admin"))
   now=datetime.now();shift=rs.create_shift(ResourceShiftCreateRequest(shift_code=carrier,shift_date=now.date(),start_at=now-timedelta(minutes=1),finish_at=now+timedelta(hours=1),ware_id=1,status="OPEN",created_by="admin"))
   audit_session=rs.login_session(ResourceSessionLoginRequest(shift_id=shift,resource_id=audit_resource,operator_user_id=auditor,created_by="admin"))
   admin.set_qualification(audit_resource,"INVENTORY_CHECK",True,"admin")
   admin.position(audit_session,cell,auditor)
  if case_resource_mode:
   from datetime import datetime,timedelta
   from app.services.resource_management_service import ResourceManagementService
   from app.schemas import ResourceCreateRequest,ResourceShiftCreateRequest,ResourceSessionLoginRequest,CasePickTaskActionRequest,CasePickTransferRequest
   from app.modules.resources.infrastructure.qualification_admin import QualificationAdmin
   rs=ResourceManagementService();admin=QualificationAdmin(OracleGateway());group="QCG"+tag
   meta("insert into USER_GROUP(ID,NAME) values(:id,'NI03.2 CASE fixture')",id=group)
   for right in ("case_pick_execute","case_pick_view"):
    meta("insert into RIGHTS(ID,RIGHT1,USER_GROUP,DESCR) select nvl(max(ID),0)+1,:right,:g,'NI03.2 CASE QA' from RIGHTS",right=right,g=group)
   def picker_context(suffix):
    user="QCP"+suffix+tag
    meta("insert into RUSERS(ID,NAME,PASS,USER_GROUP,DELETED) values(:id,'QA picker','qa-test-only',:g,0)",id=user,g=group)
    resource=rs.create_resource(ResourceCreateRequest(resource_code=carrier+suffix,resource_name="QA picker",resource_type="CASE_PICKER",ware_id=1,user_id=user,created_by="admin"))
    now=datetime.now();shift=rs.create_shift(ResourceShiftCreateRequest(shift_code=carrier+suffix,shift_date=now.date(),start_at=now-timedelta(minutes=1),finish_at=now+timedelta(hours=1),ware_id=1,status="OPEN",created_by="admin"))
    session=rs.login_session(ResourceSessionLoginRequest(shift_id=shift,resource_id=resource,operator_user_id=user,created_by="admin"))
    return user,resource,session
   picker,picker_resource,picker_session=picker_context("1")
   second_picker,second_resource,second_session=picker_context("2")
   meta("update RRL_CASE_PICK_TASK set ASSIGNED_TO=null,STATUS='NEW' where CASE_PICK_TASK_ID=:id",id=ct)
   service=CasePickService()
   request=CasePickTaskActionRequest(resource_id=picker_resource,resource_session_id=picker_session,actor=picker)
   try:service.claim_task(ct,request);raise AssertionError("Missing CASE qualification accepted")
   except HTTPException as exc:assert exc.status_code==409
   admin.set_qualification(picker_resource,"CASE_PICK",True,"admin")
   admin.set_qualification(second_resource,"CASE_PICK",True,"admin")
   service.claim_task(ct,request);service.start_task(ct,request);service.start_task(ct,request)
   q.execute("select count(*) from RRL_CASE_PICK_EVENT where CASE_PICK_TASK_ID=:id and EVENT_TYPE='STARTED'",id=ct);assert q.fetchone()==(1,)
  if reach_mode:
   from datetime import datetime,timedelta
   from app.services.resource_management_service import ResourceManagementService
   from app.schemas import ResourceCreateRequest,ResourceShiftCreateRequest,ResourceSessionLoginRequest,ResourceEquipmentCreateRequest
   from app.modules.resources.infrastructure.qualification_admin import QualificationAdmin
   rs=ResourceManagementService();qual=QualificationAdmin(OracleGateway());group="QRG"+tag;reach_user="QRU"+tag
   meta("insert into USER_GROUP(ID,NAME) values(:id,'NI03.2 reach fixture')",id=group)
   meta("insert into RUSERS(ID,NAME,PASS,USER_GROUP,DELETED) values(:id,'QA reach','qa-test-only',:g,0)",id=reach_user,g=group)
   for right in ("warehouse_task_execute","warehouse_task_view"):
    meta("insert into RIGHTS(ID,RIGHT1,USER_GROUP,DESCR) select nvl(max(ID),0)+1,:right,:g,'NI03.2 QA' from RIGHTS",right=right,g=group)
   reach_equipment=rs.create_equipment(ResourceEquipmentCreateRequest(equipment_code=carrier+"R",equipment_type="REACHTRUCK",ware_id=1,created_by="admin"))
   reach_resource=rs.create_resource(ResourceCreateRequest(resource_code=carrier+"R",resource_name="QA reach",resource_type="REACHTRUCK",equipment_id=reach_equipment,user_id=reach_user,ware_id=1,created_by="admin"))
   now=datetime.now();shift=rs.create_shift(ResourceShiftCreateRequest(shift_code=carrier+"R",shift_date=now.date(),start_at=now-timedelta(minutes=1),finish_at=now+timedelta(hours=1),ware_id=1,status="OPEN",created_by="admin"))
   reach_session=rs.login_session(ResourceSessionLoginRequest(shift_id=shift,resource_id=reach_resource,equipment_id=reach_equipment,operator_user_id=reach_user,created_by="admin"))
   qual.set_qualification(reach_resource,"REPLENISHMENT",True,"admin");qual.position(reach_session,store,reach_user)
  for uid,c,qty in ((lots[0],cell,"3"),(lots[1],store,"2")):
   post("INVENTORY_REGISTER_LOT",{"uid":uid,"cell":c,"article":article,"quantity":qty,"expiry_date":"2030-01-01","price":0,"reason":"NI03.2 isolated short case"},{"revision_id":rev})
  post("RESERVATION_CREATE",{"uid_pallet":lots[0],"cell":cell,"articul":article,"qty":"3","unit_code":"EA","ware_id":1,"reservation_kind":"HARD","reservation_scope":"QTY","reservation_domain":"PICKING","source_doc_type":"PICK_WAVE","source_doc_id":wave,"source_line_id":pt},{"type":"PICK_WAVE","id":wave})
  body={"fact_qty":"1","scan_cell":cell,"scan_container":carrier,"scan_product":article,"offline_event_id":"PICK:"+tag}
  first=post("CASE_PICK_CONFIRM",body,{"case_task_id":ct,"case_line_id":cl},"SHORT.QA.PICK:"+tag,actor=picker)
  if case_resource_mode:
   before=svc_task=CasePickService().get_task(ct)
   handoff=CasePickTransferRequest(to_resource_id=second_resource,to_resource_session_id=second_session,reason="Explicit handoff after one physical unit",actor="admin",offline_event_id="HANDOFF:"+tag,scan_container=carrier,expected_content_version=int(before["content_version"]),expected_assigned_to=before["assigned_to"],expected_from_session_id=before["resource_session_id"])
   for bad,code in ((handoff.model_copy(update={"scan_container":"wrong"}),"CASE_HANDOFF_WRONG_CARRIER"),(handoff.model_copy(update={"expected_content_version":int(before["content_version"])+1}),"CASE_HANDOFF_STALE_OWNER_OR_CONTENT")):
    try:CasePickService().transfer_task(ct,bad);raise AssertionError("Invalid handoff accepted")
    except HTTPException as exc:assert exc.status_code==409 and code in str(exc.detail),exc
   CasePickService().transfer_task(ct,handoff);CasePickService().transfer_task(ct,handoff)
   try:CasePickService().transfer_task(ct,handoff.model_copy(update={"reason":"changed"}));raise AssertionError("Changed handoff replay accepted")
   except HTTPException as exc:assert exc.status_code==409 and "CASE_HANDOFF_CONTENT_CONFLICT" in str(exc.detail)
   q.execute("select count(*) from RRL_CASE_PICK_EVENT where OFFLINE_EVENT_ID=:id",id=handoff.offline_event_id);assert q.fetchone()==(1,)
   after=CasePickService().get_task(ct)
   assert after["assigned_to"]==second_picker and after["picked_qty"]==before["picked_qty"] and after["current_cell"]==before["current_cell"]
   picker=second_picker
   print("PASS CASE qualification, start replay, handoff scan/version/replay/conflict, actual owner and physical carrier preserved",flush=True)
  req=CasePickLineShortRequest(picked_qty="1",short_qty="2",reason_text="Physical stock missing; restore order",offline_event_id="REPORT:"+tag,actor=picker)
  svc=CasePickService();report=svc.short_line(ct,cl,req);short=report["case_pick_short_id"]
  assert svc.short_line(ct,cl,req)["case_pick_short_id"]==short
  try:svc.short_line(ct,cl,req.model_copy(update={"reason_text":"changed"}));raise AssertionError("Changed report replay accepted")
  except HTTPException as exc:assert exc.status_code==409
  q.execute("select RECOVERY_DEADLINE_AT from RRL_CASE_PICK_SHORT where CASE_PICK_SHORT_ID=:id",id=short);deadline=q.fetchone()[0]
  approved=post("CASE_SHORT_APPROVE",{"decision":"RESTORE","reason":"Restore remaining quantity"},{"short_id":short},"SHORT.QA.RESTORE:"+tag)
  it=approved["inventory_task_id"]
  if auditor_mode:
   assigned=ShortRecoveryWorker(OracleGateway(),"admin","AUDIT.QA:"+tag,assign_warehouse).process_one()
   assert assigned and assigned.get("assigned") and assigned["assigned_to"]==auditor,assigned
   q.execute("select CURRENT_INVENTORY_TASK_ID from RRL_RESOURCE_SESSION where SESSION_ID=:id",id=audit_session)
   assert q.fetchone()==(it,)

  q.execute("select STOCK_VERSION,BASE_UOM from RRL_REMAINS where UID_POLETA=:lot and CELL=:c",lot=lots[0],c=cell);version,unit=q.fetchone()
  counted=post("INVENTORY_COUNT",{"inventory_task_id":it,"reason":"Physical recount confirmed missing stock","counts":[{"uid":lots[0],"cell":cell,"article":article,"unit":unit,"quantity":"0","expected_stock_version":int(version),"unit_keys":[]}]},{"revision_id":rev},"SHORT.QA.COUNT:"+tag,actor=auditor)
  assert counted["recovery_state"]=="WAIT_REPLENISHMENT",counted
  if auditor_mode:
   q.execute("select CURRENT_INVENTORY_TASK_ID from RRL_RESOURCE_SESSION where SESSION_ID=:id",id=audit_session)
   assert q.fetchone()==(None,)

  worker=ShortRecoveryWorker(OracleGateway(),"admin","QA:"+tag,assign_warehouse);worked=worker.process_one();print("worker",worked,flush=True)
  assert worked and not worked.get("error"),worked
  if reach_mode:assert worked["dispatch"]["assigned"] and worked["dispatch"]["assigned_to"]==reach_user,worked
  q.execute("select t.TASK_ID,t.UID_PALLET,t.FROM_CELL,t.TO_CELL,t.QTY,t.PRIORITY from RRL_WAREHOUSE_TASK t where t.TASK_SOURCE='WAVE' and t.SOURCE_TASK_ID=:id",id=counted["replenish_task_id"]);task,uid,src,dst,qty,priority=q.fetchone()
  assert priority==0 and dst==cell and qty==(1 if chunk_mode else 2)
  if chunk_mode:
   post("TASK_COMPLETE",{"fact_qty":"1","scanned_pallet":uid,"scanned_from_cell":src,"scanned_to_cell":dst},{"task_id":int(task)},"SHORT.QA.REPL1:"+tag,actor=reach_user)
   q.execute("select RECOVERY_STATE from RRL_CASE_PICK_SHORT where CASE_PICK_SHORT_ID=:id",id=short);assert q.fetchone()==("READY",)
   post("CASE_PICK_CONFIRM",{**body,"fact_qty":"2","offline_event_id":"PART2:"+tag},{"case_task_id":ct,"case_line_id":cl},"SHORT.QA.CHUNK:"+tag,actor=picker)
   q.execute("select RECOVERY_STATE,RESTORED_AT,RECOVERY_DEADLINE_AT,REPLENISH_TASK_ID from RRL_CASE_PICK_SHORT where CASE_PICK_SHORT_ID=:id",id=short)
   state,restored,current_deadline,next_repl=q.fetchone()
   assert state=="WAIT_REPLENISHMENT" and restored is None and current_deadline==deadline
   worker=ShortRecoveryWorker(OracleGateway(),"admin","QA.NEXT:"+tag,assign_warehouse)
   worked=worker.process_one();assert worked and not worked.get("error"),worked
   q.execute("select TASK_ID,UID_PALLET,FROM_CELL,TO_CELL,QTY from RRL_WAREHOUSE_TASK where TASK_SOURCE='WAVE' and SOURCE_TASK_ID=:id",id=next_repl)
   task,uid,src,dst,qty=q.fetchone();assert qty==1

  post("TASK_COMPLETE",{"fact_qty":str(qty),"scanned_pallet":uid,"scanned_from_cell":src,"scanned_to_cell":dst},{"task_id":int(task)},"SHORT.QA.REPL:"+tag,actor=reach_user)
  q.execute("select RECOVERY_STATE from RRL_CASE_PICK_SHORT where CASE_PICK_SHORT_ID=:id",id=short);assert q.fetchone()==("READY",)
  final=post("CASE_PICK_CONFIRM",{**body,"fact_qty":"3","offline_event_id":"FINISH:"+tag},{"case_task_id":ct,"case_line_id":cl},"SHORT.QA.FINISH:"+tag,actor=picker)
  assert post("CASE_PICK_CONFIRM",{**body,"fact_qty":"3","offline_event_id":"FINISH:"+tag},{"case_task_id":ct,"case_line_id":cl},"SHORT.QA.FINISH:"+tag,actor=picker)==final
  q.execute("select RECOVERY_STATE,RECOVERY_DEADLINE_AT from RRL_CASE_PICK_SHORT where CASE_PICK_SHORT_ID=:id",id=short);assert q.fetchone()==("RESUMED",deadline)
  q.execute("select PICKED_QTY from RRL_CASE_PICK_LINE where CASE_PICK_LINE_ID=:id",id=cl);assert q.fetchone()==(3,)
  print("PASS: physical CASE 1, shortage 2, immutable report, urgent recount, existing replenishment, resumed CASE total3/replay",flush=True)
  if chunk_mode:print("PASS recovery in two capacity1 chunks: intermediate wait, final restoration only after all3, original deadline unchanged",flush=True)
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
  print("QA stock restored through root commands; movement history retained",flush=True)
