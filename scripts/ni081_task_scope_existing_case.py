"""144 current users/ware and original120 replay; no new goods or task."""
import sys,json
from pathlib import Path
import httpx,oracledb
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment()
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"api/wms_api_server"))
from app.config import get_settings
s=get_settings();actor="Q1341a19738325";op="INTERWARE.PUT.COMPLETE:b69f937895"
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select min(TASK_ID)from RRL_WAREHOUSE_TASK where FROM_WARE_ID=6667491 or TO_WARE_ID=6667491");own=q.fetchone()[0];assert own
 q.execute("select count(*),sum(BASE_QTY)from RRL_EVENTS where OPERATION_ID=:op",op=op);before=q.fetchone()
 q.execute("select CANONICAL_REQUEST,RESULT_JSON from RRL_STOCK_OPERATION where OPERATION_ID=:op",op=op);raw,result=q.fetchone()
 read=lambda x:x.read()if hasattr(x,"read")else x
 request=read(raw);value=read(result);saved=value if isinstance(value,dict)else json.loads(value)
 def forbidden(task,user,assignee=None):
  try:q.callproc("RRL_WAREHOUSE_TASK_ACCESS.assert_scope",[task,user,assignee])
  except oracledb.DatabaseError as exc:
   assert exc.args[0].code==20882,exc;return
  raise AssertionError("Foreign or inactive user admitted")
 q.callproc("RRL_WAREHOUSE_TASK_ACCESS.assert_scope",[own,actor,None])
 forbidden(829,actor);forbidden(829,"admin",actor)
 try:
  q.execute("update RUSERS set DELETED=1 where ID=:id",id=actor);forbidden(own,actor)
 finally:c.rollback()
 try:
  q.execute("update RUSERS set WARE_ID=9104 where ID=:id",id=actor)
  q.callproc("RRL_WAREHOUSE_TASK_ACCESS.assert_scope",[829,actor,None]);forbidden(own,actor)
 finally:c.rollback()
 with httpx.Client(auth=("admin","admin123"),timeout=35)as client:
  body={"operation_id":op,"scanned_pallet":"FULL.QA:9b15cf997d","scanned_from_cell":"QIR349bc1ff57","scanned_to_cell":"QIOec6052b26e","fact_qty":"3"}
  r=client.post("http://127.0.0.1:8088/api/warehouse-tasks/829/complete",json=body)
  if r.status_code==503:r=client.post("http://127.0.0.1:8088/api/warehouse-tasks/829/complete",json=body)
  assert r.status_code==200,(r.status_code,r.text[:1800]);assert r.json()["result"]==saved,(r.json(),saved)
 q.execute("select count(*),sum(BASE_QTY)from RRL_EVENTS where OPERATION_ID=:op",op=op);assert q.fetchone()==before==(1,3)
 print("PASS144 own current ware/foreign actor+assignee denied/current inactive denied/current ware change respected; original DONE829 native replay exact/event1 qty3 unchanged",flush=True)
