exec(open('scripts/ni063_slow_queries.py',encoding='utf-8').read().split('with oracledb.connect',1)[0])
from fastapi import FastAPI
from fastapi.testclient import TestClient
from app.routers.gps import router
from app.oracle_gateway import OracleGateway
from app.services.geofencing import check_geofences
from time import perf_counter
app=FastAPI();app.include_router(router)
folder=Path('reports/nicora/2026-10-13/codex/GEOFENCES');folder.mkdir(exist_ok=True);results={}
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select PASS from RUSERS where ID='admin'");password=q.fetchone()[0]
 address='NI081.SHOP.0b960a9257';q.execute('select GEO_FENCE_RADIUS_M from RRL_ADDR where ADDR=:a',a=address);original=q.fetchone()[0]
 with TestClient(app)as client:
  start=perf_counter();r=client.get('/api/admin/transport/geofences',auth=('admin',password));assert r.status_code==200,r.text;items=r.json();assert len(items)<=200 and all(isinstance(x['addr_id'],str)and -90<=x['lat']<=90 and -180<=x['lon']<=180 for x in items);results['GET']={'rows':len(items),'ms':round((perf_counter()-start)*1000,2)}
  try:
   r=client.patch('/api/admin/transport/geofences/'+address,json={'radius_m':213},auth=('admin',password));assert r.status_code==200,r.text
   r=client.get('/api/admin/transport/geofences',params={'addr_mask':address},auth=('admin',password));assert r.status_code==200 and len(r.json())==1 and r.json()[0]['radius_m']==213,r.text;results['own_roundtrip']=r.json()
  finally:
   q.callproc('RRL_STOCK_METADATA_TX.begin_change',['admin','warehouse_settings_edit'])
   try:q.execute('update RRL_ADDR set GEO_FENCE_RADIUS_M=:r where ADDR=:a',r=original,a=address);c.commit()
   finally:q.callproc('RRL_STOCK_METADATA_TX.end_change')
  r=client.patch('/api/admin/transport/geofences/'+address,json={'radius_m':0},auth=('admin',password));assert r.status_code==422
  r=client.patch('/api/admin/transport/geofences/OWN/ABSENT',json={'radius_m':200},auth=('admin',password));assert r.status_code==404,r.text;results['invalid_radius']=422;results['slash_address_route']=404
 # Real query only: impossible vehicle ID guarantees no physical event or operational fact.
 results['gps_lookup']=check_geofences(-987654321,0.0,0.0,OracleGateway());assert results['gps_lookup']==[]
 q.execute("select SQL_ID,EXECUTIONS,round(ELAPSED_TIME/nullif(EXECUTIONS,0)/1000,3)MS,BUFFER_GETS from V$SQL where PARSING_SCHEMA_NAME='RABAEV' and SQL_TEXT like '%SHIROTA AS LATITUDE%' and SQL_TEXT like '%GEO_FENCE_RADIUS_M%' and SQL_TEXT not like '%V$SQL%' order by LAST_ACTIVE_TIME desc fetch first 5 rows only");results['sql']=q.fetchall()
results['restored_radius']=original
(folder/'native.json').write_text(json.dumps(results,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps(results,ensure_ascii=True))
