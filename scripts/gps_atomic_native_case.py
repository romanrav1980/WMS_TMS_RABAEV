exec(open('scripts/ni063_slow_queries.py',encoding='utf-8').read().split('with oracledb.connect',1)[0])
from datetime import datetime,timedelta
from contextlib import contextmanager
from uuid import uuid4
from app.modules.transport.public import ingest_gps
from app.routers.gps import GpsTrackRequest
from pydantic import ValidationError
from time import perf_counter
folder=Path('reports/retailcase/2026-10-13/codex/GEOFENCES');result={}
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.callproc('RRL_STOCK_CONFIG_API.begin_change',['admin','warehouse_settings_edit'])
 try:vid=int(q.callfunc('RRL_TR_VEHICLE_ADD',oracledb.DB_TYPE_NUMBER,['GPSQA'+uuid4().hex[:8],'20',10,2,1,None]))
 finally:q.callproc('RRL_STOCK_CONFIG_API.end_change')
 class RollbackGateway:
  @contextmanager
  def transaction(self,_name):
   yield q
 try:
  start=perf_counter();gw=RollbackGateway();new=datetime(2030,1,15,9,30,0)
  first=ingest_gps(gw,vid,41,44,0,new)
  stale=ingest_gps(gw,vid,42,45,0,new-timedelta(minutes=1))
  equal=ingest_gps(gw,vid,41.1,44.1,0,new)
  q.execute('select LAT,LON,TS from RRL_VEHICLE_GPS_LAST where VEHICLE_ID=:v',v=vid);last=q.fetchone();assert last==(41.1,44.1,new),last
  q.execute('select count(*)from RRL_VEHICLE_GPS where VEHICLE_ID=:v',v=vid);assert q.fetchone()[0]==3
  assert first['current_position_updated']and not stale['current_position_updated']and equal['current_position_updated']
  result={'fixture_vehicle':vid,'rollback':True,'packets':3,'history':3,'last_timestamp':last[2].isoformat(),'ms':round((perf_counter()-start)*1000,2)}
 finally:c.rollback()
 q.execute('select count(*)from RRL_VEHICLE_GPS where VEHICLE_ID=:v',v=vid);assert q.fetchone()[0]==0
 q.execute('select count(*)from RRL_VEHICLE_GPS_LAST where VEHICLE_ID=:v',v=vid);assert q.fetchone()[0]==0
 q.execute('select count(*)from RRL_TR_VEHICLE where ID=:v',v=vid);assert q.fetchone()[0]==0
 q.execute("select SQL_ID,EXECUTIONS,round(ELAPSED_TIME/nullif(EXECUTIONS,0)/1000,3),BUFFER_GETS from V$SQL where PARSING_SCHEMA_NAME='RABAEV'and(SQL_TEXT like 'insert into RRL_VEHICLE_GPS(%'or SQL_TEXT like 'select ID from RRL_TR_VEHICLE where ID=:vid%'or SQL_TEXT like 'update RRL_VEHICLE_GPS_LAST set LAT%')order by LAST_ACTIVE_TIME desc fetch first 4 rows only");result['sql']=q.fetchall()
for ts in ['2030-01-15T09:30:00Z','2030-01-15T09:30:00.1','2030-99-01T09:30:00',123]:
 try:GpsTrackRequest(vehicle_id=1,lat=0,lon=0,ts=ts);raise AssertionError('invalid timestamp accepted')
 except ValidationError:pass
assert GpsTrackRequest(vehicle_id=1,lat=0,lon=0,ts='2030-01-15T09:30:00').ts==datetime(2030,1,15,9,30)
result['timestamp_validation']='PASS'
(folder/'gps_atomic.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps(result))
