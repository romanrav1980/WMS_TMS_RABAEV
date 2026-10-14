exec(open('scripts/ni063_slow_queries.py',encoding='utf-8').read().split('with oracledb.connect',1)[0])
from datetime import datetime
from uuid import uuid4
from time import perf_counter
from app.modules.platform.public import read_oracle_json
outdir=Path('reports/retailcase/2026-10-13/codex/NI081');file=outdir/'fixture.json'
assert not file.exists(),'Fixture already allocated; resume explicitly'
tag=uuid4().hex[:10];base='NI081.BASE.'+tag;shop='NI081.SHOP.'+tag;ware=9102
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor()
 def native(name,args):
  result=q.var(oracledb.DB_TYPE_CLOB);q.callproc(name,args+[result]);return read_oracle_json(result.getvalue())
 def seq(name):q.execute('select '+name+'.nextval from dual');return int(q.fetchone()[0])
 trip=seq('RRL_TRANSPORT_TASK_SQ');st=seq('RRL_SBORKA_PALLETS_SQ');ops=[seq('SEQ_TT_OPERATIONS'),seq('SEQ_TT_OPERATIONS')]
 q.execute('select NUM from RRL_TR_VEHICLE where ID=10059');plate=q.fetchone()[0]
 q.execute('select CONDITION from RRL_TRANSPORT_TASK where ID=33564');condition=q.fetchone()[0];c.rollback()
 data={'trip_id':trip,'st_id':st,'warehouse_id':ware,'base':base,'shop':shop,'tag':tag,'operation_ids':ops,'road_provider':'NI081TEST','planning_only':True,'stock_rows_created':0};file.write_text(json.dumps(data,indent=2),encoding='utf-8')
 q.callproc('RRL_STOCK_CONFIG_API.begin_change',['admin','finished_goods_edit'])
 try:
  for address in [base,shop]:q.execute('insert into RRL_ADDR(ADDR,SHIROTA,DOLGOTA,UNLOAD_NORM_MIN,TW_STRICT,DELETED3)values(:a,41,44,30,1,0)',a=address)
  q.execute("insert into RRL_TRANSPORT_TASK(ID,TRANSPORT,VODITEL_ID,CONDITION,SHIPMENT_DATE,SHIPMENT_TIME,USER_ID,DELETED)values(:id,:plate,1,:cond,date'2030-01-15',date'2030-01-15'+8/24,'admin',0)",id=trip,plate=plate,cond=condition)
  q.execute("insert into RRL_SBORKA_PALLETS(ID,ST_NUMBER,PALLET_UID,TRANSTASK_ID,WARE_ID,ADDR,ORD,CONDITION,STDATE,ZONE_TIME_PLAN_IN,ZONE_TIME_PLAN_OUT)values(:id,:sn,:pallet_uid,:tt,:ware,:addr,1,1,date'2030-01-15',date'2030-01-15'+8/24,date'2030-01-15'+20/24)",id=st,sn='NI081.ST.'+tag,pallet_uid='NI081.P.'+tag,tt=trip,ware=ware,addr=shop)
  for oid,code,ordinal,start,end in [(ops[0],'DRIVE',1,8,12),(ops[1],'DRIVE_BACK',2,12,18)]:
   q.execute("insert into RRL_TT_OPERATIONS(ID,TT_ID,OPERATION_CODE,ORD,DURATION_MIN,PLAN_START,PLAN_END)values(:id,:tt,:code,:ord,:duration,date'2030-01-15'+:a/24,date'2030-01-15'+:b/24)",id=oid,tt=trip,code=code,ord=ordinal,duration=(end-start)*60,a=start,b=end)
  for a,b,minutes in [(base,shop,150),(shop,base,90)]:q.execute("insert into RRL_ADDR_DISTANCE_MATRIX(FROM_ADDR,TO_ADDR,DISTANCE_KM,DURATION_MIN,DURATION_BASIS,SOURCE,UPDATED_AT)values(:a,:b,50,:minutes,'ROAD_PROFILE_ESTIMATE','NI081TEST',sysdate)",a=a,b=b,minutes=minutes)
  c.commit()
 finally:q.callproc('RRL_STOCK_CONFIG_API.end_change')
 before=native('RRL_WARE_DEPOT_API.context',[ware,'admin']);c.rollback()
 native('RRL_WARE_DEPOT_API.apply_setting',['NI081.DEPOT:'+tag,'admin',json.dumps({'warehouse_id':ware,'expected_version':before['version'],'depot_address':base,'reason':'Own isolated NI081 planning-only synthetic road fixture'})]);c.commit()
 ctx=native('RRL_TT_TIME_API.context',[trip,'admin']);c.rollback()
 body={'trip_id':trip,'expected_version':ctx['version'],'source_hash':ctx['source_hash'],'time_zone':'Asia/Tbilisi','reason':'Own NI081 native route-rest approval, outer rollback'}
 wire=json.dumps(body,sort_keys=True,separators=(',',':'));start=perf_counter()
 try:
  result=native('RRL_TT_TIME_API.approve',['NI081.APPROVE:'+tag,'admin',wire]);assert result['source_contract_version']==6 and result['route_schedule']['driver_breaks_included']and not result['operational_admission'];data['approval_ms']=round((perf_counter()-start)*1000,2);data['result']=result
 finally:c.rollback()
 after=native('RRL_TT_TIME_API.context',[trip,'admin']);assert after['version']==ctx['version'];c.rollback();data['approval_rollback_verified']=True
 q.callproc('RRL_STOCK_CONFIG_API.begin_change',['admin','finished_goods_edit'])
 try:q.execute('update RRL_ADDR_DISTANCE_MATRIX set UPDATED_AT=sysdate-2 where FROM_ADDR=:a and TO_ADDR=:b',a=base,b=shop);c.commit()
 finally:q.callproc('RRL_STOCK_CONFIG_API.end_change')
 try:native('RRL_TT_TIME_API.approve',['NI081.STALE:'+tag,'admin',wire])
 except oracledb.DatabaseError as e:assert 'TT_TIME_SOURCE_CHANGED'in str(e),str(e);data['changed_source_rejected']=True
 else:raise AssertionError('Old source accepted')
 finally:c.rollback()
 # Restore only the own synthetic road timestamp; keep planning fixture, no approved/executable plan.
 q.callproc('RRL_STOCK_CONFIG_API.begin_change',['admin','finished_goods_edit'])
 try:q.execute('update RRL_ADDR_DISTANCE_MATRIX set UPDATED_AT=sysdate where FROM_ADDR=:a and TO_ADDR=:b',a=base,b=shop);c.commit()
 finally:q.callproc('RRL_STOCK_CONFIG_API.end_change')
 data['approval_status']=native('RRL_TT_TIME_API.context',[trip,'admin'])['approval_status'];file.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8');print('PASS own TT',trip,'V6 positive rolled back, stale source refused; no stock',data['approval_ms'])
