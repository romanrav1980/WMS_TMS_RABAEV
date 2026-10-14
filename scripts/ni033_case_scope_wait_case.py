"""165 current CASE scope rechecked after a real row wait; prepare only/no stock effect."""
import sys,json,time
from pathlib import Path
from uuid import uuid4
from concurrent.futures import ThreadPoolExecutor
import oracledb
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment();sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"api/wms_api_server"))
from app.config import get_settings
from app.modules.inventory.public import StockCommand
s=get_settings();actor="Q1341a19738325";op="CASE.SCOPE165:"+uuid4().hex[:10];module="Q165_WAIT_"+op[-10:]
def connect():return oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)
with connect()as setup,connect()as blocker:
 q=setup.cursor();b=blocker.cursor()
 q.execute("select USER_GROUP,WARE_ID,DELETED from RUSERS where ID=:id",id=actor);group,ware,deleted=q.fetchone()
 q.execute("select count(*)from RIGHTS where USER_GROUP=:grp and lower(trim(RIGHT1))='case_pick_manage'",grp=group);had=q.fetchone()[0]
 q.execute("select c.SSCC,l.CASE_PICK_LINE_ID,l.CELL_CODE,l.ARTICUL from RRL_CASE_PICK_TASK c join RRL_CASE_PICK_LINE l on l.CASE_PICK_TASK_ID=c.CASE_PICK_TASK_ID where c.CASE_PICK_TASK_ID=1031")
 carrier,line,cell,article=q.fetchone()
 request=StockCommand(op,"CASE_PICK_CONFIRM",actor,(),{"case_task_id":1031,"case_line_id":line},metadata={"fact_qty":"1","scan_cell":cell,"scan_container":carrier,"scan_product":article}).canonical_json()
 if not had:q.execute("insert into RIGHTS(USER_GROUP,RIGHT1)values(:grp,'case_pick_manage')",grp=group);setup.commit()
 def worker():
  with connect()as c:
   c.call_timeout=20000;cur=c.cursor()
   cur.callproc("dbms_application_info.set_module",[module,"prepare only"])
   wire=cur.var(oracledb.DB_TYPE_CLOB);wire.setvalue(0,request);out=cur.var(oracledb.DB_TYPE_CLOB)
   try:cur.callproc("RRL_STOCK_POSTING_API.prepare_command",[wire,actor,out,None]);return "UNEXPECTED_PREPARED"
   except oracledb.DatabaseError as exc:return exc.args[0].code,str(exc.args[0]).split("\n",1)[0]
   finally:cur.callproc("RRL_STOCK_POSTING_API.reset_connection");c.rollback()
 try:
  b.execute("select RRL_STOCK_LOCK_API.resource_lock_id(20,RRL_STOCK_LOCK_API.resource_key('ROW','RRL_CASE_PICK_TASK','1031'))from dual")
  lock_id=int(b.fetchone()[0]);assert b.callfunc("sys.dbms_lock.request",oracledb.DB_TYPE_NUMBER,[lock_id,6,0,True])==0
  with ThreadPoolExecutor(max_workers=1)as pool:
   future=pool.submit(worker)
   waiting=False
   for _ in range(80):
    q.execute("select count(*)from v$session where MODULE=:module and EVENT='enq: UL - contention'and STATE='WAITING'",module=module)
    if q.fetchone()[0]:waiting=True;break
    if future.done():break
    time.sleep(.05)
   assert waiting,("Real CASE native mutex wait not observed",future.result()if future.done()else"stillrunning")
   q.execute("update RUSERS set WARE_ID=9104 where ID=:id",id=actor);setup.commit()
   b.callfunc("sys.dbms_lock.release",oracledb.DB_TYPE_NUMBER,[lock_id]);blocker.rollback()
   result=future.result(timeout=22)
   assert isinstance(result,tuple)and result[0]==20882 and "CASE_USER_WAREHOUSE_FORBIDDEN"in result[1],result
 finally:
  blocker.rollback()
  q.execute("update RUSERS set WARE_ID=:ware,DELETED=:deleted where ID=:id",ware=ware,deleted=deleted,id=actor)
  if not had:q.execute("delete from RIGHTS where USER_GROUP=:grp and RIGHT1='case_pick_manage'",grp=group)
  setup.commit()
 q.execute("select count(*)from RRL_STOCK_OPERATION where OPERATION_ID=:op",op=op);assert q.fetchone()[0]==0
 q.execute("select sum(r.REMAIN),sum(r.HARD_RESERVED_BASE)from RRL_REMAINS r join RRL_CELLS x on x.CELL=r.CELL where x.WARE_ID=6667491");assert q.fetchone()==(20,20)
 print("PASS165 real native CASE mutex wait observed/currentWARE changed while waiting/afterlock20882/no operation/journal/stock; ownactor/right restored")
