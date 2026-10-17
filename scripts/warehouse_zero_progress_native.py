"""Actual encrypted local OPC zero -> HTTP metadata intents -> native ZERO caller rollback.
No loaded weight, capture archive, stock command or MAIN1136 mutation is executed.
"""
import asyncio
from copy import deepcopy
from datetime import datetime,timezone,timedelta
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import oracledb
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT),str(ROOT/'scripts'),str(ROOT/'api/wms_api_server')]
from stock_posting_environment import load_local_oracle_environment
load_local_oracle_environment()
from app.oracle_gateway import OracleGateway
from app.modules.inventory.infrastructure.warehouse_scale_requests import WarehouseWeighRequests
from app.modules.platform.public import read_oracle_json
from warehouse_scale_requests_native import call,wire
from warehouse_zero_progress_fixture import REPORT as FIXTURE,stock,DEVICE
from api.wms_api_server.app.modules.integrations.infrastructure.scale_opc_client import Opc40200Client
from api.wms_api_server.app.modules.integrations.infrastructure.warehouse_scale_request_http import HttpWarehouseScaleRequests
from api.wms_api_server.app.modules.integrations.application.warehouse_zero_progress import zero_event,validate_zero_ack
RUNTIME=ROOT/'runtime/warehouse-zero-progress-native'
REPORT=ROOT/'reports/retailcase/2026-10-15/warehouse-weigh-request/zero-native.json'
API='RRL_WH_WEIGH_REQUEST_API.'


class RollbackTrial(Exception):
    pass


def freeze(path:Path,body:bytes)->bytes:
    if path.exists():return path.read_bytes()
    with path.open('xb')as handle:
        handle.write(body);handle.flush()
        import os
        os.fsync(handle.fileno())
    return body


def rejection(c,request,body,expected):
    try:call(c,API+'confirm_zero',request,wire(body),'WHREQ15.GW')
    except oracledb.DatabaseError as exc:
        assert expected in str(exc),(expected,str(exc))
    else:raise AssertionError('Expected '+expected)


def changed_evidence(event,field,value):
    result=deepcopy(event);e=json.loads(event['zero_evidence_json'])
    e['values'][field]['value']=value
    result['zero_evidence_json']=wire(e)
    result['zero_source_sha256']=hashlib.sha256(result['zero_evidence_json'].encode()).hexdigest().upper()
    return result


def first_capture_guard(c,context,weight,stamp,expected):
    packet=dict(context,zero_confirmed=True,zero_check_kg=weight,zero_check_at=stamp)
    source=wire(packet)
    c.callproc(API+'before_capture',[source,'WHREQ15.GW'])
    c.execute('select DEVICE_ID from RRL_WH_SCALE_DEVICE where DEVICE_ID=:id for update',id=context['device_id'])
    try:c.callproc(API+'validate_first_capture',[source,'WHREQ15.GW'])
    except oracledb.DatabaseError as exc:assert expected in str(exc),(expected,str(exc))
    else:raise AssertionError('Expected capture admission rejection '+expected)
    finally:c.callproc(API+'clear_capture_context')


def native_trial(g,fixture,claim,event,body):
    before=stock(g);case=g.fetch_all('select *from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=:id',{'id':fixture['case']})
    checks=[];result=None
    try:
        with g.transaction('Actual OPC ZERO validation; only ZERO rows caller rollback')as c:
            first_capture_guard(c,claim['capture_context'],'0',event['zero_observed_at'],'WH_ZERO_PROGRESS_BEFORE_CAPTURE_REQUIRED');checks.append('flagged_capture_requires_zero')
            bad=deepcopy(event);bad['zero_source_sha256']='F'*64
            rejection(c,claim['request_id'],bad,'WH_ZERO_SOURCE_PROFILE_HASH_REQUIRED');checks.append('source_hash')
            for field,value,error in [('current_weight',dict(Gross='0.001',Net='0.001',Tare='0.0'),'WH_ZERO_ACTUAL_EMPTY_REQUIRED'),
                ('center_zero',False,'WH_ZERO_FLAGS_REJECTED'),('tare_mode',event['no_tare_mode']+1,'WH_ZERO_TARE_MODE_REJECTED'),
                ('engineering_units',dict(namespace_uri=event['unit_namespace_uri'],unit_id=event['kg_unit_id']+1),'WH_ZERO_REPORTED_PROFILE_UNIT_MISMATCH')]:
                rejection(c,claim['request_id'],changed_evidence(event,field,value),error);checks.append(field)
            bad=deepcopy(event);e=json.loads(event['zero_evidence_json']);e['values']['stable']['status_code']=2147483648
            bad['zero_evidence_json']=wire(e);bad['zero_source_sha256']=hashlib.sha256(bad['zero_evidence_json'].encode()).hexdigest().upper()
            rejection(c,claim['request_id'],bad,'WH_ZERO_OPC_GOOD_REQUIRED');checks.append('quality')
            bad=deepcopy(event);bad['zero_observed_at']=(datetime.fromisoformat(event['zero_observed_at'])+timedelta(seconds=1)).isoformat()
            rejection(c,claim['request_id'],bad,'WH_ZERO_TIMESTAMP_MISMATCH');checks.append('timestamp_binding')
            result=call(c,API+'confirm_zero',claim['request_id'],body.decode(),'WHREQ15.GW')
            validate_zero_ack(body,wire(result).encode(),claim);checks.append('actual_opc_native_zero_strict_ack')
            assert result['current']['measurement_stage']=='ZERO_CONFIRMED'and result['current']['load_allowed']is True
            replay=call(c,API+'confirm_zero',claim['request_id'],body.decode(),'WHREQ15.GW')
            assert replay['receipt']==result['receipt'];checks.append('exact_immutable_receipt')
            bad=deepcopy(event);bad['profile_sha256']='F'*64
            rejection(c,claim['request_id'],bad,'WH_ZERO_PAYLOAD_CONFLICT');checks.append('immutable_payload')
            first_capture_guard(c,claim['capture_context'],'0.001',event['zero_observed_at'],'WH_ZERO_CAPTURE_MASS_MISMATCH');checks.append('same_timestamp_nonzero_capture_rejected')
            wrong_stamp=(datetime.fromisoformat(event['zero_observed_at'])+timedelta(seconds=1)).isoformat()
            first_capture_guard(c,claim['capture_context'],'0',wrong_stamp,'WH_ZERO_CAPTURE_TIMESTAMP_MISMATCH');checks.append('capture_timestamp_binding')
            for action in('delete from','update'):
                try:
                    sql='delete from RRL_WH_WEIGH_ZERO where CLAIM_ID=:id'if action=='delete from'else'update RRL_WH_WEIGH_ZERO set ZERO_SOURCE_SHA256=ZERO_SOURCE_SHA256 where CLAIM_ID=:id'
                    c.execute(sql,id=claim['claim_id'])
                except oracledb.DatabaseError as exc:assert 'WH_ZERO_APPEND_ONLY'in str(exc)
                else:raise AssertionError('Append-only guard required')
            checks.append('append_only_update_delete')
            c.execute('select count(*)from RRL_WH_SCALE_CAPTURE where DEVICE_ID=:id',id=DEVICE);assert c.fetchone()[0]==0
            raise RollbackTrial()
    except RollbackTrial:
        pass
    assert g.fetch_all('select count(*)N from RRL_WH_WEIGH_ZERO where CLAIM_ID=:id',{'id':claim['claim_id']})[0]['n']==0
    assert g.fetch_all('select count(*)N from RRL_WH_SCALE_CAPTURE where DEVICE_ID=:id',{'id':DEVICE})[0]['n']==0
    assert stock(g)==before
    assert g.fetch_all('select *from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=:id',{'id':fixture['case']})==case
    checks.append('zero_rollback_case_stock_archive_unchanged')
    return dict(status='PASS',checks=checks,count=len(checks),receipt=result,stock_before=before,stock_after=stock(g),
        zero_rows_rollback_verified=True,capture_rows=0,goods_stock_committed=False,actual_encrypted_local_opc=True,physical_hardware=False)


async def run():
    assert not REPORT.exists(),'Completed proof cannot silently fork or renew a claim'
    RUNTIME.mkdir(parents=True,exist_ok=True)
    fixture=json.loads(FIXTURE.read_text(encoding='utf-8-sig'));g=OracleGateway()
    row=g.fetch_all('select SSCC,CONTENT_VERSION,STATUS,PICKED_QTY from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=:id',{'id':fixture['case']})[0]
    assert row['status']=='NEW'and row['picked_qty']==0
    module_spec=importlib.util.spec_from_file_location('zero_opc_fixture',ROOT/'tests/retailcase/test_scale_opc_client.py')
    module=importlib.util.module_from_spec(module_spec);module_spec.loader.exec_module(module)
    secret=json.loads((ROOT/'runtime/warehouse-weigh-qa-secrets.json').read_text(encoding='utf-8-sig'))['WHREQ15.GW']
    if isinstance(secret,dict):secret=secret['password']
    operator=HttpWarehouseScaleRequests('http://127.0.0.1:8088','admin','admin123',allow_loopback_http=True)
    sender=HttpWarehouseScaleRequests('http://127.0.0.1:8088','WHREQ15.GW',secret,allow_loopback_http=True)
    async with module.opc_fixture(RUNTIME)as(profile,state):
        profile.data['device_id']=DEVICE
        path=profile.root/'zero-profile.json';path.write_text(json.dumps(profile.data),encoding='utf-8');profile=type(profile).load(path)
        reader=Opc40200Client(profile);await reader.connect()
        try:
            await reader.read()
            request=dict(request_id='WHZERO15.AK06.REQUEST',device_id=DEVICE,purpose='EMPTY_TARE',case_task_id=fixture['case'],
                expected_content_version=int(row['content_version']),scan_container=row['sscc'],zero_progress_required=True)
            request_body=freeze(RUNTIME/'request.json',wire(request).encode())
            requested=json.loads(await asyncio.to_thread(operator._request,'/api/inventory/warehouse-scales/requests',request_body))
            assert requested['measurement_stage']=='WAITING_ZERO'and requested['load_allowed']is False
            claim_body=freeze(RUNTIME/'claim.json',wire(dict(claim_id='WHZERO15.AK06.CLAIM1',device_id=DEVICE)).encode())
            claim=json.loads(await asyncio.to_thread(sender.claim_request,request['request_id'],claim_body))
            assert claim['claim_active']is True and claim['measurement_stage']=='WAITING_ZERO'and claim['load_allowed']is False
            while True:
                zero=await reader.read()
                if datetime.fromisoformat(zero.evidence['values']['current_weight']['server_timestamp'])>=datetime.fromisoformat(claim['claim_created_at']):break
                await asyncio.sleep(.05)
            assert zero.center_zero and zero.stable and zero.gross==0
            body=freeze(RUNTIME/'zero-event.json',zero_event(claim,zero,profile.data,profile.digest));event=json.loads(body)
            result=await asyncio.to_thread(native_trial,g,fixture,claim,event,body)
            status=json.loads(await asyncio.to_thread(operator._request,'/api/inventory/warehouse-scales/requests/'+request['request_id']))
            assert status['load_allowed']is False and status['measurement_stage']=='WAITING_ZERO'
            result.update(request_id=request['request_id'],claim_id=claim['claim_id'],http_before_after=['REQUESTED_WAITING_ZERO','CLAIMED_WAITING_ZERO','ZERO_ROLLBACK_WAITING_ZERO'],
                request_claim_metadata_committed=True,immutable_request_claim_history_retained=True,profile_sha256=profile.digest,isolated_device=DEVICE)
            REPORT.write_text(json.dumps(result,indent=2,default=str),encoding='utf-8')
            print(json.dumps(dict(status='PASS',native_checks=result['count'],http_checks=3,zero_rollback=True,captures=0,physical_hardware=False)))
        finally:await reader.disconnect()


if __name__=='__main__':asyncio.run(run())
