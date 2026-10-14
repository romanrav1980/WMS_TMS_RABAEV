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
path=Path("tmp/context987.json");assert not path.exists(),"987 already exists; retained phase only"
record={"tag":tag,"stage":"NEW"}
def save():path.write_text(json.dumps(record,indent=2,default=str),encoding="utf-8")
save()
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
  from app.services.case_pick_service import CasePickService
  from app.modules.inventory.infrastructure.replenishment_continuation import ReplenishmentContinuation
  from app.modules.resources.public import sync_existing_wave_tasks
  ReplenishmentContinuation(OracleGateway(),sync_existing_wave_tasks).reconcile(ware,"admin")
  CasePickService(OracleGateway()).ensure_wave_case_pick_tasks(wave,"admin")
  record.update(ware=ware,article=article,wave=wave,revision=revision,orders=orders,lot=lot,dst=dst);save()
  released=post("WAVE_PICK_RELEASE",{},{"wave_id":wave})
  assert released["released_at"] is not None
  q.execute("select ct.CASE_PICK_TASK_ID,cl.CASE_PICK_LINE_ID,ct.SSCC,cl.PLANNED_QTY,cl.CELL_CODE from RRL_CASE_PICK_TASK ct join RRL_CASE_PICK_LINE cl on cl.CASE_PICK_TASK_ID=ct.CASE_PICK_TASK_ID where ct.PICK_WAVE_ID=:w order by ct.CUSTOMER_ORDER_ID",w=wave)
  lines=q.fetchall();assert len(lines)==2,lines
  from app.services.case_pick_service import CasePickService
  from app.schemas import CasePickTaskActionRequest
  cases=CasePickService()
  q.execute("select PALLET_TYPE_ID from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=:id",id=lines[0][0]);tare_type=int(q.fetchone()[0])
  post("TARE_COUNT",{"owner_ware_id":ware,"pallet_type_id":tare_type,"condition":"GOOD","observed_quantity":"2","expected_version":0,"reason":"Own software multiCASE opening tare observation","decision_reference":"MULTI987:"+tag},{},"TARE987.COUNT:"+tag)
  for caseid,*unused in lines:
   post("TARE_BOOK",{"pallet_type_id":None},{"place_kind":"CASE","place_id":str(caseid)},"TARE987.BOOK:"+tag+":"+str(caseid))
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
   meta("insert into RRL_SBORKA_PALLETS(ID,PALLET_UID,ST_NUMBER,WARE_ID,CONDITION,ADDR) values(:sid,:u,:st,:ware,0,'Own existing CASE QC ST')",sid=sid,u=identifier,st='MULTI987:'+tag)
   meta("insert into RRL_SBORKA_PALLET_ROWS(ID,PALLET_UID,ARTICUL,EI,QUANTITY) values(RRL_SBORKA_PALLET_ROWS_SQ.nextval,:u,:a,'EA',:qty)",u=identifier,a=article,qty=qty)
   meta("insert into RRL_CUSTOMER_ORDER_FULFILLMENT(FULFILLMENT_ID,CUSTOMER_ORDER_ID,LEGACY_SBORKA_PALLET_ID,PALLET_UID,STATUS,FACT_QTY) values(:ff,:o,:sid,:u,'PLANNED',0)",ff=ff,o=order,sid=sid,u=identifier)
   q.execute("select CONTENT_VERSION from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=:id",id=ct);version=q.fetchone()[0]
   bind_case_shipment(OracleGateway(),int(ct),identifier,carrier,int(version),"admin");shipments[int(ct)]=identifier
   record.update(cases=[list(x)for x in lines],shipments=shipments,stage="BOUND");save()
  from app.modules.transport.infrastructure.st_deferral import StDeferral
  from app.modules.inventory.application.case_carrier_move import CaseCarrierMove
  from app.modules.inventory.infrastructure.stock_posting_uow import StockPosting
  from app.modules.inventory.infrastructure.task_completion import complete_existing_task
  from app.modules.platform.public import read_oracle_json
  from app.schemas import WarehouseTaskStatusRequest
  wait="QW"+tag;control="QX"+tag;st="MULTI987:"+tag
  for cell,system in((wait,0),(control,1)):
   meta("insert into RRL_CELLS(CELL,WARE_ID,X,Y,Z,OTBOR,IS_SYSTEM,LIMIT_HEIGHT,LIMIT_WEIGHT)values(:c,:ware,0,0,0,0,:sys,0,0)",c=cell,sys=system)
   meta("insert into RRL_STOCK_POLICY_GUARD(POLICY_KEY,LOCK_ID)select RRL_STOCK_LOCK_API.resource_key('CELL',:c),nvl(max(LOCK_ID),900000000)+1 from RRL_STOCK_POLICY_GUARD",c=cell)
  meta("update RRL_RECEIPT_WARE_SETTINGS set DEFER_WAIT_CELL=:c where WARE_ID=:ware",c=wait)
  mover=CaseCarrierMove(StockPosting())
  for ct,cl,carrier,qty,cell in lines:
   moved=mover.execute("PRE987:"+tag+":"+str(ct),"admin",int(ct),carrier,control,1);assert moved["content_version"]==2
  q.execute("select TRANSPORTTYPE from RRL_TRANSPORT_TYPE where TRANSPORTTYPE='15'");trtype=q.fetchone()[0]
  q.execute("select min(ID)from RRL_TR_VODITEL where ID>0");driver=q.fetchone()[0]
  vehicle=int(q.callfunc("RRL_TR_VEHICLE_ADD",oracledb.DB_TYPE_NUMBER,["QM"+tag,trtype,40,2,0,None]));conn.commit()
  source_trip=seq("RRL_TRANSPORT_TASK_SQ");target_trip=seq("RRL_TRANSPORT_TASK_SQ");dock="QD"+tag
  meta("insert into RRL_TT_DOCK(DOCK,WARE_ID,DOCK_IS_BLOCKED)values(:dock,:ware,0)",dock=dock)
  for trip,offset in((source_trip,1),(target_trip,2)):
   meta("insert into RRL_TRANSPORT_TASK(ID,TRANSPORT,TRANSTYPE,CONDITION,SHIPMENT_DATE,VODITEL_ID,DOCK,DELETED)values(:id,:plate,:typ,'Спланирован',trunc(sysdate)+:d,:driver,:dock,0)",id=trip,plate="QM"+tag,typ=trtype,d=offset,driver=driver,dock=dock)
  meta("update RRL_SBORKA_PALLETS set TRANSTASK_ID=:trip where ST_NUMBER=:st",trip=source_trip,st=st)
  record.update(st=st,wait=wait,control=control,source_trip=source_trip,target_trip=target_trip,stage="PREPARED");save()
  defer=StDeferral(OracleGateway());seen=defer.context(st,"admin");prep=seen["physical_preparation"]
  assert prep["state"]=="PREPARED_CASES"and prep["case_count"]==2 and prep["lot_count"]==2,prep
  decision="DEC987:"+tag;body={"st_number":st,"target_trip_id":target_trip,"expected_version":seen["version"],"source_hash":seen["source_hash"],"reason":"Two fully prepared CASE places on one existing ST","reference":"MULTI987:"+tag}
  result=defer.defer(decision,body,"admin");assert defer.defer(decision,body,"admin")==result
  record.update(decision=decision,decision_body=body,decision_result=result,stage="DEFERRED");save()
  def plan():
   out=q.var(oracledb.DB_TYPE_CLOB);q.callproc("RRL_ST_DEFER_WAIT_API.plan_waiting",["PLAN987:"+tag,decision,"admin",out]);return read_oracle_json(out.getvalue())
  trial=plan();assert len(trial["tasks"])==2;conn.rollback()
  q.execute("select count(*)from RRL_ST_DEFER_WAIT_RUN where OPERATION_ID=:op",op="PLAN987:"+tag);assert q.fetchone()==(0,)
  planned=plan();conn.commit();assert plan()==planned;conn.rollback()
  record.update(plan=planned,stage="PLANNED");save()
  results=[]
  for i,item in enumerate(planned["tasks"]):
   task=int(item["task_id"]);caseid=int(item["case_pick_task_id"]);carrier=item["pallet_identifier"]
   request=WarehouseTaskStatusRequest(operation_id="MOVE987:"+tag+":"+str(caseid),fact_qty="1",updated_by="admin",scanned_pallet=carrier,scanned_from_cell=control,scanned_to_cell=wait)
   moved=complete_existing_task(OracleGateway(),task,request,"admin");assert complete_existing_task(OracleGateway(),task,request,"admin")==moved
   results.append({"task":task,"case":caseid,"request":request.model_dump(mode="json"),"result":moved});record.update(moves=results,stage="PARTIAL"if i==0 else"DONE");save()
   # The first completion must not invalidate the other frozen member.
   q.execute("select STATUS from RRL_WAREHOUSE_TASK where TASK_ID=:id",id=task);assert q.fetchone()==("DONE",)
  for caseid,*unused in lines:
   q.execute("select c.CONTENT_VERSION,f.PICKED_CONTENT_VERSION,c.CURRENT_CELL from RRL_CASE_PICK_TASK c join RRL_CUSTOMER_ORDER_FULFILLMENT f on f.PICKED_CASE_TASK_ID=c.CASE_PICK_TASK_ID where c.CASE_PICK_TASK_ID=:id",id=caseid);assert q.fetchone()==(3,3,wait)
  q.execute("select sum(r.REMAIN),sum(r.HARD_RESERVED_BASE),min(r.CELL),max(r.CELL)from RRL_REMAINS r join RRL_CASE_CARRIER_LOT l on l.LOT_UID=r.UID_POLETA join RRL_CASE_PICK_TASK ct on ct.CASE_PICK_TASK_ID=l.CASE_PICK_TASK_ID where ct.PICK_WAVE_ID=:w and r.REMAIN>0",w=wave);assert q.fetchone()==(20,20,wait,wait)
  q.execute("select sum(BASE_QTY),count(*)from RRL_WAREHOUSE_TASK_STOCK_MOVE where OPERATION_ID in(:a,:b)",a=results[0]["request"]["operation_id"],b=results[1]["request"]["operation_id"]);assert q.fetchone()==(20,2)
  q.execute("select sum(r.REMAIN),sum(r.HARD_RESERVED_BASE)from RRL_REMAINS r join RRL_CELLS c on c.CELL=r.CELL where c.WARE_ID=6667491");assert q.fetchone()==(20,20)
  record["evidence"]={"single_st":True,"cases":2,"task_places":"1+1","goods_by_case":["12","8"],"physical_total":"20","hard_total":"20","case_ff_versions":"3/3 each","sibling_after_first_completion":True,"plan_rollback":True,"exact_replays":True,"protected_ware_unchanged":True};save()
  print("PASS987 one original ST/two actual preparedCASE12+8 -> plan rollback/replay -> firstDONE does not invalidate sibling -> bothDONE1CASE/currentFF3/CT3/P20H20/journals12+8/protectedWARE",flush=True)
 except BaseException as exc:
  record["error"]=str(exc);save();raise
