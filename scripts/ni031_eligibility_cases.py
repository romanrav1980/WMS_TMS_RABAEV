"""Bounded committed dev fixture, policy/locked-command denials, and restored zero stock."""
import json,sys
from pathlib import Path
from uuid import uuid4
import oracledb
from stock_posting_environment import load_local_oracle_environment
ROOT=Path(__file__).resolve().parents[1]
load_local_oracle_environment();sys.path.insert(0,str(ROOT/"api/wms_api_server"))
from app.config import get_settings
s=get_settings();tag=uuid4().hex[:12];uid="NI031-QA-"+tag;cell="QA"+tag;lot=uid
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn) as c:
 q=c.cursor();c.call_timeout=15000
 q.execute("select user,sys_context('USERENV','SERVICE_NAME') from dual");assert q.fetchone()==("RABAEV","orcl")
 q.execute("select STATE from RRL_STOCK_RELEASE where RELEASE_ID=1");assert q.fetchone()==("ACTIVE",)
 q.execute("select p.ARTICUL from RRL_PALLETS p where p.UID_PALLET='DS-BASE-B1'");article=q.fetchone()[0]
 def configure(sql,**binds):
  q.callproc("RRL_STOCK_CONFIG_API.begin_change",["admin","warehouse_settings_edit"])
  try:q.execute(sql,binds);c.commit()
  except BaseException:c.rollback();raise
  finally:q.callproc("RRL_STOCK_CONFIG_API.end_change")
 configure("insert into RRL_CELLS(CELL,WARE_ID,X,Y,Z,OTBOR,IS_SYSTEM) values(:cell,1,0,0,0,1,0)",cell=cell)
 configure("insert into RRL_STOCK_POLICY_GUARD(POLICY_KEY,LOCK_ID) select RRL_STOCK_LOCK_API.resource_key('CELL',:cell),nvl(max(LOCK_ID),900000000)+1 from RRL_STOCK_POLICY_GUARD",cell=cell)
 revision=int(q.callfunc("REVIZION.create_revizion",oracledb.DB_TYPE_NUMBER,[1,"admin"]));c.commit()
 configure("insert into RRL_PICK_WAVE(PICK_WAVE_ID,WAVE_CODE,WARE_ID,CREATED_BY) values(RRL_PICK_WAVE_SQ.nextval,:code,1,'admin')",code=uid)
 q.execute("select PICK_WAVE_ID from RRL_PICK_WAVE where WAVE_CODE=:code",code=uid);wave=int(q.fetchone()[0])
 def post(kind,meta,source):
  doc={"contract_version":2,"operation_id":"NI031:"+uuid4().hex,"command_type":kind,"actor":"admin","source":source,"lines":[],"units":[],"metadata":meta}
  inp=q.var(oracledb.DB_TYPE_CLOB);inp.setvalue(0,json.dumps(doc));out=q.var(oracledb.DB_TYPE_CLOB)
  try:
   q.callproc("RRL_STOCK_POSTING_API.prepare_command",[inp,"admin",out,None])
   if out.getvalue() is None:q.callproc("RRL_STOCK_POSTING_API.execute_prepared",[out])
   wire=out.getvalue();result=json.loads(wire.read() if hasattr(wire,"read") else wire);c.commit();return result
  except BaseException:c.rollback();raise
  finally:q.callproc("RRL_STOCK_POSTING_API.reset_connection")
 def reason(qty=1,purpose="ALLOCATE",owner=None,days=None,ware=1):
  q.execute("select RRL_STOCK_ELIGIBILITY.reason(:lot,:cell,:ware,:qty,:days,null,:purpose,:owner,:article) from dual",
   lot=uid,cell=cell,ware=ware,qty=qty,days=days,purpose=purpose,owner=owner,article=article)
  return q.fetchone()[0]
 meta={"uid_pallet":lot,"cell":cell,"articul":article,"qty":"1","unit_code":"EA","ware_id":1,"reservation_kind":"HARD",
 "reservation_scope":"QTY","reservation_domain":"PICKING","source_doc_type":"PICK_WAVE","source_doc_id":wave}
 reservation=None
 try:
  post("INVENTORY_REGISTER_LOT",{"uid":lot,"cell":cell,"article":article,"quantity":"1","expiry_date":"2030-01-01","price":0,"reason":"NI03.1 isolated fixture"},{"revision_id":revision})
  assert reason() is None
  assert reason(ware=2)=="WAREHOUSE_LOCATION_CONFLICT"
  assert reason(days=10000)=="SOURCE_SHELF_DAYS"
  configure("update RRL_CELLS set BLOCKED_FOR_REMAINS=1,BLOCKED_FOR_POPOLNENIE=1 where CELL=:cell",cell=cell)
  assert reason()=="LOCATION_BLOCKED"
  try:post("RESERVATION_CREATE",meta,{});raise AssertionError("Quarantine reservation accepted")
  except oracledb.DatabaseError as exc:assert "LOCATION_BLOCKED" in str(exc),exc
  q.execute("select REMAIN,HARD_RESERVED_BASE from RRL_REMAINS where UID_POLETA=:lot and CELL=:cell",lot=uid,cell=cell);assert q.fetchone()==(1,0)
  configure("update RRL_CELLS set BLOCKED_FOR_REMAINS=0,BLOCKED_FOR_POPOLNENIE=0 where CELL=:cell",cell=cell)
  configure("insert into RRL_WAREHOUSE_TASK(TASK_ID,TASK_TYPE,TASK_SOURCE,UID_PALLET,FROM_CELL,TO_CELL,QTY,QTY_MODE,CREATED_BY) values(RRL_WAREHOUSE_TASK_SQ.nextval,'PUTAWAY','MANUAL',:lot,:cell,'----',1,'PALLET','admin')",lot=uid,cell=cell)
  assert reason()=="SOURCE_PUTAWAY_REQUIRED"
  configure("insert into RRL_RECEIPT_SKU_RULE(WARE_ID,ARTICUL,PICK_CELL,SOURCE_PICK_MODE) values(1,:article,:cell,'DIRECT')",article=article,cell=cell)
  assert reason(purpose="PICK") is None
  assert reason(purpose="REPLENISH")=="SOURCE_PUTAWAY_REQUIRED"
  configure("update RRL_WAREHOUSE_TASK set STATUS='CANCELLED' where UID_PALLET=:lot",lot=uid)
  reservation=post("RESERVATION_CREATE",meta,{})["reservation_id"]
  assert reason()=="SOURCE_FREE_INSUFFICIENT"
  assert reason(owner=reservation) is None
  post("RESERVATION_RELEASE",{},{"reservation_id":reservation});reservation=None
  q.execute("select STOCK_VERSION from RRL_REMAINS where UID_POLETA=:lot and CELL=:cell",lot=uid,cell=cell);version=int(q.fetchone()[0])
  post("INVENTORY_COUNT",{"reason":"End isolated NI03.1 case","counts":[{"uid":lot,"cell":cell,"article":article,"unit":"EA","quantity":"0","expected_stock_version":version,"unit_keys":[]}]},{"revision_id":revision})
  print("PASS: accessible source, wrong warehouse/shelf-life, quarantine denial with P preserved, pending placement, explicit DIRECT, HARD excludes reuse and own HARD recognized")
 finally:
  if reservation is not None:post("RESERVATION_RELEASE",{},{"reservation_id":reservation})
  q.execute("select REMAIN,STOCK_VERSION from RRL_REMAINS where UID_POLETA=:lot and CELL=:cell",lot=uid,cell=cell)
  current=q.fetchone()
  if current and current[0]>0:
   post("INVENTORY_COUNT",{"reason":"Cleanup isolated NI03.1 case","counts": [{"uid":uid,"cell":cell,"article":article,"unit":"EA","quantity":"0","expected_stock_version":int(current[1]),"unit_keys":[]}]},{"revision_id":revision})
  configure("update RRL_CELLS set BLOCKED_FOR_REMAINS=0,BLOCKED_FOR_POPOLNENIE=0 where CELL=:cell",cell=cell)
  configure("update RRL_RECEIPT_SKU_RULE set SOURCE_PICK_MODE='AFTER_PUTAWAY' where WARE_ID=1 and ARTICUL=:article and PICK_CELL=:cell",article=article,cell=cell)
  configure("update RRL_WAREHOUSE_TASK set STATUS='CANCELLED' where UID_PALLET=:lot and STATUS!='DONE'",lot=uid)
  configure("update RRL_PICK_WAVE set STATUS='CANCELLED' where PICK_WAVE_ID=:wave",wave=wave)
 q.execute("select REMAIN,HARD_RESERVED_BASE from RRL_REMAINS where UID_POLETA=:lot and CELL=:cell",lot=uid,cell=cell);assert q.fetchone()==(0,0)
 print("PASS: fixture quantity/H restored to zero; immutable operations retained; fixture="+uid)
