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
 alt1="QA"+tag;alt2="QB"+tag
 for cell in (src,dst,alt1,alt2):
  meta("insert into RRL_CELLS(CELL,WARE_ID,X,Y,Z,OTBOR,IS_SYSTEM) values(:c,1,0,0,0,:pick,0)",c=cell,pick=int(cell!=src))
  meta("insert into RRL_STOCK_POLICY_GUARD(POLICY_KEY,LOCK_ID) select RRL_STOCK_LOCK_API.resource_key('CELL',:c),nvl(max(LOCK_ID),900000000)+1 from RRL_STOCK_POLICY_GUARD",c=cell)
 face=seq("RRL_PICK_FACE_SQ")
 meta("insert into RRL_PICK_FACE(PICK_FACE_ID,WARE_ID,CELL_CODE,MAX_VOLUME,CREATED_BY) values(:id,1,:c,0.05,'admin')",id=face,c=dst)
 meta("insert into RRL_PICK_FACE_ARTICUL(PICK_FACE_ARTICUL_ID,PICK_FACE_ID,ARTICUL,BOX_VOLUME_M3,USE_ARTICUL_REPLENISH_RULE,REPLENISHMENT_QTY_MODE) values(RRL_PICK_FACE_ARTICUL_SQ.nextval,:id,:a,0.24,0,'FULL_PALLET')",id=face,a=article)
 route=seq("RRL_PICK_ROUTE_SQ")
 meta("insert into RRL_PICK_ROUTE(PICK_ROUTE_ID,ROUTE_CODE,ROUTE_NAME,WARE_ID) values(:id,:c,'Private source-group route',1)",id=route,c="MULTI"+tag)
 for cell in (dst,alt1,alt2):
  meta("insert into RRL_PICK_ROUTE_CELL(PICK_ROUTE_CELL_ID,PICK_ROUTE_ID,WARE_ID,CELL_CODE,PICK_SEQUENCE) values(RRL_PICK_ROUTE_CELL_SQ.nextval,:r,1,:c,:n)",r=route,c=cell,n=(dst,alt1,alt2).index(cell)+1)
  if cell!=dst:
   meta("insert into RRL_PICK_FACE(PICK_FACE_ID,WARE_ID,CELL_CODE,MAX_VOLUME,PICK_FACE_TYPE,CREATED_BY) values(RRL_PICK_FACE_SQ.nextval,1,:c,0.1,'DYNAMIC','admin')",c=cell)
 revision=int(q.callfunc("REVIZION.create_revizion",oracledb.DB_TYPE_NUMBER,[1,"admin"]));conn.commit()
 orders=[];plans=[];wave=None;service=PickingService()
 try:
  for lot_uid in (lot,other):
   post("INVENTORY_REGISTER_LOT",{"uid":lot_uid,"cell":src,"article":article,"quantity":"10","expiry_date":"2030-01-01","price":0,"reason":"Two existing physical-source groups"},{"revision_id":revision})
  for qty in (6,6):
   order=seq("RRL_CUSTOMER_ORDER_SQ");orders.append(order)
   meta("insert into RRL_CUSTOMER_ORDER(CUSTOMER_ORDER_ID,ORDER_NO,CUSTOMER_ID,WARE_ID) values(:id,:no,:c,1)",id=order,no=lot+str(qty),c=customer)
   meta("insert into RRL_CUSTOMER_ORDER_ROW(CUSTOMER_ORDER_ROW_ID,CUSTOMER_ORDER_ID,LINE_NO,ARTICUL,ORDER_QTY,UNIT_CODE) values(RRL_CUSTOMER_ORDER_ROW_SQ.nextval,:o,1,:a,:qty,'EA')",o=order,a=article,qty=qty)
   plan=service.create_plan(PickingPlanCreateRequest(customer_order_id=order,created_by="admin"));plans.append(plan)
   q.execute("select TASK_TYPE,QTY,TARGET_CELL_CODE from RRL_PICK_TASK where PICK_PLAN_ID=:p",p=plan)
   rows=q.fetchall();assert sum(r[1] for r in rows)==qty and all(r[0]=="CASE_PICK" and r[2]==dst for r in rows),rows
  wave=service.create_wave(PickWaveCreateRequest(wave_code=lot,ware_id=1,created_by="admin"))
  meta("update RRL_PICK_WAVE set ROUTE_ID=:r where PICK_WAVE_ID=:w",r=route,w=wave)
  for plan in plans:service.add_wave_plan(wave,PickWaveAddPlanRequest(pick_plan_id=plan,created_by="admin"))
  service.preview_wave(wave,PickWaveActionRequest(updated_by="admin"))
  launch=PickWaveActionRequest(updated_by="admin",operation_id="NATIVE.LAUNCH:"+tag)
  service.launch_wave(wave,launch)
  q.execute("select TARGET_CELL_CODE,sum(QTY),count(*) from RRL_PICK_WAVE_TASK where PICK_WAVE_ID=:w and TASK_TYPE='CASE_PICK' group by TARGET_CELL_CODE order by TARGET_CELL_CODE",w=wave)
  groups=q.fetchall();assert len(groups)==2 and sum(r[1] for r in groups)==12 and {r[0] for r in groups}=={alt1,alt2},groups
  q.execute("select TARGET_CELL_CODE,DEMAND_QTY,TASK_COUNT from RRL_PICK_WAVE_DEMAND where PICK_WAVE_ID=:w and DEMAND_QTY>0 order by TARGET_CELL_CODE",w=wave)
  assert q.fetchall()==groups
  q.execute("select TASK_ID,UID_PALLET,FROM_CELL,TO_CELL,QTY from RRL_WAREHOUSE_TASK where TASK_SOURCE='WAVE' and SOURCE_DOC_ID=:w and TASK_TYPE='REPLENISHMENT' and STATUS not in('DONE','CANCELLED')",w=wave)
  tasks=q.fetchall();assert len(tasks)==2 and {r[3] for r in tasks}=={alt1,alt2} and all(r[4]==10 for r in tasks),tasks
  for task,uid,from_cell,to_cell,qty in tasks:
   post("TASK_COMPLETE",{"fact_qty":"10","scanned_pallet":uid,"scanned_from_cell":from_cell,"scanned_to_cell":to_cell},{"task_id":int(task)})
  q.execute("select CELL,sum(REMAIN),sum(HARD_RESERVED_BASE) from RRL_REMAINS r join RRL_PALLETS p on p.UID_PALLET=r.UID_POLETA where p.ARTICUL=:a and r.REMAIN>0 group by CELL",a=article)
  state=q.fetchall();assert len(state)==2 and sorted((r[1],r[2]) for r in state)==[(10,2),(10,10)],state
  release=post("WAVE_PICK_RELEASE",{},{"wave_id":wave});assert release["released_at"]
  print("PASS native plans6+6 / two physical pallets10+10 -> existing source groups10+2 -> two dynamic faces -> whole moves10+10 -> HARD10+2/free8 -> pick release",flush=True)
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
