"""Continue original134 operation; no new employee/norm/stock fixture."""
import sys
from pathlib import Path
from datetime import datetime,timezone,timedelta
import httpx,oracledb
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment();sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'api/wms_api_server'))
from app.config import get_settings
s=get_settings();tag='1a19738325';actor='Q134'+tag;group=actor.upper();ware=6667491;base='http://127.0.0.1:8088'
admin=httpx.Client(auth=('admin','admin123'),timeout=35)
def api(path,body,status=200):
 r=admin.post(base+path,json=body);assert r.status_code==status,(r.status_code,r.text[:2200]);return r.json()
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute('select PASS from RUSERS where ID=:id',id=actor);secret=q.fetchone()[0]
 api('/api/admin/rights/groups/'+group+'/rights',{'right_name':'wms_admin_login','description':'Own workload manager shell'})
 q.execute('select RESOURCE_ID from RRL_RESOURCE where RESOURCE_CODE=:code',code='Q134:'+tag);resource=int(q.fetchone()[0])
 norm={'operation_id':'WORKLOAD134.NORM:'+tag,'warehouse_id':ware,'site_code':'QA134','article':'QNATIVE6436439964','base_uom':'EA','base_per_hour':'5','expected_version':0,'active':True,'reason':'Own dev norm 5EA per person-hour'}
 saved=api('/api/resources/workload/norms',norm);assert api('/api/resources/workload/norms',norm)==saved
 api('/api/resources/workload/norms',{**norm,'base_per_hour':'6'},409)
 api('/api/resources/workload/norms',{**norm,'operation_id':norm['operation_id']+'.STALE'},409)
 q.execute("""select to_char(START_AT at time zone 'UTC','YYYY-MM-DD"T"HH24:MI:SS.FF6TZH:TZM'),
 to_char(FINISH_AT at time zone 'UTC','YYYY-MM-DD"T"HH24:MI:SS.FF6TZH:TZM')from RRL_WORKLOAD_ATTENDANCE where PLAN_OPERATION_ID=:op""",op='WORKLOAD134.ATTEND:'+tag)
 times=q.fetchone();start=datetime.fromisoformat(times[0])if times else datetime.now(timezone.utc)+timedelta(hours=1);end=datetime.fromisoformat(times[1])if times else start+timedelta(hours=2)
 plan={'operation_id':'WORKLOAD134.ATTEND:'+tag,'warehouse_id':ware,'site_code':'QA134','resource_id':resource,'start_at':start.isoformat(),'finish_at':end.isoformat(),'reason':'Own two-hour CASE attendance plan'}
 saved=api('/api/resources/workload/attendance',plan);assert api('/api/resources/workload/attendance',plan)==saved
 api('/api/resources/workload/attendance',{**plan,'operation_id':plan['operation_id']+'.NAIVE','start_at':start.replace(tzinfo=None).isoformat()},422)
 reader=httpx.Client(auth=(actor,secret),timeout=35)
 r=reader.get(base+f'/api/resources/workload/warehouses/{ware}');assert r.status_code==200,r.text
 assert any(row['person_id']==actor for row in r.json()['planned_attendance'])
 q.execute('update RUSERS set WARE_ID=9104 where ID=:id',id=actor);c.commit()
 assert reader.get(base+f'/api/resources/workload/warehouses/{ware}').status_code==403
 assert reader.post(base+'/api/resources/workload/norms',json=norm).status_code==403
 q.execute('update RUSERS set WARE_ID=:ware where ID=:id',ware=ware,id=actor);c.commit()
 print('PASS134 original norm v1/replay/stale+changed409, existing resource43/person '+actor+' planned2h/naive422/foreign read+saved replay403, original plan retained for135; no stock or physical presence',flush=True)
