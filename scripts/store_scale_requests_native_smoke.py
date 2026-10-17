"""Rollback-only native weighing intent + synthetic capture; never NativeAPI.post."""
import json,sys
from datetime import datetime,timedelta,timezone
from pathlib import Path
from uuid import uuid4
import oracledb
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'scripts'),str(ROOT/'api/wms_api_server')]
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment()
from app.oracle_gateway import OracleGateway
from app.modules.platform.public import read_oracle_json
from app.modules.integrations.application.scale_gateway import validate_scale_ack

class RollbackTrial(Exception):pass

def call(c,name,args):
 out=c.var(oracledb.DB_TYPE_CLOB);c.callproc(name,[*args,out]);return read_oracle_json(out.getvalue())

def packet(body):return json.dumps(body,sort_keys=True,separators=(',',':'),ensure_ascii=True)

def rejects(c,name,args,text):
 try:call(c,name,args)
 except oracledb.DatabaseError as error:assert text in str(error),str(error)
 else:raise AssertionError('Expected refusal '+text)

def fixture(c,tag,address):
 group='wg'+tag;sender='wgs'+tag;receiver='wgr'+tag;other='wgo'+tag;device='WEIGH.ROLLBACK:'+tag
 for actor in(sender,receiver,other):
  c.execute("insert into RUSERS(ID,NAME,PASS,USER_GROUP,DELETED,PRAVO_ADMIN_LOGIN)values(:id,'Weigh rollback','not-used',:grp,0,0)",id=actor,grp=group)
 for right in('store_scale_ingest','store_receipt_confirm'):
  c.execute("insert into RIGHTS(RIGHT1,USER_GROUP,DESCR)values(:right,:grp,'Rollback fixture')",right=right,grp=group)
 for actor in(receiver,other):
  c.execute("insert into RRL_STORE_RECEIPT_USER(USER_ID,STORE_ADDR,ASSIGNED_BY)values(:id,:addr,'admin')",id=actor,addr=address)
 c.execute("update RRL_STORE_RECEIPT_POLICY set RECEIPT_MODE='WEIGHT_PHOTO',POLICY_VERSION=POLICY_VERSION+1 where STORE_ADDR=:addr",addr=address)
 c.execute("""insert into RRL_STORE_SCALE_DEVICE(DEVICE_ID,STORE_ADDR,SENDER_ID,POLICY_VERSION,ACTIVE_FLAG,CAPACITY_KG,RESOLUTION_KG,CALIBRATION_REF,CALIBRATED_UNTIL,CHANGED_BY)
 values(:id,:addr,:sender,1,1,100,0.01,:cal,systimestamp+interval '1'day,'admin')""",id=device,addr=address,sender=sender,cal='SYNTHETIC:'+tag)
 return sender,receiver,other,device

def exercise(c,tag,checks):
 load='FLOOR1194.LOAD:f49901f5d2';address='Own full-pallet ST';api='RRL_STORE_WEIGH_API.'
 sender,receiver,other,device=fixture(c,tag,address)
 source=call(c,'RRL_STOCK_STORE_RECEIPT_READ.describe_load',[load,receiver,address]);assert not source['already_received']
 body=dict(request_id='WEIGH.REQUEST:'+tag,device_id=device,load_operation_id=load,store_address=address,expected_composition_signature=source['composition_signature'])
 first=call(c,api+'request_capture',[packet(body),receiver]);assert first['state']=='REQUESTED'and first['capture_key']is None
 assert call(c,api+'request_capture',[packet(body),receiver])==first
 rejects(c,api+'request_capture',[packet({**body,'expected_composition_signature':'0'*64}),receiver],'PAYLOAD_CONFLICT')
 rejects(c,api+'request_capture',[packet(body),other],'OWNER_REQUIRED')
 rejects(c,api+'request_capture',[packet({**body,'request_id':'BUSY:'+tag}),receiver],'DEVICE_BUSY')
 checks.extend(['exact_intent_replay','same_id_payload_conflict','other_receiver_owner_denied','second_outstanding_intent_busy'])
 pending=call(c,api+'pending_requests',[device,sender]);assert[r['request_id']for r in pending['items']]==[body['request_id']]
 rejects(c,api+'pending_requests',[device,other],'DEDICATED_DEVICE_SENDER_REQUIRED')
 own=next(r for r in call(c,api+'devices',[load,address,receiver])['items']if r['device_id']==device)
 assert own['readiness']=='READY'and own['connectivity']=='UNKNOWN'and own['active']is True
 checks.extend(['dedicated_gateway_only','configured_not_connected_device_status'])
 c.execute('select sys_extract_utc(systimestamp) from dual');now=c.fetchone()[0].replace(tzinfo=timezone.utc);stamp=lambda v:v.strftime('%Y-%m-%dT%H:%M:%S.%f+00:00')
 capture=dict(device_id=device,capture_id=body['request_id'],load_operation_id=load,store_address=address,device_policy_version=1,calibration_ref='SYNTHETIC:'+tag,
  unit='KG',basis='GROSS',preset_tare_kg='0',zero_confirmed=True,zero_check_kg='0',zero_check_at=stamp(now-timedelta(seconds=5)),measured_at=stamp(now),
  samples=[dict(offset_ms=i*500,gross_weight_kg='10')for i in range(5)])
 archived=call(c,'RRL_STORE_SCALE_API.capture',[packet(capture),sender])
 validate_scale_ack(packet(capture).encode('utf-8'),json.dumps(archived).encode('utf-8'));checks.append('gateway_ack_validator_matches_native_identity_and_source_hash')
 status=call(c,api+'request_status',[body['request_id'],receiver])
 assert status['state']=='CAPTURED'and status['capture_key']==archived['capture_key']and not status['receipt_confirmed'], status
 checks.append('existing_native_capture_completes_intent_without_receipt')
 rejects(c,api+'request_capture',[packet({**body,'request_id':'CHANGED:'+tag,'expected_composition_signature':'0'*64}),receiver],'COMPOSITION_CHANGED')
 next_body={**body,'request_id':'WEIGH.OLD:'+tag}
 second=call(c,api+'request_capture',[packet(next_body),receiver]);assert second['state']=='REQUESTED'
 call(c,'RRL_STORE_SCALE_API.capture',[packet({**capture,'capture_id':next_body['request_id']}),sender])
 stale=call(c,api+'request_status',[next_body['request_id'],receiver])
 assert stale['state']=='STALE'and stale['capture_key']is None and stale['reason']=='CAPTURE_DOES_NOT_MATCH_REQUEST'
 checks.extend(['changed_composition_rejected','pre_request_measurement_not_accepted'])
 c.execute('update RUSERS set DELETED=1 where ID=:id',id=receiver)
 rejects(c,api+'request_status',[body['request_id'],receiver],'CURRENT_RECEIVER_REQUIRED')
 assert call(c,api+'pending_requests',[device,sender])['items']==[]
 checks.append('current_receiver_revocation_hides_status_and_gateway_work')

def main():
 g=OracleGateway();tag=uuid4().hex[:10];checks=[]
 try:
  with g.transaction('Rollback-only weighing intent and synthetic native capture')as c:
   entered=False
   try:
    c.callproc('RRL_STOCK_CONFIG_API.begin_change',['admin','warehouse_settings_edit']);entered=True
    exercise(c,tag,checks)
   finally:
    if entered:c.callproc('RRL_STOCK_CONFIG_API.end_change')
   raise RollbackTrial()
 except RollbackTrial:pass
 for table,column,value in(('RRL_STORE_WEIGH_REQUEST','REQUEST_ID','WEIGH.REQUEST:'+tag),('RRL_STORE_SCALE_CAPTURE','CAPTURE_ID','WEIGH.REQUEST:'+tag),('RRL_STORE_WEIGH_REQUEST','REQUEST_ID','WEIGH.OLD:'+tag),('RRL_STORE_SCALE_CAPTURE','CAPTURE_ID','WEIGH.OLD:'+tag),('RRL_STORE_SCALE_DEVICE','DEVICE_ID','WEIGH.ROLLBACK:'+tag),('RUSERS','ID','wgr'+tag)):
  assert g.fetch_all('select count(*) N from '+table+' where '+column+'=:id',{'id':value})[0]['n']==0
 result=dict(status='PASS',checks=checks,transaction_rollback_verified=True,physical_hardware=False,stock_effect='NONE')
 (ROOT/'reports/retailcase/2026-10-15/store-app/scale-request-native.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
 print(json.dumps(result))
if __name__=='__main__':main()
