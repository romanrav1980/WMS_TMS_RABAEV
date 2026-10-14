"""Existing unfinished CASE12+8 and own134 metadata, no new stock/tasks."""
import sys
from pathlib import Path
from decimal import Decimal
from datetime import datetime,timedelta
import httpx,oracledb
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment();sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'api/wms_api_server'))
from app.config import get_settings
s=get_settings();base='http://127.0.0.1:8088';admin=httpx.Client(auth=('admin','admin123'),timeout=35)
ware=6667491;tag='1a19738325';actor='Q134'+tag;plan_id='WORKLOAD134.ATTEND:'+tag
def post(path,body,status=200):
 r=admin.post(base+path,json=body);assert r.status_code==status,(r.status_code,r.text[:2000]);return r.json()
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor()
 post('/api/resources/workload/norms',{'operation_id':'WORKLOAD135.NORM:d9a5c53b54','warehouse_id':ware,'site_code':'QA134','article':'QNATIVED9A5C53B54','base_uom':'EA','base_per_hour':'5','expected_version':0,'active':True,'reason':'Own dev norm 5EA per person-hour'})
 q.execute("""select to_char(START_AT at time zone 'UTC','YYYY-MM-DD"T"HH24:MI:SS.FF6TZH:TZM'),
 to_char(FINISH_AT at time zone 'UTC','YYYY-MM-DD"T"HH24:MI:SS.FF6TZH:TZM')from RRL_WORKLOAD_ATTENDANCE where PLAN_OPERATION_ID=:op""",op=plan_id)
 start,end=q.fetchone()
 q.execute("select sum(r.REMAIN),sum(r.HARD_RESERVED_BASE)from RRL_REMAINS r join RRL_CELLS c on c.CELL=r.CELL where c.WARE_ID=:ware",ware=ware);stock=q.fetchone()
 query={'site_code':'QA134','start_at':start,'finish_at':end,'interval_minutes':60,'wave_windows':[]}
 path=f'/api/resources/workload/warehouses/{ware}/preview'
 unscheduled=post(path,query);assert unscheduled['status']=='UNSCHEDULED_WORK'and len(unscheduled['unscheduled_work'])==2,unscheduled
 query['wave_windows']=[{'wave_id':395,'start_at':start,'finish_at':end}]
 preview=post(path,query)
 assert preview['status']=='PREVIEW'and len(preview['work'])==2 and Decimal(preview['known_remaining_person_hours'])==4,preview
 assert sum(Decimal(row['required_person_hours'])for row in preview['intervals'])==4
 assert sum(Decimal(row['planned_person_hours'])for row in preview['intervals'])==2
 assert sum(Decimal(row['deficit_person_hours'])for row in preview['intervals'])==2
 assert not preview['plan_applied']and not preview['task_assignments_changed']and not preview['stock_changed']
 duplicate={'operation_id':'WORKLOAD135.OVERLAP:'+tag,'warehouse_id':ware,'site_code':'QA134','resource_id':43,'start_at':start,'finish_at':end,'reason':'Own duplicate role overlap for same person'}
 post('/api/resources/workload/attendance',duplicate)
 overlap=post(path,query)
 assert sum(Decimal(row['planned_person_hours'])for row in overlap['intervals'])==2
 assert all(row['planned_people']==1 for row in overlap['intervals'])
 post(path,{**query,'wave_windows':query['wave_windows']*2},409)
 post(path,{**query,'wave_windows':[{'wave_id':999999,'start_at':start,'finish_at':end}]},409)
 moved_start=(datetime.fromisoformat(start)+timedelta(hours=1)).isoformat();moved_end=(datetime.fromisoformat(end)+timedelta(hours=1)).isoformat()
 moved=post(path,{**query,'wave_windows':[{'wave_id':395,'start_at':moved_start,'finish_at':moved_end}]})
 assert Decimal(moved['intervals'][0]['required_person_hours'])==0
 post('/api/resources/workload/attendance/cancel',{'operation_id':'WORKLOAD135.CANCEL:'+tag,'warehouse_id':ware,'plan_operation_id':duplicate['operation_id'],'reason':'Close own overlapping-role demonstration'})
 q.execute("select sum(r.REMAIN),sum(r.HARD_RESERVED_BASE)from RRL_REMAINS r join RRL_CELLS c on c.CELL=r.CELL where c.WARE_ID=:ware",ware=ware);assert q.fetchone()==stock
 print('PASS135 actual CASE12+8/5EA per hour=4 person-hours, planned own person2h/deficit2h, overlapping same person not doubled, moving preview changes first interval without stock/tasks/legacy plans; unscheduled and foreign/duplicate window denials',flush=True)
