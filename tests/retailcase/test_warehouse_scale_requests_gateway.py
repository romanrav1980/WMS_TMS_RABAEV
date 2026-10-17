"""Claim durability/projection faults; no Oracle or physical device writes."""
import asyncio
from datetime import datetime,timedelta,timezone
from decimal import Decimal
import hashlib
import json
from concurrent.futures import ThreadPoolExecutor
from http.server import BaseHTTPRequestHandler
import pytest
from api.wms_api_server.app.modules.integrations.application.warehouse_opc_capture import OpcWarehouseCapture
from api.wms_api_server.app.modules.integrations.application.warehouse_scale_claim import validate_claim
from api.wms_api_server.app.modules.integrations.contracts_scale_opc import OpcWeightObservation
from api.wms_api_server.app.modules.integrations.contracts_scales import ScaleGatewayError
from api.wms_api_server.app.modules.integrations.infrastructure.warehouse_scale_claims import SqliteWarehouseScaleClaims
from api.wms_api_server.app.modules.integrations.infrastructure.warehouse_scale_request_http import HttpWarehouseScaleRequests
from api.wms_api_server.app.modules.integrations.infrastructure.scale_device_lease import SqliteScaleDeviceLease
from api.wms_api_server.app.modules.integrations.infrastructure.scale_bundle_journal import SqliteScaleBundleJournal
from api.wms_api_server.app.modules.integrations.infrastructure.scale_outbox import SqliteScaleOutbox
from tests.retailcase.test_warehouse_scale_gateway import vector,server


def claim_vector(body,purpose='EMPTY_TARE'):
    profile,packet,_=vector(purpose)
    context=json.loads(packet)
    for field in ('zero_confirmed','zero_check_kg','zero_check_at','measured_at','samples'):
        context.pop(field)
    claim=json.loads(body)
    context['capture_id']=claim['claim_id']
    now=datetime.now(timezone.utc)
    return dict(request_id='request1',device_id=profile.device_id,case_task_id=12,purpose=purpose,
        state='CLAIMED',current_context='CURRENT',stock_posted=False,claim_active=True,
        claim_id=claim['claim_id'],capture_context=context,
        expires_at=(now+timedelta(seconds=120)).isoformat(),claim_expires_at=(now+timedelta(seconds=30)).isoformat())


def observation(gross,zero=False):
    now=datetime.now(timezone.utc)
    stamp=now.isoformat(timespec='microseconds')
    value=dict(variant_type='Double',value=str(gross),status_code=0,source_timestamp=stamp,server_timestamp=stamp)
    evidence=dict(observed_at=stamp,values={key:dict(value)for key in ('current_weight','stable','center_zero','overload','underload','tare_mode','engineering_units')})
    return OpcWeightObservation(Decimal(gross),Decimal(gross),Decimal(0),True,zero,now,evidence)


class Reader:
    def __init__(self):self.reads=0
    async def read(self):
        self.reads+=1
        return observation('0',True)


class Api:
    def __init__(self,purpose='EMPTY_TARE'):
        self.bodies=[];self.purpose=purpose;self.fail=False;self.change=None
    def claim_request(self,request_id,body):
        self.bodies.append(body)
        if self.fail:raise ScaleGatewayError('LOST_CLAIM_ACK',True)
        result=claim_vector(body,self.purpose)
        if self.change:self.change(result)
        return json.dumps(result).encode()


def capture_service(tmp_path,api=None,reader=None,pending=lambda:False):
    profile,_,_=vector()
    data=dict(device_id=profile.device_id,station_id='post1',warehouse_pick_mode='SEALED_WEIGHT_BOX',model_namespace_uri='http://opcfoundation.org/UA/Scales/V2/',
        server_application_uri='urn:test',security=dict(server_sha256='B'*64),nodes={})
    claims=SqliteWarehouseScaleClaims(tmp_path/'claims.sqlite')
    bundle=SqliteScaleBundleJournal(tmp_path/'bundles.sqlite')
    api=api or Api()
    capture=OpcWarehouseCapture(reader or Reader(),SqliteScaleDeviceLease(tmp_path/'lease.sqlite'),data,'A'*64,
        profile,bundle,claims,api,pending)
    request=dict(device_id=profile.device_id,request_id='request1',case_task_id=12,purpose=api.purpose,state='REQUESTED')
    return capture,request,api


def test_two_processes_get_one_original_claim_and_no_new_id_after_terminal(tmp_path):
    path=tmp_path/'claims.sqlite';SqliteWarehouseScaleClaims(path)
    with ThreadPoolExecutor(2)as pool:
        bodies=list(pool.map(lambda _:SqliteWarehouseScaleClaims(path).prepare('request1','scale1'),range(2)))
    assert bodies[0]==bodies[1]
    SqliteWarehouseScaleClaims(path).terminal('request1','EXPIRED')
    with pytest.raises(ScaleGatewayError,match='TERMINAL'):SqliteWarehouseScaleClaims(path).prepare('request1','scale1')
    assert SqliteWarehouseScaleClaims(path).prepare('request2','scale1')!=bodies[0]


def test_lost_claim_response_restart_reuses_exact_id_without_instrument_read(tmp_path):
    api=Api();api.fail=True
    capture,request,_=capture_service(tmp_path,api)
    with pytest.raises(ScaleGatewayError,match='LOST_CLAIM_ACK'):asyncio.run(capture.capture(request))
    assert capture.reader.reads==0
    restarted,_,_=capture_service(tmp_path,api)
    with pytest.raises(ScaleGatewayError):asyncio.run(restarted.capture(request))
    assert api.bodies[0]==api.bodies[1]and restarted.reader.reads==0


@pytest.mark.parametrize('change',[
    lambda r:r.update(claim_id='foreign'),lambda r:r.update(current_context='STALE'),
    lambda r:r['capture_context'].update(case_task_id=True),lambda r:r['capture_context'].update(samples=[]),
    lambda r:r['capture_context'].update(basis='NET'),lambda r:r.update(stock_posted=True)])
def test_bad_claim_ack_never_reads_hardware(tmp_path,change):
    api=Api();api.change=change
    capture,request,_=capture_service(tmp_path,api)
    with pytest.raises(ScaleGatewayError,match='ACK_INVALID'):asyncio.run(capture.capture(request))
    assert capture.reader.reads==0


def test_expired_claim_is_terminal_without_new_claim_or_measurement(tmp_path):
    api=Api();api.change=lambda r:r.update(claim_active=False,state='REQUESTED')
    capture,request,_=capture_service(tmp_path,api)
    with pytest.raises(ScaleGatewayError,match='EXPIRED_OR_CAPTURED'):asyncio.run(capture.capture(request))
    with pytest.raises(ScaleGatewayError,match='TERMINAL'):asyncio.run(capture.capture(request))
    assert len(api.bodies)==1 and capture.reader.reads==0


def test_pending_previous_outbox_blocks_new_claim_before_hardware(tmp_path):
    capture,request,api=capture_service(tmp_path,pending=lambda:True)
    with pytest.raises(ScaleGatewayError,match='DRAIN_REQUIRED'):asyncio.run(capture.capture(request))
    assert not api.bodies and capture.reader.reads==0


@pytest.mark.parametrize('purpose',['EMPTY_TARE','FINAL_GROSS','PICK'])
def test_projection_stages_atomic_pair_restart_ignores_new_bad_measurements(tmp_path,monkeypatch,purpose):
    async def window(reader,renew,timeout):
        renew()
        return [observation('12.345')for _ in range(5)],[0,500,1000,1500,2000]
    monkeypatch.setattr('api.wms_api_server.app.modules.integrations.application.warehouse_opc_capture.collect_opc_window',window)
    capture,request,api=capture_service(tmp_path,Api(purpose))
    body,raw=asyncio.run(capture.capture(request))
    source,evidence=json.loads(body),json.loads(raw)
    assert source['capture_id']==json.loads(api.bodies[0])['claim_id']
    assert source['samples'][-1]['weight_kg']=='12.345'and source['zero_check_kg']=='0'
    assert evidence['capture_kind']==('WAREHOUSE_PICK'if purpose=='PICK'else'WAREHOUSE_FINAL')
    assert evidence['capture_sha256']==hashlib.sha256(body).hexdigest().upper()
    restarted,_,_=capture_service(tmp_path,api)
    assert asyncio.run(restarted.capture(request))==(body,raw)
    assert restarted.reader.reads==0 and len(api.bodies)==1
    boxes=[SqliteScaleOutbox(tmp_path/name)for name in ('capture.sqlite','raw.sqlite')]
    capture.bundle.reconcile(*boxes)
    assert list(boxes[0].bodies())==[body]and list(boxes[1].bodies())==[raw]


def test_http_real_paths_protocol_and_exact_claim_body(tmp_path):
    received=[]
    class Handler(BaseHTTPRequestHandler):
        def log_message(self,*args):pass
        def answer(self,result):
            self.send_response(200);self.send_header('Content-Type','application/json');self.end_headers();self.wfile.write(json.dumps(result).encode())
        def do_GET(self):
            assert self.path=='/api/inventory/warehouse-scales/gateway/requests?device_id=scale1'
            self.answer(dict(device_id='scale1',items=[dict(request_id='request/1',device_id='scale1',state='REQUESTED')]))
        def do_POST(self):
            body=self.rfile.read(int(self.headers['Content-Length']))
            received.append(body)
            assert self.path=='/api/inventory/warehouse-scales/gateway/requests/request%2F1/claim'
            assert self.headers['X-Scale-Protocol-Version']=='1.0'
            self.answer(claim_vector(body))
    with server(Handler)as origin:
        api=HttpWarehouseScaleRequests(origin,'sender','test-only',allow_loopback_http=True)
        assert api.requests('scale1')[0]['request_id']=='request/1'
        body=SqliteWarehouseScaleClaims(tmp_path/'claims.sqlite').prepare('request/1','scale1')
        api.claim_request('request/1',body)
    assert received==[body]

def test_uncommissioned_gross_pick_and_net_profiles_do_not_claim(tmp_path):
    capture,request,api=capture_service(tmp_path,Api('PICK'))
    capture.profile.pop('warehouse_pick_mode')
    with pytest.raises(ScaleGatewayError,match='PICK_COMMISSIONING_REQUIRED'):asyncio.run(capture.capture(request))
    capture.station=capture.station.model_copy(update=dict(basis='NET'))
    with pytest.raises(ScaleGatewayError,match='NET_PROFILE_UNSUPPORTED'):asyncio.run(capture.capture(request))
    assert not api.bodies and capture.reader.reads==0


def test_other_local_worker_cannot_claim_same_physical_device(tmp_path):
    capture,request,api=capture_service(tmp_path)
    import time
    token=capture.lease.acquire('scale1',time.time(),15)
    try:
        with pytest.raises(ScaleGatewayError):asyncio.run(capture.capture(request))
        assert not api.bodies and capture.reader.reads==0
    finally:capture.lease.release('scale1',token)


def test_local_claim_deadline_prevents_any_zero_read(tmp_path):
    api=Api();api.change=lambda r:r.update(claim_expires_at=(datetime.now(timezone.utc)+timedelta(seconds=5)).isoformat())
    capture,request,_=capture_service(tmp_path,api)
    with pytest.raises(ScaleGatewayError,match='ACTUAL_EMPTY_PLATFORM_ZERO_REQUIRED'):asyncio.run(capture.capture(request))
    assert capture.reader.reads==0


def test_outbox_pending_count_includes_backoff_not_terminal_history(tmp_path):
    box=SqliteScaleOutbox(tmp_path/'box.sqlite');_,body,_=vector()
    box.stage(body)
    assert box.pending_count()==1
    delivery=box.claim(100)
    box.defer(delivery,200,'LOST_ACK')
    assert box.pending_count()==1 and box.claim(101)is None
    box.suspend(box.claim(200),'LATE_FIRST_CAPTURE')
    assert box.pending_count()==0 and box.has_capture('scale1','capture1')

def test_crash_after_local_bundle_commit_restarts_without_claim_or_new_read(tmp_path,monkeypatch):
    async def window(reader,renew,timeout):
        return [observation('12.345')for _ in range(5)],[0,500,1000,1500,2000]
    monkeypatch.setattr('api.wms_api_server.app.modules.integrations.application.warehouse_opc_capture.collect_opc_window',window)
    capture,request,api=capture_service(tmp_path)
    original=capture.bundle.stage
    def crash(body,raw):
        original(body,raw)
        raise RuntimeError('SIMULATED_PROCESS_CRASH_AFTER_COMMIT')
    capture.bundle.stage=crash
    with pytest.raises(RuntimeError,match='AFTER_COMMIT'):asyncio.run(capture.capture(request))
    claim_id=json.loads(api.bodies[0])['claim_id']
    retained=capture.bundle.get('WAREHOUSE_FINAL','scale1',claim_id)
    restarted,_,_=capture_service(tmp_path,api)
    assert asyncio.run(restarted.capture(request))==retained
    assert restarted.reader.reads==0 and len(api.bodies)==1


def test_preclaim_timestamp_cannot_become_new_packet(tmp_path,monkeypatch):
    async def window(reader,renew,timeout):
        series=[observation('12.345')for _ in range(5)]
        series[0].evidence['values']['current_weight']['server_timestamp']=(datetime.now(timezone.utc)-timedelta(seconds=10)).isoformat()
        return series,[0,500,1000,1500,2000]
    monkeypatch.setattr('api.wms_api_server.app.modules.integrations.application.warehouse_opc_capture.collect_opc_window',window)
    capture,request,api=capture_service(tmp_path)
    with pytest.raises(ScaleGatewayError,match='OUTSIDE_LOCAL_CLAIM'):asyncio.run(capture.capture(request))
    assert capture.bundle.get('WAREHOUSE_FINAL','scale1',json.loads(api.bodies[0])['claim_id'])is None


def test_zero_flag_and_stability_are_required_not_merely_numeric_zero(tmp_path,monkeypatch):
    class NotZeroReader:
        def __init__(self):self.reads=0
        async def read(self):
            self.reads+=1
            if self.reads==1:return observation('0',False)
            return observation('0',True)
    async def no_wait(seconds):pass
    monkeypatch.setattr('api.wms_api_server.app.modules.integrations.application.warehouse_opc_capture.asyncio.sleep',no_wait)
    reader=NotZeroReader();capture,_,_=capture_service(tmp_path,reader=reader)
    import time
    result=asyncio.run(capture._zero(lambda:None,time.time()+30))
    assert reader.reads==2 and result.center_zero


def test_bundle_crash_between_warehouse_mirrors_replays_both_originals(tmp_path,monkeypatch):
    async def window(reader,renew,timeout):
        return [observation('12.345')for _ in range(5)],[0,500,1000,1500,2000]
    monkeypatch.setattr('api.wms_api_server.app.modules.integrations.application.warehouse_opc_capture.collect_opc_window',window)
    capture,request,_=capture_service(tmp_path)
    body,raw=asyncio.run(capture.capture(request))
    capturebox=SqliteScaleOutbox(tmp_path/'captures.sqlite');rawbox=SqliteScaleOutbox(tmp_path/'raw.sqlite')
    original=rawbox.stage
    rawbox.stage=lambda body:(_ for _ in ()).throw(RuntimeError('SIMULATED_CRASH_BETWEEN_MIRRORS'))
    with pytest.raises(RuntimeError,match='BETWEEN_MIRRORS'):capture.bundle.reconcile(capturebox,rawbox)
    assert list(capturebox.bodies())==[body]and not list(rawbox.bodies())
    rawbox.stage=original
    SqliteScaleBundleJournal(tmp_path/'bundles.sqlite').reconcile(capturebox,rawbox)
    assert list(capturebox.bodies())==[body]and list(rawbox.bodies())==[raw]
