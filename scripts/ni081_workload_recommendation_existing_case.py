"""161 existing20 remainingCASE/rate5; future scenario only, no people/tasks/stock mutations."""
import sys
from pathlib import Path
from decimal import Decimal
import httpx,oracledb
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment();sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"api/wms_api_server"))
from app.config import get_settings
s=get_settings();body={"site_code":"QA134","start_at":"2026-10-11T10:00:00+00:00","finish_at":"2026-10-11T12:00:00+00:00","interval_minutes":60,
 "wave_windows":[{"wave_id":395,"start_at":"2026-10-11T10:00:00+00:00","finish_at":"2026-10-11T12:00:00+00:00"}]}
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select sum(r.REMAIN),sum(r.HARD_RESERVED_BASE)from RRL_REMAINS r join RRL_CELLS c on c.CELL=r.CELL where c.WARE_ID=6667491");stock=q.fetchone()
 q.execute("select count(*)from RRL_WORKLOAD_ATTENDANCE");plans=q.fetchone()
 q.execute("select count(*)from RRL_WAVE_TIME_PLAN");wave_plans=q.fetchone()
 with httpx.Client(auth=("admin","admin123"),timeout=30)as client:
  path="http://127.0.0.1:8088/api/resources/workload/warehouses/6667491/preview"
  response=client.post(path,json=body);assert response.status_code==200,(response.status_code,response.text[:1800])
  result=response.json();proposal=result["recommendations"]
  assert Decimal(result["known_remaining_person_hours"])==4,result
  assert proposal["status"]=="CAPACITY_ACTIONS"and len(proposal["capacity_actions"])==2,proposal
  assert all(row["additional_full_interval_people"]==2 and row["additional_planned_person_hours"]=="2.000000000"for row in proposal["capacity_actions"])
  wave=next(row for row in proposal["wave_duration_scenarios"]if row["wave_id"]==395)
  assert wave["one_person_to_utc"]=="2026-10-11T14:00:00+00:00"and wave["one_person_required_seconds"]=="14400",wave
  assert wave["current_window_change_required"]is True and not wave["wave_time_applied"]
  assert not proposal["operational_admission"] and not proposal["planned_attendance_applied"]
  unknown=client.post(path,json={**body,"site_code":"QA161_UNCONFIGURED"})
  assert unknown.status_code==200,(unknown.status_code,unknown.text[:1800])
  missing=unknown.json()["recommendations"]
  assert missing["status"]=="SOURCE_COMPLETION_REQUIRED"and missing["unresolved_intervals"]and not missing["capacity_actions"],missing
 q.execute("select count(*)from RRL_WORKLOAD_ATTENDANCE");assert q.fetchone()==plans
 q.execute("select count(*)from RRL_WAVE_TIME_PLAN");assert q.fetchone()==wave_plans
 q.execute("select sum(r.REMAIN),sum(r.HARD_RESERVED_BASE)from RRL_REMAINS r join RRL_CELLS c on c.CELL=r.CELL where c.WARE_ID=6667491");assert q.fetchone()==stock==(20,20)
 print("PASS161 existing CASE20/rate5 ->4personhours; proposed2h interval needs2people/oneperson until14UTC; no futureavailability assumed/missingnorm no definiteaction/no roster/wave/task/P20H20 mutation",flush=True)
