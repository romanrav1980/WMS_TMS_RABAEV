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
 ware=100000+int(tag[:6],16)
 meta("insert into RRL_WARES(ID,NAME,PREFIX) values(:w,:n,:p)",w=ware,n="Target private "+tag,p="Q"+tag[:2])
 for cell in (src,dst,"CPT_"+str(ware)):

  meta("insert into RRL_CELLS(CELL,WARE_ID,X,Y,Z,OTBOR,IS_SYSTEM) values(:c,:w,0,0,0,:pick,:sys)",c=cell,pick=int(cell==dst),sys=int(cell.startswith('CPT_')),w=ware)
  meta("insert into RRL_STOCK_POLICY_GUARD(POLICY_KEY,LOCK_ID) select RRL_STOCK_LOCK_API.resource_key('CELL',:c),nvl(max(LOCK_ID),900000000)+1 from RRL_STOCK_POLICY_GUARD",c=cell)
 face=seq("RRL_PICK_FACE_SQ")
 meta("insert into RRL_PICK_FACE(PICK_FACE_ID,WARE_ID,CELL_CODE,MAX_VOLUME,CREATED_BY) values(:id,:w,:c,0.3,'admin')",id=face,c=dst,w=ware)
 meta("insert into RRL_PICK_FACE_ARTICUL(PICK_FACE_ARTICUL_ID,PICK_FACE_ID,ARTICUL,BOX_VOLUME_M3,USE_ARTICUL_REPLENISH_RULE,REPLENISHMENT_QTY_MODE) values(RRL_PICK_FACE_ARTICUL_SQ.nextval,:id,:a,0.24,0,'FULL_PALLET')",id=face,a=article)
 revision=int(q.callfunc("REVIZION.create_revizion",oracledb.DB_TYPE_NUMBER,[ware,"admin"]));conn.commit()
 orders=[];plans=[];wave=None;service=PickingService()
 try:
  post("INVENTORY_REGISTER_LOT",{"uid":lot,"cell":src,"article":article,"quantity":"20","expiry_date":"2030-01-01","price":0,"reason":"Native complete warehouse flow"},{"revision_id":revision})
  for qty in (12,8):
   order=seq("RRL_CUSTOMER_ORDER_SQ");orders.append(order)
   meta("insert into RRL_CUSTOMER_ORDER(CUSTOMER_ORDER_ID,ORDER_NO,CUSTOMER_ID,WARE_ID) values(:id,:no,:c,:w)",id=order,no=lot+str(qty),c=customer,w=ware)
   meta("insert into RRL_CUSTOMER_ORDER_ROW(CUSTOMER_ORDER_ROW_ID,CUSTOMER_ORDER_ID,LINE_NO,ARTICUL,ORDER_QTY,UNIT_CODE) values(RRL_CUSTOMER_ORDER_ROW_SQ.nextval,:o,1,:a,:qty,'EA')",o=order,a=article,qty=qty)
   plan=service.create_plan(PickingPlanCreateRequest(customer_order_id=order,created_by="admin"));plans.append(plan)
   q.execute("select TASK_TYPE,QTY,TARGET_CELL_CODE from RRL_PICK_TASK where PICK_PLAN_ID=:p",p=plan)
   assert q.fetchone()==("CASE_PICK",qty,dst),"Free portion of a shared physical pallet classified FULL"
  wave=service.create_wave(PickWaveCreateRequest(wave_code=lot,ware_id=ware,created_by="admin"))
  for plan in plans:service.add_wave_plan(wave,PickWaveAddPlanRequest(pick_plan_id=plan,created_by="admin"))
  service.preview_wave(wave,PickWaveActionRequest(updated_by="admin"))
  launch=PickWaveActionRequest(updated_by="admin",operation_id="NATIVE.LAUNCH:"+tag)
  post("WAVE_LAUNCH",{},{"wave_id":wave},launch.operation_id)
  q.execute("select sum(BASE_QTY) from RRL_STOCK_RESERVATION where SOURCE_DOC_TYPE='PICK_WAVE' and SOURCE_DOC_ID=:w and RESERVATION_DOMAIN='PICKING' and STATUS='ACTIVE'",w=wave);assert q.fetchone()==(20,)

  post("INVENTORY_REGISTER_LOT",{"uid":other,"cell":dst,"article":article,"quantity":"4","expiry_date":"2030-01-01","price":0,"reason":"Existing target stock for sequential replacement"},{"revision_id":revision})
  meta("update RRL_CELLS set BLOCKED_FOR_REMAINS=1 where CELL=:c",c=dst)
  service._enrich_replenishment_settings(wave,"admin");service._refresh_replenishment_deficit(wave,"admin")
  from app.modules.inventory.infrastructure.wave_commands import reserve_wave_sources
  gateway=OracleGateway();reserve_wave_sources(gateway,wave,"admin")
  extra=lot+"B"
  post("INVENTORY_REGISTER_LOT",{"uid":extra,"cell":src,"article":article,"quantity":"12","expiry_date":"2030-01-01","price":0,"reason":"Second physical source for same existing owner"},{"revision_id":revision})
  q.execute("select PICK_TASK_ID,CUSTOMER_ORDER_ID,PICK_PLAN_ID,PICK_PLAN_LINE_ID from RRL_PICK_TASK where PICK_PLAN_ID=:plan",plan=plans[0]);pt,co,pp,pl=q.fetchone()
  q.execute("select RESERVATION_ID from RRL_STOCK_RESERVATION where SOURCE_DOC_TYPE='PICK_WAVE'and SOURCE_DOC_ID=:w and SOURCE_LINE_ID=:pt and RESERVATION_KIND='HARD'and BASE_QTY>0 and STATUS in('ACTIVE','ALLOCATED','PICKING')",w=wave,pt=pt);old=[r[0]for r in q];assert len(old)==1
  post("RESERVATION_RELEASE",{"reason":"Own explicit source rebalance"},{"reservation_id":int(old[0])})
  ids=[]
  for source_uid in (lot,extra):
   result=post("RESERVATION_CREATE",{"reservation_kind":"HARD","reservation_scope":"QTY","reservation_domain":"PICKING","source_doc_type":"PICK_WAVE","source_doc_id":wave,"source_line_id":int(pt),"customer_id":customer,"customer_order_id":int(co),"pick_plan_id":int(pp),"pick_plan_line_id":int(pl),"qty":"6","unit_code":"EA","articul":article,"uid_pallet":source_uid,"cell":src,"ware_id":ware},{"type":"STOCK_RESERVATION"})
   ids.append(result["reservation_id"])
  q.execute("select PICK_WAVE_REPLENISH_TASK_ID from RRL_PICK_WAVE_REPLENISH_TASK where PICK_WAVE_ID=:w and PICK_TASK_ID=:pt",w=wave,pt=pt);rt=int(q.fetchone()[0])
  meta("update RRL_PICK_WAVE_REPLENISH_TASK set SOURCE_RESERVATION_ID=:rid where PICK_WAVE_REPLENISH_TASK_ID=:rt",rid=ids[0],rt=rt)
  q.execute("select PICK_TASK_ID,CUSTOMER_ORDER_ID,PICK_PLAN_ID,PICK_PLAN_LINE_ID from RRL_PICK_TASK where PICK_PLAN_ID=:plan",plan=plans[1]);pt2,co2,pp2,pl2=q.fetchone()
  q.execute("select RESERVATION_ID from RRL_STOCK_RESERVATION where SOURCE_DOC_TYPE='PICK_WAVE'and SOURCE_DOC_ID=:w and SOURCE_LINE_ID=:pt and RESERVATION_KIND='HARD'and BASE_QTY>0 and STATUS in('ACTIVE','ALLOCATED','PICKING')",w=wave,pt=pt2)
  for(row_id,)in q.fetchall():post("RESERVATION_RELEASE",{"reason":"Private partial shared-owner split"},{"reservation_id":int(row_id)})
  second_ids=[]
  for source_uid in (lot,extra):
   result=post("RESERVATION_CREATE",{"reservation_kind":"HARD","reservation_scope":"QTY","reservation_domain":"PICKING","source_doc_type":"PICK_WAVE","source_doc_id":wave,"source_line_id":int(pt2),"customer_id":customer,"customer_order_id":int(co2),"pick_plan_id":int(pp2),"pick_plan_line_id":int(pl2),"qty":"4","unit_code":"EA","articul":article,"uid_pallet":source_uid,"cell":src,"ware_id":ware},{"type":"STOCK_RESERVATION"})
   second_ids.append(result["reservation_id"])
  q.execute("select PICK_WAVE_REPLENISH_TASK_ID from RRL_PICK_WAVE_REPLENISH_TASK where PICK_WAVE_ID=:w and PICK_TASK_ID=:pt",w=wave,pt=pt2);rt2=int(q.fetchone()[0])
  meta("update RRL_PICK_WAVE_REPLENISH_TASK set SOURCE_RESERVATION_ID=:rid where PICK_WAVE_REPLENISH_TASK_ID=:rt",rid=second_ids[0],rt=rt2)
  meta("update RRL_CELLS set BLOCKED_FOR_REMAINS=0 where CELL=:c",c=dst)
  service._enrich_replenishment_settings(wave,"admin");service._refresh_replenishment_deficit(wave,"admin")
  meta("update RRL_PICK_FACE set MAX_VOLUME=0.1 where PICK_FACE_ID=:id",id=face)
  service._enrich_replenishment_settings(wave,"admin");service._refresh_replenishment_deficit(wave,"admin")
  reserve_wave_sources(gateway,wave,"admin",[rt])
  q.execute("select REMAIN,HARD_RESERVED_BASE from RRL_REMAINS where UID_POLETA=:u and CELL=:c",u=lot,c=src);assert q.fetchone()==(20,10)
  q.execute("select REMAIN,HARD_RESERVED_BASE from RRL_REMAINS where UID_POLETA=:u and CELL=:c",u=extra,c=src);assert q.fetchone()==(12,10)
  q.execute("select REMAIN,HARD_RESERVED_BASE from RRL_REMAINS where UID_POLETA=:u and CELL=:c",u=other,c=dst);assert q.fetchone()==(4,0)
  meta("update RRL_PICK_FACE set MAX_VOLUME=0.5 where PICK_FACE_ID=:id",id=face)
  service._enrich_replenishment_settings(wave,"admin");service._refresh_replenishment_deficit(wave,"admin")
  reserve_wave_sources(gateway,wave,"admin",[rt])
  q.execute("select REMAIN,HARD_RESERVED_BASE from RRL_REMAINS where UID_POLETA=:u and CELL=:c",u=lot,c=src);assert q.fetchone()==(20,6)
  q.execute("select REMAIN,HARD_RESERVED_BASE from RRL_REMAINS where UID_POLETA=:u and CELL=:c",u=extra,c=src);assert q.fetchone()==(12,10)
  q.execute("select REMAIN,HARD_RESERVED_BASE from RRL_REMAINS where UID_POLETA=:u and CELL=:c",u=other,c=dst);assert q.fetchone()==(4,4)
  q.execute("select RESERVE_REQUEST_JSON from RRL_PICK_WAVE_REPLENISH_TASK where PICK_WAVE_REPLENISH_TASK_ID=:rt",rt=rt);wire=q.fetchone()[0];wire=json.loads(wire.read()if hasattr(wire,"read")else wire)
  from app.modules.inventory.contracts_stock import StockCommand
  from app.modules.inventory.infrastructure.stock_posting_uow import StockPosting
  command=StockCommand(operation_id=wire["operation_id"],command_type=wire["command_type"],actor=wire["actor"],lines=(),source=wire["source"],metadata=wire["metadata"])
  first=StockPosting().post(command);assert StockPosting().post(command)==first
  Path("tmp/context850.json").write_text(json.dumps({"wave":wave,"rt":rt,"article":article,"source_uid":lot,"continuation_uid":extra,"target_uid":other,"source_cell":src,"target_cell":dst,"operation_id":wire["operation_id"],"status":"SEQUENTIAL_REBIND_PASS"},indent=2),encoding="utf-8")
  q.execute("select SOURCE_RESERVATION_ID,QTY,DEMAND_BASE_QTY,PALLET_UID from RRL_PICK_WAVE_REPLENISH_TASK where PICK_WAVE_REPLENISH_TASK_ID=:rt",rt=rt)
  assert q.fetchone()==(ids[0],20,2,lot),"First retained whole source was not selected"
  from app.modules.resources.public import sync_existing_wave_tasks
  reserve_wave_sources(gateway,wave,"admin")
  sync_existing_wave_tasks(gateway,wave,"admin")
  q.execute("select TASK_ID,UID_PALLET,FROM_CELL,TO_CELL,QTY from RRL_WAREHOUSE_TASK where TASK_SOURCE='WAVE'and SOURCE_DOC_ID=:w and TASK_TYPE='REPLENISHMENT'and STATUS not in('DONE','CANCELLED')",w=wave)
  physical=q.fetchall();assert len(physical)==1,physical
  tid,puid,pfrom,pto,pqty=physical[0];assert puid==lot and pqty==20,physical
  moved=post("TASK_COMPLETE",{"fact_qty":"20","scanned_pallet":puid,"scanned_from_cell":pfrom,"scanned_to_cell":pto},{"task_id":int(tid)},"SEQ850.MOVE:"+tag)
  assert post("TASK_COMPLETE",{"fact_qty":"20","scanned_pallet":puid,"scanned_from_cell":pfrom,"scanned_to_cell":pto},{"task_id":int(tid)},"SEQ850.MOVE:"+tag)==moved
  q.execute("select REMAIN,HARD_RESERVED_BASE from RRL_REMAINS where UID_POLETA=:u and CELL=:c",u=lot,c=dst);assert q.fetchone()==(20,6)
  q.execute("select PICK_WAVE_REPLENISH_TASK_ID,DEMAND_BASE_QTY,STATUS from RRL_PICK_WAVE_REPLENISH_TASK where PARENT_REPLENISH_TASK_ID=:rt",rt=rt)
  next_rows=q.fetchall();assert len(next_rows)==1 and next_rows[0][1]==6,next_rows
  from app.modules.inventory.infrastructure.replenishment_continuation import ReplenishmentContinuation
  # A separate existing order/wave owns the ten free arrived units. This forces
  # the first owner's remaining six to come from its second physical source.
  third_order=seq("RRL_CUSTOMER_ORDER_SQ");orders.append(third_order)
  meta("insert into RRL_CUSTOMER_ORDER(CUSTOMER_ORDER_ID,ORDER_NO,CUSTOMER_ID,WARE_ID) values(:id,:no,:c,:w)",id=third_order,no=lot+"THIRD",c=customer,w=ware)
  meta("insert into RRL_CUSTOMER_ORDER_ROW(CUSTOMER_ORDER_ROW_ID,CUSTOMER_ORDER_ID,LINE_NO,ARTICUL,ORDER_QTY,UNIT_CODE) values(RRL_CUSTOMER_ORDER_ROW_SQ.nextval,:o,1,:a,14,'EA')",o=third_order,a=article)
  third_plan=service.create_plan(PickingPlanCreateRequest(customer_order_id=third_order,created_by="admin"));plans.append(third_plan)
  third_wave=service.create_wave(PickWaveCreateRequest(wave_code=lot+"T",ware_id=ware,created_by="admin"))
  service.add_wave_plan(third_wave,PickWaveAddPlanRequest(pick_plan_id=third_plan,created_by="admin"))
  service.preview_wave(third_wave,PickWaveActionRequest(updated_by="admin"))
  post("WAVE_LAUNCH",{},{ "wave_id":third_wave},"SEQ850.THIRD:"+tag)
  q.execute("select nvl(sum(BASE_QTY),0)from RRL_STOCK_RESERVATION where SOURCE_DOC_TYPE='PICK_WAVE'and SOURCE_DOC_ID=:w and RESERVATION_KIND='HARD'and STATUS in('ACTIVE','ALLOCATED','PICKING')",w=third_wave);assert q.fetchone()==(14,)
  q.execute("select SOURCE_DOC_ID,SOURCE_LINE_ID,UID_PALLET,CELL,BASE_QTY,STATUS from RRL_STOCK_RESERVATION where ARTICUL=:a and RESERVATION_KIND='HARD'and BASE_QTY>0 order by RESERVATION_ID",a=article)
  print("PRE_NEXT_OWNERS",q.fetchall(),flush=True)
  q.execute("select rt.PICK_WAVE_REPLENISH_TASK_ID,rt.STATUS,rt.SOURCE_RESERVATION_ID,rt.TARGET_CELL_CODE,RRL_STOCK_REPL_NEED.remaining_for_task(rt.PICK_TASK_ID,rt.TARGET_CELL_CODE),RRL_STOCK_REPL_CAPACITY.remaining_base_quantity(rt.TARGET_CELL_CODE,rt.ARTICUL,rt.PICK_WAVE_REPLENISH_TASK_ID),RRL_STOCK_REPL_ADMISSION.mode_for(rt.PICK_WAVE_REPLENISH_TASK_ID),w.STATUS from RRL_PICK_WAVE_REPLENISH_TASK rt join RRL_PICK_WAVE w on w.PICK_WAVE_ID=rt.PICK_WAVE_ID where rt.PARENT_REPLENISH_TASK_ID=:id",id=rt)
  print("PRE_NEXT_ROW",q.fetchall(),flush=True)
  q.execute("select sr.RESERVATION_ID,RRL_STOCK_REPL_SHARED.allowed(sr.UID_PALLET,sr.CELL,:dst,:ware,sr.RESERVATION_ID),RRL_STOCK_ELIGIBILITY.reason(sr.UID_PALLET,sr.CELL,:ware,0,0,0,'REPLENISH',sr.RESERVATION_ID,sr.ARTICUL)from RRL_STOCK_RESERVATION sr where sr.UID_PALLET=:p_uid and sr.BASE_QTY>0 and sr.RESERVATION_KIND='HARD'",dst=dst,ware=ware,p_uid=extra)
  print("PRE_NEXT_ADMISSION",q.fetchall(),flush=True)
  ReplenishmentContinuation(gateway,sync_existing_wave_tasks).reconcile(ware,"admin")
  q.execute("select TASK_ID,UID_PALLET,FROM_CELL,TO_CELL,QTY from RRL_WAREHOUSE_TASK where TASK_SOURCE='WAVE'and SOURCE_DOC_ID=:w and UID_PALLET=:p_uid and TASK_TYPE='REPLENISHMENT'and STATUS not in('DONE','CANCELLED')",w=wave,p_uid=extra)
  second=q.fetchall();assert len(second)==1,second
  q.execute("select SOURCE_RESERVATION_ID,STATUS,DEMAND_BASE_QTY from RRL_PICK_WAVE_REPLENISH_TASK where PICK_WAVE_REPLENISH_TASK_ID=:id",id=rt2)
  other_progress=q.fetchone();assert 0<other_progress[2]<=4 and other_progress[0] is not None,other_progress
  t2,u2,c2,d2,q2=second[0];assert u2==extra and q2==12,second
  moved2=post("TASK_COMPLETE",{"fact_qty":"12","scanned_pallet":u2,"scanned_from_cell":c2,"scanned_to_cell":d2},{"task_id":int(t2)},"SEQ850.SECOND:"+tag)
  assert post("TASK_COMPLETE",{"fact_qty":"12","scanned_pallet":u2,"scanned_from_cell":c2,"scanned_to_cell":d2},{"task_id":int(t2)},"SEQ850.SECOND:"+tag)==moved2
  q.execute("select nvl(sum(BASE_QTY),0)from RRL_STOCK_RESERVATION where SOURCE_DOC_TYPE='PICK_WAVE'and SOURCE_DOC_ID=:w and SOURCE_LINE_ID=:pt and CELL=:dst and RESERVATION_KIND='HARD'and STATUS in('ACTIVE','ALLOCATED','PICKING')",w=wave,pt=pt,dst=dst);assert q.fetchone()==(12,)
  q.execute("select REMAIN,HARD_RESERVED_BASE from RRL_REMAINS where UID_POLETA=:u and CELL=:c",u=extra,c=src);assert q.fetchone()==(0,0)
  q.execute("select nvl(sum(BASE_QTY),0)from RRL_STOCK_RESERVATION where SOURCE_DOC_TYPE='PICK_WAVE'and SOURCE_DOC_ID=:w and SOURCE_LINE_ID!=:pt and RESERVATION_KIND='HARD'and STATUS in('ACTIVE','ALLOCATED','PICKING')",w=wave,pt=pt);assert q.fetchone()==(8,)
  Path("tmp/context850.json").write_text(json.dumps({"wave":wave,"rt":rt,"task":int(tid),"next_rt":int(next_rows[0][0]),"article":article,"ware":ware,"target":dst,"source":src,"first_uid":lot,"second_uid":extra,"target_uid":other,"second_task":int(t2),"third_wave":int(third_wave),"partial_shared_rt":rt2,"stage":"PARTIAL_SHARED_RESUMED_OWNER12_OTHER8_THIRD14","stock_changed_only_by_original_TASK_COMPLETE":True},indent=2),encoding="utf-8")
  print("PASS850 partially covered shared owner requeued4; original next6 + shared whole12 second arrival; original12/other8/third14 preserved; same replay; cleanup follows",flush=True)
 finally:
  if wave is not None:
   q.execute("select CASE_PICK_TASK_ID,SSCC,CONTENT_VERSION from RRL_CASE_PICK_TASK where PICK_WAVE_ID=:w",w=wave)
   for ct,carrier,version in q.fetchall():
    q.execute("select LOT_UID from RRL_CASE_CARRIER_LOT where CASE_PICK_TASK_ID=:id",id=ct);lots=[r[0] for r in q.fetchall()]
    if lots:post("CASE_CARRIER_RETURN",{"destinations":{u:dst for u in lots},"scan_container":carrier,"expected_content_version":int(version),"reason":"End native wave fixture"},{"case_task_id":int(ct)})
   q.execute("select RESERVATION_ID from RRL_STOCK_RESERVATION where SOURCE_DOC_TYPE='PICK_WAVE' and SOURCE_DOC_ID in(select PICK_WAVE_ID from RRL_PICK_WAVE where WARE_ID=:w) and STATUS in('ACTIVE','ALLOCATED','PICKING') and BASE_QTY>0",w=ware)
   for (rid,) in q.fetchall():post("RESERVATION_RELEASE",{"reason":"End native fixture"},{"reservation_id":int(rid)})
   meta("update RRL_WAREHOUSE_TASK set STATUS='CANCELLED' where TASK_SOURCE='WAVE' and SOURCE_DOC_ID in(select PICK_WAVE_ID from RRL_PICK_WAVE where WARE_ID=:w) and STATUS not in('DONE','CANCELLED')",w=ware)
   meta("update RRL_PICK_WAVE_REPLENISH_TASK set STATUS='CANCELLED' where PICK_WAVE_ID in(select PICK_WAVE_ID from RRL_PICK_WAVE where WARE_ID=:w) and STATUS not in('DONE','CANCELLED')",w=ware)
   meta("update RRL_PICK_WAVE set STATUS='DONE' where WARE_ID=:w",w=ware)
  q.execute("select s.UID_POLETA,s.CELL,s.BASE_UOM,s.STOCK_VERSION from RRL_REMAINS s join RRL_PALLETS p on p.UID_PALLET=s.UID_POLETA where p.ARTICUL=:a and s.REMAIN>0",a=article)
  counts=[{"uid":u,"cell":cell,"article":article,"unit":unit,"quantity":"0","expected_stock_version":int(version),"unit_keys":[]} for u,cell,unit,version in q.fetchall()]
  if counts:post("INVENTORY_COUNT",{"reason":"End private native warehouse case","counts":counts},{"revision_id":revision})
  for plan in plans:meta("update RRL_PICK_RESERVATION set RESERVATION_STATUS='RELEASED' where PICK_PLAN_ID=:p and RESERVATION_STATUS='ACTIVE'",p=plan)
  print("Own P/H restored; native document and movement evidence retained",flush=True)
