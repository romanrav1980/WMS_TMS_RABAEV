"""HTTP trust boundary: receiver intent contains no mass and cannot impersonate gateway."""
from types import SimpleNamespace
import oracledb
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from api.wms_api_server.app.modules.delivery.api.store_scale_request_routes import router
from api.wms_api_server.app.modules.delivery.contracts_scale_requests import store_scale_requests_service
from api.wms_api_server.app.modules.delivery.contracts import StoreReceiptError
from api.wms_api_server.app.modules.delivery.infrastructure.store_scale_requests import request_failure
from api.wms_api_server.app.modules.platform.public import AdminUser, get_current_user

BODY = dict(request_id="intent.1", device_id="scale.1", load_operation_id="load.1",
            store_address="Store 1", expected_composition_signature="A" * 64)


@pytest.fixture
def client():
    app = FastAPI()
    app.include_router(router)
    calls = []
    class Service:
        def request(self, body, actor):
            calls.append((body, actor))
            if body["request_id"] == "lost":
                raise StoreReceiptError("SCALE_REQUEST_OUTCOME_UNCERTAIN", "lost", 503)
            if body["request_id"] == "conflict":
                raise StoreReceiptError("SCALE_REQUEST_REJECTED", "ORA-20886: WEIGH_REQUEST_PAYLOAD_CONFLICT", 409)
            if body["request_id"] == "busy":
                raise StoreReceiptError("SCALE_REQUEST_REJECTED", "ORA-20886: WEIGH_DEVICE_BUSY", 409)
            return dict(request_id=body["request_id"], state="REQUESTED", capture_key=None)
        def pending(self, device_id, actor):
            calls.append((device_id, actor))
            return {"items": []}
    app.dependency_overrides[store_scale_requests_service] = lambda: Service()
    app.dependency_overrides[get_current_user] = lambda: AdminUser("receiver", "Receiver", "NONE", set())
    with TestClient(app) as value:
        yield value, calls


def test_receiver_needs_identity_not_legacy_admin_permission(client):
    http, calls = client
    response = http.post("/api/delivery/store-scales/requests", json=BODY)
    assert response.status_code == 200
    assert calls == [(BODY, "receiver")]
    assert response.json()["capture_key"] is None


@pytest.mark.parametrize("patch", [dict(gross_weight_kg="10"), dict(actor="gateway"),
                                  dict(expected_composition_signature="bad"), dict(device_id=123)])
def test_browser_cannot_submit_mass_actor_or_malformed_identity(client, patch):
    http, calls = client
    assert http.post("/api/delivery/store-scales/requests", json={**BODY, **patch}).status_code == 422
    assert not calls


def test_unknown_outcome_keeps_original_request_for_retry(client):
    http, _ = client
    response = http.post("/api/delivery/store-scales/requests", json={**BODY, "request_id": "lost"})
    assert response.status_code == 503
    assert response.json()["detail"]["request_id"] == "lost"
    assert response.json()["detail"]["retry_same_request"] is True


def test_protocol_rejection_happens_before_service(client):
    http, calls = client
    response = http.post("/api/delivery/store-scales/requests", json=BODY, headers={"X-Scale-Protocol-Version": "2.0"})
    assert response.status_code == 422 and not calls


@pytest.mark.parametrize("request_id,confirmed,read_before", [("conflict", False, True), ("busy", True, False)])
def test_payload_conflict_never_proves_original_request_rejected(client, request_id, confirmed, read_before):
    http, _ = client
    response = http.post("/api/delivery/store-scales/requests", json={**BODY, "request_id": request_id})
    assert response.status_code == 409
    detail = response.json()["detail"]
    assert detail["request_id"] == request_id and detail["outcome_confirmed"] is confirmed
    assert detail["read_before_retry"] is read_before


def test_receiver_cannot_poll_equipment_inbox(client):
    http, calls = client
    assert http.get("/api/delivery/store-scales/gateway/requests", params={"device_id": "scale.1"}).status_code == 403
    assert not calls


@pytest.mark.parametrize("code,status", [(20882, 403), (20884, 404), (20886, 409), (30006, 503), (3113, 503)])
def test_native_error_classification_preserves_uncertain_network_outcome(code, status):
    error = oracledb.DatabaseError(SimpleNamespace(code=code))
    assert request_failure(error).status == status
