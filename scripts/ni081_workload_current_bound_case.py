"""Same committed134 person and135 wave; changed boundary only, no fresh stock."""
import sys
from pathlib import Path
import httpx,oracledb
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment();sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'api/wms_api_server'))
from app.config import get_settings
s=get_settings();base='http://127.0.0.1:8088';admin=httpx.Client(auth=('admin','admin123'),timeout=35)
r=admin.post(base+'/api/admin/rights/groups/Q1341A19738325/rights',json={'right_name':'case_pick_execute','description':'Own planned CASE operator capability'});assert r.status_code==200,r.text
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("""select to_char(START_AT at time zone 'UTC','YYYY-MM-DD"T"HH24:MI:SS.FF6TZH:TZM'),
 to_char(FINISH_AT at time zone 'UTC','YYYY-MM-DD"T"HH24:MI:SS.FF6TZH:TZM')from RRL_WORKLOAD_ATTENDANCE where PLAN_OPERATION_ID='WORKLOAD134.ATTEND:1a19738325'""")
 start,end=q.fetchone();query={'site_code':'QA134','start_at':start,'finish_at':end}
 path=base+'/api/resources/workload/warehouses/6667491/preview'
 r=admin.post(path,json=query);assert r.status_code==200,r.text
 assert all(row['required_person_hours']is None and row['deficit_person_hours']is None for row in r.json()['intervals']),r.json()
 r=admin.get(base+'/api/resources/workload/warehouses/6667491');assert r.status_code==200,r.text
 assert any(row['resource_id']==43 for row in r.json()['eligible_case_resources'])
 body={'operation_id':'WORKLOAD135.FOREIGN_SITE:1a19738325','warehouse_id':6667491,'site_code':'FOREIGN_SITE','resource_id':43,'start_at':start,'finish_at':end,'reason':'Own cross-site overlap denial'}
 r=admin.post(base+'/api/resources/workload/attendance',json=body)
 if r.status_code==503:r=admin.post(base+'/api/resources/workload/attendance',json=body)
 assert r.status_code==409 and 'WORKLOAD_PERSON_OVERLAPPING_OTHER_SITE'in r.text,r.text
 print('PASS135 unscheduled workload suppresses interval required/deficit instead of false0, shift-view provides current qualified CASE resources without separate resource-admin grant, cross-site same person overlap denied409, no stock/tasks/new plan',flush=True)
