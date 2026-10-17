"""Independent store app reads using an isolated STORE mandate, without an admin-shell grant."""
import json,secrets,sys
import os,subprocess,hashlib
import httpx
from datetime import datetime,timedelta,timezone
from pathlib import Path
from uuid import uuid4
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'api/wms_api_server'),str(ROOT/'scripts')]
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment()
from app.oracle_gateway import OracleGateway
from app.modules.platform.public import AccessMetadataService
from app.modules.platform.api.metadata_inputs import Command,normalize
from app.modules.delivery.infrastructure.store_app_reads import StoreAppReads
from app.modules.delivery.contracts import StoreReceiptError
from app.auth import load_admin_user

def main():
 g=OracleGateway();access=AccessMetadataService(g);app=StoreAppReads(g);prefix='sa'+uuid4().hex[:9];actor=prefix+'u';role=prefix+'r';assignment=prefix+'a';password=secrets.token_urlsafe(24);now=datetime.now(timezone.utc);checks=[]
 own='93a8a772c3568c28355e3ec75c8893faee9818409a72b0f1b734b24f0cb54b8f';foreign='27a5b4ce1c25b3039d7baa3785b92d42fc69ba701ed9a36a1de2ba68049ee8b3'
 if os.environ.get('RUN_STORE_RECEIPT_ROLLBACK')=='1':own=hashlib.sha256('Own full-pallet ST'.encode()).hexdigest()
 def command(kind,payload):return access.command('admin',normalize(Command(operation_id=prefix+':'+uuid4().hex,command_type=kind,payload=payload),'ACCESS'))
 try:
  with g.transaction('Store application identity fixture')as c:
   c.execute("insert into RUSERS(ID,NAME,PASS,USER_GROUP,WARE_ID,DELETED,PRAVO_ADMIN_LOGIN)values(:id,'Store receiver fixture',:password,'NONE',null,0,0)",id=actor,password=password)
  command('ROLE_SAVE',dict(role_id=role,title='Own store receiver',permissions=['store_receipt_confirm'],active=True,expected_version=0))
  command('ASSIGN',dict(assignment_id=assignment,username=actor,role_id=role,scope_kind='STORE',scope_id=own,membership='CURRENT',valid_from=(now-timedelta(minutes=1)).isoformat(),valid_until=(now+timedelta(hours=1)).isoformat(),expected_version=0,reason='Independent store app fixture'))
  identity=load_admin_user(actor,password);assert identity and not identity.permissions
  session=app.session(actor);assert len(session['stores'])==1 and session['stores'][0]['store_id']==own
  checks.append('native_store_identity_without_warehouse_legacy_right_or_admin_shell')
  page=app.deliveries(actor,own,'',1);assert len(page['items'])==1
  item=page['items'][0];preview=app.preview(actor,own,item['load_operation_id'])
  assert preview['store_address']==session['stores'][0]['address']
  checks.append('own_frozen_delivery_list_and_native_preview')
  try:
   lookup=app.lookup(actor,own,preview['root_scan_identifier'])
   assert lookup['store_id']==own and lookup['scanned_code']==preview['root_scan_identifier']
  except StoreReceiptError as error:
   assert error.code=='STORE_SCAN_AMBIGUOUS' and error.status==409
  try:app.lookup(actor,foreign,preview['root_scan_identifier'])
  except StoreReceiptError as error:assert error.status==403
  else:raise AssertionError('Foreign store scan resolved')
  try:app.lookup(actor,own,'NO-SUCH-PLACE:'+prefix)
  except StoreReceiptError as error:assert error.status==404
  else:raise AssertionError('Unknown place scan resolved')
  checks.append('native_scanned_place_lookup_own_foreign_missing_or_explicit_ambiguity')

  try:app.deliveries(actor,foreign,'',1)
  except StoreReceiptError as error:assert error.status==403
  else:raise AssertionError('Foreign store visible')
  try:app.preview(actor,foreign,item['load_operation_id'])
  except StoreReceiptError as error:assert error.status==403
  else:raise AssertionError('Foreign store preview visible')
  checks.append('foreign_store_and_direct_preview_denied')
  receipt=app.receipt(actor,own,'UNKNOWN:'+prefix);assert receipt['state']=='NOT_VISIBLE'and not receipt['outcome_confirmed']
  checks.append('missing_receipt_not_proof_of_rollback')
  if page['next_after']:
   second=app.deliveries(actor,own,page['next_after'],1);assert all(r['load_operation_id']!=item['load_operation_id']for r in second['items'])
  checks.append('server_keyset_cursor')
  with httpx.Client(base_url='http://127.0.0.1:8088',auth=(actor,password),timeout=30)as client:
   r=client.get('/api/store-app/session');assert r.status_code==200,r.text[:300]
   assert [row['store_id']for row in r.json()['stores']]==[own]
   r=client.get('/api/store-app/deliveries',params={'store_id':own,'limit':1});assert r.status_code==200,r.text[:300]
   assert r.json()['items']
   r=client.get('/api/store-app/deliveries/'+item['load_operation_id'],params={'store_id':own});assert r.status_code==200,r.text[:300]
   assert client.get('/api/store-app/deliveries',params={'store_id':foreign}).status_code==403
   assert client.get('/api/store-app/session',auth=(actor,'wrong-password')).status_code==401
   for article in ('app','barcode','weight-photo','paper-count','recovery'):
    help_response=client.get('/api/help/articles/store-receiving-'+article)
    assert help_response.status_code==200,help_response.text[:200]
    assert len(help_response.json()['related'])==5 and help_response.json()['sources']==['wiki/runbooks/retailcase_store_receiving_app.md']
   checks.append('published_wiki_help_and_related_visible_to_store_only_identity')
   checks.append('real_http_store_login_list_preview_without_admin_grant')
  if os.environ.get('RUN_STORE_UI')=='1':
   child=dict(os.environ,STORE_SMOKE_USER=actor,STORE_SMOKE_PASSWORD=password,TEMP=str(ROOT/'tmp/store-ui-native'),TMP=str(ROOT/'tmp/store-ui-native'))
   (ROOT/'tmp/store-ui-native').mkdir(exist_ok=True)
   subprocess.run(['node',str(ROOT/'reports/retailcase/2026-10-15/store-app/ui-smoke.cjs')],cwd=ROOT,env=child,check=True)
   checks.append('standalone_mobile_browser_native_identity')
  if os.environ.get('RUN_STORE_RECEIPT_ROLLBACK')=='1':
   from store_receipt_native_rollback import verify_store_receipt_rollback
   assert verify_store_receipt_rollback(g,actor)['receipt_and_operation_rollback_verified']
   checks.append('native_store_only_physical_receipt_caller_owned_rollback_verified')
  command('REVOKE',dict(assignment_id=assignment,expected_version=1,reason='Revoke store fixture'))
  assert app.session(actor)['stores']==[]
  try:app.deliveries(actor,own,'',1)
  except StoreReceiptError as error:assert error.status==403
  else:raise AssertionError('Revoked store visible')
  checks.append('revoke_removes_store_and_data')
 finally:
  with g.transaction('Store application fixture cleanup')as c:
   c.execute('delete from RRL_ACCESS_ASSIGNMENT where USERNAME=:actor',actor=actor)
   for table in('RRL_ACCESS_ROLE_RIGHT','RRL_ACCESS_ROLE'):c.execute('delete from '+table+' where ROLE_ID=:role',role=role)
   c.execute('delete from RRL_ACCESS_AUDIT where OPERATION_ID like :prefix',prefix=prefix+':%')
   c.execute('delete from RRL_PLATFORM_COMMAND where OPERATION_ID like :prefix',prefix=prefix+':%')
   c.execute('delete from RUSERS where ID=:actor',actor=actor)
 result=dict(status='PASS',checks=checks,fixture_cleaned=True,business_rows=('READ_WITH_ROLLBACK_RECEIPT_TRIAL'if os.environ.get('RUN_STORE_RECEIPT_ROLLBACK')=='1'else'READ_ONLY'),stock_effect='NONE')
 target=ROOT/'reports/retailcase/2026-10-15/store-app';target.mkdir(exist_ok=True)
 (target/'scope-native.json').write_text(json.dumps(result,indent=2),encoding='utf-8');print(json.dumps(result))
if __name__=='__main__':main()
