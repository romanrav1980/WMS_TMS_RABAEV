"""Reuse136 source metadata; original ARM chain repeated without losing actual facts."""
import sys
from pathlib import Path
from datetime import date
from uuid import uuid4
import httpx,oracledb
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment();sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"api/wms_api_server"))
from app.config import get_settings
from app.modules.platform.public import read_oracle_json
from app.modules.transport.public import create_existing_cluster,update_existing_trip,cancel_trip
from app.oracle_gateway import OracleGateway
s=get_settings();base="http://127.0.0.1:8088/api/admin/transport";client=httpx.Client(auth=("admin","admin123"),timeout=30)
def request(method,path,body=None,status=200):
 r=client.request(method,base+path,json=body)
 if r.status_code==503:
  print("Unconfirmed503: repeat same native metadata request once",flush=True)
  r=client.request(method,base+path,json=body)
 assert r.status_code==status,(r.status_code,r.text[:2000]);return r.json()
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select PAYLOAD from RRL_PLANNER_PLANS where ID=632")
 route=read_oracle_json(q.fetchone()[0])["routes"][0];primary=route["vehicle_id"];plate=route["vehicle_num"]
 q.execute("update RRL_TR_VEHICLE set DELETED=0,BLOCKED=0 where ID=:id",id=primary);c.commit()
 trip=None
 try:
  created=create_existing_cluster(OracleGateway(),"OWN136",date(2026,10,10),"20",
   {"transport":plate},route["stops"],"admin","CLUSTER141:"+uuid4().hex[:12])
  trip=created["task_id"]
  update_existing_trip(OracleGateway(),trip,{"shipment_time":"08:00"},"admin")
  planned=request("POST",f"/tasks/{trip}/plan-operations")
  assert len(planned)==12 and planned[0]["plan_start"]=="2026-10-10 08:00",planned
  again=request("POST",f"/tasks/{trip}/plan-operations");assert planned==again
  loading=next(row for row in planned if row["operation_code"]=="LOADING")
  assert loading["duration_min"]==6 and not loading["time_window_admission"],loading
  operation=planned[0]["op_id"]
  fact={"fact_start":"2026-10-10 08:00","fact_end":"2026-10-10 08:15","note":"Own141 actual metadata proof"}
  request("PATCH",f"/operations/{operation}/fact",fact)
  denied=request("POST",f"/tasks/{trip}/plan-operations",status=409)
  assert "OP_PLAN_EXECUTION_HISTORY_FROZEN"in str(denied)
  for sql in ["delete from RRL_TT_OPERATIONS where ID=:id",
              "update RRL_TT_OPERATIONS set FACT_START=null where ID=:id",
              "update RRL_TT_OPERATIONS set PLAN_START=PLAN_START+1 where ID=:id"]:
   try:q.execute(sql,id=operation);raise AssertionError("Actual history changed")
   except oracledb.DatabaseError as exc:assert exc.args[0].code==20886,str(exc);c.rollback()
  request("PATCH",f"/operations/{operation}/fact",{"fact_end":"2026-10-10 07:59"},409)
  q.execute("select to_char(FACT_START,'YYYY-MM-DD HH24:MI'),to_char(FACT_END,'YYYY-MM-DD HH24:MI'),NOTE from RRL_TT_OPERATIONS where ID=:id",id=operation)
  assert q.fetchone()==(fact["fact_start"],fact["fact_end"],fact["note"])
  print("PASS141 original136 twoST trip "+str(trip)+": 12 original ARM stages/date+clock/LOADING6min/identical replay IDs; recorded fact preserved, recalculation409/direct delete-clear-plan20886/negative interval409; no stock",flush=True)
 finally:
  if trip is not None:cancel_trip(OracleGateway(),trip,"admin")
  q.execute("update RRL_TR_VEHICLE set DELETED=1,BLOCKED=1 where ID=:id",id=primary);c.commit()
