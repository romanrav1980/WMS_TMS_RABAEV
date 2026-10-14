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

 wave=seq("RRL_PICK_WAVE_SQ")
 meta("insert into RRL_PICK_WAVE(PICK_WAVE_ID,WAVE_CODE,WARE_ID,STATUS,CREATED_BY) values(:id,:code,:w,'LAUNCHED','admin')",id=wave,code="PHYSICAL.EPOCH:"+tag,w=ware)
 def state():
  q.execute("select REMAIN,HARD_RESERVED_BASE,STOCK_VERSION,PHYSICAL_VERSION,BASE_UOM from RRL_REMAINS where UID_POLETA=:u and CELL=:c",u=lot,c=src);return q.fetchone()
 def composition():
  q.execute("select STOCK_COMPOSITION_VERSION from RRL_PALLETS where UID_PALLET=:u",u=lot);return int(q.fetchone()[0])
 def count(qty):
  row=state()
  return post("INVENTORY_COUNT",{"reason":"Own physical epoch observation","counts":[{"uid":lot,"cell":src,"article":article,"unit":row[4],"quantity":str(qty),"expected_stock_version":int(row[2]),"unit_keys":[]}]},{"revision_id":revision})
 try:
  post("INVENTORY_REGISTER_LOT",{"uid":lot,"cell":src,"article":article,"quantity":"5","expiry_date":"2030-01-01","price":0,"reason":"Own physical epoch stock"},{"revision_id":revision})
  before=state();assert before[0:2]==(5,0) and before[3]==1 and composition()==1
  allocated=post("RESERVATION_CREATE",{"uid_pallet":lot,"cell":src,"articul":article,"qty":"2","unit_code":"EA","ware_id":ware,
   "reservation_kind":"HARD","reservation_scope":"QTY","reservation_domain":"WAVE","source_doc_type":"PICK_WAVE","source_doc_id":wave},{"type":"PICK_WAVE","id":wave})
  held=state();assert held[0:2]==(5,2) and held[2]>before[2] and held[3]==before[3]
  q.execute("select RESERVATION_ID from RRL_STOCK_RESERVATION where SOURCE_DOC_TYPE='PICK_WAVE' and SOURCE_DOC_ID=:w and STATUS='ACTIVE'",w=wave);rid=int(q.fetchone()[0])
  post("RESERVATION_RELEASE",{"reason":"Own physical epoch release"},{"reservation_id":rid})
  released=state();assert released[0:2]==(5,0) and released[3]==1 and composition()==1
  count(6);assert state()[3]==2 and composition()==2
  count(5);assert state()[3]==3 and composition()==3
  try:
   q.execute("update RRL_REMAINS set PHYSICAL_VERSION=0 where UID_POLETA=:u and CELL=:c",u=lot,c=src);conn.commit()
  except oracledb.DatabaseError as exc:conn.rollback();assert "DIRECT_STOCK_WRITE_FORBIDDEN" in str(exc) or "PHYSICAL_STOCK_VERSION" in str(exc),str(exc)
  else:raise AssertionError("Physical epoch changed without root")
  q.execute("select RRL_STOCK_HU_UNIT_SIGNATURE.signature_for(:u,:c) from dual",u=lot,c=src);assert len(q.fetchone()[0])==64
  try:
   q.execute("update RRL_PALLETS set STOCK_COMPOSITION_VERSION=0 where UID_PALLET=:u",u=lot);conn.commit()
  except oracledb.DatabaseError as exc:conn.rollback();assert "DIRECT_STOCK_WRITE_FORBIDDEN" in str(exc) or "COMPOSITION_VERSION" in str(exc),str(exc)
  else:raise AssertionError("Composition epoch changed outside coordinator")
  move_op="COMPOSITION.MOVE:"+tag
  body={"uid":lot,"source_cell":src,"target_cell":dst,"quantity":"0","unit":"EA"}
  moved=post("INTERNAL_MOVE",body,{},move_op);assert post("INTERNAL_MOVE",body,{},move_op)==moved and composition()==3
  post("INTERNAL_MOVE",{**body,"source_cell":dst,"target_cell":src},{})
  assert state()[0:2]==(5,0) and composition()==3
  print("PASS per-UID composition1 through HARD/release,2->3 after P6->P5; whole sameUID cell move/replay/back preserves3; direct reset denied",flush=True)
  print("PASS P5/H0 physical epoch1; HARD2/release advance stock version but preserve physical epoch; P6->P5 epochs2->3; direct epoch rewrite denied/bounded unit signature",flush=True)
 finally:
  q.execute("select RESERVATION_ID from RRL_STOCK_RESERVATION where SOURCE_DOC_TYPE='PICK_WAVE' and SOURCE_DOC_ID=:w and STATUS in('ACTIVE','ALLOCATED','PICKING') and BASE_QTY>0",w=wave)
  for (rid,) in q.fetchall():post("RESERVATION_RELEASE",{"reason":"End own physical fixture"},{"reservation_id":int(rid)})
  if state() and state()[0]>0:count(0)
  assert state()[0:2]==(0,0)
  meta("update RRL_PICK_WAVE set STATUS='DONE' where PICK_WAVE_ID=:w",w=wave)
  print("Own P/H cleared via root; physical/journal history retained",flush=True)
