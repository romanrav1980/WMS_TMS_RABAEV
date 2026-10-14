"""Own metadata fixtures only, existing resources API and SKU BASE policy."""
import sys,json
from pathlib import Path
from uuid import uuid4
from datetime import datetime,timezone,timedelta
import httpx,oracledb
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment()
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'api/wms_api_server'))
from app.config import get_settings
s=get_settings();tag=uuid4().hex[:10];actor='Q134'+tag;group=actor.upper();secret=uuid4().hex
ware=6667491;article='QNATIVE6436439964'
admin=httpx.Client(auth=('admin','admin123'),timeout=35)
base='http://127.0.0.1:8088'
def api(path,body,status=200):
 r=admin.post(base+path,json=body);assert r.status_code==status,(r.status_code,r.text[:2200]);return r.json()
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor()
 q.execute("insert into RUSERS(ID,PASS,NAME,USER_GROUP,WARE_ID,DELETED,PRAVO_ADMIN_LOGIN)values(:id,:secret,'Own planned CASE operator',:grp,:ware,0,0)",id=actor,secret=secret,grp=group,ware=ware);c.commit()
 api('/api/admin/rights/groups',{'id':group,'name':'Own planned CASE operator'})
 for right in ['resource_shift_edit','resource_shift_view','wms_admin_login','case_pick_execute']:
  api('/api/admin/rights/groups/'+group+'/rights',{'right_name':right,'description':'Own workload'})
 resource=api('/api/resources',{'resource_code':'Q134:'+tag,'resource_name':'Own workload CASE person','resource_type':'CASE_PICKER','user_id':actor,'ware_id':ware,'created_by':'admin'})['id']
 r=admin.put(base+f'/api/resources/{resource}/qualifications',json={'task_type':'CASE_PICK','active':True});assert r.status_code==200,r.text
 q.execute("select nvl(max(VERSION_NO),0)from RRL_WORKLOAD_NORM where WARE_ID=:ware and SITE_CODE='QA134'and ARTICLE=:article and BASE_UOM='EA'",ware=ware,article=article);version=int(q.fetchone()[0])
 norm={'operation_id':'WORKLOAD134.NORM:'+tag,'warehouse_id':ware,'site_code':'QA134','article':article,'base_uom':'EA','base_per_hour':'5','expected_version':version,'active':True,'reason':'Own dev norm 5EA per person-hour'}
 saved=api('/api/resources/workload/norms',norm);assert api('/api/resources/workload/norms',norm)==saved
 conflict=api('/api/resources/workload/norms',{**norm,'base_per_hour':'6'},409)
 stale=api('/api/resources/workload/norms',{**norm,'operation_id':norm['operation_id']+'.STALE'},409)
 start=datetime.now(timezone.utc).replace(microsecond=0)+timedelta(hours=1);end=start+timedelta(hours=2)
 plan={'operation_id':'WORKLOAD134.ATTEND:'+tag,'warehouse_id':ware,'site_code':'QA134','resource_id':int(resource),'start_at':start.isoformat(),'finish_at':end.isoformat(),'reason':'Own two-hour CASE attendance plan'}
 attendance=api('/api/resources/workload/attendance',plan);assert api('/api/resources/workload/attendance',plan)==attendance
 api('/api/resources/workload/attendance',{**plan,'operation_id':plan['operation_id']+'.NAIVE','start_at':start.replace(tzinfo=None).isoformat()},422)
 reader=httpx.Client(auth=(actor,secret),timeout=35)
 r=reader.get(base+f'/api/resources/workload/warehouses/{ware}');assert r.status_code==200,r.text
 assert any(row['person_id']==actor for row in r.json()['planned_attendance'])
 q.execute('update RUSERS set WARE_ID=9104 where ID=:id',id=actor);c.commit()
 assert reader.get(base+f'/api/resources/workload/warehouses/{ware}').status_code==403
 assert reader.post(base+'/api/resources/workload/norms',json=norm).status_code==403
 q.execute('update RUSERS set WARE_ID=:ware where ID=:id',ware=ware,id=actor);c.commit()
 # Keep active own planned person for following bounded monitor slice; no real attendance asserted.
 print('PASS134 norm version/replay/stale+changed409, existing CASE resource '+str(resource)+' / person '+actor+' / aware planned2h / naive422 / foreign read+saved replay403; plan='+plan['operation_id'],flush=True)
 print('Fixture intentionally kept active for following workload monitor; planned, not physical presence.',flush=True)
