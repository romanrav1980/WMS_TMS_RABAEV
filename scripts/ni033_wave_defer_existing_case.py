"""169 owned returned wave402: late rollback, concurrent replay, original demand preserved."""
import sys,json
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import httpx,oracledb
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment();sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"api/wms_api_server"))
from app.config import get_settings
from app.modules.inventory.contracts_stock import StockCommand
s=get_settings();wave=402;op="WAVE.DEFER169:402.ROLLBACK";url="http://127.0.0.1:8088/api/picking/waves/402/finish-execution"
body={"operation_id":op,"disposition":"RETURNED_TO_PLANNING","reason":"Own167 returned place; original demand retained for current planning"}
def post():
 with httpx.Client(auth=("admin","admin123"),timeout=60)as client:
  response=client.post(url,json=body);assert response.status_code==200,(response.status_code,response.text[:1800]);return response.json()
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select count(*)from RRL_STOCK_OPERATION where OPERATION_ID=:p_op",p_op=op);already=q.fetchone()[0]
 def pool():
  q.execute("select RRL_STOCK_POOL_READ.snapshot_json(20052672,'QC16700CDC0EF51')from dual");raw=q.fetchone()[0];j=json.loads(raw.read()if hasattr(raw,"read")else raw)
  return next(x for x in j["orders"]if x["order_id"]==1928)
 before=pool();assert before["quantity"]=="1"and before["picked_quantity"]=="0"and before["hard_quantity"]=="0"
 q.execute("select RRL_WAVE_EXEC_ACCESS.deferred_snapshot_json(400)from dual");raw=q.fetchone()[0];snap=json.loads(raw.read()if hasattr(raw,"read")else raw);assert snap["eligible"],snap
 command=StockCommand(operation_id="WAVE.DEFER169:400.UNCOMMITTED",command_type="WAVE_EXECUTION_FINISH",actor="admin",lines=(),source={"wave_id":400},metadata={"disposition":body["disposition"],"reason":body["reason"]})
 result=q.var(oracledb.DB_TYPE_CLOB);request=q.var(oracledb.DB_TYPE_CLOB);request.setvalue(0,command.canonical_json())
 q.callproc("RRL_STOCK_POSTING_API.prepare_command",[request,"admin",result,None]);assert result.getvalue()is None
 try:
  q.callproc("RRL_STOCK_POSTING_API.execute_prepared",[result])
  q.execute("select STATUS from RRL_PICK_WAVE where PICK_WAVE_ID=400");assert q.fetchone()[0]=="DONE"
 finally:
  c.rollback();q.callproc("RRL_STOCK_POSTING_API.reset_connection")
 q.execute("select STATUS from RRL_PICK_WAVE where PICK_WAVE_ID=400");assert q.fetchone()[0]=="LAUNCHED"
 q.execute("select count(*)from RRL_STOCK_OPERATION where OPERATION_ID='WAVE.DEFER169:400.UNCOMMITTED'");assert q.fetchone()[0]==0
 with ThreadPoolExecutor(max_workers=2)as pool_threads:answers=list(pool_threads.map(lambda _:post(),range(2)))
 assert answers[0]==answers[1]
 assert answers[0]["completion_outcome"]=="UNFULFILLED_RETURNED_TO_PLANNING"
 assert not answers[0]["order_fulfilled"]and not answers[0]["physical_stock_changed"]
 with httpx.Client(auth=("admin","admin123"),timeout=30)as client:
  assert client.post(url,json={**body,"reason":"Different decision"}).status_code==409
  assert client.post(url,json={**body,"operation_id":op+".NO_REASON","reason":" "}).status_code==422
  bad=client.post(url.replace("/402/","/395/"),json={**body,"operation_id":op+".OPEN"});assert bad.status_code==409,(bad.status_code,bad.text[:1000])
 assert pool()==before
 q.execute("select STATUS,PICKED_QTY from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=1037");assert q.fetchone()==("CANCELLED",1)
 q.execute("select sum(r.REMAIN),sum(r.HARD_RESERVED_BASE)from RRL_REMAINS r join RRL_CELLS x on x.CELL=r.CELL where x.WARE_ID=6667491");assert q.fetchone()==(20,20)
 q.execute("select count(*)from RRL_STOCK_OPERATION where OPERATION_ID=:p_op",p_op=op);assert q.fetchone()[0]==1
 print("PASS169 native400 late rollback restores wave/operation; legacy committed402 wrapper result preserved; concurrent HTTP one decision/exact replay/changed409/reason422/open395409; wave402 DONE UNFULFILLED, CASE1037 CANCELLED historical1, original demand1928 remains1; P20H20 unchanged")
