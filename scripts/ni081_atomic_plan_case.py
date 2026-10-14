"""Own metadata plan/ST/vehicles only; no physical goods or quantity postings."""
import sys,json
from pathlib import Path
from uuid import uuid4
from datetime import date
from concurrent.futures import ThreadPoolExecutor
import httpx,oracledb
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment();sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'api/wms_api_server'))
from app.config import get_settings
from app.oracle_gateway import OracleGateway
from app.modules.transport.public import cancel_trip
s=get_settings();tag=uuid4().hex[:10];base='http://127.0.0.1:8088';admin=httpx.Client(auth=('admin','admin123'),timeout=35)
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 c.call_timeout=15000;q=c.cursor()
 def seq(name):q.execute('select '+name+'.nextval from dual');return int(q.fetchone()[0])
 numbers=['PLAN136.ST:'+tag+':'+str(i)for i in range(3)];row_ids=[];vehicles=[]
 for index,capacity in enumerate((1000,10)):
  vid=int(q.callfunc('RRL_TR_VEHICLE_ADD',oracledb.DB_TYPE_NUMBER,['QA136'+tag+str(index),'20',capacity,2,1,None]));vehicles.append(vid)
 for number in numbers:
  sid=seq('RRL_SBORKA_PALLETS_SQ');row_ids.append(sid)
  q.execute("insert into RRL_SBORKA_PALLETS(ID,PALLET_UID,ST_NUMBER,WARE_ID,CONDITION,ADDR)values(:id,:u,:st,1,0,:addr)",id=sid,u=number,st=number,addr='Own136 '+tag)
  q.execute("insert into RRL_SBORKA_PALLET_ROWS(ID,PALLET_UID,ARTICUL,ORDER_WEIGHT,QUANTITY)values(RRL_SBORKA_PALLET_ROWS_SQ.nextval,:u,'DS-BASE',100,1)",u=number)
 plans=[]
 def plan(routes):
  pid=seq('SEQ_PLANNER_PLANS')
  q.execute("insert into RRL_PLANNER_PLANS(ID,PLAN_DATE,SOLVER,PAYLOAD,CREATED_BY)values(:id,:day,'AUTHOR_METADATA',:body,'admin')",id=pid,day=date(2026,10,10),body=json.dumps({'routes':routes}))
  plans.append(pid);return pid
 failure=plan([{'vehicle_id':vehicles[0],'vehicle_num':'QA136'+tag+'0','stops':[numbers[0]]},{'vehicle_id':vehicles[1],'vehicle_num':'QA136'+tag+'1','stops':[numbers[1]]}])
 success=plan([{'vehicle_id':vehicles[0],'vehicle_num':'QA136'+tag+'0','stops':numbers[:2]}])
 c.commit()
 q.execute('select count(*)from RRL_TRANSPORT_TASK');before=q.fetchone()[0]
 path=base+'/api/admin/transport/planner/apply'
 body={'plan_id':failure,'shipment_date':'2026-10-10'}
 r=admin.post(path,json=body);assert r.status_code==409 and 'PLAN_WEIGHT_CAPACITY_EXCEEDED'in r.text,(r.status_code,r.text)
 q.execute('select count(*)from RRL_TRANSPORT_TASK');assert q.fetchone()[0]==before
 q.execute('select APPLIED_AT from RRL_PLANNER_PLANS where ID=:id',id=failure);assert q.fetchone()[0]is None
 q.execute('select count(*)from RRL_PLANNER_APPLY_RESULT where PLAN_ID=:id',id=failure);assert q.fetchone()==(0,)
 def apply():
  with httpx.Client(auth=('admin','admin123'),timeout=35)as caller:
   answer=caller.post(path,json={'plan_id':success,'shipment_date':'2026-10-10'});assert answer.status_code==200,(answer.status_code,answer.text);return answer.json()
 with ThreadPoolExecutor(max_workers=2)as pool:
  a,b=list(pool.map(lambda _:apply(),range(2)))
 assert a==b and a['tasks_created']==1 and not a['driver_inferred_from_vehicle'],(a,b)
 trip=a['created_task_ids'][0]
 q.execute('select TRANSPORT,VODITEL_ID from RRL_TRANSPORT_TASK where ID=:id',id=trip);plate,driver=q.fetchone();assert plate=='QA136'+tag+'0'and driver is None
 r=admin.post(path,json={'plan_id':success,'shipment_date':'2026-10-10','dock':'Changed'});assert r.status_code==409,r.text
 r=admin.post(base+f'/api/admin/transport/tasks/{trip}/sts',json={'st_numbers':[numbers[2]]});assert r.status_code==409 and 'PLAN_PALLET_CAPACITY_EXCEEDED'in r.text,(r.status_code,r.text)
 q.execute('select TRANSTASK_ID from RRL_SBORKA_PALLETS where ID=:id',id=row_ids[2]);assert q.fetchone()[0]in(None,0)
 q.execute('select count(*)from RRL_TRANSPORT_TASK');assert q.fetchone()[0]==before+1
 print('PASS136 later-route overweight rolls whole apply back/no first TT/member/proof; concurrent same plan '+str(success)+' returns one originalTT '+str(trip)+' / independent driverNULL / changed dock409 / shared manual third pallet over capacity409; no stock fixtures',flush=True)
 cancel_trip(OracleGateway(),trip,'admin')
 for vid in vehicles:q.execute('update RRL_TR_VEHICLE set BLOCKED=1,DELETED=1 where ID=:id',id=vid)
 c.commit();print('Own metadata trip cancelled/native membership released/vehicles retired; immutable plan proof retained.',flush=True)
