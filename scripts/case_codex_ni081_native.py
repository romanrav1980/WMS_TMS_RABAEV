exec(open('scripts/ni063_slow_queries.py',encoding='utf-8').read().split('with oracledb.connect',1)[0])
from copy import deepcopy
from time import perf_counter
outdir=Path('reports/nicora/2026-10-13/codex/NI081');outdir.mkdir(exist_ok=True)
source={'members':[{'address':'SHOP','route_ordinal':1,'st_number':'SAP_2135','delivery_window_from':'2026-10-14 08:00:00','delivery_window_to':'2026-10-14 18:00:00'}],
 'destination_rules':[{'address':'SHOP','address_count':1,'unload_norm_min':30,'window_strict':1}],
 'operations':[{'code':'DRIVE','plan_start':'2026-10-14 08:00:00','plan_end':'2026-10-14 12:00:00'},{'code':'DRIVE_BACK','plan_start':'2026-10-14 12:30:00','plan_end':'2026-10-14 18:00:00'}],
 'route_material':{'policy_id':'REV55_ROUTE_V6_120_15_540_ROAD24H','order_valid':True,'depot_address':'BASE','stops':['SHOP'],'legs':[
 {'from_address':'BASE','to_address':'SHOP','duration_min':150,'duration_basis':'ROAD_PROFILE_ESTIMATE','fresh':True},
 {'from_address':'SHOP','to_address':'BASE','duration_min':90,'duration_basis':'ROAD_PROFILE_ESTIMATE','fresh':True}]}}
results=[]
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute('set transaction read only');wire=q.var(oracledb.DB_TYPE_CLOB);out=q.var(oracledb.DB_TYPE_CLOB)
 def calc(label,data):
  wire.setvalue(0,json.dumps(data));start=perf_counter();q.callproc('RRL_TT_ROUTE_SCHEDULE.calculate',[wire,'Asia/Tbilisi',out]);value=json.loads(out.getvalue().read());results.append({'case':label,'ms':round((perf_counter()-start)*1000,2),'result':value});return value
 a=calc('150+90 split with REST, string ST',source);assert not a['issues'] and a['stops'][0]['st_numbers']==['SAP_2135'] and len([x for x in a['segments']if x['code']=='REST'])==1,a
 x=deepcopy(source);x['route_material']['legs'][0]['fresh']=False;b=calc('stale road',x);assert any(i['code']=='ROUTE_ROAD_MISSING_STALE_OR_UNSUPPORTED'for i in b['issues'])
 x=deepcopy(source);x['members'][0]['delivery_window_to']='2026-10-14 09:00:00';b=calc('hard late',x);assert any(i['code']=='DELIVERY_HARD_WINDOW_MISSED'for i in b['issues'])
 x['destination_rules'][0]['window_strict']=0;b=calc('soft late warning',x);assert not b['issues'] and b['warnings'][0]['code']=='DELIVERY_SOFT_WINDOW_MISSED'
 x=deepcopy(source);x['operations'][1]['plan_end']='2026-10-14 10:00:00';b=calc('short resource envelope',x);assert any(i['code']=='ROUTE_EXCEEDS_PLANNED_RESOURCE_ENVELOPE'for i in b['issues'])
 x=deepcopy(source);x['route_material']['legs'][0]['duration_min']=550;b=calc('drive >540',x);assert any(i['code']=='DRIVER_TRIP_DRIVE_LIMIT'for i in b['issues'])
 wire.setvalue(0,json.dumps(a['segments']));q.callproc('RRL_TT_ROUTE_SCHEDULE.assert_chain',[wire,'Asia/Tbilisi']);results.append({'case':'native combined chain valid','pass':True})
 bad=[{'code':'DRIVE','start_at':'2026-10-14T08:00:00.000000+04:00','finish_at':'2026-10-14T09:30:00.000000+04:00'},{'code':'WAIT','start_at':'2026-10-14T09:30:00.000000+04:00','finish_at':'2026-10-14T10:00:00.000000+04:00'},{'code':'DRIVE','start_at':'2026-10-14T10:00:00.000000+04:00','finish_at':'2026-10-14T11:00:00.000000+04:00'}]
 wire.setvalue(0,json.dumps(bad))
 try:q.callproc('RRL_TT_ROUTE_SCHEDULE.assert_chain',[wire,'Asia/Tbilisi'])
 except oracledb.DatabaseError as e:assert 'TT_TIME_DRIVER_CONTINUOUS_LIMIT'in str(e);results.append({'case':'WAIT does not reset continuous across trips','pass':True})
 else:raise AssertionError('WAIT reset driving')
 q.callproc('RRL_TT_TIME_API.context',[33564,'admin',out]);v=json.loads(out.getvalue().read());assert v['source']['source_contract_version']==6 and 'route_material'in v['source'];results.append({'case':'real TT33564 current V6 GET','status':v['approval_status'],'source_hash':v['source_hash']})
(outdir/'native_cases.json').write_text(json.dumps(results,ensure_ascii=False,indent=2),encoding='utf-8');print('PASS',len(results),'native readonly cases')
