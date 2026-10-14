"""Existing projected sources, no fresh stock or departed cargo."""
import sys
from pathlib import Path
from uuid import uuid4
import httpx,oracledb
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment()
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'api/wms_api_server'))
from app.config import get_settings
s=get_settings();actor='Q133'+uuid4().hex[:10];group=actor.upper();secret=uuid4().hex
admin=httpx.Client(auth=('admin','admin123'),timeout=35)
receiver=httpx.Client(auth=(actor,secret),timeout=35)
base='http://127.0.0.1:8088';load='CASE.SINGLE.LOAD:a6bcf2cbe3:1029'
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor()
 q.execute("insert into RUSERS(ID,PASS,NAME,USER_GROUP,WARE_ID,DELETED,PRAVO_ADMIN_LOGIN)values(:id,:secret,'Own forecast reader',:grp,11027346,0,0)",id=actor,secret=secret,grp=group);c.commit()
 try:
  r=admin.post(base+'/api/admin/rights/groups',json={'id':group,'name':'Own forecast reader'});assert r.status_code==200,r.text
  for right in ['transport_dispatch_view','transport_dispatch_edit']:
   r=admin.post(base+'/api/admin/rights/groups/'+group+'/rights',json={'right_name':right,'description':'Own forecast'});assert r.status_code==200,r.text
  path=base+'/api/transport/warehouse-forecast'
  r=receiver.post(path+'/source',json={'source_load_operation_id':load});assert r.status_code==200,r.text
  assert receiver.post(path+'/source',json={'source_load_operation_id':load}).json()==r.json()
  q.execute('select LOAD_COUNT,TOP_PLACES from RRL_FORECAST_DAY where WARE_ID=11027346 and DAY_UTC=date\'2026-10-10\'');assert q.fetchone()==(2,2)
  q.execute('update RUSERS set WARE_ID=9104 where ID=:id',id=actor);c.commit()
  assert receiver.post(path+'/source',json={'source_load_operation_id':load}).status_code==403
  assert receiver.post(path+'/warehouses/11027346/view',json={}).status_code==403
  assert receiver.post(path+'/warehouses/11027346/project').status_code==403
  try:
   q.execute("update RRL_FORECAST_DAY set LOAD_COUNT=LOAD_COUNT+1,TOP_PLACES=TOP_PLACES+1 where WARE_ID=11027346")
   raise AssertionError('Direct write unexpectedly allowed')
  except oracledb.DatabaseError as exc:
   assert exc.args[0].code==20863,str(exc)
   c.rollback()
  print('PASS133 current own actor/replayed exact source, foreign materialization/replay/read403, direct counter DML20863, original counts2/top2',flush=True)
 finally:
  q.execute('update RUSERS set DELETED=1 where ID=:id',id=actor);c.commit()
