"""Real local HTTP transport; supplier fixture is not physical weighing evidence."""
from contextlib import contextmanager
import hashlib
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import threading

import pytest

from api.wms_api_server.app.modules.integrations.application.scale_gateway import ScaleGatewayWorker
from api.wms_api_server.app.modules.integrations.contracts_scales import ScaleGatewayError
from api.wms_api_server.app.modules.integrations.infrastructure.scale_http import HttpScaleGateway
from api.wms_api_server.app.modules.integrations.infrastructure.scale_outbox import SqliteScaleOutbox


@contextmanager
def server(handler):
    http = ThreadingHTTPServer(("127.0.0.1", 0), handler)
    thread = threading.Thread(target=http.serve_forever, daemon=True)
    thread.start()
    try:
        yield "http://127.0.0.1:" + str(http.server_port)
    finally:
        http.shutdown()
        http.server_close()
        thread.join(timeout=2)


def fixture_data():
    request = dict(request_id="r1", device_id="scale1", load_operation_id="load1", store_address="store1",
                   state="REQUESTED", device_policy_version=1, calibration_ref="cal1",
                   expected_composition_signature="sha1", expires_at="2099-01-01T00:00:00+00:00")
    body = json.dumps(dict(device_id="scale1", capture_id="r1", load_operation_id="load1",
                           store_address="store1", device_policy_version=1, calibration_ref="cal1",
                           measured_at="2026-10-15T08:00:00.000000+00:00",
                           samples=[{"offset_ms": index*500, "gross_weight_kg": "12.345"} for index in range(5)]), separators=(",", ":")).encode()
    result = json.loads(body)
    result.update(capture_key=hashlib.sha256(b'["scale1","r1"]').hexdigest().upper(),
                  status="ARCHIVED", receipt_confirmed=False, gross_weight_kg="12.345",
                  source_sha256=hashlib.sha256(json.dumps(json.loads(body), ensure_ascii=True,
                                                        sort_keys=True, separators=(",", ":")).encode()).hexdigest().upper())
    return request, body, result


def test_http_lost_response_retries_exact_body_even_when_request_disappeared(tmp_path):
    request, packet, ack = fixture_data()
    received = []
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *args):
            pass

        def do_GET(self):
            assert self.path.endswith("device_id=scale1")
            assert self.headers["Authorization"].startswith("Basic ")
            assert self.headers["X-Scale-Protocol-Version"] == "1.0"
            self.reply({"items": [] if received else [request]})

        def do_POST(self):
            received.append(self.rfile.read(int(self.headers["Content-Length"])))
            if len(received) == 1:
                self.close_connection = True
                return
            self.reply(ack)

        def reply(self, data):
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(data).encode())

    with server(Handler) as origin:
        api = HttpScaleGateway(origin, "sender", "test-only", allow_loopback_http=True)
        clock = [100.0]
        worker = ScaleGatewayWorker(api, SqliteScaleOutbox(tmp_path / "q.sqlite"), "scale1", lambda: clock[0])
        assert worker.cycle(packet)["status"] == "RETRY_PENDING"
        clock[0] += 5
        assert worker.cycle()["status"] == "ARCHIVED"
        assert received == [packet, packet]
        assert worker.cycle()["status"] == "WAITING_FOR_VENDOR_PACKET"


@pytest.mark.parametrize("mutation", ["capture_key", "store_address", "receipt_confirmed", "status",
                                       "source_sha256", "gross_weight_kg", "device_policy_version",
                                       "calibration_ref", "measured_at"])
def test_wrong_ack_does_not_acknowledge_a_capture(tmp_path, mutation):
    request, packet, ack = fixture_data()
    ack[mutation] = "wrong"
    class Api:
        def requests(self, device):
            return [request]
        def post_capture(self, body):
            return json.dumps(ack).encode()
    box = SqliteScaleOutbox(tmp_path / "q.sqlite")
    result = ScaleGatewayWorker(Api(), box, "scale1", lambda: 100).cycle(packet)
    assert result == {"status": "RETRY_PENDING", "error": "SCALE_CAPTURE_ACK_INVALID"}
    assert box.claim(100) is None
    assert box.claim(103).body == packet


def test_ack_hash_is_server_canonical_not_raw_supplier_whitespace_or_key_order():
    from api.wms_api_server.app.modules.integrations.application.scale_gateway import validate_scale_ack
    _, packet, ack = fixture_data()
    reordered = json.dumps(dict(reversed(list(json.loads(packet).items()))), indent=3).encode()
    assert hashlib.sha256(reordered).hexdigest().upper() != ack["source_sha256"]
    validate_scale_ack(reordered, json.dumps(ack).encode())


@pytest.mark.parametrize("field,value", [("store_address", "other"), ("device_id", "other"),
                                         ("expires_at", "2000-01-01T00:00:00+00:00"),
                                         ("expires_at", "2099-01-01T00:00:00"), ("state", "CANCELLED")])
def test_foreign_expired_or_cancelled_request_never_sends(tmp_path, field, value):
    request, packet, _ = fixture_data()
    request[field] = value
    class Api:
        def requests(self, device):
            return [request]
        def post_capture(self, body):
            pytest.fail("No POST allowed")
    with pytest.raises(ScaleGatewayError):
        ScaleGatewayWorker(Api(), SqliteScaleOutbox(tmp_path / "q.sqlite"), "scale1", lambda: 1000000000).cycle(packet)


def test_permanent_api_rejection_is_suspended_not_automatically_retried(tmp_path):
    request, packet, _ = fixture_data()
    class Api:
        def requests(self, device):
            return [request]
        def post_capture(self, body):
            raise ScaleGatewayError("SCALE_HTTP_409")
    box = SqliteScaleOutbox(tmp_path / "q.sqlite")
    result = ScaleGatewayWorker(Api(), box, "scale1", lambda: 100).cycle(packet)
    assert result["status"] == "SUSPENDED"
    assert box.claim(9999999) is None


@pytest.mark.parametrize("origin", ["http://example.com", "https://u:p@example.com", "https://example.com/path"])
def test_transport_rejects_plaintext_remote_and_embedded_credentials(origin):
    with pytest.raises(ValueError):
        HttpScaleGateway(origin, "sender", "secret", allow_loopback_http=True)


@pytest.mark.parametrize("mode,code", [("redirect", "SCALE_HTTP_302"),
                                       ("oversize", "SCALE_HTTP_RESPONSE_TOO_LARGE"),
                                       ("html", "SCALE_HTTP_JSON_REQUIRED")])
def test_transport_never_follows_redirect_or_accepts_unbounded_nonjson_response(mode, code):
    visited = []
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *args):
            pass
        def do_GET(self):
            visited.append(self.path)
            self.send_response(302 if mode == "redirect" else 200)
            if mode == "redirect":
                self.send_header("Location", "/must-not-receive-credentials")
            self.send_header("Content-Type", "text/html" if mode == "html" else "application/json")
            self.end_headers()
            self.wfile.write(b"x" * (65537 if mode == "oversize" else 1))
    with server(Handler) as origin:
        api = HttpScaleGateway(origin, "sender", "never-print-this", allow_loopback_http=True)
        with pytest.raises(ScaleGatewayError) as caught:
            api.requests("scale1")
        assert caught.value.code == code
        assert "never-print-this" not in str(caught.value)
    assert len(visited) == 1
