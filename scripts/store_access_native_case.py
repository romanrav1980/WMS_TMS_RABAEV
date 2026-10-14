exec(open('scripts/ni063_slow_queries.py',encoding='utf-8').read().split('with oracledb.connect',1)[0])
from app.modules.platform.public import read_oracle_json
from app.modules.master_data.infrastructure.store_profile import StoreProfile
from app.modules.master_data.contracts_store_profile import StoreProfileInput
from app.modules.transport.infrastructure.vehicle_profile import VehicleProfiles
from app.oracle_gateway import OracleGateway
from uuid import uuid4
from time import perf_counter
folder=Path('reports/nicora/2026-10-13/codex/STORE_ACCESS');folder.mkdir(exist_ok=True)
tag=uuid4().hex[:10];address='ACCESS.QA:'+tag;st='ACCESS.ST:'+tag;checks=[];gateway=OracleGateway();stores=StoreProfile(gateway);fleet=VehicleProfiles(gateway)
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select count(*)from USER_OBJECTS where OBJECT_NAME='RRL_STORE_ACCESS_RULES'and OBJECT_TYPE='PACKAGE BODY'and STATUS='VALID'");assert q.fetchone()[0]==1,'Root must apply bundle first'
 def change(permission,fn):
  c.rollback();q.callproc('RRL_STOCK_CONFIG_API.begin_change',['admin',permission])
  try:value=fn();c.commit();return value
  except BaseException:c.rollback();raise
  finally:q.callproc('RRL_STOCK_CONFIG_API.end_change')
 vehicle=change('transport_fleet_edit',lambda:int(q.callfunc('RRL_TR_VEHICLE_ADD',oracledb.DB_TYPE_NUMBER,['ACCESS'+tag,'20',10000,10,1,None])))
 q.execute('select RRL_SBORKA_PALLETS_SQ.nextval from dual');sid=int(q.fetchone()[0])
 def setup():
  q.execute("insert into RRL_ADDR(ADDR,TRANSPORT_TYPE,STOL,TW_STRICT,UNLOAD_NORM_MIN,DELETED3)values(:a,'0',0,0,30,null)",a=address)
  q.execute('insert into RRL_SBORKA_PALLETS(ID,ST_NUMBER,PALLET_UID,WARE_ID,ADDR,CONDITION)values(:id,:st,:st,1,:addr,0)',id=sid,st=st,addr=address)
  q.execute("insert into RRL_SBORKA_PALLET_ROWS(ID,PALLET_UID,ARTICUL,EI,QUANTITY,ORDER_WEIGHT)values(RRL_SBORKA_PALLET_ROWS_SQ.nextval,:st,'DS-BASE','EA',1,100)",st=st)
 change('warehouse_settings_edit',setup)
 result={'fixture':tag,'vehicle':vehicle,'store':address,'st_id':sid,'st_number':st,'stage':'SETUP'};(folder/'native.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
 def store(height,length):
  version=stores.read(address)['version'];body=StoreProfileInput(operation_id='ACCESS.STORE:'+uuid4().hex,store_addr=address,expected_version=version,reason='Own TEST store vehicle access fixture',max_vehicle_outer_height_mm=height,max_vehicle_outer_length_mm=length);return stores.save('admin',body.model_dump(mode='json'))
 def plan(complete):
  c.rollback();out=q.var(oracledb.DB_TYPE_CLOB);q.callproc('RRL_TRANSPORT_PLAN_RULES.check_vehicle',[vehicle,json.dumps([st]),complete,out]);return read_oracle_json(out.getvalue())
 def final():
  c.rollback();q.callproc('RRL_STOCK_CONFIG_API.begin_change',['admin','warehouse_settings_edit'])
  try:q.callproc('RRL_STORE_ACCESS_RULES.assert_members',[vehicle,json.dumps([sid])])
  finally:q.callproc('RRL_STOCK_CONFIG_API.end_change');c.rollback()
 def rejected(fn,code):
  try:fn();raise AssertionError('Expected '+code)
  except oracledb.DatabaseError as exc:assert code in str(exc),str(exc);c.rollback()
 try:
  start=perf_counter();store(3500,6500)
  empty=q.var(oracledb.DB_TYPE_CLOB);q.callproc('RRL_STORE_ACCESS_RULES.check_sts',[vehicle,'[]',0,empty]);assert read_oracle_json(empty.getvalue())['complete'];checks.append('empty draft no new restriction / NULL deleted flag active')
  assert not plan(0)['store_access']['complete'];rejected(lambda:plan(1),'STORE_ACCESS_CURRENT_OUTER_DIMENSIONS_REQUIRED');rejected(final,'STORE_ACCESS_CURRENT_OUTER_DIMENSIONS_REQUIRED');checks.append('unknown draft warning / final refusal')
  current=fleet.read(vehicle,'admin');fleet.configure(dict(operation_id='ACCESS.FLEET:'+tag,vehicle_id=vehicle,expected_version=0,expected_source_hash=current['base_hash'],vehicle_size_class='TEST_ACCESS',cargo_length_mm=5000,cargo_width_mm=2000,cargo_height_mm=2200,outer_height_mm=3500,outer_length_mm=6500,reason='Own TEST access fixture',evidence_reference='Synthetic metadata, not measured vehicle'),'admin')
  assert plan(0)['store_access']['complete']and plan(1)['store_access']['complete'];final();checks.append('equality plan and final pass')
  store(3499,6500);rejected(lambda:plan(0),'STORE_ACCESS_OUTER_HEIGHT_EXCEEDED');rejected(final,'STORE_ACCESS_OUTER_HEIGHT_EXCEEDED');checks.append('known height exceeds draft/final refuse')
  store(3500,6499);rejected(lambda:plan(1),'STORE_ACCESS_OUTER_LENGTH_EXCEEDED');rejected(final,'STORE_ACCESS_OUTER_LENGTH_EXCEEDED');checks.append('known length exceeds plan/final refuse')
  store(3500,6500);change('transport_fleet_edit',lambda:q.execute('update RRL_TR_VEHICLE set PALLETS=11 where ID=:v',v=vehicle));assert not plan(0)['store_access']['complete'];rejected(final,'STORE_ACCESS_CURRENT_OUTER_DIMENSIONS_REQUIRED');checks.append('stale fleet draft warning / final refusal')
  store(None,None);assert plan(1)['store_access']['complete'];final();checks.append('null limits have no new restriction')
  result.update(stage='PASS',checks=checks,elapsed_ms=round((perf_counter()-start)*1000,2))
 finally:
  c.rollback();store(None,None)
  change('warehouse_settings_edit',lambda:q.execute('update RRL_SBORKA_PALLETS set CONDITION=2 where ID=:id',id=sid))
  change('transport_fleet_edit',lambda:q.callproc('RRL_TR_VEHICLE_DEL',[vehicle]))
  result['cleanup']='Own planning ST condition2, own fleet soft-deleted, store limits cleared via profile owner; immutable histories retained; no stock/load/shipment'
  (folder/'native.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
 q.execute("select SQL_ID,EXECUTIONS,round(ELAPSED_TIME/nullif(EXECUTIONS,0)/1000,3),BUFFER_GETS,substr(SQL_TEXT,1,200)from V$SQL where PARSING_SCHEMA_NAME='RABAEV'and(SQL_TEXT like 'SELECT CFG.STORE_ADDR,CFG.PROFILE_VERSION%'or SQL_TEXT like 'SELECT DISTINCT P.ADDR FROM JSON_TABLE%'or SQL_TEXT like 'SELECT COUNT(*)FROM JSON_TABLE%')order by LAST_ACTIVE_TIME desc fetch first 6 rows only");result['sql']=q.fetchall()
(folder/'native.json').write_text(json.dumps(result,indent=2),encoding='utf-8');print('PASS native store dimensions planning/final guards; own metadata cleanup')
