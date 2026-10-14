"""Own136 metadata rows reused; actual departed trip guard is refusal only."""
import sys
from pathlib import Path
import httpx,oracledb
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment();sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'api/wms_api_server'))
from app.config import get_settings
from app.modules.platform.public import read_oracle_json
from app.modules.transport.public import cancel_trip
from app.oracle_gateway import OracleGateway
s=get_settings();base='http://127.0.0.1:8088';admin=httpx.Client(auth=('admin','admin123'),timeout=35)
def post(path,body,status=200):
 r=admin.post(base+path,json=body);assert r.status_code==status,(r.status_code,r.text[:2200]);return r.json()
def patch(trip,body,status=200):
 r=admin.patch(base+f'/api/admin/transport/tasks/{trip}',json=body);assert r.status_code==status,(r.status_code,r.text[:2200]);return r
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute('select PAYLOAD from RRL_PLANNER_PLANS where ID=632');route=read_oracle_json(q.fetchone()[0])['routes'][0]
 primary=route['vehicle_id'];plate=route['vehicle_num'];numbers=route['stops'];tag=plate[5:-1]
 q.execute('select ID,NUM from RRL_TR_VEHICLE where NUM=:num',num='QA136'+tag+'1');small,small_plate=q.fetchone()
 q.execute('update RRL_TR_VEHICLE set DELETED=0,BLOCKED=0 where ID in(:a,:b)',a=primary,b=small);c.commit()
 trip=post('/api/admin/transport/tasks',{'transtype':'20','shipment_date':'2026-10-10'})['task_id']
 try:
  q.execute('select USER_ID from RRL_TRANSPORT_TASK where ID=:id',id=trip);assert q.fetchone()==('admin',)
  patch(trip,{'transport':plate})
  post(f'/api/admin/transport/tasks/{trip}/sts',{'st_numbers':numbers})
  rejected=patch(trip,{'transport':small_plate},409);assert 'PLAN_WEIGHT_CAPACITY_EXCEEDED'in rejected.text,rejected.text
  q.execute('select TRANSPORT from RRL_TRANSPORT_TASK where ID=:id',id=trip);assert q.fetchone()==(plate,)
  patch(trip,{'primechanie':'Own137 consistent manual transport note'})
  q.execute('select PRIMECHANIE from RRL_TRANSPORT_TASK where ID=:id',id=trip);assert q.fetchone()[0]=='Own137 consistent manual transport note'
  q.execute('select SHIPMENT_DATE from RRL_TRANSPORT_TASK where ID=33521');original=q.fetchone()
  try:
   q.execute("update RRL_TRANSPORT_TASK set SHIPMENT_DATE=nvl(SHIPMENT_DATE,date'2026-10-10')+1 where ID=33521")
   raise AssertionError('Departed shipment date changed')
  except oracledb.DatabaseError as exc:
   assert exc.args[0].code==20886,str(exc);c.rollback()
  q.execute('select SHIPMENT_DATE from RRL_TRANSPORT_TASK where ID=33521');assert q.fetchone()==original
  print('PASS137 original metadata STs/current shared gate: owned draft '+str(trip)+' actual authenticated creator, twoST source current vehicle, smaller vehicle rejected409/oldplate retained, note saved; actual departed33521 direct shipment-date change20886/unchanged/no stock',flush=True)
 finally:
  cancel_trip(OracleGateway(),trip,'admin')
  q.execute('update RRL_TR_VEHICLE set DELETED=1,BLOCKED=1 where ID in(:a,:b)',a=primary,b=small);c.commit()
