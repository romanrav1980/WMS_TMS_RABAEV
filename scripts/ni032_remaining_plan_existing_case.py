"""174 existing original1931 requested4/shipped3: concurrent remainder planning, no stock writer."""
import sys
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from uuid import uuid4
import oracledb
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment()
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"api/wms_api_server"))
from app.config import get_settings
from app.modules.inventory.contracts_stock import StockCommand
from app.modules.inventory.infrastructure.stock_posting_uow import StockPosting
s=get_settings();posting=StockPosting();uid="MIXED173.CASE:00cdc0ef51";cell="Q167D00cdc0ef51";article="QC16700CDC0EF51";plans=[]
def connection():
 return oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)
with connection()as c:
 q=c.cursor()
 def count(quantity):
  q.execute("select STOCK_VERSION from RRL_REMAINS where UID_POLETA=:p_uid and CELL=:p_cell",p_uid=uid,p_cell=cell)
  return posting.post(StockCommand(operation_id="QA174:"+uuid4().hex,command_type="INVENTORY_COUNT",actor="admin",source={"revision_id":233},metadata={"reason":"Owned174 remaining-demand planning fixture","counts":[{"uid":uid,"cell":cell,"article":article,"unit":"EA","quantity":quantity,"expected_stock_version":int(q.fetchone()[0]),"unit_keys":[]}]},lines=()))
 q.execute("select OBJECT_NAME,OBJECT_TYPE,STATUS from USER_OBJECTS where OBJECT_NAME in('RRL_PICK_PLAN_ADMISSION','RRL_PICKING_API')")
 assert all(row[2]=="VALID"for row in q.fetchall())
 q.execute("select NAME,LINE,TEXT from USER_ERRORS where NAME in('RRL_PICK_PLAN_ADMISSION','RRL_PICKING_API')")
 assert not q.fetchall()
 try:
  count("1")
  def create():
   with connection()as other:
    cur=other.cursor()
    try:
     plan=int(cur.callfunc("RRL_PICKING_API.create_plan",oracledb.DB_TYPE_NUMBER,[1931,"FEFO","admin"]))
     other.commit();return ("OK",plan)
    except oracledb.DatabaseError as exc:
     code=exc.args[0].code
     # Preserve transaction to prove the function itself removed partial metadata.
     cur.execute("select count(*)from RRL_PICK_PLAN where CUSTOMER_ORDER_ID=1931 and STATUS='DRAFT'")
     assert cur.fetchone()[0]==0
     other.rollback();return ("REFUSED",code,str(exc.args[0]).split("\n")[0])
  with ThreadPoolExecutor(max_workers=2)as workers:results=list(workers.map(lambda _:create(),range(2)))
  plans=[r[1]for r in results if r[0]=="OK"]
  assert len(plans)==1,results
  assert any(r[0]=="REFUSED"and r[1]==20886 for r in results),results
  q.execute("select TOTAL_ORDER_QTY,TOTAL_PLANNED_QTY from RRL_PICK_PLAN where PICK_PLAN_ID=:p_plan",p_plan=plans[0])
  assert q.fetchone()==(1,1)
  q.execute("select sum(RESERVED_QTY)from RRL_PICK_RESERVATION where PICK_PLAN_ID=:p_plan and RESERVATION_STATUS='ACTIVE'and RESERVATION_LEVEL='SOFT'",p_plan=plans[0])
  assert q.fetchone()==(1,)
  q.execute("select REMAIN,HARD_RESERVED_BASE from RRL_REMAINS where UID_POLETA=:p_uid and CELL=:p_cell",p_uid=uid,p_cell=cell)
  assert q.fetchone()==(1,0)
  print("PASS174 original4/shipped3 -> requested/planned1; two concurrent callers -> one SOFT1 and one20886; no partial DRAFT and no P/H mutation",results)
 finally:
  for plan in plans:
   posting.post(StockCommand(operation_id="QA174.CANCEL:"+str(plan),command_type="PICK_PLAN_CANCEL",actor="admin",source={"document_type":"PICK_PLAN","document_id":plan},metadata={"reason":"Retire owned174 unlaunched plan","only_cancelled_replenishment":0,"reservation_kind":None},lines=()))
  count("0")
 q.execute("select sum(r.REMAIN),sum(r.HARD_RESERVED_BASE)from RRL_REMAINS r join RRL_CELLS x on x.CELL=r.CELL where x.WARE_ID=6667491")
 assert q.fetchone()==(20,20)
 print("PASS174 own plan cancelled by existing native owner/stock fixture cleared; original135 P20H20 unchanged")
