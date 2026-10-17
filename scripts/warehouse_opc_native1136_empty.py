"""Explicit TEST1136 encrypted OPC -> actual warehouse request/claim/capture/raw.

Only EMPTY_TARE is executable here. No ASM step, consent or stock command is sent.
Use only after root's release. Optional fixture hold keeps the same encrypted server
at .5; another phase requires separate owner approval and another client.
"""
import argparse
import asyncio
from datetime import datetime,timezone
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import threading
import time
from uuid import uuid4
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT),str(ROOT/'scripts')]
from warehouse_task_scoped_complete_smoke import OracleGateway
from api.wms_api_server.app.modules.integrations.infrastructure.scale_opc_profile import OpcScaleProfile
from api.wms_api_server.app.modules.integrations.infrastructure.scale_opc_client import Opc40200Client
from api.wms_api_server.app.modules.integrations.infrastructure.scale_device_lease import SqliteScaleDeviceLease
from api.wms_api_server.app.modules.integrations.infrastructure.scale_bundle_journal import SqliteScaleBundleJournal
from api.wms_api_server.app.modules.integrations.infrastructure.scale_outbox import SqliteScaleOutbox
from api.wms_api_server.app.modules.integrations.infrastructure.warehouse_scale_claims import SqliteWarehouseScaleClaims
from api.wms_api_server.app.modules.integrations.infrastructure.warehouse_scale_request_http import HttpWarehouseScaleRequests
from api.wms_api_server.app.modules.integrations.application.warehouse_opc_capture import OpcWarehouseCapture
from api.wms_api_server.app.modules.integrations.application.warehouse_scale_gateway import WarehouseScaleGatewayWorker
from api.wms_api_server.app.modules.integrations.application.scale_evidence_delivery import deliver_evidence
from api.wms_api_server.app.modules.integrations.contracts_warehouse_gateway import WarehouseGatewayProfile

RUNTIME=ROOT/'runtime/warehouse-opc-native1136'
REPORT=ROOT/'reports/retailcase/2026-10-15/warehouse-weigh-request/opc-empty-native-http.json'


def fixture_server():
    spec=importlib.util.spec_from_file_location('opc_test_fixture',ROOT/'tests/retailcase/test_scale_opc_client.py')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    return module.opc_fixture


def stock(gateway):
    return gateway.fetch_all("select UID_POLETA,CELL,REMAIN,HARD_RESERVED_BASE,STOCK_VERSION from RRL_REMAINS where UID_POLETA=:lot order by CELL",{'lot':'REUSE.RETURN:e6c16d0bbd'})


def password(secrets,actor):
    value=secrets[actor]
    return value['password']if isinstance(value,dict)else value


def original_request(case):
    path=RUNTIME/'operator-request.json'
    if path.exists():return path.read_bytes()
    body=dict(request_id='WHREQ15.OPC.EMPTY:'+uuid4().hex,device_id='WHREQ15.SCALE',purpose='EMPTY_TARE',
        case_task_id=1136,expected_content_version=case['content_version'],scan_container=case['sscc'],resource_session_id=case['resource_session_id'])
    value=json.dumps(body,ensure_ascii=True,sort_keys=True,separators=(',',':')).encode()
    with path.open('xb')as handle:handle.write(value);handle.flush();import os;os.fsync(handle.fileno())
    return value


async def serve(args):
    RUNTIME.mkdir(parents=True,exist_ok=True)
    g=OracleGateway();before=stock(g)
    assert [(r['remain'],r['hard_reserved_base'])for r in before]==[(24,1),(0,0)],before
    case=g.fetch_all('select CASE_PICK_TASK_ID,SSCC,CONTENT_VERSION,RESOURCE_SESSION_ID,STATUS from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=1136')[0]
    assert case['content_version']==2 and case['resource_session_id']==54 and case['status']=='IN_PROGRESS'
    lines=g.fetch_all('select CASE_PICK_LINE_ID,ARTICUL,CELL_CODE,PLANNED_QTY,PICKED_QTY from RRL_CASE_PICK_LINE where CASE_PICK_TASK_ID=1136')
    assert len(lines)==1 and lines[0]['case_pick_line_id']==1139 and lines[0]['planned_qty']==1 and lines[0]['picked_qty']==0
    device=g.fetch_all("select DEVICE_ID,WARE_ID,POST_CELL,DEVICE_MODE,POLICY_VERSION,CALIBRATION_REF,MEASUREMENT_BASIS,ACTIVE_FLAG from RRL_WH_SCALE_DEVICE where DEVICE_ID='WHREQ15.SCALE'")[0]
    assert device['device_mode']=='TEST'and device['measurement_basis']=='GROSS'and device['policy_version']==1 and device['active_flag']==1
    station=WarehouseGatewayProfile(device_id=device['device_id'],warehouse_id=device['ware_id'],post_cell=device['post_cell'],
        device_mode=device['device_mode'],device_policy_version=device['policy_version'],calibration_ref=device['calibration_ref'],basis=device['measurement_basis'])
    secrets=json.loads((ROOT/'runtime/warehouse-weigh-qa-secrets.json').read_text(encoding='utf-8-sig'))
    operator=HttpWarehouseScaleRequests('http://127.0.0.1:8088','WHREQ15.OP',password(secrets,'WHREQ15.OP'),allow_loopback_http=True)
    api=HttpWarehouseScaleRequests('http://127.0.0.1:8088','WHREQ15.GW',password(secrets,'WHREQ15.GW'),allow_loopback_http=True)
    bundle=SqliteScaleBundleJournal(RUNTIME/'bundles.sqlite');box=SqliteScaleOutbox(RUNTIME/'captures.sqlite')
    rawbox=SqliteScaleOutbox(RUNTIME/'raw.sqlite',max_packet_bytes=131072)
    worker=WarehouseScaleGatewayWorker(api,box,station,time.time)
    bundle.reconcile(box,rawbox)
    await asyncio.to_thread(worker.cycle)
    await asyncio.to_thread(deliver_evidence,api.post_evidence,rawbox,time.time())
    assert box.pending_count()==0 and rawbox.pending_count()==0,'Original outboxes must drain before OPC'
    body=original_request(case);request_id=json.loads(body)['request_id']
    # Explicit operator command only on --execute-empty; its original bytes survive timeout/restart.
    await asyncio.to_thread(operator._request,'/api/inventory/warehouse-scales/requests',body)
    queue=await asyncio.to_thread(api.requests,station.device_id)
    request=next(r for r in queue if r['request_id']==request_id)
    marker=g.fetch_all('select nvl(max(LOG_ID),0) N from RRL_SQL_SLOW_LOG')[0]['n']
    async with fixture_server()(RUNTIME)as(profile,state):
        data=dict(profile.data);data.update(device_id=station.device_id,station_id=station.post_cell)
        passport=RUNTIME/'commissioned-test-profile.json';passport.write_text(json.dumps(data,sort_keys=True,indent=2),encoding='utf-8')
        profile=OpcScaleProfile.load(passport)
        reader=Opc40200Client(profile)
        claimed=threading.Event()
        class ClaimsApi:
            def claim_request(self,request_id,body):
                result=api.claim_request(request_id,body);claimed.set();return result
        producer=OpcWarehouseCapture(reader,SqliteScaleDeviceLease(ROOT/'runtime/opc-device-leases.sqlite'),profile.data,profile.digest,station,bundle,
            SqliteWarehouseScaleClaims(RUNTIME/'claims.sqlite'),ClaimsApi(),lambda:box.pending_count()>0 or rawbox.pending_count()>0)
        await reader.connect()
        try:
            async def replace_empty_container():
                while not claimed.is_set():await asyncio.sleep(.02)
                await asyncio.sleep(.75);state.update(gross=.5,zero=False)
            placement=asyncio.create_task(replace_empty_container())
            packet,raw=await producer.capture(request)
            await placement
            bundle.reconcile(box,rawbox)
            capture_result=await asyncio.to_thread(worker.cycle)
            evidence_result=await asyncio.to_thread(deliver_evidence,api.post_evidence,rawbox,time.time())
            assert capture_result['status']=='ARCHIVED'and evidence_result==dict(status='EVIDENCE_ARCHIVED',binding='MATCHED'),(capture_result,evidence_result)
            status=json.loads(await asyncio.to_thread(operator._request,'/api/inventory/warehouse-scales/requests/'+request_id))
            assert status['state']=='CAPTURED'and status['claim_id']==json.loads(packet)['capture_id']
            assert stock(g)==before
            report=dict(status='PASS',case_task_id=1136,case_line_id=lines[0]['case_pick_line_id'],request_id=request_id,
                capture_key=status['capture_key'],measured_at=json.loads(packet)['measured_at'],weight_kg='0.5',capture=capture_result,evidence=evidence_result,
                capture_sha256=hashlib.sha256(packet).hexdigest().upper(),evidence_sha256=hashlib.sha256(raw).hexdigest().upper(),
                stock_before=before,stock_after=stock(g),physical_hardware=False,local_encrypted_opc=True,
                native_mutations='TEST_EMPTY_REQUEST_CLAIM_CAPTURE_RAW_ONLY',profile_path=str(passport),
                slow_sql=g.fetch_all('select *from(select LOG_ID,ELAPSED_MS,SQL_TEXT from RRL_SQL_SLOW_LOG where LOG_ID>:marker order by ELAPSED_MS desc)where rownum<=10',{'marker':marker}))
            REPORT.write_text(json.dumps(report,indent=2,default=str),encoding='utf-8')
            print(json.dumps(dict(status='EMPTY_TARE_CAPTURED',capture_key=status['capture_key'],measured_at=report['measured_at'],physical_hardware=False)),flush=True)
            # Keep this same TEST server at .5 for separately approved subsequent clients.
            end=time.monotonic()+args.hold_seconds
            while time.monotonic()<end:
                control=RUNTIME/'approved-test-gross.json'
                if control.exists():
                    change=json.loads(control.read_text(encoding='utf-8-sig'))
                    if change.get('owner_approved')is not True or change.get('gross_kg')not in ['0','0.5','1.5']:
                        raise ValueError('Explicit TEST fixture state change rejected')
                    state.update(gross=float(change['gross_kg']),zero=change['gross_kg']=='0')
                await asyncio.sleep(.25)
        finally:await reader.disconnect()


def main():
    parser=argparse.ArgumentParser(description='Root-release-only TEST1136 real OPC EMPTY_TARE protocol proof')
    parser.add_argument('--execute-empty',action='store_true')
    parser.add_argument('--hold-seconds',type=int,default=600)
    args=parser.parse_args()
    if not args.execute_empty:
        print('PREPARED_ONLY: wait for root release before --execute-empty');return
    if not 0<=args.hold_seconds<=1800:raise ValueError('TEST hold must be bounded')
    asyncio.run(serve(args))


if __name__=='__main__':main()
