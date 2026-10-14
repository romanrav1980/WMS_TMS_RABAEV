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
cfg=get_settings();tag=uuid4().hex[:10];lot="FULL.QA:"+tag;other=lot+"O";src="QF"+tag;dst="QG"+tag;st_uid="FULL.ST:"+tag
with oracledb.connect(user=cfg.oracle_user,password=cfg.oracle_password,dsn=cfg.oracle_dsn) as conn:
 conn.call_timeout=15000;q=conn.cursor()
 def meta(sql,**b):
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

 q.execute("select ARTICUL from RRL_PALLETS where UID_PALLET='DS-BASE-B1'");base_article=q.fetchone()[0]
 article="QNATIVE"+tag.upper()
 meta("declare r RRL_ARTICULS%rowtype;begin select * into r from RRL_ARTICULS where ACTICUL=:old;r.ACTICUL:=:a;r.BARCODE_SHT:=:bc;r.ABC_GROUP:='A';insert into RRL_ARTICULS values r;end;",old=base_article,a=article,bc="QN"+tag)
 meta("insert into RRL_STOCK_UOM_CONVERSION(ARTICUL,INPUT_UOM,BASE_UOM,POLICY_VERSION,NUMERATOR,DENOMINATOR,BASE_SCALE,PROVENANCE) select :a,INPUT_UOM,BASE_UOM,POLICY_VERSION,NUMERATOR,DENOMINATOR,BASE_SCALE,'Native wave fixture' from RRL_STOCK_UOM_CONVERSION where ARTICUL=:old",a=article,old=base_article)
 meta("insert into RRL_STOCK_POLICY_GUARD(POLICY_KEY,LOCK_ID) select RRL_STOCK_LOCK_API.resource_key('SKU',:a),nvl(max(LOCK_ID),900000000)+1 from RRL_STOCK_POLICY_GUARD",a=article)
 q.execute("select min(CUSTOMER_ID) from RRL_CUSTOMER");customer=q.fetchone()[0]
 for cell in (src,dst):
  meta("insert into RRL_CELLS(CELL,WARE_ID,X,Y,Z,OTBOR,IS_SYSTEM) values(:c,1,0,0,0,:pick,0)",c=cell,pick=int(cell==dst))
  meta("insert into RRL_STOCK_POLICY_GUARD(POLICY_KEY,LOCK_ID) select RRL_STOCK_LOCK_API.resource_key('CELL',:c),nvl(max(LOCK_ID),900000000)+1 from RRL_STOCK_POLICY_GUARD",c=cell)
 face=seq("RRL_PICK_FACE_SQ")
 meta("insert into RRL_PICK_FACE(PICK_FACE_ID,WARE_ID,CELL_CODE,MAX_VOLUME,CREATED_BY) values(:id,1,:c,0.2,'admin')",id=face,c=dst)
 meta("insert into RRL_PICK_FACE_ARTICUL(PICK_FACE_ARTICUL_ID,PICK_FACE_ID,ARTICUL,BOX_VOLUME_M3,USE_ARTICUL_REPLENISH_RULE,REPLENISHMENT_QTY_MODE) values(RRL_PICK_FACE_ARTICUL_SQ.nextval,:id,:a,0.24,0,'FULL_PALLET')",id=face,a=article)
 revision=int(q.callfunc("REVIZION.create_revizion",oracledb.DB_TYPE_NUMBER,[1,"admin"]));conn.commit()
 orders=[];plans=[];wave=None;service=PickingService()
 try:
  post("INVENTORY_REGISTER_LOT",{"uid":lot,"cell":src,"article":article,"quantity":"20","expiry_date":"2030-01-01","price":0,"reason":"Native complete warehouse flow"},{"revision_id":revision})
  for qty in (12,8):
   order=seq("RRL_CUSTOMER_ORDER_SQ");orders.append(order)
   meta("insert into RRL_CUSTOMER_ORDER(CUSTOMER_ORDER_ID,ORDER_NO,CUSTOMER_ID,WARE_ID) values(:id,:no,:c,1)",id=order,no=lot+str(qty),c=customer)
   meta("insert into RRL_CUSTOMER_ORDER_ROW(CUSTOMER_ORDER_ROW_ID,CUSTOMER_ORDER_ID,LINE_NO,ARTICUL,ORDER_QTY,UNIT_CODE) values(RRL_CUSTOMER_ORDER_ROW_SQ.nextval,:o,1,:a,:qty,'EA')",o=order,a=article,qty=qty)
   plan=service.create_plan(PickingPlanCreateRequest(customer_order_id=order,created_by="admin"));plans.append(plan)
   q.execute("select TASK_TYPE,QTY,TARGET_CELL_CODE from RRL_PICK_TASK where PICK_PLAN_ID=:p",p=plan)
   assert q.fetchone()==("CASE_PICK",qty,dst),"Free portion of a shared physical pallet classified FULL"
  wave=service.create_wave(PickWaveCreateRequest(wave_code=lot,ware_id=1,created_by="admin"))
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

  for order,qty in zip(orders,(12,8)):
   assert OrderExecution(OracleGateway()).get(order)["lines"][0]["picked_quantity"]==str(qty)
  q.execute("select REMAIN,HARD_RESERVED_BASE from RRL_REMAINS where UID_POLETA=:u and CELL=:c",u=lot,c=dst);assert q.fetchone()==(0,0)
  print("PASS native create_plan12+8 on physical20 -> both CASE; existing wave/launch -> one whole replenishment with two owners -> coverage/release -> physical CASE12+8/replay",flush=True)
 finally:
  if wave is not None:
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
  print("Own P/H restored; native document and movement evidence retained",flush=True)
