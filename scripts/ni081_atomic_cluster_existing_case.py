"""Reuse private136 metadata only; cluster failure must roll back the new trip."""
import sys
from pathlib import Path
from datetime import date
import oracledb
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment()
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"api/wms_api_server"))
from app.config import get_settings
from app.modules.platform.public import read_oracle_json
from app.modules.transport.public import create_existing_cluster, TransportPlanError, cancel_trip
from app.oracle_gateway import OracleGateway
s=get_settings()
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn) as c:
 q=c.cursor()
 q.execute("select PAYLOAD from RRL_PLANNER_PLANS where ID=632")
 route=read_oracle_json(q.fetchone()[0])["routes"][0]
 primary=route["vehicle_id"];plate=route["vehicle_num"];numbers=route["stops"]
 tag=plate[5:-1]
 q.execute("select ID,NUM from RRL_TR_VEHICLE where NUM=:num",num="QA136"+tag+"1")
 small,small_plate=q.fetchone()
 q.execute("update RRL_TR_VEHICLE set DELETED=0,BLOCKED=0 where ID in(:a,:b)",a=primary,b=small);c.commit()
 trip=None
 try:
  q.execute("select count(*)from RRL_TRANSPORT_TASK");before=q.fetchone()[0]
  try:
   create_existing_cluster(OracleGateway(),"OWN136",date(2026,10,10),"20",{"transport":small_plate},numbers,"admin")
   raise AssertionError("Overweight cluster accepted")
  except TransportPlanError as exc:
   assert exc.status==409 and "PLAN_WEIGHT_CAPACITY_EXCEEDED" in str(exc),str(exc)
  q.execute("select count(*)from RRL_TRANSPORT_TASK");assert q.fetchone()[0]==before
  for number in numbers:
   q.execute("select TRANSTASK_ID from RRL_SBORKA_PALLETS where ST_NUMBER=:n",n=number)
   assert all(row[0] is None for row in q.fetchall())
  result=create_existing_cluster(OracleGateway(),"OWN136",date(2026,10,10),"20",{"transport":plate},numbers,"admin")
  trip=result["task_id"]
  assert result["st_count"]==2
  q.execute("select USER_ID,VODITEL_ID from RRL_TRANSPORT_TASK where ID=:id",id=trip)
  assert q.fetchone()==("admin",None)
  print("PASS138 existing cluster one UOW: overweight rollback leaves no new TT/membership; healthy twoST native assignment owned trip "+str(trip)+"; no stock operations",flush=True)
 finally:
  if trip is not None:cancel_trip(OracleGateway(),trip,"admin")
  q.execute("update RRL_TR_VEHICLE set DELETED=1,BLOCKED=1 where ID in(:a,:b)",a=primary,b=small);c.commit()
