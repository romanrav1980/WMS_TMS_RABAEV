"""151 original150 metadata chain only, no fixture/stock/calendar edits."""
import sys
from pathlib import Path
import httpx,oracledb
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment();sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"api/wms_api_server"))
from app.config import get_settings
s=get_settings()
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select CANCEL_OPERATION_ID from RRL_WORKLOAD_ATTEND_CANCEL where PLAN_OPERATION_ID='WORKLOAD150.ORIGINAL:646cf96a33'");new=q.fetchone()[0]
 q.execute("select count(*)from RRL_WORKLOAD_OPERATION");before=q.fetchone()
 with httpx.Client(auth=("admin","admin123"),timeout=30)as client:
  path="http://127.0.0.1:8088/api/resources/workload/warehouses/6667491/attendance/"+new+"/history"
  r=client.get(path,params={"limit":1});assert r.status_code==200,(r.status_code,r.text[:1800]);first=r.json()
  assert first["has_more"]and first["rows"][0]["plan_operation_id"]==new
  old=first["next_plan_operation_id"];assert old=="WORKLOAD150.ORIGINAL:646cf96a33",first
  previous=client.get(path.replace(new,old),params={"limit":1});assert previous.status_code==200
  parent=previous.json();assert not parent["has_more"]and parent["rows"][0]["cancel_operation_id"]==new,parent
  assert first["rows"][0]["cancel_operation_id"]=="WORKLOAD150.CLEAN:646cf96a33"
  whole=client.get(path);assert whole.status_code==200 and len(whole.json()["rows"])==2
  assert whole.json()["rows"][0]["planned_by"]=="admin"and whole.json()["rows"][1]["planned_by"]=="admin"
  assert not first["actual_presence_created"]and not first["frozen_daily_report"]
  wrong=client.get(path.replace("warehouses/6667491","warehouses/9104"));assert wrong.status_code==404,(wrong.status_code,wrong.text[:1000])
 q.execute("select count(*)from RRL_WORKLOAD_OPERATION");assert q.fetchone()==before
 print("PASS151 original150 chain2/limit1 continuation/aware original and cancel times/source lineage/foreign plan404/operation count unchanged; no actual attendance claimed",flush=True)
