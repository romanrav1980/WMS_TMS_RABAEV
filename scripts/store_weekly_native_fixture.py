exec(open('scripts/ni063_slow_queries.py',encoding='utf-8').read().split('with oracledb.connect')[0])
from contextlib import contextmanager
from time import perf_counter
from uuid import uuid4
from app.modules.platform.public import read_oracle_json
from app.modules.master_data.infrastructure.store_profile import StoreProfile,read_profile
f=json.loads(Path('reports/nicora/2026-10-13/codex/NI081/fixture.json').read_text(encoding='utf-8'))
assert f['trip_id']==33641 and f['st_id']==641515 and f['planning_only']
report={'trip_id':f['trip_id'],'writes_scope':'own planning fixture only; profile restore new version; ST/road exact restore; final approval rollback','cases':{},'timings_ms':{}}
tag='WEEKLY.'+uuid4().hex[:10]
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 c.call_timeout=30000;q=c.cursor()
 class Gateway:
  @contextmanager
  def transaction(self,label):
   try:yield q
   except Exception:c.rollback();raise
   else:c.commit()
 owner=StoreProfile(Gateway())
 def native(name,args):
  out=q.var(oracledb.DB_TYPE_CLOB);start=perf_counter();q.callproc(name,args+[out]);result=read_oracle_json(out.getvalue());report['timings_ms'].setdefault(name,[]).append(round((perf_counter()-start)*1000,3));return result
 def context():return native('RRL_TT_TIME_API.context',[f['trip_id'],'admin'])
 def calc(ctx):return native('RRL_TT_ROUTE_SCHEDULE.calculate',[json.dumps(ctx['source']),'Asia/Tbilisi'])
 def profile_save(version,windows,suffix):
  return owner.save('admin',{'operation_id':tag+suffix,'store_addr':f['shop'],'expected_version':version,'reason':'Own NI081 bounded weekly native acceptance, outer rollback','receiving_window_mode':'WEEKLY','timezone_region':'Asia/Tbilisi','windows':windows})
 def config(sql,params):
  q.callproc('RRL_STOCK_CONFIG_API.begin_change',['admin','finished_goods_edit'])
  try:q.execute(sql,params)
  finally:q.callproc('RRL_STOCK_CONFIG_API.end_change')
  c.commit()
 before=context();before_profile=read_profile(q,f['shop']);
 q.execute('select ZONE_TIME_PLAN_IN,ZONE_TIME_PLAN_OUT from RRL_SBORKA_PALLETS where ID=:id',id=f['st_id']);old_windows=q.fetchone()
 q.execute("select FROM_ADDR,TO_ADDR,UPDATED_AT from RRL_ADDR_DISTANCE_MATRIX where SOURCE='NI081TEST' and ((FROM_ADDR=:a and TO_ADDR=:b)or(FROM_ADDR=:b and TO_ADDR=:a))",a=f['base'],b=f['shop']);old_roads=q.fetchall();c.rollback()
 saved=None
 try:
  config('update RRL_ADDR_DISTANCE_MATRIX set UPDATED_AT=sysdate where SOURCE=\'NI081TEST\' and ((FROM_ADDR=:a and TO_ADDR=:b)or(FROM_ADDR=:b and TO_ADDR=:a))',{'a':f['base'],'b':f['shop']})
  # 2030-01-15 Tuesday; opening 11:30 forces wait after 150 min road +15 rest.
  windows=[{'weekday':2,'from_minute':690,'to_minute':900},{'weekday':2,'from_minute':960,'to_minute':1080}]
  saved=profile_save(before_profile['version'],windows,'.PROFILE1')
  materialized=context();m=calc(materialized)
  assert m['stops'][0]['window_source']=='ST_MATERIALIZED',m
  report['cases']['materialized_precedence']={'window_source':m['stops'][0]['window_source'],'service_start':m['stops'][0]['service_start_at']}
  config('update RRL_SBORKA_PALLETS set ZONE_TIME_PLAN_IN=null,ZONE_TIME_PLAN_OUT=null where ID=:id',{'id':f['st_id']})
  ctx=context();preview=calc(ctx)
  assert not preview['issues'],preview
  assert preview['stops'][0]['window_source']=='STORE_WEEKLY',preview
  assert 'T11:30:' in preview['stops'][0]['service_start_at'],preview
  report['cases']['weekly_fallback']=preview
  body={'trip_id':f['trip_id'],'expected_version':ctx['version'],'source_hash':ctx['source_hash'],'time_zone':'Asia/Tbilisi','reason':'Own weekly final calculator proof, outer rollback'}
  approved=native('RRL_TT_TIME_API.approve',[tag+'.APPROVE','admin',json.dumps(body)])
  assert approved['route_schedule']==preview,(approved['route_schedule'],preview)
  report['cases']['same_final_calculator']={'version':approved['version'],'source_contract_version':approved['source_contract_version'],'schedule_equal':True}
  c.rollback()
  changed=profile_save(saved['version'],[{'weekday':2,'from_minute':720,'to_minute':1080}],'.PROFILE2')
  changed_ctx=context();assert changed_ctx['source_hash']!=ctx['source_hash']
  report['cases']['profile_edit_invalidates_hash']={'old':ctx['source_hash'],'new':changed_ctx['source_hash'],'approval_status':changed_ctx['approval_status']}
  try:native('RRL_TT_TIME_API.approve',[tag+'.STALE','admin',json.dumps(body)])
  except oracledb.DatabaseError as error:
   assert 'TT_TIME_SOURCE_CHANGED'in str(error),str(error);report['cases']['stale_rejected']=True
  else:raise AssertionError('Stale hash was approved')
 finally:
  c.rollback()
  config('update RRL_SBORKA_PALLETS set ZONE_TIME_PLAN_IN=:a,ZONE_TIME_PLAN_OUT=:b where ID=:id',{'a':old_windows[0],'b':old_windows[1],'id':f['st_id']})
  for a,b,t in old_roads:config('update RRL_ADDR_DISTANCE_MATRIX set UPDATED_AT=:t where FROM_ADDR=:a and TO_ADDR=:b',{'a':a,'b':b,'t':t})
  current=read_profile(q,f['shop']);c.rollback()
  if saved is not None:
   restored=owner.save('admin',{'operation_id':tag+'.RESTORE','store_addr':f['shop'],'expected_version':current['version'],'reason':'Restore original own fixture profile semantics after bounded weekly test',**before_profile['profile'],'windows':before_profile['windows']})
  after=context();after_profile=read_profile(q,f['shop']);c.rollback()
  clean_before=dict(before['source']);clean_after=dict(after['source']);clean_before.pop('store_window_profiles',None);clean_after.pop('store_window_profiles',None)
  report['rollback']={'original_nonprofile_source_restored':clean_before==clean_after,'approval_version_restored':after['version']==before['version'],'profile_semantics_restored':after_profile['profile']==before_profile['profile']and after_profile['windows']==before_profile['windows'],'profile_new_restore_version':after_profile['version']}
  Path('reports/nicora/2026-10-13/codex/STORE_WEEKLY/native_fixture.json').write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding='utf-8')
  assert all(report['rollback'].values()),report['rollback']
print(json.dumps({'cases':list(report['cases']),'timings_ms':report['timings_ms'],'rollback':report['rollback']}))
