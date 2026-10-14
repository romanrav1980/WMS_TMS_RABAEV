"""Reuse135 current wave395/P20H20 and original roster; no new goods."""
import sys
from pathlib import Path
from datetime import datetime,timedelta
from decimal import Decimal
import httpx,oracledb
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment()
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"api/wms_api_server"))
from app.config import get_settings
s=get_settings();base="http://127.0.0.1:8088/api/resources/workload";client=httpx.Client(auth=("admin","admin123"),timeout=30)
def call(method,path,body=None,status=200):
 r=client.request(method,base+path,json=body)
 if r.status_code==503:
  print("Unconfirmed503: retrying identical operation/body once",flush=True)
  r=client.request(method,base+path,json=body)
 assert r.status_code==status,(r.status_code,r.text[:1900])
 return r.json()
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select START_AT,FINISH_AT from RRL_WORKLOAD_ATTENDANCE where PLAN_OPERATION_ID='WORKLOAD134.ATTEND:1a19738325'")
 # Use aware explicit wire values, not driver/session default timezone.
 q.execute("""select to_char(START_AT at time zone 'UTC','YYYY-MM-DD"T"HH24:MI:SS.FF6TZH:TZM'),
 to_char(FINISH_AT at time zone 'UTC','YYYY-MM-DD"T"HH24:MI:SS.FF6TZH:TZM') from RRL_WORKLOAD_ATTENDANCE where PLAN_OPERATION_ID='WORKLOAD134.ATTEND:1a19738325'""")
 start,finish=map(datetime.fromisoformat,q.fetchone())
 q.execute("select sum(r.REMAIN),sum(r.HARD_RESERVED_BASE)from RRL_REMAINS r join RRL_CELLS c on c.CELL=r.CELL where c.WARE_ID=6667491");original=q.fetchone()
 context=call("GET","/waves/395/time-context");assert context["version"]in(0,1),context
 def proposal(ctx,op,shift=0):
  return {"operation_id":op,"wave_id":395,"expected_version":ctx["version"],"source_token":ctx["source_token"],
   "start_at":(start+timedelta(hours=shift)).isoformat(),"finish_at":(finish+timedelta(hours=shift)).isoformat(),
   "time_zone":"Asia/Tbilisi","reason":"Own140 explicit shift approval with current staffing"}
 if context["version"]==0:
  first=proposal(context,"WAVE140.APPROVE:d9a5c53b54")
  a=call("POST","/waves/approve-time",first);assert a["version"]==1
  assert call("POST","/waves/approve-time",first)==a
  stale={**first,"operation_id":"WAVE140.STALE:d9a5c53b54"}
  rejected=call("POST","/waves/approve-time",stale,409);assert "WAVE_TIME_SOURCE_CHANGED"in str(rejected)
 monitor={"site_code":"QA134","start_at":start.isoformat(),"finish_at":finish.isoformat(),"interval_minutes":60,"wave_windows":[]}
 before=call("POST","/warehouses/6667491/preview",monitor)
 assert not before["unscheduled_work"] and Decimal(before["known_remaining_person_hours"])==4,before
 context=call("GET","/waves/395/time-context");assert context["plan_status"]=="APPROVED"
 shifted=proposal(context,"WAVE140.SHIFT:d9a5c53b54",1)
 b=call("POST","/waves/approve-time",shifted);assert b["version"]==2
 after=call("POST","/warehouses/6667491/preview",monitor)
 assert Decimal(after["intervals"][0]["required_person_hours"])==0,after
 assert Decimal(before["intervals"][0]["required_person_hours"])==2,before
 assert after["work_outside_view"],after
 # Mimic a legacy plan edit only on this private unstarted wave.
 q.execute("update RRL_PICK_WAVE set PLANNED_START_AT=PLANNED_START_AT+1/1440 where PICK_WAVE_ID=395");c.commit()
 changed=call("GET","/waves/395/time-context");assert changed["plan_status"]=="LEGACY_PLAN_CHANGED",changed
 invalid=call("POST","/warehouses/6667491/preview",monitor);assert invalid["unscheduled_work"],invalid
 restored=call("POST","/waves/approve-time",proposal(changed,"WAVE140.RECONFIRM:d9a5c53b54",1));assert restored["version"]==3
 naive={**proposal(call("GET","/waves/395/time-context"),"WAVE140.NAIVE:d9a5c53b54"),"start_at":"2026-10-10T14:52:16"}
 call("POST","/waves/approve-time",naive,422)
 q.execute("select sum(r.REMAIN),sum(r.HARD_RESERVED_BASE)from RRL_REMAINS r join RRL_CELLS c on c.CELL=r.CELL where c.WARE_ID=6667491");assert q.fetchone()==original==(20,20)
 q.execute("select STATUS from RRL_CASE_PICK_TASK where PICK_WAVE_ID=395");assert all(row[0]=="NEW"for row in q.fetchall())
 q.execute("select to_char(PLANNED_START_AT,'YYYY-MM-DD HH24:MI:SS')from RRL_PICK_WAVE where PICK_WAVE_ID=395")
 assert q.fetchone()[0]=="2026-10-10 19:52:16"
 print("PASS140 original wave395 aware approval/replay/stale409, monitor4person-hours; shift+1 moves first interval2->0 and work outside; legacy change invalidated/reconfirmedv3; naive422/P20H20/tasksNEW unchanged; Tbilisi planned wall19:52:16",flush=True)
