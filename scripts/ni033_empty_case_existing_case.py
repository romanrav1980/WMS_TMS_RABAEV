"""170 actual owned empty CASE1033/H1; native rollback/replay and root cleanup."""
import sys,json
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from uuid import uuid4
import httpx,oracledb
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment();sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"api/wms_api_server"))
from app.config import get_settings
from app.modules.inventory.contracts_stock import StockCommand
from app.modules.inventory.infrastructure.stock_posting_uow import StockPosting
s=get_settings();posting=StockPosting();op="CASE.EMPTY170:1033";task=1033;wave=397;uid="CASE167.QA:00cdc0ef51";cell="Q167S00cdc0ef51";article="QC16700CDC0EF51";ware=20052672
url="http://127.0.0.1:8088/api/case-pick/tasks/1033/return-carrier";reservation=None
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor()
 def cmd(kind,source,metadata,operation=None):
  return posting.post(StockCommand(operation_id=operation or "QA170:"+uuid4().hex,command_type=kind,actor="admin",source=source,metadata=metadata,lines=()))
 def count(quantity):
  q.execute("select STOCK_VERSION from RRL_REMAINS where UID_POLETA=:p_uid and CELL=:p_cell",p_uid=uid,p_cell=cell);version=int(q.fetchone()[0])
  return cmd("INVENTORY_COUNT",{"revision_id":233},{"reason":"Own170 isolated empty cancellation quantity fixture","counts":[{"uid":uid,"cell":cell,"article":article,"unit":"EA","quantity":quantity,"expected_stock_version":version,"unit_keys":[]}]})
 q.execute("select STATUS,SSCC,CONTENT_VERSION from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=:p_task",p_task=task);state,carrier,version=q.fetchone()
 body={"operation_id":op,"scan_container":carrier,"expected_content_version":0,"destinations":{},"allow_empty":True,"reason":"Own170 cancel unused place; original order retained"}
 try:
  if state!="CANCELLED":
   assert version==0
   count("1")
   q.execute("select PICK_TASK_ID from RRL_CASE_PICK_LINE where CASE_PICK_TASK_ID=:p_task",p_task=task);pt=int(q.fetchone()[0])
   result=cmd("RESERVATION_CREATE",{},{"reservation_kind":"HARD","reservation_scope":"QTY","reservation_domain":"PICKING","source_doc_type":"PICK_WAVE","source_doc_id":wave,"source_line_id":pt,"uid_pallet":uid,"cell":cell,"articul":article,"ware_id":ware,"unit_code":"EA","qty":"1"})
   reservation=result["reservation_id"]
   q.execute("select REMAIN,HARD_RESERVED_BASE from RRL_REMAINS where UID_POLETA=:p_uid and CELL=:p_cell",p_uid=uid,p_cell=cell);assert q.fetchone()==(1,1)
   wire=StockCommand(operation_id=op+".UNCOMMITTED",command_type="CASE_CARRIER_RETURN",actor="admin",lines=(),source={"case_task_id":task},metadata={k:v for k,v in body.items()if k!="operation_id"})
   inp=q.var(oracledb.DB_TYPE_CLOB);inp.setvalue(0,wire.canonical_json());out=q.var(oracledb.DB_TYPE_CLOB)
   q.callproc("RRL_STOCK_POSTING_API.prepare_command",[inp,"admin",out,None])
   try:
    q.callproc("RRL_STOCK_POSTING_API.execute_prepared",[out])
    q.execute("select REMAIN,HARD_RESERVED_BASE from RRL_REMAINS where UID_POLETA=:p_uid and CELL=:p_cell",p_uid=uid,p_cell=cell);assert q.fetchone()==(1,0)
   finally:c.rollback();q.callproc("RRL_STOCK_POSTING_API.reset_connection")
   q.execute("select STATUS,CONTENT_VERSION from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=:p_task",p_task=task);assert q.fetchone()==(state,version)
   q.execute("select REMAIN,HARD_RESERVED_BASE from RRL_REMAINS where UID_POLETA=:p_uid and CELL=:p_cell",p_uid=uid,p_cell=cell);assert q.fetchone()==(1,1)
  def call():
   with httpx.Client(auth=("admin","admin123"),timeout=60)as client:
    r=client.post(url,json=body);assert r.status_code==200,(r.status_code,r.text[:1800]);return r.json()
  with ThreadPoolExecutor(max_workers=2)as pool:results=list(pool.map(lambda _:call(),range(2)))
  assert results[0]==results[1]and results[0]["status"]=="CANCELLED_EMPTY"and not results[0]["physical_quantity_changed"]
  q.execute("select STATUS,PICKED_QTY from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=:p_task",p_task=task);assert q.fetchone()==("CANCELLED",0)
  q.execute("select count(*)from RRL_STOCK_OPERATION where OPERATION_ID=:p_op",p_op=op);assert q.fetchone()[0]==1
  with httpx.Client(auth=("admin","admin123"),timeout=30)as client:
   assert client.post(url,json={**body,"reason":"Different empty decision"}).status_code==409
   assert client.post(url,json={**body,"operation_id":op+".NO_REASON","reason":" "}).status_code==422
   assert client.post(url,json={k:v for k,v in {**body,"operation_id":op+".NOT_EMPTY"}.items()if k not in("allow_empty","reason")}).status_code==422
  print("PASS170 " + ("new empty1033/H1 native rollback/cancellation" if state!="CANCELLED" else "saved empty1033 receipt replay only; H1/rollback not repeated") + "; concurrent exact responses/reason422/changed409; no physical quantity movement")
 finally:
  if reservation:
   q.execute("select STATUS from RRL_STOCK_RESERVATION where RESERVATION_ID=:p_id",p_id=reservation)
   if q.fetchone()[0]in("ACTIVE","ALLOCATED","PICKING"):cmd("RESERVATION_RELEASE",{"reservation_id":reservation},{"reason":"Own170 exception cleanup"})
  q.execute("select REMAIN,HARD_RESERVED_BASE from RRL_REMAINS where UID_POLETA=:p_uid and CELL=:p_cell",p_uid=uid,p_cell=cell);stock=q.fetchone()
  if stock[0]>0:count("0")
 q.execute("select sum(r.REMAIN),sum(r.HARD_RESERVED_BASE)from RRL_REMAINS r join RRL_CELLS x on x.CELL=r.CELL where x.WARE_ID=6667491");assert q.fetchone()==(20,20)
 print("Own170 stock fixture cleared through root count; original135 P20H20 unchanged; order demand/history preserved")
