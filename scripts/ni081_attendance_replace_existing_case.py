"""150 metadata-only future plan on existing135 resource43, cleanup via native cancellation."""
import sys,json
from pathlib import Path
from datetime import datetime,timezone,timedelta
from uuid import uuid4
from concurrent.futures import ThreadPoolExecutor
import httpx,oracledb
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment();sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"api/wms_api_server"))
from app.config import get_settings
s=get_settings();base="http://127.0.0.1:8088/api/resources/workload";tag=uuid4().hex[:10]
client=httpx.Client(auth=("admin","admin123"),timeout=35)
start=(datetime.now(timezone.utc)+timedelta(days=1)).replace(hour=10,minute=0,second=0,microsecond=0)
source="WORKLOAD150.ORIGINAL:"+tag
def post(path,body,status=200):
 r=client.post(base+path,json=body)
 if r.status_code==503:r=client.post(base+path,json=body)
 assert r.status_code==status,(r.status_code,r.text[:1800]);return r.json()
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor()
 q.execute("select sum(r.REMAIN),sum(r.HARD_RESERVED_BASE)from RRL_REMAINS r join RRL_CELLS c on c.CELL=r.CELL where c.WARE_ID=6667491");stock=q.fetchone()
 original={"operation_id":source,"warehouse_id":6667491,"site_code":"QA150","resource_id":43,"start_at":start.isoformat(),"finish_at":(start+timedelta(hours=2)).isoformat(),"reason":"Own metadata-only future replacement scenario"}
 post("/attendance",original);winner=None
 try:
  body={**original,"operation_id":"WORKLOAD150.REPLACE:"+tag,"plan_operation_id":source,
   "start_at":(start+timedelta(hours=1)).isoformat(),"finish_at":(start+timedelta(hours=3)).isoformat(),"reason":"Own atomic future interval change preserves original history"}
  bad={**body,"operation_id":"WORKLOAD150.BAD:"+tag,"resource_id":99999999}
  post("/attendance/replace",bad,404)
  q.execute("select count(*)from RRL_WORKLOAD_ATTEND_CANCEL where PLAN_OPERATION_ID=:op",op=source);assert q.fetchone()==(0,)
  q.execute("select count(*)from RRL_WORKLOAD_OPERATION where OPERATION_ID=:op",op=bad["operation_id"]);assert q.fetchone()==(0,)
  # An outer SQL caller catches the late error and commits: own savepoint must still preserve source.
  raw={k:v for k,v in bad.items()if k!="operation_id"}
  for key in("start_at","finish_at"):raw[key]=datetime.fromisoformat(raw[key]).astimezone(timezone.utc).isoformat(timespec="microseconds")
  caught="WORKLOAD150.CAUGHT:"+tag
  q.execute("""declare v_result clob;begin
    begin RRL_WORKLOAD_CONFIG_API.execute_command(:op,'admin','REPLACE_ATTENDANCE',:body,v_result);
    exception when no_data_found then null;end;end;""",op=caught,body=json.dumps(raw,sort_keys=True,separators=(",",":")))
  c.commit()
  q.execute("select count(*)from RRL_WORKLOAD_ATTEND_CANCEL where PLAN_OPERATION_ID=:op",op=source);assert q.fetchone()==(0,)
  q.execute("select count(*)from RRL_WORKLOAD_OPERATION where OPERATION_ID=:op",op=caught);assert q.fetchone()==(0,)
  competing={**body,"operation_id":"WORKLOAD150.RACE:"+tag,"finish_at":(start+timedelta(hours=4)).isoformat()}
  def race(value):
   with httpx.Client(auth=("admin","admin123"),timeout=35)as local:
    response=local.post(base+"/attendance/replace",json=value)
    if response.status_code==503:response=local.post(base+"/attendance/replace",json=value)
    return value,response
  with ThreadPoolExecutor(max_workers=2)as workers:
   results=list(workers.map(race,[body,competing]))
  assert sorted(r.status_code for _,r in results)==[200,409],[(r.status_code,r.text[:1000])for _,r in results]
  winner,response=next((b,r)for b,r in results if r.status_code==200);saved=response.json()
  assert saved["replaced_plan_operation_id"]==source and saved["plan_operation_id"]==winner["operation_id"]
  assert post("/attendance/replace",winner)==saved
  post("/attendance/replace",{**winner,"reason":"Different reason on the same operation identity is rejected"},409)
  current=client.get(base+"/warehouses/6667491");assert current.status_code==200
  rows=current.json()["planned_attendance"]
  assert not any(row["plan_operation_id"]==source for row in rows)
  newer=next(row for row in rows if row["plan_operation_id"]==winner["operation_id"])
  assert newer["replaced_plan_operation_id"]==source
  q.execute("select sum(r.REMAIN),sum(r.HARD_RESERVED_BASE)from RRL_REMAINS r join RRL_CELLS c on c.CELL=r.CELL where c.WARE_ID=6667491");assert q.fetchone()==stock==(20,20)
  print("PASS150 late bad resource404 and SQL catch+commit leave old future plan active/no placeholder; concurrent replacements one200 one409, same replay exact/changed409/original lineage visible/P20H20 unchanged/tag="+tag,flush=True)
 finally:
  target=winner["operation_id"]if winner else source
  post("/attendance/cancel",{"operation_id":"WORKLOAD150.CLEAN:"+tag,"warehouse_id":6667491,"plan_operation_id":target,"reason":"Close own future metadata-only scenario"})
