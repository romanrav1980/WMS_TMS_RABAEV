"""Frozen actual API, immutable capture replay; no simulated stock acceptance."""
import hashlib
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
import json
import threading
import pytest
from api.wms_api_server.app.modules.integrations.application.assembly_scale_ack import validate_assembly_ack
from api.wms_api_server.app.modules.integrations.application.assembly_scale_gateway import AssemblyScaleWorker
from api.wms_api_server.app.modules.integrations.infrastructure.assembly_scale_http import HttpAssemblyScaleGateway
from api.wms_api_server.app.modules.integrations.infrastructure.scale_outbox import SqliteScaleOutbox
from api.wms_api_server.app.modules.integrations.contracts_scales import ScaleGatewayError


def data(phase="BEFORE"):
    request = dict(session_id="s1",step_id="step1",capture_id="capture."+phase,phase=phase,device_id="d1",
        device_policy_version=1,calibration_ref="cal1",expected_before_kg=".5",min_delta_kg=".1",
        confirmation_mode="AUTO",expires_at="2099-01-01T00:00:00+00:00",tare_capture_key="A"*64)
    source = {key:request[key] for key in ("session_id","step_id","capture_id","phase","device_id","device_policy_version","calibration_ref")}
    source.update(unit="KG",basis="GROSS",preset_tare_kg="0",tare_mode_clear=True,quality_confirmed=True,
        measured_at="2026-10-15T10:00:00.000000+00:00",samples=[dict(offset_ms=i*500,weight_kg="1.5") for i in range(5)])
    body = json.dumps(source,ensure_ascii=True,sort_keys=True,separators=(",", ":")).encode()
    archive = {key:source[key] for key in ("session_id","step_id","capture_id","phase","device_id","device_policy_version","calibration_ref","measured_at")}
    archive.update(status="ARCHIVED",stock_posted=False,weight_kg="1.5",source_sha256=hashlib.sha256(body).hexdigest().upper(),
        capture_key=hashlib.sha256(json.dumps([source["device_id"],source["capture_id"]],separators=(",", ":")).encode()).hexdigest().upper())
    return request,body,dict(archive=archive,step={"state":"READY"},posting=None)


@pytest.mark.parametrize("field",["session_id","step_id","phase","capture_id","device_id","source_sha256","capture_key","weight_kg","measured_at","device_policy_version","calibration_ref","stock_posted"])
def test_wrong_immutable_archive_never_acknowledges_capture(field):
    _,body,result = data()
    result["archive"][field] = "wrong"
    with pytest.raises(ScaleGatewayError,match="ACK_INVALID"):
        validate_assembly_ack(body,json.dumps(result).encode())


def test_archived_ready_without_stock_effect_is_valid_and_canonical_hash_ignores_whitespace():
    _,body,result = data()
    pretty = json.dumps(dict(reversed(list(json.loads(body).items()))),indent=2).encode()
    assert validate_assembly_ack(pretty,json.dumps(result).encode())["stock_posted"] is False
    assert result["step"]["state"] == "READY" and result["posting"] is None


def test_lost_response_replays_original_body_even_when_queue_advanced_phase(tmp_path):
    request,body,result = data()
    received = []
    class Api:
        def requests(self,device):
            if received:
                later = dict(request,phase="AFTER",capture_id="capture.AFTER")
                return [later]
            return [request]
        def post_capture(self,wire):
            received.append(wire)
            if len(received)==1:
                raise ScaleGatewayError("SCALE_HTTP_503",True)
            return json.dumps(result).encode()
    now = [100.0]
    box = SqliteScaleOutbox(tmp_path/"queue.sqlite")
    worker = AssemblyScaleWorker(Api(),box,"d1",lambda:now[0])
    assert worker.cycle(body)["status"] == "CAPTURE_RETRY_PENDING"
    now[0] = 105
    assert worker.cycle()["status"] == "CAPTURE_ARCHIVED"
    assert received == [body,body]


def test_actual_http_prefix_and_raw_version_11_are_separate_from_capture_v10(tmp_path):
    request,body,result = data()
    calls = []
    class Handler(BaseHTTPRequestHandler):
        def log_message(self,*args):
            pass
        def do_GET(self):
            calls.append((self.path,self.headers["X-Scale-Protocol-Version"]))
            self.reply({"items":[request]})
        def do_POST(self):
            payload = self.rfile.read(int(self.headers["Content-Length"]))
            calls.append((self.path,self.headers["X-Scale-Protocol-Version"]))
            self.reply(result if self.path.endswith("/captures") else {"ok":True})
        def reply(self,value):
            self.send_response(200)
            self.send_header("Content-Type","application/json")
            self.end_headers()
            self.wfile.write(json.dumps(value).encode())
    server = ThreadingHTTPServer(("127.0.0.1",0),Handler)
    thread = threading.Thread(target=server.serve_forever,daemon=True)
    thread.start()
    try:
        api = HttpAssemblyScaleGateway("http://127.0.0.1:"+str(server.server_port),"test-sender","test-only",allow_loopback_http=True)
        worker = AssemblyScaleWorker(api,SqliteScaleOutbox(tmp_path/"queue.sqlite"),"d1",lambda:100)
        assert worker.cycle(body)["status"] == "CAPTURE_ARCHIVED"
        api.post_evidence(b'{"protocol_version":"1.1"}')
        assert calls == [("/api/inventory/assembly-scale/gateway/requests?device_id=d1","1.0"),
                         ("/api/inventory/assembly-scale/captures","1.0"),("/api/integrations/scale-evidence","1.1")]
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)
