"""Separate recovery evidence never creates a stock-posting success."""
import hashlib
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
import json
import threading
import pytest
from api.wms_api_server.app.modules.integrations.application.assembly_scale_ack import validate_assembly_ack
from api.wms_api_server.app.modules.integrations.application.assembly_scale_gateway import AssemblyScaleWorker
from api.wms_api_server.app.modules.integrations.infrastructure.assembly_scale_http import HttpAssemblyScaleGateway
from api.wms_api_server.app.modules.integrations.infrastructure.scale_outbox import SqliteScaleOutbox
from api.wms_api_server.app.modules.integrations.infrastructure.scale_bundle_journal import SqliteScaleBundleJournal
from api.wms_api_server.app.modules.integrations.contracts_scales import ScaleGatewayError


def data():
    source=dict(session_id='s',step_id='step',device_id='d',capture_id='recon.capture',phase='RECONCILE',reconciliation_id='recon.request',device_policy_version=1,calibration_ref='cal',unit='KG',basis='GROSS',preset_tare_kg='0',tare_mode_clear=True,quality_confirmed=True,measured_at='2026-10-15T10:00:00.000000+00:00',samples=[dict(offset_ms=i*500,weight_kg='.5')for i in range(5)])
    body=json.dumps(source,ensure_ascii=True,sort_keys=True,separators=(',',':')).encode()
    archive={key:source[key]for key in ('session_id','step_id','device_id','capture_id','phase','reconciliation_id','device_policy_version','calibration_ref','measured_at')}
    archive.update(status='ARCHIVED',state='COMPLETED',stock_posted=False,weight_kg='.5',source_sha256=hashlib.sha256(body).hexdigest().upper(),capture_key=hashlib.sha256(json.dumps(['d','recon.capture'],separators=(',',':')).encode()).hexdigest().upper())
    result=dict(archive=archive,step={'state':'DISCREPANCY'},posting=None)
    request=dict(source,expected_before_kg='.5',min_delta_kg='.1',expires_at='2099-01-01T00:00:00+00:00',tare_capture_key='A'*64,confirmation_mode='AUTO')
    return request,body,result


@pytest.mark.parametrize('state',['COMPLETED','DISCREPANCY'])
def test_recovery_archive_ack_is_valid_without_stock_success(state):
    _,body,result=data();result['archive']['state']=state
    assert validate_assembly_ack(body,json.dumps(result).encode())['state']==state


@pytest.mark.parametrize('change',['wrong_id','wrong_state','posting'])
def test_recovery_wrong_identity_or_posting_never_acknowledged(change):
    _,body,result=data()
    if change=='wrong_id':result['archive']['reconciliation_id']='foreign'
    elif change=='wrong_state':result['archive']['state']='APPLIED'
    else:result['posting']={'status':'APPLIED'}
    with pytest.raises(ScaleGatewayError,match='ACK_INVALID'):validate_assembly_ack(body,json.dumps(result).encode())


def test_fixed_recovery_body_survives_timeout_and_completed_queue_removal(tmp_path):
    request,body,result=data();calls=[]
    class Api:
        def requests(self,device):return []if calls else[request]
        def post_capture(self,wire):
            calls.append(wire)
            if len(calls)==1:raise ScaleGatewayError('SCALE_HTTP_503',True)
            return json.dumps(result).encode()
    now=[100];worker=AssemblyScaleWorker(Api(),SqliteScaleOutbox(tmp_path/'captures.sqlite'),'d',lambda:now[0])
    assert worker.cycle(body)['status']=='CAPTURE_RETRY_PENDING';now[0]=110
    answer=worker.cycle();assert answer['status']=='CAPTURE_ARCHIVED'and answer['stock_outcome']=='NO_STOCK_EFFECT_RECONCILIATION'
    assert calls==[body,body]


def test_foreign_reconciliation_request_id_never_staged(tmp_path):
    request,body,_=data();request['reconciliation_id']='other'
    class Api:
        def requests(self,device):return[request]
    box=SqliteScaleOutbox(tmp_path/'capture.sqlite');worker=AssemblyScaleWorker(Api(),box,'d',lambda:100)
    with pytest.raises(ScaleGatewayError,match='REQUEST_MISMATCH'):worker.cycle(body)
    assert not box.has_capture('d','recon.capture')


def test_recovery_bundle_and_http_headers_keep_capture_v10_raw_v12(tmp_path):
    request,body,result=data();calls=[]
    raw=json.dumps(dict(protocol_version='1.2',capture_kind='WAREHOUSE_ASSEMBLY_RECON',device_id='d',capture_id='recon.capture',capture_sha256=hashlib.sha256(body).hexdigest().upper())).encode()
    bundle=SqliteScaleBundleJournal(tmp_path/'bundle.sqlite');bundle.stage(body,raw)
    capture=SqliteScaleOutbox(tmp_path/'capture.sqlite');evidence=SqliteScaleOutbox(tmp_path/'raw.sqlite',max_packet_bytes=131072);bundle.reconcile(capture,evidence)
    assert capture.claim(100).body==body and evidence.claim(100).body==raw
    class Handler(BaseHTTPRequestHandler):
        def log_message(self,*_):pass
        def do_POST(self):
            wire=self.rfile.read(int(self.headers['Content-Length']));calls.append((self.path,self.headers['X-Scale-Protocol-Version'],wire))
            self.send_response(200);self.send_header('Content-Type','application/json');self.end_headers();self.wfile.write(json.dumps(result).encode())
    server=ThreadingHTTPServer(('127.0.0.1',0),Handler);thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
    try:
        api=HttpAssemblyScaleGateway('http://127.0.0.1:'+str(server.server_port),'test-only','test-only',allow_loopback_http=True)
        api.post_capture(body);api.post_evidence(raw)
        assert [(p,v)for p,v,_ in calls]==[('/api/inventory/assembly-scale/captures','1.0'),('/api/integrations/scale-evidence','1.2')]
        assert[c[2]for c in calls]==[body,raw]
    finally:server.shutdown();server.server_close();thread.join()

