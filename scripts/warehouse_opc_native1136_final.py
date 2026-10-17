"""Root-released TEST1136 FINAL_GROSS on the already-running encrypted OPC server.

Only request/claim/capture/raw metadata. No finish or stock command. Fresh actual
zero is read after claim; the fixture then replaces the simulated full carrier.
"""
import argparse
import asyncio
import hashlib
import json
from pathlib import Path
import sys
import time
from uuid import uuid4
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT),str(ROOT/'scripts')]
from warehouse_opc_native1136_empty import (OracleGateway,OpcScaleProfile,Opc40200Client,
    SqliteScaleDeviceLease,SqliteScaleBundleJournal,SqliteScaleOutbox,SqliteWarehouseScaleClaims,
    HttpWarehouseScaleRequests,OpcWarehouseCapture,WarehouseScaleGatewayWorker,deliver_evidence,
    WarehouseGatewayProfile,password)
RUNTIME=ROOT/'runtime/warehouse-opc-native1136-final'


def control(gross):
    path=ROOT/'runtime/warehouse-opc-native1136/approved-test-gross.json'
    path.write_text(json.dumps(dict(owner_approved=True,gross_kg=gross)),encoding='utf-8')


def snapshot(g):
    return dict(source=g.fetch_all("select UID_POLETA,CELL,REMAIN,HARD_RESERVED_BASE,STOCK_VERSION from RRL_REMAINS where UID_POLETA='REUSE.RETURN:e6c16d0bbd'order by CELL"),
        child=g.fetch_all('select l.LOT_UID,r.CELL,r.REMAIN,r.HARD_RESERVED_BASE from RRL_CASE_CARRIER_LOT l join RRL_REMAINS r on r.UID_POLETA=l.LOT_UID where l.CASE_PICK_TASK_ID=1136 and r.REMAIN>0'))


async def run(args):
    g=OracleGateway();before=snapshot(g)
    case=g.fetch_all('select SSCC,CONTENT_VERSION,RESOURCE_SESSION_ID,STATUS,LEGACY_SBORKA_PALLET_ID from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=1136')[0]
    assert case['content_version']==3 and case['legacy_sborka_pallet_id']==641520 and case['resource_session_id']==54,case
    assert before['child'][0]['remain']==1 and before['child'][0]['hard_reserved_base']==1
    profile=OpcScaleProfile.load(ROOT/'runtime/warehouse-opc-native1136/commissioned-test-profile.json')
    device=g.fetch_all("select DEVICE_ID,WARE_ID,POST_CELL,DEVICE_MODE,POLICY_VERSION,CALIBRATION_REF,MEASUREMENT_BASIS from RRL_WH_SCALE_DEVICE where DEVICE_ID='WHREQ15.SCALE'")[0]
    station=WarehouseGatewayProfile(device_id=device['device_id'],warehouse_id=device['ware_id'],post_cell=device['post_cell'],device_mode=device['device_mode'],device_policy_version=device['policy_version'],calibration_ref=device['calibration_ref'],basis=device['measurement_basis'])
    secrets=json.loads((ROOT/'runtime/warehouse-weigh-qa-secrets.json').read_text(encoding='utf-8-sig'))
    operator=HttpWarehouseScaleRequests('http://127.0.0.1:8088','WHREQ15.OP',password(secrets,'WHREQ15.OP'),allow_loopback_http=True)
    api=HttpWarehouseScaleRequests('http://127.0.0.1:8088','WHREQ15.GW',password(secrets,'WHREQ15.GW'),allow_loopback_http=True)
    RUNTIME.mkdir(parents=True,exist_ok=True)
    path=RUNTIME/'operator-request.json'
    if not path.exists():
        value=dict(request_id='WHREQ15.OPC.FINAL:'+uuid4().hex,device_id=device['device_id'],purpose='FINAL_GROSS',case_task_id=1136,expected_content_version=3,scan_container=case['sscc'],tare_capture_key='F4B685621BE6DED35F6AD0EE6C6B610AC3315B390734C832CB839B608622BB89',expected_composition_signature=args.signature)
        with path.open('xb')as handle:
            handle.write(json.dumps(value,sort_keys=True,separators=(',',':')).encode());handle.flush();import os;os.fsync(handle.fileno())
    requestbody=path.read_bytes();request_id=json.loads(requestbody)['request_id']
    box=SqliteScaleOutbox(RUNTIME/'captures.sqlite');rawbox=SqliteScaleOutbox(RUNTIME/'raw.sqlite',max_packet_bytes=131072)
    bundle=SqliteScaleBundleJournal(RUNTIME/'bundles.sqlite');worker=WarehouseScaleGatewayWorker(api,box,station,time.time)
    bundle.reconcile(box,rawbox);await asyncio.to_thread(worker.cycle);await asyncio.to_thread(deliver_evidence,api.post_evidence,rawbox,time.time())
    assert box.pending_count()==0 and rawbox.pending_count()==0
    await asyncio.to_thread(operator._request,'/api/inventory/warehouse-scales/requests',requestbody)
    initial=json.loads(await asyncio.to_thread(operator._request,'/api/inventory/warehouse-scales/requests/'+request_id))
    marker=g.fetch_all('select nvl(max(LOG_ID),0)N from RRL_SQL_SLOW_LOG')[0]['n']
    if initial['state']=='CAPTURED':
        from api.wms_api_server.app.modules.integrations.application.warehouse_scale_ack import validate_warehouse_ack
        from api.wms_api_server.app.modules.integrations.application.scale_evidence_delivery import validate_evidence_ack
        body,raw=bundle.get('WAREHOUSE_FINAL',station.device_id,initial['claim_id']);request=json.loads(requestbody)
        response=await asyncio.to_thread(api.post_capture,body);validate_warehouse_ack(body,response,station)
        raw_ack=validate_evidence_ack(raw,await asyncio.to_thread(api.post_evidence,raw))
        archive=dict(status='ARCHIVED',exact_replay=True);evidence=dict(status='EVIDENCE_ARCHIVED',binding=raw_ack['binding'])
    else:
        request=next(r for r in await asyncio.to_thread(api.requests,station.device_id)if r['request_id']==request_id)
        reader=Opc40200Client(profile)
        class Claims:
            def claim_request(self,request_id,body):
                result=api.claim_request(request_id,body);control('0');return result
            def confirm_zero(self,request_id,body):return api.confirm_zero(request_id,body)
        class PlacementReader:
            placed=False
            async def read(self):
                observation=await reader.read()
                if not self.placed and observation.gross==0:
                    self.placed=True;control('1.5');await asyncio.sleep(.7)
                return observation
        producer=OpcWarehouseCapture(PlacementReader(),SqliteScaleDeviceLease(ROOT/'runtime/opc-device-leases.sqlite'),profile.data,profile.digest,station,bundle,SqliteWarehouseScaleClaims(RUNTIME/'claims.sqlite'),Claims(),lambda:box.pending_count()>0 or rawbox.pending_count()>0)
        marker=g.fetch_all('select nvl(max(LOG_ID),0)N from RRL_SQL_SLOW_LOG')[0]['n']
        await reader.connect()
        try:body,raw=await producer.capture(request)
        finally:await reader.disconnect()
        bundle.reconcile(box,rawbox)
        archive=await asyncio.to_thread(worker.cycle);evidence=await asyncio.to_thread(deliver_evidence,api.post_evidence,rawbox,time.time())
    assert archive['status']=='ARCHIVED'and evidence==dict(status='EVIDENCE_ARCHIVED',binding='MATCHED'),(archive,evidence)
    status=json.loads(await asyncio.to_thread(operator._request,'/api/inventory/warehouse-scales/requests/'+request_id))
    assert status['state']=='CAPTURED'and snapshot(g)==before
    native=g.fetch_all('select RESULT_JSON from RRL_WH_SCALE_CAPTURE where CAPTURE_KEY=:key_value',{'key_value':status['capture_key']})[0]['result_json']
    native=json.loads(native)if isinstance(native,str)else native
    assert native['signature_domain']=='ASM_FINAL'and native['composition_signature_version']==3 and native['composition_signature']==args.signature,native
    report=dict(status='PASS',native_archive=native,capture_key=status['capture_key'],measured_at=json.loads(body)['measured_at'],weight_kg='1.5',request=request,archive=archive,evidence=evidence,source_before=before,source_after=snapshot(g),physical_hardware=False,stock_changed=False,local_encrypted_opc=True,capture_sha256=hashlib.sha256(body).hexdigest().upper(),raw_sha256=hashlib.sha256(raw).hexdigest().upper(),slow_sql=g.fetch_all('select *from(select LOG_ID,ELAPSED_MS,SQL_TEXT from RRL_SQL_SLOW_LOG where LOG_ID>:marker order by ELAPSED_MS desc)where rownum<=10',{'marker':marker}))
    (ROOT/'reports/retailcase/2026-10-15/warehouse-weigh-request/opc-final-native-http.json').write_text(json.dumps(report,indent=2,default=str),encoding='utf-8')
    print(json.dumps({k:report[k]for k in ['status','capture_key','measured_at','stock_changed','physical_hardware']}))


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--execute-final',action='store_true');parser.add_argument('--signature');args=parser.parse_args()
    if not args.execute_final:print('PREPARED_ONLY: wait for root close/bind release');return
    if not args.signature or len(args.signature)!=64:raise ValueError('Root current composition signature required')
    asyncio.run(run(args))


if __name__=='__main__':main()

