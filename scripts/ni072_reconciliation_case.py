import sys
from pathlib import Path
from uuid import uuid4
import httpx,oracledb
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment()
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"api/wms_api_server"))
from app.config import get_settings
s=get_settings();tag=uuid4().hex[:10];actor="QDR"+tag;group=actor.upper();secret=uuid4().hex
admin=httpx.Client(auth=("admin","admin123"),timeout=35);user=httpx.Client(auth=(actor,secret),timeout=35);base="http://127.0.0.1:8088"
def get(client,ware,status=200,zone="Asia/Tbilisi"):
 r=client.get(base+f"/api/finance/day-reconciliation/warehouses/{ware}",params={"business_date":"2026-10-10","timezone_region":zone});assert r.status_code==status,(r.status_code,r.text[:1600]);return r.json()
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn) as c:
 q=c.cursor();ware=2378876
 q.execute("insert into RUSERS(ID,PASS,NAME,USER_GROUP,WARE_ID,DELETED,PRAVO_ADMIN_LOGIN)values(:id,:secret,'Own consistent day observer',:grp,:ware,0,0)",id=actor,secret=secret,grp=group,ware=ware);c.commit()
 r=admin.post(base+"/api/admin/rights/groups",json={"id":group,"name":"Own day reconciliation"});assert r.status_code==200
 r=admin.post(base+f"/api/admin/rights/groups/{group}/rights",json={"right_name":"transport_dispatch_view","description":"Own day read only"});assert r.status_code==200
 try:
  q.execute("select count(*)from RRL_EVENTS");before=q.fetchone()[0]
  result=get(user,ware);assert result["consistent_snapshot"] and not result["day_closed"]
  assert result["from_utc"]=="2026-10-09T20:00:00+00:00"
  assert result["daily_facts"]["physical_places_loaded"]==1 and result["daily_facts"]["store_receipts"]==1
  assert result["current_backlog"]["expense_allocation_pending"]==0
  assert any(row["status"]=="EXPORTED" for row in result["erp_unacknowledged"]) and any(row["code"]=="external_erp_ack_pending"for row in result["open_items"])
  assert result["stock"]["physical_unit_composition_conflicts"]==0
  get(user,9104,403);get(user,ware,422,"No/Such_Zone")
  q.execute("select count(*)from RRL_EVENTS");assert q.fetchone()[0]==before
  print("PASS116 current warehouse/read-only consistent snapshot/Tbilisi exact UTC day/loaded1/store1/source finance no pending allocation/EXPORTED still ERP pending/current stock units/no goods, foreign403 and invalid zone422; tag="+tag,flush=True)
 finally:
  q.execute("update RUSERS set DELETED=1 where ID=:id",id=actor);c.commit()
 q.execute("""select SQL_ID,round(ELAPSED_TIME/1000/nullif(EXECUTIONS,0),3),EXECUTIONS from V$SQL where upper(SQL_TEXT) like '%:DAY_FROM%' and upper(SQL_TEXT) not like '%V$SQL%' and EXECUTIONS>0 order by ELAPSED_TIME desc fetch first 4 rows only""")
 print("SQL milliseconds/executions",q.fetchall())
