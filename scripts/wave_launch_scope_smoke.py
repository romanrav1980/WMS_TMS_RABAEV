"""Native wave-launch scope gates, using existing waves without posting physical effects."""
import json,secrets,sys
from datetime import datetime,timedelta,timezone
from pathlib import Path
from uuid import uuid4
import oracledb
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'api/wms_api_server'),str(ROOT/'scripts')]
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment()
from app.oracle_gateway import OracleGateway
from app.modules.platform.public import AccessMetadataService
from app.modules.platform.api.metadata_inputs import Command,normalize
from app.modules.inventory.public import StockPosting,StockCommand,StockPostingError

def main():
 g=OracleGateway();access=AccessMetadataService(g);prefix='wl'+uuid4().hex[:9];actor=prefix+'u';role=prefix+'r';assignment=prefix+'a';now=datetime.now(timezone.utc);checks=[]
 def command(kind,payload):return access.command('admin',normalize(Command(operation_id=prefix+':'+uuid4().hex,command_type=kind,payload=payload),'ACCESS'))
 def payload(wave):return StockCommand(operation_id=prefix+':'+uuid4().hex,command_type='WAVE_LAUNCH',actor=actor,source={'wave_id':wave},lines=(),metadata={})
 def guard(wave,denied=False):
  with g.transaction('Native launch scope acceptance')as c:
   try:c.callproc('RRL_WAVE_EXEC_ACCESS.assert_command',[payload(wave).canonical_json(),actor])
   except oracledb.DatabaseError as e:
    assert denied and e.args[0].code in(20851,20882),str(e)
   else:assert not denied
 try:
  with g.transaction('Launch scope identity fixture')as c:
   c.execute("insert into RUSERS(ID,NAME,PASS,USER_GROUP,WARE_ID,DELETED,PRAVO_ADMIN_LOGIN)values(:id,'Wave launch fixture',:password,'NONE',1,0,1)",id=actor,password=secrets.token_urlsafe(24))
  command('ROLE_SAVE',dict(role_id=role,title='Native launch mandate',permissions=['pick_wave_launch'],active=True,expected_version=0))
  command('ASSIGN',dict(assignment_id=assignment,username=actor,role_id=role,scope_kind='WAREHOUSE',scope_id='16447976',membership='CURRENT',valid_from=(now-timedelta(minutes=1)).isoformat(),valid_until=(now+timedelta(hours=1)).isoformat(),expected_version=0,reason='Native launch scope fixture'))
  guard(561);guard(560,True);checks.append('native_only_launch_mandate_actual_wave_warehouse')
  try:StockPosting().post(payload(560))
  except StockPostingError as e:assert e.oracle_code in(20851,20882)
  else:raise AssertionError('Foreign launch passed')
  checks.append('canonical_post_foreign_rejected_before_stock_plan')
  try:StockPosting().post(payload(561))
  except StockPostingError as e:assert e.oracle_code==20886 and e.rule_reason=='WAVE_NO_SOFT_RESERVATIONS',(e.oracle_code,e.rule_reason)
  else:raise AssertionError('Historical launched wave unexpectedly launchable')
  checks.append('own_mandate_reaches_existing_business_rule_without_flat_grant')
  command('REVOKE',dict(assignment_id=assignment,expected_version=1,reason='Revoke fixture mandate'))
  guard(561,True);checks.append('revoke_denies_next_native_command')
  assert g.fetch_all("select count(*) N from RRL_STOCK_OPERATION where OPERATION_ID like :prefix",{'prefix':prefix+':%'})[0]['n']==0
  assert g.fetch_all("select count(*) N from USER_OBJECTS where STATUS='INVALID'")[0]['n']==0
 finally:
  with g.transaction('Launch scope fixture cleanup')as c:
   c.execute('delete from RRL_ACCESS_ASSIGNMENT where USERNAME=:actor',actor=actor)
   for table in('RRL_ACCESS_ROLE_RIGHT','RRL_ACCESS_ROLE'):c.execute('delete from '+table+' where ROLE_ID=:role',role=role)
   c.execute('delete from RRL_ACCESS_AUDIT where OPERATION_ID like :prefix',prefix=prefix+':%')
   c.execute('delete from RRL_PLATFORM_COMMAND where OPERATION_ID like :prefix',prefix=prefix+':%')
   c.execute('delete from RUSERS where ID=:actor',actor=actor)
 result=dict(status='PASS',checks=checks,fixture_cleaned=True,stock_effect='NONE',positive_launch='PENDING_SEPARATE_PREVIEW_FIXTURE')
 (ROOT/'reports/retailcase/2026-10-15/resource-timeline/launch-scope-native.json').write_text(json.dumps(result,indent=2),encoding='utf-8');print(json.dumps(result))
if __name__=='__main__':main()
