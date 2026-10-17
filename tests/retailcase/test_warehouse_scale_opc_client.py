"""Encrypted local OPC through actual HTTP request/claim/capture/raw; not hardware/native acceptance."""
import asyncio
from datetime import datetime,timedelta,timezone
import hashlib
from http.server import BaseHTTPRequestHandler
import json
import threading
import time
import pytest
pytest.importorskip('asyncua')
from tests.retailcase.test_scale_opc_client import opc_fixture
from tests.retailcase.test_warehouse_scale_gateway import vector,server
from tests.retailcase.test_warehouse_scale_requests_gateway import claim_vector
from api.wms_api_server.app.modules.integrations.infrastructure.scale_opc_client import Opc40200Client
from api.wms_api_server.app.modules.integrations.infrastructure.scale_bundle_journal import SqliteScaleBundleJournal
from api.wms_api_server.app.modules.integrations.infrastructure.scale_device_lease import SqliteScaleDeviceLease
from api.wms_api_server.app.modules.integrations.infrastructure.scale_outbox import SqliteScaleOutbox
from api.wms_api_server.app.modules.integrations.infrastructure.warehouse_scale_claims import SqliteWarehouseScaleClaims
from api.wms_api_server.app.modules.integrations.infrastructure.warehouse_scale_request_http import HttpWarehouseScaleRequests
from api.wms_api_server.app.modules.integrations.application.warehouse_opc_capture import OpcWarehouseCapture
from api.wms_api_server.app.modules.integrations.application.warehouse_scale_gateway import WarehouseScaleGatewayWorker
from api.wms_api_server.app.modules.integrations.application.scale_evidence_delivery import deliver_evidence
from api.wms_api_server.app.modules.integrations.contracts_scale_evidence import ScaleEvidence
from api.wms_api_server.app.modules.inventory.contracts_warehouse_scale import WarehouseFinalScalePacket,WarehouseScalePacket


@pytest.mark.parametrize('purpose',['EMPTY_TARE','FINAL_GROSS','PICK'])
@pytest.mark.parametrize('zero_required',[False,True])
def test_claim_then_actual_empty_zero_replace_and_fresh_gross_bundle_exact_delivery(tmp_path,purpose,zero_required):
    async def scenario():
        async with opc_fixture(tmp_path)as(profile,state):
            station,_,_=vector(purpose)
            station=station.model_copy(update=dict(device_id=profile.data['device_id']))
            profile.data['warehouse_pick_mode']='SEALED_WEIGHT_BOX'
            path=profile.root/'profile.json'
            path.write_text(json.dumps(profile.data),encoding='utf-8')
            profile=type(profile).load(path)
            received=[];claimed=threading.Event();claim_result={}
            request=dict(request_id='request1',device_id=station.device_id,purpose=purpose,case_task_id=12,state='REQUESTED')
            if zero_required:request['zero_progress_required']=True
            class Handler(BaseHTTPRequestHandler):
                def log_message(self,*args):pass
                def answer(self,result):
                    self.send_response(200);self.send_header('Content-Type','application/json');self.end_headers();self.wfile.write(json.dumps(result).encode())
                def do_GET(self):
                    assert self.path.startswith('/api/inventory/warehouse-scales/gateway/requests?')
                    self.answer(dict(device_id=station.device_id,items=[request]))
                def do_POST(self):
                    body=self.rfile.read(int(self.headers['Content-Length']));source=json.loads(body)
                    received.append((self.path,body,self.headers['X-Scale-Protocol-Version']))
                    if self.path.endswith('/claim'):
                        result=claim_vector(body,purpose);result['device_id']=station.device_id
                        result['capture_context']['device_id']=station.device_id
                        if zero_required:
                            result.update(zero_progress_required=True,claim_created_at=datetime.now(timezone.utc).isoformat())
                        else:claimed.set()
                        claim_result.update(result);self.answer(result)
                    elif self.path.endswith('/zero-confirmed'):
                        evidence=json.loads(source['zero_evidence_json'])
                        assert evidence['values']['current_weight']['value']['Gross']=='0.0'
                        assert evidence['values']['stable']['value'] is True
                        receipt={key:source[key]for key in('claim_id','device_id','zero_observed_at','zero_source_sha256','profile_sha256')}
                        receipt.update(request_id='request1',zero_confirmed=True,stock_posted=False,
                            claim_expires_at=claim_result['claim_expires_at'],source_sha256=hashlib.sha256(body).hexdigest().upper())
                        current=dict(claim_result,measurement_stage='ZERO_CONFIRMED',load_allowed=True,
                            zero_source_sha256=source['zero_source_sha256'],zero_confirmed_at=source['zero_observed_at'],
                            server_now=datetime.now(timezone.utc).isoformat())
                        claimed.set();self.answer(dict(receipt=receipt,current=current))
                    elif self.path=='/api/integrations/scale-evidence':
                        evidence=ScaleEvidence.model_validate_json(body)
                        assert evidence.canonical_bytes()==body
                        result={key:source[key]for key in ('protocol_version','capture_kind','device_id','capture_id','capture_sha256')}
                        result.update(status='ARCHIVED',binding='MATCHED',stock_posted=False,provenance='GATEWAY_REPORTED',evidence_sha256=hashlib.sha256(body).hexdigest().upper())
                        self.answer(result)
                    else:
                        model=WarehouseScalePacket if purpose=='PICK'else WarehouseFinalScalePacket
                        assert model.model_validate_json(body).basis=='GROSS'
                        identity=json.dumps([source['device_id'],source['capture_id']],ensure_ascii=False,separators=(',',':')).encode()
                        result=dict(source,status='ARCHIVED',warehouse_id=1,device_mode='TEST',stock_posted=False,
                            source_sha256=hashlib.sha256(body).hexdigest().upper(),capture_key=hashlib.sha256(identity).hexdigest().upper(),
                            case_content_version=3,weight_kg=source['samples'][-1]['weight_kg'],sample_count=len(source['samples']),
                            span_ms=source['samples'][-1]['offset_ms'],pallet_type_id=1,type_version=1,
                            composition_signature='B'*64,tare_weight_kg='1',net_weight_kg='11.345')
                        self.answer(result)
            with server(Handler)as origin:
                api=HttpWarehouseScaleRequests(origin,'test-sender','test-only',allow_loopback_http=True)
                reader=Opc40200Client(profile);await reader.connect()
                bundle=SqliteScaleBundleJournal(tmp_path/'bundle.sqlite')
                box=SqliteScaleOutbox(tmp_path/'captures.sqlite');rawbox=SqliteScaleOutbox(tmp_path/'raw.sqlite',max_packet_bytes=131072)
                producer=OpcWarehouseCapture(reader,SqliteScaleDeviceLease(tmp_path/'lease.sqlite'),profile.data,profile.digest,station,
                    bundle,SqliteWarehouseScaleClaims(tmp_path/'claims.sqlite'),api,lambda:box.pending_count()>0 or rawbox.pending_count()>0)
                try:
                    actual=(await asyncio.to_thread(api.requests,station.device_id))[0]
                    async def place():
                        while not claimed.is_set():await asyncio.sleep(.01)
                        await asyncio.sleep(.75)
                        state.update(gross=12.345,zero=False)
                    loading=asyncio.create_task(place())
                    body,raw=await producer.capture(actual);await loading
                    bundle.reconcile(box,rawbox)
                    worker=WarehouseScaleGatewayWorker(api,box,station,time.time)
                    assert await asyncio.to_thread(worker.cycle)=={'status':'ARCHIVED'}
                    assert(await asyncio.to_thread(deliver_evidence,api.post_evidence,rawbox,time.time()))['binding']=='MATCHED'
                    state.update(quality=0x80000000)
                    assert await producer.capture(actual)==(body,raw)
                    assert box.pending_count()==0 and rawbox.pending_count()==0
                finally:await reader.disconnect()
            expected=['/api/inventory/warehouse-scales/gateway/requests/request1/claim']
            if zero_required:expected.append('/api/inventory/warehouse-scales/gateway/requests/request1/zero-confirmed')
            assert [path for path,_,_ in received]==expected+[
                '/api/inventory/warehouse-scales/'+('captures'if purpose=='PICK'else'final-captures'),
                '/api/integrations/scale-evidence']
            assert all(version=='1.0'for _,_,version in received)
    asyncio.run(scenario())

