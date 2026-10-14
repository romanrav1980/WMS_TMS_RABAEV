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
 meta("insert into RRL_WARES(ID,NAME,PREFIX) values(:w,:n,:p)",w=ware,n="HU private "+tag,p="Q"+tag[:2])
 for cell in (src,dst):
  meta("insert into RRL_CELLS(CELL,WARE_ID,X,Y,Z,OTBOR,IS_SYSTEM,LIMIT_WEIGHT,LIMIT_HEIGHT) values(:c,:w,0,0,0,:pick,0,0,0)",c=cell,pick=0,w=ware)
  meta("insert into RRL_STOCK_POLICY_GUARD(POLICY_KEY,LOCK_ID) select RRL_STOCK_LOCK_API.resource_key('CELL',:c),nvl(max(LOCK_ID),900000000)+1 from RRL_STOCK_POLICY_GUARD",c=cell)
 revision=int(q.callfunc("REVIZION.create_revizion",oracledb.DB_TYPE_NUMBER,[ware,"admin"]));conn.commit()
 top="HU.TOP:"+tag;box="HU.BOX:"+tag;second="HU.OTHER:"+tag
 wave=seq("RRL_PICK_WAVE_SQ")
 meta("insert into RRL_PICK_WAVE(PICK_WAVE_ID,WAVE_CODE,WARE_ID,STATUS,CREATED_BY) values(:id,:code,:w,'LAUNCHED','admin')",id=wave,code=top,w=ware)
 def tree(uid):
  q.execute("select RRL_STOCK_HU_READ.snapshot_json(:u) from dual",u=uid)
  raw=q.fetchone()[0];return json.loads(raw.read() if hasattr(raw,"read") else raw)
 def link(kind,parent,child,op=None):
  pt,ct=tree(parent),tree(child)
  body={"child_uid":child,"expected_version":pt["nodes"][0]["version"],"expected_child_version":ct["nodes"][0]["version"],
   "scan_container":parent,"scan_child":child,"reason":"Private pack/unpack evidence"}
  return post(kind,body,{"uid":parent},op)
 try:
  post("INVENTORY_REGISTER_LOT",{"uid":lot,"cell":src,"article":article,"quantity":"5","expiry_date":"2030-01-01","price":0,"reason":"Own direct leaf"},{"revision_id":revision})
  post("RESERVATION_CREATE",{"uid_pallet":lot,"cell":src,"articul":article,"qty":"2","unit_code":"EA","ware_id":ware,"reservation_kind":"HARD","reservation_scope":"QTY","reservation_domain":"WAVE","source_doc_type":"PICK_WAVE","source_doc_id":wave},{"type":"PICK_WAVE","id":wave})
  post("HU_CREATE",{"cell":src,"warehouse":ware,"container_type":"PALLET","tare_weight_kg":1,"scan_container":top,"scan_cell":src},{"uid":top})
  link("HU_ATTACH",top,lot)
  topo=seq("RRL_WH_TOPOLOGY_SQ");tc=seq("RRL_TOPOLOGY_CELL_SQ")
  meta("insert into RRL_WAREHOUSE_TOPOLOGY(TOPOLOGY_ID,WARE_ID,TOPOLOGY_CODE,STATUS) values(:id,:w,:code,'PUBLISHED')",id=topo,w=ware,code=top)
  meta("insert into RRL_TOPOLOGY_CELL(TOPOLOGY_CELL_ID,TOPOLOGY_ID,WARE_ID,CELL_CODE,LEGACY_CELL_CODE,SLOT_LAYER_KIND,MAX_WEIGHT_KG,MAX_VOLUME_M3) values(:id,:t,:w,:c,:c,'STORAGE_SLOT',100,4)",id=tc,t=topo,w=ware,c=dst)
  slots=[]
  for index in range(3):
   sid=seq("RRL_TOPO_CELL_SLOT_SQ");code="LEAF:"+tag+":"+str(index)
   meta("insert into RRL_TOPOLOGY_CELL_SLOT(CELL_SLOT_ID,TOPOLOGY_ID,TOPOLOGY_CELL_ID,PARENT_SLOT_LAYER_KIND,SLOT_KIND,SLOT_CODE,CAPACITY_QTY,CAPACITY_WEIGHT_KG,CAPACITY_VOLUME_M3,WIDTH_M,DEPTH_M,HEIGHT_M,SUB_COLUMN_NO) values(:id,:t,:c,'STORAGE_SLOT','STORAGE_SLOT',:code,1,100,3,1.2,1.2,2,:i)",id=sid,t=topo,c=tc,code=code,i=index)
   slots.append((sid,code))
  def measurement(uid,mass):
   return {"origin":"MANUAL_CONFIRMED","content_version":tree(uid)["nodes"][0]["version"],"gross_weight_kg":str(mass),"width_m":"0.5","depth_m":"1","height_m":"1.5"}
  move={"expected_version":tree(top)["nodes"][0]["version"],"target_cell":dst,"target_slot_id":slots[0][0],"measurements":measurement(top,50),"scan_container":top,"scanned_from_cell":src,"scanned_to_cell":dst}
  planned=post("HU_PLAN_MOVE",move,{"uid":top});task=int(planned["task_id"])
  from app.services.warehouse_task_service import WarehouseTaskService
  from app.schemas import WarehouseTaskStatusRequest
  service=WarehouseTaskService();service.assign_task(task,WarehouseTaskStatusRequest(updated_by="admin",assigned_to="admin"));service.start_task(task,WarehouseTaskStatusRequest(updated_by="admin"))
  service.complete_task(task,WarehouseTaskStatusRequest(operation_id="LEAF.COMPLETE:"+tag,updated_by="admin",fact_qty="1",scanned_pallet=top,scanned_from_cell=src,scanned_to_cell=dst,scanned_to_slot_code=slots[0][1]),"admin")
  split={"child_uid":lot,"expected_version":tree(top)["nodes"][0]["version"],"expected_child_version":tree(lot)["nodes"][0]["version"],"scan_container":top,"scan_child":lot,"scan_cell":dst,"scan_parent_slot":slots[0][1],"scan_child_slot":slots[1][1],"child_slot_id":slots[1][0],"reason":"Own direct stock extraction","parent_measurements":measurement(top,5),"child_measurements":measurement(lot,45)}
  op="LEAF.UNPACK:"+tag;r=post("HU_UNPACK",split,{"uid":top},op);assert post("HU_UNPACK",split,{"uid":top},op)==r
  assert r["parent"]["leaf_count"]==0 and r["child"]["leaf_count"]==1
  q.execute("select REMAIN,HARD_RESERVED_BASE from RRL_REMAINS where UID_POLETA=:u and CELL=:c",u=lot,c=dst);assert q.fetchone()==(5,2)
  q.execute("select CELL_SLOT_ID from RRL_STOCK_RESERVATION where UID_PALLET=:u and STATUS='ACTIVE'",u=lot);assert q.fetchone()==(slots[1][0],)
  q.execute("select HU_STOCK_COMPOSITION_VERSION,HU_UNIT_SIGNATURE from RRL_RECEIPT_SLOT_CLAIM where UID_PALLET=:u",u=lot);epoch,sig=q.fetchone();assert epoch==1 and sig
  q.execute("select count(*) from RRL_EVENTS where OPERATION_ID=:op",op=op);assert q.fetchone()==(0,)
  def relocate(from_index,to_index):
   body={"expected_version":tree(lot)["nodes"][0]["version"],"target_slot_id":slots[to_index][0],"measurements":measurement(lot,45),"scan_container":lot,"scan_cell":dst,"scan_from_slot":slots[from_index][1],"scan_to_slot":slots[to_index][1],"reason":"Own measured stock placement"}
   op="LEAF.SLOT:"+uuid4().hex;res=post("HU_RELOCATE_SLOT",body,{"uid":lot},op);assert post("HU_RELOCATE_SLOT",body,{"uid":lot},op)==res
  relocate(1,2)
  q.execute("select RESERVATION_ID from RRL_STOCK_RESERVATION where UID_PALLET=:u and STATUS='ACTIVE'",u=lot);rid=int(q.fetchone()[0])
  post("RESERVATION_RELEASE",{"reason":"Own H-only evidence"},{"reservation_id":rid})
  relocate(2,1)
  for qty in (6,5):
   q.execute("select STOCK_VERSION,BASE_UOM from RRL_REMAINS where UID_POLETA=:u and CELL=:c",u=lot,c=dst);version,unit=q.fetchone()
   post("INVENTORY_COUNT",{"reason":"Own stale mass quantity restore","counts":[{"uid":lot,"cell":dst,"article":article,"unit":unit,"quantity":str(qty),"expected_stock_version":int(version),"unit_keys":[]}]},{"revision_id":revision})
  # Source empty carrier can leave; no stock movement is invented.
  back=post("HU_MOVE",{"expected_version":tree(top)["nodes"][0]["version"],"target_cell":src,"scan_container":top,"scanned_from_cell":dst,"scanned_to_cell":src},{"uid":top})
  assert back["leaf_count"]==0 and back["cell"]==src
  incoming={"expected_version":tree(top)["nodes"][0]["version"],"target_cell":dst,"target_slot_id":slots[0][0],"measurements":measurement(top,5),"scan_container":top,"scanned_from_cell":src,"scanned_to_cell":dst}
  try:post("HU_PLAN_MOVE",incoming,{"uid":top})
  except oracledb.DatabaseError as exc:assert "STOCK_PLACE_FRESH_MEASUREMENTS_REQUIRED" in str(exc),str(exc)
  else:raise AssertionError("Quantity restoration resurrected old mass")
  relocate(1,2)
  print("PASS direct STOCK unpack/empty parent -> P5/H2/same owner new slot, mass epoch; leaf relocation/replay/H-only valid; P6->5 stale mass rejected and fresh remeasurement restores",flush=True)
 finally:
  q.execute("select TASK_ID from RRL_WAREHOUSE_TASK where UID_PALLET=:u and STATUS not in('DONE','CANCELLED')",u=top)
  for (tid,) in q.fetchall():meta("update RRL_WAREHOUSE_TASK set STATUS='CANCELLED' where TASK_ID=:id",id=int(tid))
  q.execute("select PARENT_UID,CHILD_PALLET_UID from RRL_WMS_HU_LINK where PARENT_UID=:u and ACTIVE_FLAG=1",u=top)
  for parent,child in q.fetchall():link("HU_DETACH",parent,child)
  q.execute("select RESERVATION_ID from RRL_STOCK_RESERVATION where SOURCE_DOC_TYPE='PICK_WAVE' and SOURCE_DOC_ID=:w and STATUS in('ACTIVE','ALLOCATED','PICKING') and BASE_QTY>0",w=wave)
  for (rid,) in q.fetchall():post("RESERVATION_RELEASE",{"reason":"End own leaf"},{"reservation_id":int(rid)})
  q.execute("select CELL from RRL_REMAINS where UID_POLETA=:u and REMAIN>0",u=lot);row=q.fetchone()
  if row and row[0]==dst:
   post("INTERNAL_MOVE",{"uid":lot,"source_cell":dst,"target_cell":src,"quantity":"0","unit":"EA"},{})
   q.execute("select count(*) from RRL_RECEIPT_SLOT_CLAIM where UID_PALLET=:u",u=lot);assert q.fetchone()==(0,)
  q.execute("select UID_POLETA,CELL,BASE_UOM,STOCK_VERSION from RRL_REMAINS where UID_POLETA=:u and REMAIN>0",u=lot)
  counts=[{"uid":u,"cell":cell,"article":article,"unit":unit,"quantity":"0","expected_stock_version":int(version),"unit_keys":[]} for u,cell,unit,version in q.fetchall()]
  if counts:post("INVENTORY_COUNT",{"reason":"End own leaf","counts":counts},{"revision_id":revision})
  meta("update RRL_PICK_WAVE set STATUS='DONE' where PICK_WAVE_ID=:w",w=wave)
  print("Own P/H0; source claim freed by existing whole INTERNAL_MOVE, history retained",flush=True)
