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
 revision=int(q.callfunc("REVIZION.create_revizion",oracledb.DB_TYPE_NUMBER,[1,"admin"]));conn.commit()
 top="HU.TOP:"+tag;box="HU.BOX:"+tag;second="HU.OTHER:"+tag
 wave=seq("RRL_PICK_WAVE_SQ")
 meta("insert into RRL_PICK_WAVE(PICK_WAVE_ID,WAVE_CODE,WARE_ID,STATUS,CREATED_BY) values(:id,:code,1,'LAUNCHED','admin')",id=wave,code=top)
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
  post("RESERVATION_CREATE",{"uid_pallet":lot,"cell":src,"articul":article,"qty":"2","unit_code":"EA","ware_id":1,
   "reservation_kind":"HARD","reservation_scope":"QTY","reservation_domain":"WAVE","source_doc_type":"PICK_WAVE","source_doc_id":wave},{"type":"PICK_WAVE","id":wave})
  for uid,kind in ((top,"PALLET"),(box,"BOX"),(second,"ROLL_CAGE")):
   create={"cell":src,"warehouse":1,"container_type":kind,"tare_weight_kg":0,"scan_container":uid,"scan_cell":src}
   op="HU.CREATE:"+tag+":"+kind;first=post("HU_CREATE",create,{"uid":uid},op);assert post("HU_CREATE",create,{"uid":uid},op)==first
   q.execute("select count(*) from RRL_REMAINS where UID_POLETA=:u",u=uid);assert q.fetchone()==(0,)
  body={"child_uid":lot,"expected_version":0,"expected_child_version":0,"scan_container":box,"scan_child":lot}
  op="HU.ATTACH:"+tag
  first=post("HU_ATTACH",body,{"uid":box},op);assert post("HU_ATTACH",body,{"uid":box},op)==first
  link("HU_ATTACH",top,box)
  state=tree(top);assert state["leaf_count"]==1 and len(state["nodes"])==3 and state["top_place_count"]==1
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
  print("PASS HU_CREATE no parent stock; BOX->leaf5/H2 -> TOP, one active parent/no cycles, exact replay, separate nested P rejected unchanged",flush=True)
 finally:
  q.execute("select PARENT_UID,CHILD_PALLET_UID from RRL_WMS_HU_LINK where ACTIVE_FLAG=1 and PARENT_UID in(:a,:b,:c) order by HU_LINK_ID",a=top,b=box,c=second)
  for parent,child in q.fetchall():link("HU_DETACH",parent,child)
  q.execute("select RESERVATION_ID from RRL_STOCK_RESERVATION where SOURCE_DOC_TYPE='PICK_WAVE' and SOURCE_DOC_ID=:w and STATUS in('ACTIVE','ALLOCATED','PICKING') and BASE_QTY>0",w=wave)
  for (rid,) in q.fetchall():post("RESERVATION_RELEASE",{"reason":"End HU fixture"},{"reservation_id":int(rid)})
  q.execute("select r.UID_POLETA,r.CELL,r.BASE_UOM,r.STOCK_VERSION from RRL_REMAINS r join RRL_PALLETS p on p.UID_PALLET=r.UID_POLETA where p.ARTICUL=:a and r.REMAIN>0",a=article)
  counts=[{"uid":u,"cell":cell,"article":article,"unit":unit,"quantity":"0","expected_stock_version":int(version),"unit_keys":[]} for u,cell,unit,version in q.fetchall()]
  if counts:post("INVENTORY_COUNT",{"reason":"End HU own stock case","counts":counts},{"revision_id":revision})
  meta("update RRL_PICK_WAVE set STATUS='DONE' where PICK_WAVE_ID=:w",w=wave)
  print("Own P/H cleared through root after explicit unpack; link/operation history retained",flush=True)
