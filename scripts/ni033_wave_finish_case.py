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
from app.modules.inventory.infrastructure.fullpal_shipment import FullPalletShipment
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
 q.execute("select ARTICUL from RRL_PALLETS where UID_PALLET='DS-BASE-B1'");article=q.fetchone()[0]
 q.execute("select min(CUSTOMER_ID) from RRL_CUSTOMER");customer=q.fetchone()[0]
 for cell in (src,dst):
  meta("insert into RRL_CELLS(CELL,WARE_ID,X,Y,Z,OTBOR,IS_SYSTEM) values(:c,1,0,0,0,0,0)",c=cell)
  meta("insert into RRL_STOCK_POLICY_GUARD(POLICY_KEY,LOCK_ID) select RRL_STOCK_LOCK_API.resource_key('CELL',:c),nvl(max(LOCK_ID),900000000)+1 from RRL_STOCK_POLICY_GUARD",c=cell)
 revision=int(q.callfunc("REVIZION.create_revizion",oracledb.DB_TYPE_NUMBER,[1,"admin"]));conn.commit()
 order,row,plan,pl,pt,wave,wt,task,st,ff=[seq(n) for n in ("RRL_CUSTOMER_ORDER_SQ","RRL_CUSTOMER_ORDER_ROW_SQ","RRL_PICK_PLAN_SQ","RRL_PICK_PLAN_LINE_SQ","RRL_PICK_TASK_SQ","RRL_PICK_WAVE_SQ","RRL_PICK_WAVE_TASK_SQ","RRL_WAREHOUSE_TASK_SQ","RRL_SBORKA_PALLETS_SQ","RRL_CUSTOMER_ORDER_FULF_SQ")]
 meta("insert into RRL_CUSTOMER_ORDER(CUSTOMER_ORDER_ID,ORDER_NO,CUSTOMER_ID,WARE_ID) values(:id,:no,:c,1)",id=order,no=lot,c=customer)
 meta("insert into RRL_CUSTOMER_ORDER_ROW(CUSTOMER_ORDER_ROW_ID,CUSTOMER_ORDER_ID,LINE_NO,ARTICUL,ORDER_QTY,UNIT_CODE) values(:id,:o,1,:a,3,'EA')",id=row,o=order,a=article)
 meta("insert into RRL_PICK_PLAN(PICK_PLAN_ID,CUSTOMER_ORDER_ID,CUSTOMER_ID,WARE_ID,STATUS) values(:id,:o,:c,1,'RELEASED')",id=plan,o=order,c=customer)
 meta("insert into RRL_PICK_PLAN_LINE(PICK_PLAN_LINE_ID,PICK_PLAN_ID,CUSTOMER_ORDER_ROW_ID,ARTICUL,REQUESTED_QTY,PLANNED_QTY,STATUS) values(:id,:p,:r,:a,3,3,'PLANNED_FULL')",id=pl,p=plan,r=row,a=article)
 meta("insert into RRL_PICK_TASK(PICK_TASK_ID,PICK_PLAN_ID,PICK_PLAN_LINE_ID,CUSTOMER_ORDER_ID,CUSTOMER_ID,TASK_TYPE,STATUS,ARTICUL,PALLET_UID,SOURCE_CELL_CODE,TARGET_CELL_CODE,QTY) values(:id,:p,:pl,:o,:c,'FULL_PALLET','NEW',:a,:u,:src,:dst,3)",id=pt,p=plan,pl=pl,o=order,c=customer,a=article,u=lot,src=src,dst=dst)
 meta("insert into RRL_PICK_WAVE(PICK_WAVE_ID,WAVE_CODE,WARE_ID,STATUS,CREATED_BY) values(:id,:code,1,'LAUNCHED','admin')",id=wave,code=lot)
 meta("insert into RRL_PICK_WAVE_TASK(PICK_WAVE_TASK_ID,PICK_WAVE_ID,PICK_TASK_ID,TASK_TYPE,STATUS,ARTICUL,PALLET_UID,QTY,SOURCE_CELL_CODE,TARGET_CELL_CODE) values(:id,:w,:p,'FULL_PALLET','NEW',:a,:u,3,:src,:dst)",id=wt,w=wave,p=pt,a=article,u=lot,src=src,dst=dst)
 meta("insert into RRL_WAREHOUSE_TASK(TASK_ID,TASK_TYPE,TASK_SOURCE,SOURCE_TASK_ID,SOURCE_DOC_TYPE,SOURCE_DOC_ID,UID_PALLET,FROM_CELL,TO_CELL,FROM_WARE_ID,TO_WARE_ID,QTY,UNIT_CODE,QTY_MODE,STATUS,ASSIGNED_TO,CREATED_BY) values(:id,'PICKING_MOVE','WAVE',:wt,'PICK_WAVE',:w,:u,:src,:dst,1,1,3,'EA','PALLET','ASSIGNED','admin','admin')",id=task,wt=wt,w=wave,u=lot,src=src,dst=dst)
 meta("insert into RRL_SBORKA_PALLETS(ID,PALLET_UID,ST_NUMBER,WARE_ID,CONDITION,ADDR) values(:id,:u,:u,1,0,'Own full-pallet ST')",id=st,u=st_uid)
 meta("insert into RRL_SBORKA_PALLET_ROWS(ID,PALLET_UID,ARTICUL,EI,QUANTITY) values(RRL_SBORKA_PALLET_ROWS_SQ.nextval,:u,:a,'BOX',0.125)",u=st_uid,a=article)
 meta("insert into RRL_CUSTOMER_ORDER_FULFILLMENT(FULFILLMENT_ID,CUSTOMER_ORDER_ID,LEGACY_SBORKA_PALLET_ID,PALLET_UID,STATUS,FACT_QTY) values(:id,:o,:st,:u,'PLANNED',0)",id=ff,o=order,st=st,u=st_uid)
 try:
  for u,cell in ((lot,src),(other,dst)):
   post("INVENTORY_REGISTER_LOT",{"uid":u,"cell":cell,"article":article,"quantity":"3","expiry_date":"2030-01-01","price":0,"reason":"Full-pallet binding fixture"},{"revision_id":revision})
   post("RESERVATION_CREATE",{"uid_pallet":u,"cell":cell,"articul":article,"qty":"3","unit_code":"EA","ware_id":1,"reservation_kind":"HARD","reservation_scope":"PALLET","reservation_domain":"PICKING","source_doc_type":"PICK_WAVE","source_doc_id":wave,"source_line_id":pt,"customer_order_id":order,"customer_id":customer,"pick_plan_id":plan,"pick_plan_line_id":pl},{"type":"PICK_WAVE","id":wave})
  post("WAVE_PICK_RELEASE",{},{"wave_id":wave})
  try:post("WAVE_EXECUTION_FINISH",{},{"wave_id":wave});raise AssertionError("Unperformed wave closed")
  except oracledb.DatabaseError as exc:assert "WAVE_EXECUTION_OR_SHIPPING_PENDING" in str(exc),str(exc)
  before=OrderExecution(OracleGateway()).get(order);assert before["lines"][0]["picked_quantity"]=="0"
  try:post("PICK_PALLET_BIND_SHIPMENT",{"shipment_identifier":st_uid,"scanned_pallet":lot,"expected_stock_version":0},{"task_id":task});raise AssertionError("Unperformed task bound")
  except oracledb.DatabaseError as exc:assert "FULLPAL_CONFIRMED_MOVE_REQUIRED" in str(exc),str(exc)
  completed=post("TASK_COMPLETE",{"fact_qty":"3","scanned_pallet":lot,"scanned_from_cell":src,"scanned_to_cell":dst},{"task_id":task})
  preview=FullPalletShipment(OracleGateway()).preview(task)
  assert preview["pallet_identifier"]==lot and preview["quantity"]=="3"
  body={"shipment_identifier":st_uid,"scanned_pallet":lot,"expected_stock_version":int(preview["stock_version"])}
  try:post("SHIP_PALLET",{},{"pallet_identifier":st_uid});raise AssertionError("Unbound physical pallet shipped")
  except oracledb.DatabaseError as exc:assert "FULLPAL_PHYSICAL_SHIPMENT_BIND_REQUIRED" in str(exc),str(exc)
  op="FULL.BIND:"+tag;bound=post("PICK_PALLET_BIND_SHIPMENT",body,{"task_id":task},op)
  assert post("PICK_PALLET_BIND_SHIPMENT",body,{"task_id":task},op)==bound
  q.execute("select STATUS,FACT_QTY,FACT_UOM,PICKED_WAREHOUSE_TASK_ID,PICKED_PALLET_UID from RRL_CUSTOMER_ORDER_FULFILLMENT where FULFILLMENT_ID=:id",id=ff)
  assert q.fetchone()==("PICKED",3,"EA",task,lot)
  assert OrderExecution(OracleGateway()).get(order)["lines"][0]["picked_quantity"]=="3"
  meta("update RRL_SBORKA_PALLET_ROWS set EI='EA',QUANTITY=1 where PALLET_UID=:u",u=st_uid)
  try:post("SHIP_PALLET",{},{"pallet_identifier":st_uid});raise AssertionError("Bound whole pallet partially shipped after ST edit")
  except oracledb.DatabaseError as exc:assert "FULLPAL_BOUND_WHOLE_COMPOSITION_REQUIRED" in str(exc),str(exc)
  q.execute("select REMAIN,HARD_RESERVED_BASE from RRL_REMAINS where UID_POLETA=:u and CELL=:c",u=lot,c=dst);assert q.fetchone()==(3,3)
  meta("update RRL_SBORKA_PALLET_ROWS set EI='BOX',QUANTITY=0.125 where PALLET_UID=:u",u=st_uid)
  shipop="FULL.SHIP:"+tag;shipped=post("SHIP_PALLET",{},{"pallet_identifier":st_uid},shipop)
  assert post("SHIP_PALLET",{},{"pallet_identifier":st_uid},shipop)==shipped
  q.execute("select REMAIN,HARD_RESERVED_BASE from RRL_REMAINS where UID_POLETA=:u and CELL=:c",u=lot,c=dst);assert q.fetchone()==(0,0)
  q.execute("select REMAIN,HARD_RESERVED_BASE from RRL_REMAINS where UID_POLETA=:u and CELL=:c",u=other,c=dst);assert q.fetchone()==(3,3)
  q.execute("select STATUS,FACT_QTY,FACT_UOM,SHIPPED_OPERATION_ID from RRL_CUSTOMER_ORDER_FULFILLMENT where FULFILLMENT_ID=:id",id=ff);assert q.fetchone()==("SHIPPED",3,"EA",shipop)
  from app.modules.inventory.infrastructure.wave_execution import WaveExecution
  lifecycle=WaveExecution(OracleGateway())
  waiting=lifecycle.preview(wave, "admin");assert not waiting["ready"] and any(x["reason"]=="ACTIVE_WAVE_HARD_REMAINS" for x in waiting["items"])
  try:post("WAVE_EXECUTION_FINISH",{},{"wave_id":wave});raise AssertionError("Wave with active HARD closed")
  except oracledb.DatabaseError as exc:assert "WAVE_EXECUTION_OR_SHIPPING_PENDING" in str(exc),str(exc)
  q.execute("select RESERVATION_ID from RRL_STOCK_RESERVATION where UID_PALLET=:u and SOURCE_DOC_ID=:w and BASE_QTY>0 and STATUS in('ACTIVE','ALLOCATED','PICKING')",u=other,w=wave)
  for (rid,) in q.fetchall():post("RESERVATION_RELEASE",{"reason":"Release separate fixture owner after preserved-stock proof"},{"reservation_id":int(rid)})
  assert lifecycle.preview(wave, "admin")["ready"]
  finishop="WAVE.FINISH:"+tag
  finished=post("WAVE_EXECUTION_FINISH",{},{"wave_id":wave},finishop);assert finished["completed"] and finished["status"]=="DONE"
  assert post("WAVE_EXECUTION_FINISH",{},{"wave_id":wave},finishop)==finished
  print("PASS root wave finish denied before physical execution and while own HARD remains; shipped facts + no HARD -> DONE/replay",flush=True)
  print("PASS actual full pallet3 -> ST0.125BOX binding + BASE3/provenance/replay -> pinned shipment consumes this pallet only, other owned pallet remains3",flush=True)
 finally:
  q.execute("select RESERVATION_ID from RRL_STOCK_RESERVATION where SOURCE_DOC_TYPE='PICK_WAVE' and SOURCE_DOC_ID=:w and STATUS in('ACTIVE','ALLOCATED','PICKING') and BASE_QTY>0",w=wave)
  for (rid,) in q.fetchall():post("RESERVATION_RELEASE",{"reason":"End private full-pallet fixture"},{"reservation_id":int(rid)})
  q.execute("select UID_POLETA,CELL,BASE_UOM,STOCK_VERSION from RRL_REMAINS where UID_POLETA in(:a,:b) and REMAIN>0",a=lot,b=other)
  counts=[{"uid":u,"cell":cell,"article":article,"unit":unit,"quantity":"0","expected_stock_version":int(version),"unit_keys":[]} for u,cell,unit,version in q.fetchall()]
  if counts:post("INVENTORY_COUNT",{"reason":"End private full-pallet fixture","counts":counts},{"revision_id":revision})
  meta("update RRL_WAREHOUSE_TASK set STATUS='CANCELLED' where TASK_ID=:id and STATUS!='DONE'",id=task)
  meta("update RRL_PICK_WAVE set STATUS='DONE' where PICK_WAVE_ID=:w",w=wave)
  print("Own P/H restored; immutable operation and fulfillment history retained",flush=True)
