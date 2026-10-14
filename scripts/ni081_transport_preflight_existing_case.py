"""163 current saved633 and historical632; no source/transport/quantity changes."""
import sys,json
from pathlib import Path
import httpx,oracledb
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment();sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"api/wms_api_server"))
from app.config import get_settings
from app.oracle_gateway import OracleGateway
from app.modules.transport.public import TransportPreflight
s=get_settings()
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select count(*)from RRL_TRANSPORT_TASK");trips=q.fetchone()[0]
 q.execute("select sum(r.REMAIN),sum(r.HARD_RESERVED_BASE)from RRL_REMAINS r join RRL_CELLS x on x.CELL=r.CELL where x.WARE_ID=6667491");stock=q.fetchone()
 preview=TransportPreflight(OracleGateway())
 controlled=preview.plan(633,"admin")
 assert controlled["status"]=="BLOCKED" and controlled["read_only"] and not controlled["operational_admission"]
 assert sum(x["code"]=="PLAN_ST_NOT_FOUND" for x in controlled["routes"][0]["source_blockers"])==2,controlled
 historical=preview.plan(632,"admin");assert historical["already_applied"] and historical["status"]=="BLOCKED"
 numbers=historical["routes"][0]["st_numbers"]
 manual=preview.trip(33523,numbers,"admin");assert manual["status"]=="BLOCKED" and manual["read_only"]
 assert any(x["code"]=="PLAN_ACTIVE_UNBILLED_TRIP_REQUIRED"for x in manual["routes"][0]["source_blockers"])
 with httpx.Client(auth=("admin","admin123"),timeout=25)as client:
  response=client.get("http://127.0.0.1:8088/api/transport/preflight/plans/633")
  assert response.status_code==200,(response.status_code,response.text[:1200])
  assert response.json()["status"]=="BLOCKED"
  response=client.post("http://127.0.0.1:8088/api/transport/preflight/trips/33523",json={"additional_st_numbers":numbers})
  assert response.status_code==200 and response.json()["status"]=="BLOCKED",(response.status_code,response.text[:1200])
  bad=client.get("http://127.0.0.1:8088/api/transport/preflight/plans/0");assert bad.status_code==422
  bad=client.get("http://127.0.0.1:8088/api/transport/preflight/plans/999999999");assert bad.status_code==404
 q.execute("select count(*)from RRL_TRANSPORT_TASK");assert q.fetchone()[0]==trips
 q.execute("select sum(r.REMAIN),sum(r.HARD_RESERVED_BASE)from RRL_REMAINS r join RRL_CELLS x on x.CELL=r.CELL where x.WARE_ID=6667491");assert q.fetchone()==stock==(20,20)
 print("PASS163 real existing633 currentmissingST explained; original632 applied/retired and33523 cancelled blocked; HTTP plan/manual preview; currentnative rules/no TT/ST/P20H20 mutation")
