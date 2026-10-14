exec(open('scripts/ni063_slow_queries.py',encoding='utf-8').read().split('with oracledb.connect',1)[0])
from app.modules.platform.public import read_oracle_json
from uuid import uuid4
from time import perf_counter
folder=Path('reports/nicora/2026-10-13/codex/VEHICLE_OUTER');folder.mkdir(exist_ok=True)
with oracledb.connect(user=s.oracle_user,password=s.oracle_password,dsn=s.oracle_dsn)as c:
 q=c.cursor();q.execute("select count(*)from USER_TAB_COLUMNS where TABLE_NAME='RRL_VEHICLE_PROFILE_HIST'and COLUMN_NAME in('OUTER_HEIGHT_MM','OUTER_LENGTH_MM')");assert q.fetchone()[0]==2,'Apply prepared migration first; no auto-apply'
 tag=uuid4().hex[:10];q.callproc('RRL_STOCK_CONFIG_API.begin_change',['admin','transport_fleet_edit'])
 try:vehicle=int(q.callfunc('RRL_TR_VEHICLE_ADD',oracledb.DB_TYPE_NUMBER,['OUTER'+tag,'20',10,2,1,None]))
 finally:q.callproc('RRL_STOCK_CONFIG_API.end_change')
 c.commit()
 evidence={'vehicle_id':vehicle,'plate':'OUTER'+tag,'tag':tag,'synthetic':True,'stage':'SETUP_COMMITTED'}
 (folder/'native.json').write_text(json.dumps(evidence,indent=2),encoding='utf-8')
 try:
  def read():return read_oracle_json(q.callfunc('RRL_VEHICLE_PROFILE_API.describe_profile',oracledb.DB_TYPE_CLOB,[vehicle]))
  def post(body):
   wire=q.var(oracledb.DB_TYPE_CLOB);wire.setvalue(0,json.dumps(body));out=q.var(oracledb.DB_TYPE_CLOB)
   try:
    q.callproc('RRL_VEHICLE_PROFILE_API.configure',[wire,'admin',out]);result=read_oracle_json(out.getvalue());c.commit();return result
   except BaseException:c.rollback();raise
  current=read();base=dict(operation_id='OUTER.QA:'+tag,vehicle_id=vehicle,expected_version=0,expected_source_hash=current['base_hash'],vehicle_size_class='TEST_OUTER',cargo_length_mm=5000,cargo_width_mm=2000,cargo_height_mm=2200,outer_height_mm=3500,outer_length_mm=6500,reason='Own retained TEST outer dimensions case',evidence_reference='Synthetic fixture; not physical measurement')
  started=perf_counter();first=post(base);assert first==post(base);assert read()['profile']['outer_height_mm']==3500
  for body,code in [(dict(base,outer_height_mm=3600),'VEHICLE_PROFILE_OPERATION_CONFLICT'),(dict(base,operation_id='OUTER.STALE:'+tag),'VEHICLE_PROFILE_VERSION_CONFLICT')]:
   try:post(body);raise AssertionError('conflicting command accepted')
   except oracledb.DatabaseError as exc:assert code in str(exc),str(exc)
  preserve=dict(base,operation_id='OUTER.PRESERVE:'+tag,expected_version=1);preserve.pop('outer_height_mm');preserve.pop('outer_length_mm');second=post(preserve);assert second['outer_height_mm']==3500 and second['outer_length_mm']==6500
  clear=dict(preserve,operation_id='OUTER.CLEAR:'+tag,expected_version=2,outer_height_mm=None);third=post(clear);assert third['outer_height_mm']is None and third['outer_length_mm']==6500
  try:post(dict(clear,operation_id='OUTER.BAD:'+tag,expected_version=3,outer_height_mm=1000));raise AssertionError('outer belowcargo accepted')
  except oracledb.DatabaseError as exc:assert 'VEHICLE_OUTER_SMALLER_THAN_CARGO'in str(exc),str(exc)
  q.execute('select count(*)from RRL_VEHICLE_PROFILE_HIST where VEHICLE_ID=:v',v=vehicle);assert q.fetchone()[0]==3
  evidence.update({'stage':'PASS','rollback':False,'retained_test_metadata':True,'checks':['set/read','exact replay','changedbody conflict','staleversion conflict','omitted preserves','explicitnull clears onlyone','smallerthancargo refuses'],'version':read()['version'],'elapsed_ms':round((perf_counter()-started)*1000,2)})
 finally:
  c.rollback();q.callproc('RRL_STOCK_CONFIG_API.begin_change',['admin','transport_fleet_edit'])
  try:q.callproc('RRL_TR_VEHICLE_DEL',[vehicle]);c.commit()
  finally:q.callproc('RRL_STOCK_CONFIG_API.end_change')
  evidence['cleanup']='Own TEST vehicle soft-deleted through RRL_TR_VEHICLE_DEL; immutable profile history retained'
  (folder/'native.json').write_text(json.dumps(evidence,indent=2),encoding='utf-8')
 q.execute('select count(*)from RRL_VEHICLE_PROFILE_HIST where VEHICLE_ID=:v',v=vehicle);assert q.fetchone()[0]==3
 q.execute('select DELETED from RRL_TR_VEHICLE where ID=:v',v=vehicle);assert q.fetchone()[0]==1
 q.execute("select SQL_ID,EXECUTIONS,round(ELAPSED_TIME/nullif(EXECUTIONS,0)/1000,3),BUFFER_GETS,substr(SQL_TEXT,1,180)from V$SQL where PARSING_SCHEMA_NAME='RABAEV'and(SQL_TEXT like 'SELECT OUTER_HEIGHT_MM,OUTER_LENGTH_MM%'or SQL_TEXT like 'INSERT INTO RRL_VEHICLE_PROFILE_HIST%'or SQL_TEXT like 'SELECT HIST.*INTO H FROM RRL_VEHICLE_PROFILE_HIST%')order by LAST_ACTIVE_TIME desc fetch first 5 rows only");evidence['sql']=q.fetchall()
(folder/'native.json').write_text(json.dumps(evidence,indent=2),encoding='utf-8');print('PASS own outer profile native fixture; own vehicle soft-deleted; immutable history retained')
