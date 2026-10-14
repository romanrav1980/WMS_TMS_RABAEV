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
qc_actor="admin";cfg=get_settings()
context_path=Path("tmp/context955.json");context=json.loads(context_path.read_text(encoding="utf-8"))
assert context["stage"]=="NEW","Use a separate phase continuation for a progressed source"
tag=context["tag"];lot=context["lot"];ware=context["ware"];article=context["article"];src=context["src"];dst=context["dst"]
def save_context():context_path.write_text(json.dumps(context,indent=2),encoding="utf-8")
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
 q.execute("select PICK_WAVE_ID from RRL_PICK_WAVE where WAVE_CODE=:code",code=lot);wave=int(q.fetchone()[0])
 q.execute("select PICK_PLAN_ID from RRL_PICK_WAVE_ORDER where PICK_WAVE_ID=:w",w=wave);plans=[int(r[0])for r in q.fetchall()]
 q.execute("select CUSTOMER_ORDER_ID from RRL_PICK_WAVE_ORDER where PICK_WAVE_ID=:w order by CUSTOMER_ORDER_ID",w=wave);orders=[int(r[0])for r in q.fetchall()]
 revision=int(q.callfunc("REVIZION.create_revizion",oracledb.DB_TYPE_NUMBER,[ware,"admin"]));conn.commit()
 context.update(wave=wave,orders=orders,revision=revision);save_context()
 from app.services.case_pick_service import CasePickService
 CasePickService(OracleGateway()).ensure_wave_case_pick_tasks(wave,"admin")
 try:
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
   context.update(cases=[list(x)for x in lines],shipments=shipments,wave=wave,orders=orders);save_context()
  from app.modules.transport.infrastructure.st_deferral import StDeferral
  from app.modules.inventory.infrastructure.task_completion import complete_existing_task
  from app.schemas import WarehouseTaskStatusRequest
  from app.modules.platform.public import read_oracle_json
  wait="QW"+tag
  meta("insert into RRL_CELLS(CELL,WARE_ID,X,Y,Z,OTBOR,IS_SYSTEM,LIMIT_HEIGHT,LIMIT_WEIGHT)values(:c,:ware,0,0,0,0,0,0,0)",c=wait)
  meta("insert into RRL_STOCK_POLICY_GUARD(POLICY_KEY,LOCK_ID) select RRL_STOCK_LOCK_API.resource_key('CELL',:c),nvl(max(LOCK_ID),900000000)+1 from RRL_STOCK_POLICY_GUARD",c=wait)
  meta("update RRL_RECEIPT_WARE_SETTINGS set DEFER_WAIT_CELL=:c where WARE_ID=:ware",c=wait)
  q.execute("select TRANSPORTTYPE from RRL_TRANSPORT_TYPE where TRANSPORTTYPE='15'");trtype=q.fetchone()[0]
  q.execute("select min(ID)from RRL_TR_VODITEL where ID>0");driver=q.fetchone()[0]
  vehicle=int(q.callfunc("RRL_TR_VEHICLE_ADD",oracledb.DB_TYPE_NUMBER,["QW"+tag,trtype,40,2,0,None]));conn.commit()
  source_trip=seq("RRL_TRANSPORT_TASK_SQ");target_trip=seq("RRL_TRANSPORT_TASK_SQ");dock="QD"+tag
  meta("insert into RRL_TT_DOCK(DOCK,WARE_ID,DOCK_IS_BLOCKED)values(:dock,:ware,0)",dock=dock)
  for trip,offset in((source_trip,1),(target_trip,2)):
   meta("insert into RRL_TRANSPORT_TASK(ID,TRANSPORT,TRANSTYPE,CONDITION,SHIPMENT_DATE,VODITEL_ID,DOCK,DELETED)values(:id,:plate,:typ,'Спланирован',trunc(sysdate)+:d,:driver,:dock,0)",id=trip,plate="QW"+tag,typ=trtype,d=offset,driver=driver,dock=dock)
  ct,cl,carrier,qty,cell=lines[0];st=shipments[int(ct)]
  meta("update RRL_SBORKA_PALLETS set TRANSTASK_ID=:trip where PALLET_UID=:u",trip=source_trip,u=st)
  context.update(wait=wait,case=int(ct),carrier=carrier,st=st,source_trip=source_trip,target_trip=target_trip,stage="PREPARED");save_context()
  defer=StDeferral(OracleGateway());seen=defer.context(st,"admin");assert seen["physical_preparation"]["state"]=="PREPARED_CASE",seen
  body={"st_number":st,"target_trip_id":target_trip,"expected_version":seen["version"],"source_hash":seen["source_hash"],"reason":"Own prepared CASE waiting source","reference":"WAIT955:"+tag}
  decision="DEC955:"+tag;result=defer.defer(decision,body,"admin");assert defer.defer(decision,body,"admin")==result
  context.update(decision=decision,decision_body=body,decision_result=result,stage="DEFERRED");save_context()
  def planning():
   out=q.var(oracledb.DB_TYPE_CLOB);q.callproc("RRL_ST_DEFER_WAIT_API.plan_waiting",["PLAN955:"+tag,decision,"admin",out]);return read_oracle_json(out.getvalue())
  trial=planning();assert len(trial["tasks"])==1;conn.rollback()
  q.execute("select count(*)from RRL_ST_DEFER_WAIT_RUN where OPERATION_ID=:op",op="PLAN955:"+tag);assert q.fetchone()==(0,)
  planned=planning();conn.commit();assert planning()==planned;conn.rollback()
  task=int(planned["tasks"][0]["task_id"]);context.update(task=task,plan_result=planned,stage="PLANNED");save_context()
  q.execute("select PICKED_AT,PICKED_BY,FACT_QTY,FACT_UOM,FACT_COMPOSITION_JSON,PICKED_CONTENT_VERSION from RRL_CUSTOMER_ORDER_FULFILLMENT where PICKED_CASE_TASK_ID=:id",id=int(ct))
  before=q.fetchone();before=list(before);before[4]=before[4].read()if hasattr(before[4],"read")else before[4]
  q.execute("select CURRENT_CELL,CONTENT_VERSION from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=:id",id=int(ct));origin,version=q.fetchone()
  command={"fact_qty":"1","scanned_pallet":carrier,"scanned_from_cell":origin,"scanned_to_cell":wait,"physical_task_id":task,"scan_container":carrier,"target_cell":wait,"expected_content_version":int(version)}
  context.update(move_body=command,move_operation="MOVE955:"+tag);save_context()
  # A wrong physical scan fails with no movement; execute through the public existing-task bridge.
  bad=dict(command,scanned_to_cell=src)
  try:post("CASE_CARRIER_MOVE",bad,{"case_task_id":int(ct)},"BAD955:"+tag);raise AssertionError("Wrong destination accepted")
  except oracledb.DatabaseError as exc:assert "CASE_CARRIER_DESTINATION_SCAN_REQUIRED"in str(exc),str(exc)
  req=WarehouseTaskStatusRequest(operation_id=context["move_operation"],updated_by="admin",fact_qty="1",scanned_pallet=carrier,scanned_from_cell=origin,scanned_to_cell=wait)
  moved=complete_existing_task(OracleGateway(),task,req,"admin");assert complete_existing_task(OracleGateway(),task,req,"admin")==moved
  context.update(move_result=moved,stage="DONE");save_context()
  q.execute("select STATUS,FACT_QTY,TO_CELL from RRL_WAREHOUSE_TASK where TASK_ID=:id",id=task);assert q.fetchone()==("DONE",1,wait)
  q.execute("select SYNC_STATUS from RRL_WAREHOUSE_TASK_SYNC where TASK_ID=:id",id=task);assert q.fetchone()==("SYNCED",)
  q.execute("select CURRENT_CELL,CONTENT_VERSION from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=:id",id=int(ct));assert q.fetchone()==(wait,int(version)+1)
  q.execute("select sum(r.REMAIN),sum(r.HARD_RESERVED_BASE),min(r.CELL),max(r.CELL)from RRL_REMAINS r join RRL_CASE_CARRIER_LOT l on l.LOT_UID=r.UID_POLETA where l.CASE_PICK_TASK_ID=:id and r.REMAIN>0",id=int(ct));assert q.fetchone()==(12,12,wait,wait)
  q.execute("select PICKED_AT,PICKED_BY,FACT_QTY,FACT_UOM,FACT_COMPOSITION_JSON,PICKED_CONTENT_VERSION from RRL_CUSTOMER_ORDER_FULFILLMENT where PICKED_CASE_TASK_ID=:id",id=int(ct));after=list(q.fetchone());after[4]=after[4].read()if hasattr(after[4],"read")else after[4]
  assert after[:5]==before[:5]and after[5]==int(version)+1
  q.execute("select count(*)from RRL_STOCK_OUTBOX where OPERATION_ID=:op",op=context["move_operation"]);assert q.fetchone()[0]>=1
  context["evidence"]={"case_quantity":"12","case_hard":"12","task_place_quantity":"1","task_status":"DONE","sync":"SYNCED","pick_facts_preserved":True,"bridge_exact_replay":True};save_context()
  print("PASS955 preparedCASE physical12/H12 -> existing ST deferral -> plan rollback/replay -> native wrong scan rollback -> existing bridge DONE1CASE/SYNCED/reserve12/exact replay/originalfacts",flush=True)
 except BaseException as exc:
  context['error']=str(exc);save_context();raise
 else:
  if "task"in context:
   meta("update RRL_WAREHOUSE_TASK set STATUS='CANCELLED'where TASK_ID=:id and STATUS not in('DONE','CANCELLED')",id=context["task"])
  if wave is not None:
   if "parent" in locals():
    q.execute("select CHILD_CASE_TASK_ID from RRL_WMS_HU_LINK where PARENT_UID=:u and ACTIVE_FLAG=1",u=parent)
    for (caseid,) in q.fetchall():
     q.execute("select CONTENT_VERSION,SSCC from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=:id",id=int(caseid));version,carrier=q.fetchone()
     post("HU_DETACH",{"child_case_task_id":int(caseid),"expected_version":hu_tree()["nodes"][0]["version"],"expected_child_version":int(version),"scan_container":parent,"scan_child":carrier,"reason":"Private cleanup after failed case"},{"uid":parent})
   q.execute("select CASE_PICK_TASK_ID,SSCC,CONTENT_VERSION from RRL_CASE_PICK_TASK where PICK_WAVE_ID=:w and STATUS not in('SHIPPED','CANCELLED')",w=wave)
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

  context['cleanup']='OWN_P_H_ZERO';save_context()
