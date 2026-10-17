"""Provenance ACK must bind exact raw source, not merely return HTTP 200."""
import hashlib
import json
import pytest
from api.wms_api_server.app.modules.integrations.application.scale_evidence_delivery import validate_evidence_ack, deliver_evidence
from api.wms_api_server.app.modules.integrations.infrastructure.scale_outbox import SqliteScaleOutbox
from api.wms_api_server.app.modules.integrations.contracts_scales import ScaleGatewayError


def data():
    source = dict(protocol_version="1.0",device_id="d", capture_id="c", capture_kind="STORE_RECEIPT", capture_sha256="A"*64)
    body = json.dumps(source, sort_keys=True, separators=(",", ":")).encode()
    ack = dict(source, status="ARCHIVED", binding="MATCHED", evidence_sha256=hashlib.sha256(body).hexdigest().upper(),
               stock_posted=False, provenance="GATEWAY_REPORTED")
    return body, ack


@pytest.mark.parametrize("field", ["protocol_version", "device_id", "capture_id", "capture_kind", "capture_sha256", "evidence_sha256", "stock_posted", "provenance", "binding"])
def test_wrong_raw_ack_keeps_original_evidence_retryable(tmp_path, field):
    body, ack = data()
    ack[field] = "wrong"
    box = SqliteScaleOutbox(tmp_path/"raw.sqlite", max_packet_bytes=131072)
    box.stage(body)
    result = deliver_evidence(lambda _:json.dumps(ack).encode(), box, 100)
    assert result["status"] == "EVIDENCE_RETRY_PENDING"
    assert box.claim(103).body == body


def test_raw_128k_option_preserves_old_store_bound_and_accepts_original_pretty_json(tmp_path):
    body, ack = data()
    pretty = json.dumps(json.loads(body), indent=2).encode()
    assert validate_evidence_ack(pretty, json.dumps(ack).encode())["binding"] == "MATCHED"
    large = json.dumps(dict(device_id="d", capture_id="large", raw="x"*70000)).encode()
    with pytest.raises(ValueError, match="SIZE_INVALID"):
        SqliteScaleOutbox(tmp_path/"store.sqlite").stage(large)
    SqliteScaleOutbox(tmp_path/"raw.sqlite", max_packet_bytes=131072).stage(large)
