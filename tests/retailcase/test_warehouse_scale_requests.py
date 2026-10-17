"""Intent trust boundary, purpose separation and unchanged fenced claim recovery."""
from fastapi import FastAPI
from fastapi.testclient import TestClient
import pytest
from api.wms_api_server.app.modules.inventory.api.warehouse_scale_request_routes import router
from api.wms_api_server.app.modules.inventory.contracts_warehouse_scale_requests import warehouse_weigh_requests_service
from api.wms_api_server.app.modules.inventory.contracts_warehouse_scale import WarehouseScaleError
from api.wms_api_server.app.modules.platform.public import AdminUser, get_current_user

PREFIX = "/api/inventory/warehouse-scales"
BODY = dict(request_id="intent.1", device_id="scale.1", purpose="EMPTY_TARE", case_task_id=1,
            expected_content_version=0, scan_container="INTERNAL.1")


@pytest.fixture
def client():
    app = FastAPI()
    app.include_router(router)
    calls = []

    class Service:
        def request(self, body, actor):
            calls.append((body, actor))
            if body["request_id"] in ("lost", "conflict", "forbidden"):
                status = {"lost": 503, "conflict": 409, "forbidden": 403}[body["request_id"]]
                message = "WH_WEIGH_REQUEST_PAYLOAD_CONFLICT" if status == 409 else "uncertain or forbidden"
                raise WarehouseScaleError("REJECTED", message, status)
            return dict(state="REQUESTED", capture_key=None, stock_posted=False)

        def claim(self, request_id, body, actor):
            calls.append((request_id, body, actor))
            return dict(claim_id=body["claim_id"], capture_context=dict(capture_id=body["claim_id"]))

        def pending(self, device_id, actor):
            calls.append((device_id, actor))
            return dict(items=[])

        def devices(self, task, purpose, actor):
            calls.append((task, purpose, actor))
            return dict(items=[], connectivity="UNKNOWN")

        def zero(self, request_id, body, actor):
            calls.append((request_id, body, actor))
            return dict(receipt=dict(zero_confirmed=True), current=dict(load_allowed=True))

    current = AdminUser("operator", "Operator", "NONE", set())
    app.dependency_overrides[warehouse_weigh_requests_service] = lambda: Service()
    app.dependency_overrides[get_current_user] = lambda: current
    with TestClient(app) as http:
        yield http, calls, current


def test_operator_identity_and_legacy_pallet_identifier(client):
    http, calls, _ = client
    response = http.post(PREFIX + "/requests", json=BODY)
    assert response.status_code == 200 and response.json()["stock_posted"] is False
    assert calls == [(BODY, "operator")]


@pytest.mark.parametrize("patch", [dict(weight_kg="10"), dict(actor="admin"), dict(device_id=1),
                                   dict(purpose="SHIPPING_GROSS"), dict(purpose="PICK"),
                                   dict(tare_capture_key="A" * 64), dict(resource_session_id="123")])
def test_mass_actor_shipping_and_invalid_purpose_fields_rejected(client, patch):
    http, calls, _ = client
    assert http.post(PREFIX + "/requests", json={**BODY, **patch}).status_code == 422
    assert not calls


def test_pick_scans_required_and_final_fields_forbidden(client):
    http, calls, _ = client
    pick = {**BODY, "purpose": "PICK", "case_line_id": 2, "scan_source_cell": "A1", "scan_product": "SKU1"}
    assert http.post(PREFIX + "/requests", json=pick).status_code == 200
    assert calls[0][0] == pick
    assert http.post(PREFIX + "/requests", json={**pick, "expected_composition_signature": "A" * 64}).status_code == 422


def test_final_requires_measured_tare_and_composition(client):
    http, calls, _ = client
    final = {**BODY, "purpose": "FINAL_GROSS", "tare_capture_key": "A" * 64, "expected_composition_signature": "B" * 64}
    assert http.post(PREFIX + "/requests", json=final).status_code == 200
    assert calls[0][0] == final
    assert http.post(PREFIX + "/requests", json={**final, "resource_session_id": 1}).status_code == 422


@pytest.mark.parametrize("request_id,status,read_before", [("lost", 503, True), ("conflict", 409, True), ("forbidden", 403, False)])
def test_unknown_conflicting_and_forbidden_results_never_prove_new_rejection(client, request_id, status, read_before):
    http, _, _ = client
    response = http.post(PREFIX + "/requests", json={**BODY, "request_id": request_id})
    assert response.status_code == status
    detail = response.json()["detail"]
    assert detail["request_id"] == request_id and detail["outcome_confirmed"] is False
    assert detail["read_before_retry"] is read_before


def test_operator_cannot_claim_or_poll_sender_inbox(client):
    http, calls, _ = client
    assert http.get(PREFIX + "/gateway/requests", params={"device_id": "scale.1"}).status_code == 403
    assert http.post(PREFIX + "/gateway/requests/intent.1/claim", json=dict(claim_id="claim.1", device_id="scale.1")).status_code == 403
    assert not calls


def test_sender_retries_exact_claim_body_and_capture_id(client):
    http, calls, actor = client
    actor.permissions.add("warehouse_scale_ingest")
    body = dict(claim_id="stable.claim", device_id="scale.1")
    first = http.post(PREFIX + "/gateway/requests/intent.1/claim", json=body)
    second = http.post(PREFIX + "/gateway/requests/intent.1/claim", json=body)
    assert first.status_code == second.status_code == 200
    assert first.json()["capture_context"]["capture_id"] == body["claim_id"]
    assert calls == [("intent.1", body, "operator")] * 2


def test_protocol_version_rejected_before_service_and_catalog_never_infers_connection(client):
    http, calls, _ = client
    assert http.post(PREFIX + "/requests", json=BODY, headers={"X-Scale-Protocol-Version": "2.0"}).status_code == 422
    assert not calls
    response = http.get(PREFIX + "/devices", params=dict(case_task_id=1, purpose="EMPTY_TARE"))
    assert response.status_code == 200 and response.json()["connectivity"] == "UNKNOWN"


def test_zero_progress_is_optional_and_legacy_request_wire_stays_unchanged(client):
    from api.wms_api_server.app.modules.inventory.contracts_warehouse_scale_requests import WarehouseWeighRequest
    from api.wms_api_server.app.modules.inventory.infrastructure.warehouse_scale_requests import WarehouseWeighRequests
    assert WarehouseWeighRequests._wire(WarehouseWeighRequest.model_validate(BODY).model_dump(exclude_none=True)) == WarehouseWeighRequests._wire(BODY)
    http, calls, _ = client
    assert http.post(PREFIX + "/requests", json={**BODY, "zero_progress_required": True}).status_code == 200
    assert calls[-1][0]["zero_progress_required"] is True
    assert http.post(PREFIX + "/requests", json={**BODY, "zero_progress_required": "true"}).status_code == 422
    for value in (False, 0, 1):
        assert http.post(PREFIX + "/requests", json={**BODY, "zero_progress_required": value}).status_code == 422


def test_zero_signal_is_sender_only_and_rejects_loaded_mass_or_actor(client):
    http, calls, actor = client
    path = PREFIX + "/gateway/requests/intent.1/zero-confirmed"
    body = dict(claim_id="claim1", device_id="scale1", zero_observed_at="2026-10-15T10:00:00Z",
                zero_source_sha256="A"*64, zero_evidence_json="{}", profile_sha256="B"*64,
                unit_namespace_uri="units", kg_unit_id=17, no_tare_mode=0)
    assert http.post(path, json=body).status_code == 403
    actor.permissions.add("warehouse_scale_ingest")
    assert http.post(path, json={**body, "weight_kg": "9"}).status_code == 422
    assert http.post(path, json={**body, "actor": "admin"}).status_code == 422
    assert http.post(path, json=body, headers={"X-Scale-Protocol-Version": "2.0"}).status_code == 422
    assert not calls
    assert http.post(path, json=body).status_code == 200
    assert calls == [("intent.1", body, "operator")]
