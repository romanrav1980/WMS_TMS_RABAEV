"""HTTP contract checks; these observations are test data, not hardware evidence."""
import sys
from copy import deepcopy
from pathlib import Path
from types import SimpleNamespace
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "api/wms_api_server"))
from app.modules.integrations.api.scale_evidence_routes import router
from app.modules.integrations.contracts_scale_evidence import (ScaleEvidence, ScaleEvidenceError,
                                                               scale_evidence_service)
from app.modules.platform.public import get_current_user


def envelope() -> dict:
    stamp = "2026-10-15T10:00:00.000000+00:00"
    def value(data: object, kind: str = "Boolean") -> dict:
        return {"variant_type": kind, "value": data, "status_code": 0,
                "source_timestamp": stamp, "server_timestamp": stamp}
    values = {"current_weight": value({"Gross": "0", "Net": "0", "Tare": "0"}, "ExtensionObject"),
              "stable": value(True), "center_zero": value(True), "overload": value(False),
              "underload": value(False), "tare_mode": value(0, "Int32"),
              "engineering_units": value({"UnitId": 4933453}, "ExtensionObject")}
    return {"protocol_version": "1.0", "device_id": "TEST.DEVICE", "capture_id": "TEST.CAPTURE",
            "capture_kind": "STORE_RECEIPT", "capture_sha256": "A" * 64, "profile_sha256": "B" * 64,
            "station_id": "TEST.STATION", "model_namespace_uri": "http://opcfoundation.org/UA/Scales/V2/",
            "opc_server": {"application_uri": "urn:test:server", "certificate_sha256": "C" * 64},
            "nodes": {key: {"namespace_uri": "urn:test:nodes", "identifier_type": "String", "identifier": key}
                      for key in values}, "zero_observation": {"observed_at": stamp, "values": values},
            "observations": [{"offset_ms": offset, "observed_at": stamp, "values": deepcopy(values)}
                             for offset in (0, 500, 1000, 1500, 2000)]}


class MemoryArchive:
    def __init__(self) -> None:
        self.items: dict = {}
        self.denied = False

    def archive(self, body: ScaleEvidence, actor: str) -> dict:
        if self.denied:
            raise ScaleEvidenceError("OPC_EVIDENCE_CURRENT_SENDER_REQUIRED", 403)
        key = body.capture_kind, body.device_id, body.capture_id
        digest = body.digest()
        if key in self.items and self.items[key]["evidence_sha256"] != digest:
            raise ScaleEvidenceError("OPC_EVIDENCE_PAYLOAD_CONFLICT")
        self.items[key] = {"status": "ARCHIVED", "binding": "PENDING", "evidence_sha256": digest}
        return self.items[key]

    def read(self, kind: str, device: str, capture: str, actor: str) -> dict:
        if self.denied:
            raise ScaleEvidenceError("OPC_EVIDENCE_CURRENT_SENDER_REQUIRED", 403)
        if (kind, device, capture) not in self.items:
            raise ScaleEvidenceError("OPC_EVIDENCE_NOT_FOUND", 404)
        return self.items[kind, device, capture]


@pytest.fixture
def client() -> tuple[TestClient, MemoryArchive]:
    app = FastAPI()
    app.include_router(router)
    service = MemoryArchive()
    app.dependency_overrides[scale_evidence_service] = lambda: service
    app.dependency_overrides[get_current_user] = lambda: SimpleNamespace(username="test-sender")
    return TestClient(app), service


def test_archive_read_exact_retry_and_conflict(client: tuple) -> None:
    http, _ = client
    body = envelope()
    first = http.post("/api/integrations/scale-evidence", json=body)
    assert first.status_code == 200
    assert http.post("/api/integrations/scale-evidence", json=body).json() == first.json()
    params = {key: body[key] for key in ("capture_kind", "device_id", "capture_id")}
    assert http.get("/api/integrations/scale-evidence", params=params).json() == first.json()
    body["profile_sha256"] = "D" * 64
    assert http.post("/api/integrations/scale-evidence", json=body).status_code == 409


@pytest.mark.parametrize("field,update", [("protocol_version", "2.0"), ("capture_kind", "PICK"),
    ("model_namespace_uri", "urn:invented"), ("capture_sha256", "abc"), ("nodes", {}),
    ("observations", []), ("unknown_field", True)])
def test_strict_versioned_shape(client: tuple, field: str, update: object) -> None:
    http, service = client
    body = envelope()
    body[field] = update
    assert http.post("/api/integrations/scale-evidence", json=body).status_code == 422
    assert not service.items


def test_revoked_and_missing(client: tuple) -> None:
    http, service = client
    body = envelope()
    params = {key: body[key] for key in ("capture_kind", "device_id", "capture_id")}
    assert http.get("/api/integrations/scale-evidence", params=params).status_code == 404
    service.denied = True
    assert http.post("/api/integrations/scale-evidence", json=body).status_code == 403
    assert http.get("/api/integrations/scale-evidence", params=params).status_code == 403


def test_bad_raw_quality_is_preserved_for_diagnostics(client: tuple) -> None:
    http, _ = client
    body = envelope()
    body["observations"][0]["values"]["current_weight"]["status_code"] = 2147483648
    body["observations"][0]["values"]["current_weight"]["source_timestamp"] = None
    assert http.post("/api/integrations/scale-evidence", json=body).status_code == 200


def test_envelope_size_and_header(client: tuple) -> None:
    http, _ = client
    assert http.post("/api/integrations/scale-evidence", json=envelope(),
                     headers={"X-Scale-Protocol-Version": "2.0"}).status_code == 422
    body = envelope()
    body["observations"][0]["values"]["current_weight"]["value"] = "x" * 131072
    assert http.post("/api/integrations/scale-evidence", json=body).status_code == 422


def test_assembly_uses_initial_tare_reference_without_fabricated_zero(client: tuple) -> None:
    http, _ = client
    body = envelope()
    body.pop("zero_observation")
    body.update(protocol_version="1.1", capture_kind="WAREHOUSE_ASSEMBLY",
                zero_reference={"session_id": "TEST.SESSION", "step_id": "TEST.STEP",
                                "phase": "AFTER", "tare_capture_key": "D" * 64})
    assert http.post("/api/integrations/scale-evidence", json=body).status_code == 422
    headers = {"X-Scale-Protocol-Version": "1.1"}
    assert http.post("/api/integrations/scale-evidence", json=body, headers=headers).status_code == 200
    body["zero_observation"] = envelope()["zero_observation"]
    assert http.post("/api/integrations/scale-evidence", json=body, headers=headers).status_code == 422


def test_original_v1_canonical_bytes_are_unchanged() -> None:
    import json
    body = envelope()
    old_bytes = json.dumps(body, ensure_ascii=True, sort_keys=True, separators=(",", ":")).encode()
    assert ScaleEvidence.model_validate(body).canonical_bytes() == old_bytes



def test_reconciliation_has_distinct_protocol_and_identity(client: tuple) -> None:
    http, _ = client
    body = envelope()
    body.pop("zero_observation")
    body.update(protocol_version="1.2", capture_kind="WAREHOUSE_ASSEMBLY_RECON",
        zero_reference=dict(session_id="TEST.S", step_id="TEST.T", phase="RECONCILE",
                            tare_capture_key="D"*64, reconciliation_id="TEST.REC"))
    headers = {"X-Scale-Protocol-Version": "1.2"}
    assert http.post("/api/integrations/scale-evidence", json=body, headers=headers).status_code == 200
    params = {key: body[key] for key in ("capture_kind", "device_id", "capture_id")}
    assert http.get("/api/integrations/scale-evidence", params=params).status_code == 422
    assert http.get("/api/integrations/scale-evidence", params=params, headers=headers).status_code == 200
    body["zero_reference"].pop("reconciliation_id")
    assert http.post("/api/integrations/scale-evidence", json=body, headers=headers).status_code == 422


def test_v11_canonical_bytes_do_not_gain_reconciliation_fields() -> None:
    import json
    from app.modules.integrations.contracts_scale_evidence import AssemblyScaleEvidence
    body = envelope()
    body.pop("zero_observation")
    body.update(protocol_version="1.1", capture_kind="WAREHOUSE_ASSEMBLY",
        zero_reference=dict(session_id="TEST.S", step_id="TEST.T", phase="AFTER", tare_capture_key="D"*64))
    assert AssemblyScaleEvidence.model_validate(body).canonical_bytes() == json.dumps(body, ensure_ascii=True, sort_keys=True, separators=(",", ":")).encode()
