"""Root-run TEST N1939 EMPTY only on retained pinned OPC server. No Stock/ASM command.
Requires separate native scoped EMPTY admission fix and current commissioned sender/device.
"""
import argparse
import asyncio
from decimal import Decimal
import hashlib
import json
import os
from pathlib import Path
import sys
import time
from typing import Any
ROOT=Path(__file__).resolve().parents[1]
RUNTIME=ROOT/'runtime/warehouse-opc-native1939-empty'
REPORT=ROOT/'reports/retailcase/2026-10-15/case-scoped-close/empty-1939.json'
OLD=ROOT/'runtime/warehouse-opc-native1136'
REQUEST='N1939.EMPTY.1139'


def control(gross:str)->None:
    assert gross in {'0','0.5'}
    (OLD/'approved-test-gross.json').write_text(json.dumps(dict(owner_approved=True,gross_kg=gross)),encoding='utf-8')


def original_request(case:dict[str,Any])->bytes:
    body=dict(request_id=REQUEST,device_id='WHREQ15.SCALE',purpose='EMPTY_TARE',case_task_id=1139,
        expected_content_version=case['content_version'],scan_container=case['sscc'],resource_session_id=59,zero_progress_required=True)
    value=json.dumps(body,ensure_ascii=True,sort_keys=True,separators=(',',':')).encode()
    path=RUNTIME/'operator-request.json'
    if path.exists():
        saved=path.read_bytes();assert saved==value,'Original request context changed; reconcile, never rewrite';return saved
    with path.open('xb')as stream:stream.write(value);stream.flush();os.fsync(stream.fileno())
    return value


async def run()->None:
    # Imports including Oracle setup happen only after explicit root execution release.
    sys.path[:0]=[str(ROOT),str(ROOT/'scripts')]
    from warehouse_opc_native1136_empty import (OracleGateway,OpcScaleProfile,Opc40200Client,SqliteScaleDeviceLease,
        SqliteScaleBundleJournal,SqliteScaleOutbox,SqliteWarehouseScaleClaims,HttpWarehouseScaleRequests,
        OpcWarehouseCapture,WarehouseScaleGatewayWorker,deliver_evidence,WarehouseGatewayProfile,password)
    from api.wms_api_server.app.modules.integrations.application.warehouse_scale_claim import validate_claim
    from api.wms_api_server.app.modules.integrations.application.warehouse_zero_progress import validate_zero_ack
    g=OracleGateway()
    from case_current_close_1939_native import snapshot
    before=snapshot(g)
    case=g.fetch_all('select SSCC,CONTENT_VERSION,ASSIGNED_TO,STATUS,ASSIGNMENT_VERSION,RESOURCE_SESSION_ID,PICKED_QTY from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=1139')[0]
    assert case['status']=='IN_PROGRESS'and case['assigned_to']=='N1939.OP'and case['resource_session_id']==59 and case['assignment_version']==2 and case['picked_qty']==0
    rows=g.fetch_all("select DEVICE_ID,WARE_ID,POST_CELL,DEVICE_MODE,POLICY_VERSION,CALIBRATION_REF,MEASUREMENT_BASIS,ACTIVE_FLAG,SENDER_ID,case when CALIBRATED_UNTIL>=systimestamp then 1 else 0 end CAL_CURRENT from RRL_WH_SCALE_DEVICE where DEVICE_ID='WHREQ15.SCALE'")
    assert len(rows)==1;d=rows[0]
    assert d['active_flag']==1 and d['cal_current']==1 and d['device_mode']=='TEST'and d['measurement_basis']=='GROSS'and d['sender_id']=='WHREQ15.GW'and d['ware_id']==13583852

    station=WarehouseGatewayProfile(device_id=d['device_id'],warehouse_id=d['ware_id'],post_cell=d['post_cell'],device_mode=d['device_mode'],device_policy_version=d['policy_version'],calibration_ref=d['calibration_ref'],basis=d['measurement_basis'])
    original=(OLD/'frozen-first-commissioned-profile.json').read_bytes()
    assert(OLD/'commissioned-test-profile.json').read_bytes()==original
    profile=OpcScaleProfile.load(OLD/'frozen-first-commissioned-profile.json')
    assert profile.data['device_id']==d['device_id']and profile.data['station_id']==d['post_cell']
    secrets=json.loads((ROOT/'runtime/warehouse-weigh-qa-secrets.json').read_text(encoding='utf-8-sig'))
    picker=json.loads((ROOT/'runtime/n1939-qa-secrets.json').read_text(encoding='utf-8-sig'))['N1939.OP']
    operator=HttpWarehouseScaleRequests('http://127.0.0.1:8088','N1939.OP',picker,allow_loopback_http=True)
    api=HttpWarehouseScaleRequests('http://127.0.0.1:8088','WHREQ15.GW',password(secrets,'WHREQ15.GW'),allow_loopback_http=True)
    RUNTIME.mkdir(parents=True,exist_ok=True)
    bundle=SqliteScaleBundleJournal(RUNTIME/'bundle.sqlite');box=SqliteScaleOutbox(RUNTIME/'capture.sqlite')
    rawbox=SqliteScaleOutbox(RUNTIME/'raw.sqlite',max_packet_bytes=131072)
    worker=WarehouseScaleGatewayWorker(api,box,station,time.time)
    bundle.reconcile(box,rawbox)
    await asyncio.to_thread(worker.cycle);await asyncio.to_thread(deliver_evidence,api.post_evidence,rawbox,time.time())
    assert box.pending_count()==0 and rawbox.pending_count()==0,'Reconcile original outbound bodies first'
    requestbody=original_request(case)
    # GET devices proves current operator admission before creating any request. No flat fallback.
    await asyncio.to_thread(operator._request,'/api/inventory/warehouse-scales/devices?case_task_id=1139&purpose=EMPTY_TARE')
    await asyncio.to_thread(operator._request,'/api/inventory/warehouse-scales/requests',requestbody)
    current=json.loads(await asyncio.to_thread(operator._request,'/api/inventory/warehouse-scales/requests/'+REQUEST))
    assert current['state']!='CAPTURED','Existing archive: read exact bundle/history; never remeasure fixed request'
    request=next(r for r in await asyncio.to_thread(api.requests,station.device_id)if r['request_id']==REQUEST)
    class Claims:
        claim:dict[str,Any]
        def claim_request(self,request_id:str,body:bytes)->bytes:
            response=api.claim_request(request_id,body)
            self.claim=validate_claim(request,body,response,station)
            control('0') # only approved simulator, after actual claim ACK
            return response
        def confirm_zero(self,request_id:str,body:bytes)->bytes:
            response=api.confirm_zero(request_id,body)
            validate_zero_ack(body,response,self.claim)
            control('0.5') # only fresh ZERO_CONFIRMED/live server load permission
            return response
    reader=Opc40200Client(profile)
    producer=OpcWarehouseCapture(reader,SqliteScaleDeviceLease(ROOT/'runtime/opc-device-leases.sqlite'),profile.data,
        profile.digest,station,bundle,SqliteWarehouseScaleClaims(RUNTIME/'claims.sqlite'),Claims(),lambda:box.pending_count()>0 or rawbox.pending_count()>0)
    await reader.connect()
    try:packet,raw=await producer.capture(request)
    finally:await reader.disconnect()
    actual_weight=json.loads(packet)['samples'][-1]['weight_kg']
    assert Decimal(actual_weight)==Decimal('0.5'),'Unexpected actual TEST EMPTY mass; preserve archive identity, no false report'
    bundle.reconcile(box,rawbox)
    result=await asyncio.to_thread(worker.cycle)
    evidence=await asyncio.to_thread(deliver_evidence,api.post_evidence,rawbox,time.time())
    assert result['status']=='ARCHIVED'and evidence==dict(status='EVIDENCE_ARCHIVED',binding='MATCHED')
    status=json.loads(await asyncio.to_thread(operator._request,'/api/inventory/warehouse-scales/requests/'+REQUEST))
    assert status['state']=='CAPTURED'and snapshot(g)==before
    assert(OLD/'frozen-first-commissioned-profile.json').read_bytes()==original
    report=dict(status='PASS',capture_key=status['capture_key'],measured_at=json.loads(packet)['measured_at'],weight_kg=actual_weight,request=json.loads(requestbody),capture=result,evidence=evidence,
        capture_sha256=hashlib.sha256(packet).hexdigest().upper(),raw_sha256=hashlib.sha256(raw).hexdigest().upper(),source_before=before,source_after=snapshot(g),physical_hardware=False,encrypted_opc=True,quantity_effect=False)
    REPORT.write_text(json.dumps(report,indent=2,default=str),encoding='utf-8')
    print(json.dumps({k:report[k]for k in ['status','capture_key','measured_at','physical_hardware','quantity_effect']}))


def main()->None:
    parser=argparse.ArgumentParser();parser.add_argument('--execute-empty',action='store_true');args=parser.parse_args()
    if not args.execute_empty:
        print('PREPARED_ONLY: root native scoped EMPTY admission + current commissioning + pinned server release required');return
    assert os.environ.get('N1939_EMPTY_ROOT_RELEASE')=='1'
    assert not REPORT.exists(),'Read original capture report; never blind remeasure'
    asyncio.run(run())


if __name__=='__main__':main()
