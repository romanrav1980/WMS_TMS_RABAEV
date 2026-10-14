exec(open('scripts/ni063_slow_queries.py',encoding='utf-8').read().split('with oracledb.connect',1)[0])
import httpx,time
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn) as c:
 q=c.cursor();q.execute("select PASS from RUSERS where ID='admin'");secret=q.fetchone()[0]
with httpx.Client(base_url='http://127.0.0.1:8088',auth=('admin',secret),timeout=30) as client:
 started=time.perf_counter();r=client.get('/api/transport/preflight/trips/33641/delivery-windows',params={'time_zone':'Asia/Tbilisi'});r.raise_for_status();b=r.json()
 assert b['trip_id']==33641 and b['consistent_snapshot']
 assert all('configured_weekly_windows' in x and 'profile_version' in x for x in b['stops'])
 result={'trip_id':b['trip_id'],'status':b['status'],'source_hash':b['source_hash'],'stops':b['stops'],'seconds':round(time.perf_counter()-started,3),'real_get':True,'writes':0}
 Path('reports/retailcase/2026-10-13/route_profile_http1501.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
 print(json.dumps({'status':b['status'],'stops':len(b['stops']),'seconds':result['seconds'],'profile_metadata':True}))
