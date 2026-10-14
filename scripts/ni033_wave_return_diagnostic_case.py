"""168 actual returned1037 + open1031; current scope; no goods mutations."""
import sys
from pathlib import Path
import httpx,oracledb
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment();sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"api/wms_api_server"))
from app.config import get_settings
from app.oracle_gateway import OracleGateway
from app.modules.inventory.infrastructure.wave_execution import WaveExecution
s=get_settings();actor="Q1341a19738325";service=WaveExecution(OracleGateway())
result=service.preview(402,"admin")
case=next(x for x in result["items"]if x["kind"]=="CASE"and x["id"]=="1037")
assert case["quantity"]=="1" and case["physical_stock_rows"]==0
assert case["display_reason"]=="CANCELLED_CASE_DEMAND_REPLAN_REQUIRED"
assert case["reason"]=="CASE_CONTROL_OR_SHIPPING_PENDING"and not result["ready"]
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select PASS,USER_GROUP,WARE_ID from RUSERS where ID=:p_actor",p_actor=actor);secret,group,ware=q.fetchone()
 q.execute("select count(*)from RIGHTS where USER_GROUP=:p_group and lower(trim(RIGHT1))='pick_wave_view'",p_group=group);had=q.fetchone()[0]
 if not had:q.execute("insert into RIGHTS(USER_GROUP,RIGHT1)values(:p_group,'pick_wave_view')",p_group=group);c.commit()
 try:
  with httpx.Client(auth=(actor,secret),timeout=30)as client:
   url="http://127.0.0.1:8088/api/picking/waves/"
   own=client.get(url+"395/execution");assert own.status_code==200,(own.status_code,own.text[:800])
   assert client.get(url+"402/execution").status_code==403
   assert client.get(url+"999999999/execution").status_code==404
 finally:
  if not had:q.execute("delete from RIGHTS where USER_GROUP=:p_group and RIGHT1='pick_wave_view'",p_group=group);c.commit()
 q.execute("select sum(r.REMAIN),sum(r.HARD_RESERVED_BASE)from RRL_REMAINS r join RRL_CELLS x on x.CELL=r.CELL where x.WARE_ID=6667491");assert q.fetchone()==(20,20)
print("PASS168 returned CASE1037 historical1/physicalrows0/replan diagnostic, native blocker unchanged; actual scoped HTTP own200/foreign403/missing404; original P20H20 unchanged")
