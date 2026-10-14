"""Original136 metadata only; concurrent cluster repeat creates one existing TT."""
import sys
from pathlib import Path
from datetime import date
from uuid import uuid4
from concurrent.futures import ThreadPoolExecutor
import oracledb
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment()
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"api/wms_api_server"))
from app.config import get_settings
from app.modules.platform.public import read_oracle_json
from app.modules.transport.public import create_existing_cluster,TransportPlanError,cancel_trip
from app.oracle_gateway import OracleGateway
s=get_settings();operation="CLUSTER139:"+uuid4().hex[:12]
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select PAYLOAD from RRL_PLANNER_PLANS where ID=632")
 route=read_oracle_json(q.fetchone()[0])["routes"][0]
 primary=route["vehicle_id"];plate=route["vehicle_num"];numbers=route["stops"];tag=plate[5:-1]
 q.execute("select ID,NUM from RRL_TR_VEHICLE where NUM=:num",num="QA136"+tag+"1");small,small_plate=q.fetchone()
 q.execute("update RRL_TR_VEHICLE set DELETED=0,BLOCKED=0 where ID in(:a,:b)",a=primary,b=small);c.commit()
 trip=None
 def create(fields, op=operation, selected=numbers):
  return create_existing_cluster(OracleGateway(),"OWN136",date(2026,10,10),"20",fields,selected,"admin",op)
 try:
  q.execute("select count(*)from RRL_TRANSPORT_TASK");before=q.fetchone()[0]
  try:
   create({"transport":small_plate},operation+".BAD")
   raise AssertionError("Overweight accepted")
  except TransportPlanError as exc:assert exc.status==409 and "PLAN_WEIGHT_CAPACITY_EXCEEDED"in str(exc),str(exc)
  q.execute("select count(*)from RRL_TRANSPORT_TASK");assert q.fetchone()[0]==before
  q.execute("select count(*)from RRL_CLUSTER_CREATE_RESULT where OPERATION_ID=:op",op=operation+".BAD");assert q.fetchone()==(0,)
  with ThreadPoolExecutor(max_workers=2)as pool:
   a,b=list(pool.map(lambda _:create({"transport":plate}),range(2)))
  assert a==b,(a,b)
  trip=a["task_id"];assert a["st_count"]==2 and a["source_st_numbers"]==sorted(numbers)
  q.execute("select count(*)from RRL_TRANSPORT_TASK");assert q.fetchone()[0]==before+1
  assert create({"transport":plate},selected=[])==a
  try:
   create({"transport":plate,"dock":"CHANGED"})
   raise AssertionError("Changed request accepted")
  except TransportPlanError as exc:assert exc.status==409 and "CLUSTER_OPERATION_PAYLOAD_CONFLICT"in str(exc),str(exc)
  try:
   q.execute("update RRL_CLUSTER_CREATE_RESULT set ACTOR='API' where OPERATION_ID=:op",op=operation)
   raise AssertionError("Proof mutated")
  except oracledb.DatabaseError as exc:assert exc.args[0].code==20863;c.rollback()
  cancel_trip(OracleGateway(),trip,"admin");trip=None
  assert create({"transport":plate},selected=[])==a
  print("PASS139 original136 source: overweight no TT/proof; concurrent same operation one TT "+str(a["task_id"])+"; empty-source replay exact; changed body409/immutable20863; cancelled TT retained as original history; no stock",flush=True)
  print("OPERATION "+operation,flush=True)
 finally:
  if trip is not None:cancel_trip(OracleGateway(),trip,"admin")
  q.execute("update RRL_TR_VEHICLE set DELETED=1,BLOCKED=1 where ID in(:a,:b)",a=primary,b=small);c.commit()
