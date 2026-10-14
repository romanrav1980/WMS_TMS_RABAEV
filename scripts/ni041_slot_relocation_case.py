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
  post("INVENTORY_REGISTER_LOT",{"uid":lot,"cell":src,"article":article,"quantity":"5","expiry_date":"2030-01-01","price":0,"reason":"HU tree private stock"},{"revision_id":revision})
  post("RESERVATION_CREATE",{"uid_pallet":lot,"cell":src,"articul":article,"qty":"2","unit_code":"EA","ware_id":ware,
   "reservation_kind":"HARD","reservation_scope":"QTY","reservation_domain":"WAVE","source_doc_type":"PICK_WAVE","source_doc_id":wave},{"type":"PICK_WAVE","id":wave})
  for uid,kind in ((top,"PALLET"),(box,"BOX"),(second,"ROLL_CAGE")):
   create={"cell":src,"warehouse":ware,"container_type":kind,"tare_weight_kg":0,"scan_container":uid,"scan_cell":src}
   op="HU.CREATE:"+tag+":"+kind;first=post("HU_CREATE",create,{"uid":uid},op);assert post("HU_CREATE",create,{"uid":uid},op)==first
   q.execute("select count(*) from RRL_REMAINS where UID_POLETA=:u",u=uid);assert q.fetchone()==(0,)
  body={"child_uid":lot,"expected_version":0,"expected_child_version":0,"scan_container":box,"scan_child":lot}
  op="HU.ATTACH:"+tag
  first=post("HU_ATTACH",body,{"uid":box},op);assert post("HU_ATTACH",body,{"uid":box},op)==first
  link("HU_ATTACH",top,box)
  post("INVENTORY_REGISTER_LOT",{"uid":other,"cell":src,"article":article,"quantity":"5","expiry_date":"2030-01-01","price":0,"reason":"Parent retained own stock"},{"revision_id":revision})
  link("HU_ATTACH",top,other)

  state=tree(top);assert state["leaf_count"]==2 and len(state["nodes"])==4 and state["top_place_count"]==1
  assert tree(box)["top_place_count"]==0
  q.execute("select REMAIN,HARD_RESERVED_BASE from RRL_REMAINS where UID_POLETA=:u and CELL=:c",u=lot,c=src);assert q.fetchone()==(5,2)
  for parent,child,code in ((box,top,"HU_CYCLE_FORBIDDEN"),(second,lot,"HU_CHILD_ALREADY_HAS_PARENT")):
   try:link("HU_ATTACH",parent,child);raise AssertionError("Invalid HU hierarchy accepted")
   except oracledb.DatabaseError as exc:assert code in str(exc),str(exc)
  q.execute("select BASE_UOM,STOCK_VERSION from RRL_REMAINS where UID_POLETA=:u and CELL=:c",u=lot,c=src);unit,version=q.fetchone()
  try:
   post("INVENTORY_COUNT",{"reason":"Separate nested leaf alteration must be denied","counts":[{"uid":lot,"cell":src,"article":article,"unit":unit,"quantity":"4","expected_stock_version":int(version),"unit_keys":[]}]},{"revision_id":revision})
   raise AssertionError("Separate nested P alteration accepted")
  except oracledb.DatabaseError as exc:assert "NESTED_HU_REQUIRES_TOP_MOVE_OR_EXPLICIT_UNPACK" in str(exc),str(exc)
  q.execute("select REMAIN,HARD_RESERVED_BASE from RRL_REMAINS where UID_POLETA=:u and CELL=:c",u=lot,c=src);assert q.fetchone()==(5,2)
  move={"expected_version":tree(top)["nodes"][0]["version"],"target_cell":dst,"scan_container":top,"scanned_from_cell":src,"scanned_to_cell":dst}
  nested={**move,"expected_version":tree(box)["nodes"][0]["version"],"scan_container":box}
  try:post("HU_MOVE",nested,{"uid":box});raise AssertionError("Nested container moved independently")
  except oracledb.DatabaseError as exc:assert "HU_TOP_LEVEL_MOVE_REQUIRED" in str(exc),str(exc)
  meta("update RRL_CELLS set BLOCKED_FOR_REMAINS=1 where CELL=:c",c=dst)
  try:post("HU_MOVE",move,{"uid":top});raise AssertionError("Blocked destination used")
  except oracledb.DatabaseError as exc:assert "LOCATION_BLOCKED" in str(exc),str(exc)
  q.execute("select REMAIN,HARD_RESERVED_BASE from RRL_REMAINS where UID_POLETA=:u and CELL=:c",u=lot,c=src);assert q.fetchone()==(5,2)
  meta("update RRL_CELLS set BLOCKED_FOR_REMAINS=0 where CELL=:c",c=dst)
  topo=seq("RRL_WH_TOPOLOGY_SQ");tc=seq("RRL_TOPOLOGY_CELL_SQ");slot=seq("RRL_TOPO_CELL_SLOT_SQ");slotcode="SLOT:"+tag
  meta("insert into RRL_WAREHOUSE_TOPOLOGY(TOPOLOGY_ID,WARE_ID,TOPOLOGY_CODE,STATUS) values(:id,:w,:code,'PUBLISHED')",id=topo,w=ware,code="HU:"+tag)
  meta("insert into RRL_TOPOLOGY_CELL(TOPOLOGY_CELL_ID,TOPOLOGY_ID,WARE_ID,CELL_CODE,LEGACY_CELL_CODE,SLOT_LAYER_KIND) values(:id,:t,:w,:c,:c,'STORAGE_SLOT')",id=tc,t=topo,w=ware,c=dst)
  meta("insert into RRL_TOPOLOGY_CELL_SLOT(CELL_SLOT_ID,TOPOLOGY_ID,TOPOLOGY_CELL_ID,PARENT_SLOT_LAYER_KIND,SLOT_KIND,SLOT_CODE,CAPACITY_QTY,CAPACITY_WEIGHT_KG,CAPACITY_VOLUME_M3,WIDTH_M,DEPTH_M,HEIGHT_M) values(:id,:t,:c,'STORAGE_SLOT','STORAGE_SLOT',:code,1,100,3,1.2,1.2,2)",id=slot,t=topo,c=tc,code=slotcode)
  measures={"origin":"MANUAL_CONFIRMED","content_version":move["expected_version"],"gross_weight_kg":"50","width_m":"1","depth_m":"1","height_m":"1.5"}
  move={**move,"target_slot_id":slot,"measurements":measures}
  for bad,reason in (({**move,"measurements":{**measures,"height_m":"3"}},"HU_SLOT_WEIGHT_VOLUME_OR_DIMENSIONS_EXCEEDED"),({**move,"measurements":{**measures,"content_version":999}},"HU_MEASUREMENT_CONTENT_VERSION_REQUIRED")):
   try:post("HU_PLAN_MOVE",bad,{"uid":top});raise AssertionError("Invalid measurements accepted")
   except oracledb.DatabaseError as exc:assert reason in str(exc),str(exc)
  meta("update RRL_CELLS set LIMIT_HEIGHT=2000 where CELL=:c",c=dst)
  try:post("HU_PLAN_MOVE",move,{"uid":top});raise AssertionError("Legacy height unit assumed")
  except oracledb.DatabaseError as exc:assert "HU_LEGACY_CELL_HEIGHT_UNIT_REQUIRED" in str(exc),str(exc)
  meta("insert into RRL_RECEIPT_WARE_SETTINGS(WARE_ID,COMPANY_PREFIX,HU_CELL_HEIGHT_UNIT) values(:w,'1234567','MM')",w=ware)
  meta("update RRL_TOPOLOGY_CELL set MAX_WEIGHT_KG=10 where TOPOLOGY_CELL_ID=:id",id=tc)
  try:post("HU_PLAN_MOVE",move,{"uid":top});raise AssertionError("Cell aggregate weight ignored")
  except oracledb.DatabaseError as exc:assert "HU_TOPOLOGY_CELL_WEIGHT_OR_VOLUME_EXCEEDED" in str(exc),str(exc)
  meta("update RRL_TOPOLOGY_CELL set MAX_WEIGHT_KG=100,MAX_VOLUME_M3=3 where TOPOLOGY_CELL_ID=:id",id=tc)
  planop="HU.PLAN:"+tag
  planned=post("HU_PLAN_MOVE",move,{"uid":top},planop);assert post("HU_PLAN_MOVE",move,{"uid":top},planop)==planned
  task=int(planned["task_id"])
  from app.services.warehouse_task_service import WarehouseTaskService
  from app.schemas import WarehouseTaskStatusRequest
  service=WarehouseTaskService()
  service.assign_task(task,WarehouseTaskStatusRequest(updated_by="admin",assigned_to="admin"))
  service.start_task(task,WarehouseTaskStatusRequest(updated_by="admin"))
  request=WarehouseTaskStatusRequest(operation_id="HU.TASK.COMPLETE:"+tag,updated_by="admin",fact_qty="1",
   scanned_pallet=top,scanned_from_cell=src,scanned_to_cell=dst,scanned_to_slot_code=slotcode)
  wrong=request.model_copy(update={"operation_id":"HU.WRONG.SLOT:"+tag,"scanned_to_slot_code":"OTHER"})
  from fastapi import HTTPException
  try:service.complete_task(task,wrong,"admin");raise AssertionError("Wrong physical slot scan accepted")
  except HTTPException as exc:assert exc.detail.get("reason")=="HU_TARGET_SLOT_SCAN_REQUIRED",str(exc.detail)
  q.execute("select count(*) from RRL_RECEIPT_SLOT_CLAIM where TASK_ID=:id",id=task);assert q.fetchone()==(0,)
  moved=service.complete_task(task,request,"admin");assert service.complete_task(task,request,"admin")==moved
  q.execute("select TASK_TYPE,TASK_SOURCE,UNIT_CODE,QTY,FACT_QTY,STATUS,HU_CONTENT_VERSION from RRL_WAREHOUSE_TASK where TASK_ID=:id",id=task)
  assert q.fetchone()==("PUTAWAY","MANUAL","HU",1,1,"DONE",move["expected_version"])
  q.execute("select count(*),sum(BASE_QTY),min(BASE_UOM) from RRL_WAREHOUSE_TASK_STOCK_MOVE where TASK_ID=:id",id=task);assert q.fetchone()==(2,10,"EA")
  q.execute("select count(*),min(SYNC_STATUS) from RRL_WAREHOUSE_TASK_SYNC where TASK_ID=:id",id=task);assert q.fetchone()==(1,"SYNCED")
  q.execute("select UID_PALLET,CELL,CELL_SLOT_ID,STATUS from RRL_RECEIPT_SLOT_CLAIM where TASK_ID=:id",id=task);assert q.fetchone()==(top,dst,slot,"OCCUPIED")
  assert moved["cell"]==dst and moved["leaf_count"]==2 and moved["top_place_count"]==1
  q.execute("select REMAIN,HARD_RESERVED_BASE from RRL_REMAINS where UID_POLETA=:u and CELL=:c",u=lot,c=src);assert q.fetchone()==(0,0)
  q.execute("select REMAIN,HARD_RESERVED_BASE from RRL_REMAINS where UID_POLETA=:u and CELL=:c",u=lot,c=dst);assert q.fetchone()==(5,2)
  q.execute("select CELL,BASE_QTY from RRL_STOCK_RESERVATION where SOURCE_DOC_TYPE='PICK_WAVE' and SOURCE_DOC_ID=:w and BASE_QTY>0 and STATUS='ACTIVE'",w=wave);assert q.fetchone()==(dst,2)
  slot2=seq("RRL_TOPO_CELL_SLOT_SQ");slotcode2=slotcode+":2"
  meta("insert into RRL_TOPOLOGY_CELL_SLOT(CELL_SLOT_ID,TOPOLOGY_ID,TOPOLOGY_CELL_ID,PARENT_SLOT_LAYER_KIND,SLOT_KIND,SLOT_CODE,CAPACITY_QTY,CAPACITY_WEIGHT_KG,CAPACITY_VOLUME_M3,WIDTH_M,DEPTH_M,HEIGHT_M,SUB_COLUMN_NO) select :id,TOPOLOGY_ID,TOPOLOGY_CELL_ID,PARENT_SLOT_LAYER_KIND,SLOT_KIND,:code,CAPACITY_QTY,CAPACITY_WEIGHT_KG,CAPACITY_VOLUME_M3,WIDTH_M,DEPTH_M,HEIGHT_M,2 from RRL_TOPOLOGY_CELL_SLOT where CELL_SLOT_ID=:old",id=slot2,code=slotcode2,old=slot)
  split={"child_uid":box,"expected_version":tree(top)["nodes"][0]["version"],"expected_child_version":tree(box)["nodes"][0]["version"],
   "scan_container":top,"scan_child":box,"scan_cell":dst,"scan_parent_slot":slotcode,"scan_child_slot":slotcode2,"child_slot_id":slot2,"reason":"Own explicit physical unpack",
   "parent_measurements":{"origin":"MANUAL_CONFIRMED","content_version":tree(top)["nodes"][0]["version"],"gross_weight_kg":"20","width_m":"0.5","depth_m":"1","height_m":"1.5"},
   "child_measurements":{"origin":"MANUAL_CONFIRMED","content_version":tree(box)["nodes"][0]["version"],"gross_weight_kg":"30","width_m":"0.5","depth_m":"1","height_m":"1.5"}}
  for bad,reason in (({**split,"scan_child_slot":"BAD"},"HU_UNPACK_CHILD_SLOT_SCAN_REQUIRED"),({**split,"child_measurements":{**split["child_measurements"],"gross_weight_kg":"90"}},"HU_TOPOLOGY_CELL_WEIGHT_OR_VOLUME_EXCEEDED")):
   try:post("HU_UNPACK",bad,{"uid":top})
   except oracledb.DatabaseError as exc:assert reason in str(exc),str(exc)
   else:raise AssertionError("Invalid slotted unpack admitted")
   q.execute("select sum(REMAIN),sum(HARD_RESERVED_BASE) from RRL_REMAINS where CELL=:c",c=dst);assert q.fetchone()==(10,2)
  split_op="HU.UNPACK:"+tag;unpacked=post("HU_UNPACK",split,{"uid":top},split_op);assert post("HU_UNPACK",split,{"uid":top},split_op)==unpacked
  assert unpacked["quantity_unchanged"] and unpacked["child"]["top_place_count"]==1
  q.execute("select count(*),sum(HU_GROSS_WEIGHT_KG),sum(HU_BOUNDING_VOLUME_M3) from RRL_RECEIPT_SLOT_CLAIM where CELL=:c and STATUS='OCCUPIED'",c=dst);assert q.fetchone()==(2,50,1.5)
  q.execute("select CELL,BASE_QTY,CELL_SLOT_ID from RRL_STOCK_RESERVATION where SOURCE_DOC_TYPE='PICK_WAVE' and SOURCE_DOC_ID=:w and BASE_QTY>0 and STATUS='ACTIVE'",w=wave);assert q.fetchone()==(dst,2,slot2)
  q.execute("select count(*) from RRL_EVENTS where OPERATION_ID=:op",op=split_op);assert q.fetchone()[0]==0
  from app.services.warehouse_task_domain_sync_service import WarehouseTaskDomainSyncService
  sync_service=WarehouseTaskDomainSyncService()
  for done_task in (task,unpacked["parent_task_id"],unpacked["child_task_id"]):
   assert sync_service.retry_task_sync(int(done_task),"admin")["sync_status"]=="SYNCED"
  slot3=seq("RRL_TOPO_CELL_SLOT_SQ");slotcode3=slotcode+":3"
  meta("insert into RRL_TOPOLOGY_CELL_SLOT(CELL_SLOT_ID,TOPOLOGY_ID,TOPOLOGY_CELL_ID,PARENT_SLOT_LAYER_KIND,SLOT_KIND,SLOT_CODE,CAPACITY_QTY,CAPACITY_WEIGHT_KG,CAPACITY_VOLUME_M3,WIDTH_M,DEPTH_M,HEIGHT_M,SUB_COLUMN_NO) select :id,TOPOLOGY_ID,TOPOLOGY_CELL_ID,PARENT_SLOT_LAYER_KIND,SLOT_KIND,:code,CAPACITY_QTY,CAPACITY_WEIGHT_KG,CAPACITY_VOLUME_M3,WIDTH_M,DEPTH_M,HEIGHT_M,3 from RRL_TOPOLOGY_CELL_SLOT where CELL_SLOT_ID=:old",id=slot3,code=slotcode3,old=slot)
  relocation={"expected_version":tree(box)["nodes"][0]["version"],"scan_container":box,"scan_cell":dst,"scan_from_slot":slotcode2,"scan_to_slot":slotcode3,"target_slot_id":slot3,
   "reason":"Own physical same-cell relocation","measurements":{**split["child_measurements"],"content_version":tree(box)["nodes"][0]["version"]}}
  for bad,reason in (({**relocation,"scan_to_slot":"BAD"},"HU_SLOT_MOVE_TO_SLOT_SCAN_REQUIRED"),({**relocation,"target_slot_id":slot,"scan_to_slot":slotcode},"HU_PHYSICAL_SLOT_OCCUPIED_OR_RESERVED")):
   try:post("HU_RELOCATE_SLOT",bad,{"uid":box})
   except oracledb.DatabaseError as exc:assert reason in str(exc),str(exc)
   else:raise AssertionError("Invalid same-cell slot relocation admitted")
  relocation_op="HU.SLOT.MOVE:"+tag
  relocated=post("HU_RELOCATE_SLOT",relocation,{"uid":box},relocation_op);assert post("HU_RELOCATE_SLOT",relocation,{"uid":box},relocation_op)==relocated
  q.execute("select sum(REMAIN),sum(HARD_RESERVED_BASE) from RRL_REMAINS where CELL=:c",c=dst);assert q.fetchone()==(10,2)
  q.execute("select CELL,BASE_QTY,CELL_SLOT_ID from RRL_STOCK_RESERVATION where SOURCE_DOC_TYPE='PICK_WAVE' and SOURCE_DOC_ID=:w and BASE_QTY>0 and STATUS='ACTIVE'",w=wave);assert q.fetchone()==(dst,2,slot3)
  q.execute("select count(*) from RRL_RECEIPT_SLOT_CLAIM where CELL_SLOT_ID=:id and STATUS='OCCUPIED'",id=slot2);assert q.fetchone()[0]==0
  q.execute("select count(*) from RRL_EVENTS where OPERATION_ID=:op",op=relocation_op);assert q.fetchone()[0]==0
  assert sync_service.retry_task_sync(int(relocated["task_id"]),"admin")["sync_status"]=="SYNCED"
  print("PASS same-cell whole BOX slotB->C, slotB freed, P10/H2/same owner preserved/no quantity journal/durable replay+sync; wrong scan and occupied target denied",flush=True)
  print("PASS slotted physical unpack TOP/BOX -> two fresh places/20+30kg/.75+.75m3; P10/H2 unchanged, same reservation now child slot, no quantity journal, exact replay; bad slot and total110kg denied",flush=True)
  print("PASS slotted existing MANUAL/PUTAWAY task plan/assign/start/complete1HU -> whole TOP/BOX/leaf5/H2; owner retained, stock move5EA/sync once/replay",flush=True)
  print("PASS HU_CREATE no parent stock; BOX->leaf5/H2 -> TOP, one active parent/no cycles, exact replay, separate nested P rejected unchanged",flush=True)
 finally:
  q.execute("select TASK_ID from RRL_WAREHOUSE_TASK where UID_PALLET=:u and STATUS not in('DONE','CANCELLED')",u=top)
  for (tid,) in q.fetchall():meta("update RRL_WAREHOUSE_TASK set STATUS='CANCELLED' where TASK_ID=:id",id=int(tid))
  for owner,index in ((top,1),(box,2)):
   current=tree(owner)
   if current["cell"]==dst and current["top_place_count"]==1:
    cleanupcell="QC"+tag+str(index)
    meta("insert into RRL_CELLS(CELL,WARE_ID,X,Y,Z,OTBOR,IS_SYSTEM,LIMIT_WEIGHT,LIMIT_HEIGHT) values(:c,:w,0,0,0,0,0,0,0)",c=cleanupcell,w=ware)
    meta("insert into RRL_STOCK_POLICY_GUARD(POLICY_KEY,LOCK_ID) select RRL_STOCK_LOCK_API.resource_key('CELL',:c),nvl(max(LOCK_ID),900000000)+1 from RRL_STOCK_POLICY_GUARD",c=cleanupcell)
    back={"expected_version":current["nodes"][0]["version"],"target_cell":cleanupcell,"scan_container":owner,"scanned_from_cell":dst,"scanned_to_cell":cleanupcell}
    post("HU_MOVE",back,{"uid":owner})
    q.execute("select count(*) from RRL_RECEIPT_SLOT_CLAIM where UID_PALLET=:u",u=owner);assert q.fetchone()==(0,)
  q.execute("select PARENT_UID,CHILD_PALLET_UID from RRL_WMS_HU_LINK where ACTIVE_FLAG=1 and PARENT_UID in(:a,:b,:c) order by HU_LINK_ID",a=top,b=box,c=second)
  for parent,child in q.fetchall():link("HU_DETACH",parent,child)
  q.execute("select RESERVATION_ID from RRL_STOCK_RESERVATION where SOURCE_DOC_TYPE='PICK_WAVE' and SOURCE_DOC_ID=:w and STATUS in('ACTIVE','ALLOCATED','PICKING') and BASE_QTY>0",w=wave)
  for (rid,) in q.fetchall():post("RESERVATION_RELEASE",{"reason":"End HU fixture"},{"reservation_id":int(rid)})
  q.execute("select r.UID_POLETA,r.CELL,r.BASE_UOM,r.STOCK_VERSION from RRL_REMAINS r join RRL_PALLETS p on p.UID_PALLET=r.UID_POLETA where p.ARTICUL=:a and r.REMAIN>0",a=article)
  counts=[{"uid":u,"cell":cell,"article":article,"unit":unit,"quantity":"0","expected_stock_version":int(version),"unit_keys":[]} for u,cell,unit,version in q.fetchall()]
  if counts:post("INVENTORY_COUNT",{"reason":"End HU own stock case","counts":counts},{"revision_id":revision})
  meta("update RRL_PICK_WAVE set STATUS='DONE' where PICK_WAVE_ID=:w",w=wave)
  print("Own P/H cleared through root after explicit unpack; link/operation history retained",flush=True)
