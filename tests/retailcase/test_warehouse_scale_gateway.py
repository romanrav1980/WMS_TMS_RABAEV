"""Protocol-only fixtures: real loopback HTTP failures are not physical scale evidence."""
from contextlib import contextmanager
from datetime import datetime, timezone
import hashlib
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import threading

import pytest
from api.wms_api_server.app.modules.integrations.application.warehouse_scale_gateway import WarehouseScaleGatewayWorker
from api.wms_api_server.app.modules.integrations.application.warehouse_scale_ack import validate_warehouse_ack
from api.wms_api_server.app.modules.integrations.contracts_warehouse_gateway import WarehouseGatewayProfile
from api.wms_api_server.app.modules.integrations.contracts_scales import ScaleGatewayError
from api.wms_api_server.app.modules.integrations.infrastructure.warehouse_scale_http import HttpWarehouseScaleGateway
from api.wms_api_server.app.modules.integrations.infrastructure.scale_outbox import SqliteScaleOutbox

NOW = datetime(2026, 10, 15, 10, tzinfo=timezone.utc).timestamp()


def vector(purpose="PICK"):
    profile = WarehouseGatewayProfile(device_id="scale1", warehouse_id=1, post_cell="post1",
        device_mode="TEST", device_policy_version=2, calibration_ref="cal1", basis="GROSS")
    source = dict(device_id="scale1", capture_id="capture1", post_cell="post1", case_task_id=12,
        expected_content_version=3, scan_container="internal-12", device_policy_version=2,
        calibration_ref="cal1", unit="KG", basis="GROSS", preset_tare_kg="0",
        zero_confirmed=True, zero_check_kg="0", zero_check_at="2026-10-15T09:59:55.000000+00:00",
        measured_at="2026-10-15T10:00:00.000000+00:00",
        samples=[dict(offset_ms=i*500, weight_kg="12.345") for i in range(5)])
    if purpose == "PICK":
        source.update(case_line_id=13, scan_source_cell="source1", scan_product="product1")
    else:
        source["purpose"] = purpose
        if purpose == "FINAL_GROSS":
            source["tare_capture_key"] = "A" * 64
    canonical = json.dumps(source, ensure_ascii=True, sort_keys=True, separators=(",", ":")).encode()
    ack = dict(source, capture_key=hashlib.sha256(b'["scale1","capture1"]').hexdigest().upper(),
        source_sha256=hashlib.sha256(canonical).hexdigest().upper(), case_content_version=3,
        warehouse_id=1, device_mode="TEST", stock_posted=False, status="ARCHIVED",
        weight_kg="12.345", sample_count=5, span_ms=2000, pallet_type_id=1, type_version=1,
        composition_signature="B"*64, tare_weight_kg="1", net_weight_kg="11.345")
    return profile, json.dumps(source, indent=2).encode(), ack


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


@pytest.mark.parametrize("purpose,path", [("PICK", "captures"), ("EMPTY_TARE", "final-captures"), ("FINAL_GROSS", "final-captures")])
def test_lost_response_restart_retains_exact_packet_after_measurement_expiry(tmp_path, purpose, path):
    profile, packet, ack = vector(purpose)
    received = []
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *args):
            pass
        def do_POST(self):
            assert self.path == "/api/inventory/warehouse-scales/" + path
            received.append(self.rfile.read(int(self.headers["Content-Length"])))
            if len(received) == 1:
                self.close_connection = True
                return
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(ack).encode())
    with server(Handler) as origin:
        api = HttpWarehouseScaleGateway(origin, "sender", "test-only", allow_loopback_http=True)
        database = tmp_path / "outbox.sqlite"
        assert WarehouseScaleGatewayWorker(api, SqliteScaleOutbox(database), profile, lambda: NOW).cycle(packet)["status"] == "RETRY_PENDING"
        restarted = WarehouseScaleGatewayWorker(api, SqliteScaleOutbox(database), profile, lambda: NOW + 40)
        assert restarted.cycle()["status"] == "ARCHIVED"
        assert restarted.cycle()["status"] == "WAITING_FOR_VENDOR_PACKET"
    assert received == [packet, packet]


@pytest.mark.parametrize("field,value", [("warehouse_id", 2), ("stock_posted", True),
    ("case_content_version", 4), ("weight_kg", "12.346"), ("source_sha256", "A"*64),
    ("case_line_id", 99), ("sample_count", True), ("device_policy_version", True)])
def test_wrong_ack_never_completes_delivery(tmp_path, field, value):
    profile, packet, ack = vector()
    ack[field] = value
    class Api:
        def post_capture(self, body):
            return json.dumps(ack).encode()
    box = SqliteScaleOutbox(tmp_path / "box.sqlite")
    worker = WarehouseScaleGatewayWorker(Api(), box, profile, lambda: NOW)
    assert worker.cycle(packet) == {"status": "RETRY_PENDING", "error": "WAREHOUSE_CAPTURE_ACK_INVALID"}
    assert box.claim(NOW + 3).body == packet


def test_new_stale_packet_body_conflict_and_store_dto_do_not_send(tmp_path):
    profile, packet, _ = vector()
    class Api:
        def post_capture(self, body):
            pytest.fail("No POST permitted")
    box = SqliteScaleOutbox(tmp_path / "box.sqlite")
    with pytest.raises(ScaleGatewayError, match="EXPIRED"):
        WarehouseScaleGatewayWorker(Api(), box, profile, lambda: NOW + 31).cycle(packet)
    assert box.claim(NOW + 100) is None
    box.stage(packet)
    with pytest.raises(ValueError, match="PAYLOAD_CONFLICT"):
        WarehouseScaleGatewayWorker(Api(), box, profile, lambda: NOW).cycle(packet.replace(b'"product1"', b'"changed"'))
    with pytest.raises(ScaleGatewayError, match="PACKET_INVALID"):
        WarehouseScaleGatewayWorker(Api(), box, profile, lambda: NOW).cycle(b'{"device_id":"scale1","load_operation_id":"store"}')


def test_same_identity_different_endpoint_body_is_conflict(tmp_path):
    box = SqliteScaleOutbox(tmp_path / "box.sqlite")
    _, pick, _ = vector("PICK")
    _, final, _ = vector("FINAL_GROSS")
    box.stage(pick)
    with pytest.raises(ValueError, match="PAYLOAD_CONFLICT"):
        box.stage(final)


def test_final_ack_wrong_tare_or_derived_net_is_rejected():
    profile, packet, ack = vector("FINAL_GROSS")
    validate_warehouse_ack(packet, json.dumps(ack).encode(), profile)
    for patch in (dict(tare_capture_key="C"*64), dict(net_weight_kg="1"), dict(composition_signature="bad")):
        with pytest.raises(ScaleGatewayError, match="ACK_INVALID"):
            validate_warehouse_ack(packet, json.dumps({**ack, **patch}).encode(), profile)


def test_non_loopback_http_requires_https():
    with pytest.raises(ValueError, match="HTTPS_REQUIRED"):
        HttpWarehouseScaleGateway("http://warehouse.example", "sender", "secret", allow_loopback_http=True)


@pytest.mark.parametrize("code,expected", [(302, "SUSPENDED"), (401, "SUSPENDED"), (409, "SUSPENDED"), (503, "RETRY_PENDING")])
def test_http_rejection_classification_and_no_redirect_follow(tmp_path, code, expected):
    profile, packet, _ = vector()
    calls = []
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *args):
            pass
        def do_POST(self):
            calls.append(self.path)
            self.rfile.read(int(self.headers["Content-Length"]))
            self.send_response(code)
            self.send_header("Location", "http://127.0.0.1:1/credential-leak")
            self.end_headers()
    with server(Handler) as origin:
        api = HttpWarehouseScaleGateway(origin, "sender", "secret", allow_loopback_http=True)
        worker = WarehouseScaleGatewayWorker(api, SqliteScaleOutbox(tmp_path / "queue.sqlite"), profile, lambda: NOW)
        result = worker.cycle(packet)
    assert result == {"status": expected, "error": "SCALE_HTTP_" + str(code)}
    assert len(calls) == 1


def test_queued_retry_retains_original_policy_and_calibration_after_reconfiguration(tmp_path):
    profile, packet, ack = vector()
    box = SqliteScaleOutbox(tmp_path / "queue.sqlite")
    box.stage(packet)
    changed = profile.model_copy(update=dict(device_policy_version=9, calibration_ref="new"))
    class Api:
        def post_capture(self, body):
            assert body == packet
            return json.dumps(ack).encode()
    assert WarehouseScaleGatewayWorker(Api(), box, changed, lambda: NOW + 40).cycle(packet)["status"] == "ARCHIVED"
