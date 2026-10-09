"""Bounded real Oracle competition, rollback and guarded-writer checks after cutover."""
import json
import sys
import threading
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from uuid import uuid4
import oracledb
from stock_posting_environment import load_local_oracle_environment
ROOT=Path(__file__).resolve().parents[1]
load_local_oracle_environment()
sys.path.insert(0,str(ROOT/"api/wms_api_server"))
from app.config import get_settings
s=get_settings()
def connect():
 c=oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn);c.call_timeout=15000;return c
def invoke(q,doc):
 inp=q.var(oracledb.DB_TYPE_CLOB);inp.setvalue(0,json.dumps(doc,sort_keys=True,separators=(",",":")))
 out=q.var(oracledb.DB_TYPE_CLOB)
 q.callproc("RRL_STOCK_POSTING_API.prepare_command",[inp,"admin",out,None])
 if out.getvalue() is None:q.callproc("RRL_STOCK_POSTING_API.execute_prepared",[out])
 value=out.getvalue();return json.loads(value.read() if hasattr(value,"read") else value)
def reset(c):
 c.rollback();c.cursor().callproc("RRL_STOCK_POSTING_API.reset_connection")
with connect() as c:
 q=c.cursor()
 q.execute("select STATE from RRL_STOCK_RELEASE where RELEASE_ID=1");assert q.fetchone()==("ACTIVE",)
 q.execute("select s.UID_POLETA,s.CELL,p.ARTICUL,s.STOCK_VERSION,c.WARE_ID from RRL_REMAINS s join RRL_PALLETS p on p.UID_PALLET=s.UID_POLETA join RRL_CELLS c on c.CELL=s.CELL where s.REMAIN=0 order by s.UID_POLETA fetch first 1 row only")
 uid,cell,article,version,ware=q.fetchone()
 revision=int(q.callfunc("REVIZION.create_revizion",oracledb.DB_TYPE_NUMBER,[ware,"admin"]));c.commit()
 def document(qty,ver,op=None):
  return {"contract_version":2,"operation_id":op or "CUTOVER.CASE:"+uuid4().hex,"command_type":"INVENTORY_COUNT","actor":"admin",
    "source":{"revision_id":revision},"lines":[],"units":[],"metadata":{"reason":"Isolated dev cutover case","counts":[{"uid":uid,"cell":cell,"article":article,"unit":"EA","quantity":qty,"expected_stock_version":int(ver),"unit_keys":[]}]}}
 invoke(q,document("1",version));c.commit();reset(c)
 q.execute("select STOCK_VERSION from RRL_REMAINS where UID_POLETA=:u and CELL=:c",u=uid,c=cell);version=q.fetchone()[0]
 gate=threading.Barrier(2)
 def contender(doc):
  with connect() as worker:
   try:
    gate.wait(timeout=10);result=invoke(worker.cursor(),doc);worker.commit();return ("APPLIED",doc,result)
   except oracledb.DatabaseError as e:
    worker.rollback();return ("REJECTED",doc,e.args[0].code)
   finally:reset(worker)
 with ThreadPoolExecutor(max_workers=2) as pool:
  a=pool.submit(contender,document("0",version));b=pool.submit(contender,document("0",version));results=[a.result(),b.result()]
 assert sorted(x[0] for x in results)==["APPLIED","REJECTED"],results
 assert next(x[2] for x in results if x[0]=="REJECTED") in (20867,20890),results
 q.execute("select REMAIN,HARD_RESERVED_BASE from RRL_REMAINS where UID_POLETA=:u and CELL=:c",u=uid,c=cell);assert q.fetchone()==(0,0)
 print("PASS: concurrent same-stock/same-version commands: exactly one applied, one stale; P=H=0")
 winner=next(x for x in results if x[0]=="APPLIED")
 changed=winner[1];changed["metadata"]["counts"][0]["quantity"]="1"
 try:
  invoke(q,changed);raise AssertionError("Same operation with another payload was accepted")
 except oracledb.DatabaseError:
  reset(c)
 q.execute("select (select count(*) from RRL_EVENTS),(select count(*) from RRL_STOCK_OPERATION) from dual");before=q.fetchone()
 born="CUTOVER-ABORT-"+uuid4().hex
 doc={"contract_version":2,"operation_id":"CUTOVER.ABORT:"+uuid4().hex,"command_type":"INVENTORY_REGISTER_LOT","actor":"admin","source":{"revision_id":revision},"lines":[],"units":[],
 "metadata":{"uid":born,"cell":cell,"article":article,"quantity":"1","expiry_date":"2030-01-01","price":0,"reason":"Rollback after executed lot birth"}}
 invoke(q,doc)
 q.execute("select REMAIN from RRL_REMAINS where UID_POLETA=:u",u=born);assert q.fetchone()==(1,)
 # Simulates an intermediate DB/application failure after stock + journal + domain + outbox DML, before commit.
 try:q.execute("select 1/0 from dual")
 except oracledb.DatabaseError:reset(c)
 q.execute("select count(*) from RRL_PALLETS where UID_PALLET=:u",u=born);assert q.fetchone()==(0,)
 q.execute("select count(*) from RRL_REMAINS where UID_POLETA=:u",u=born);assert q.fetchone()==(0,)
 q.execute("select (select count(*) from RRL_EVENTS),(select count(*) from RRL_STOCK_OPERATION) from dual");assert q.fetchone()==before
 q.execute("select count(*) from RRL_EVENT_OUTBOX where json_value(PAYLOAD_JSON,'$.operation_id')=:o",o=doc["operation_id"]);assert q.fetchone()==(0,)
 print("PASS: failure after real birth DML: lot, stock, journal, operation and outbox rolled back together")
 try:
  q.execute("update RRL_REMAINS set REMAIN=1 where UID_POLETA=:u and CELL=:c",u=uid,c=cell)
  raise AssertionError("Uncontrolled stock write accepted")
 except oracledb.DatabaseError:reset(c)
 q.execute("select REMAIN,HARD_RESERVED_BASE from RRL_REMAINS where UID_POLETA=:u and CELL=:c",u=uid,c=cell);assert q.fetchone()==(0,0)
 print("PASS: uncontrolled direct stock UPDATE rejected; release ACTIVE; all case stock restored to zero")
