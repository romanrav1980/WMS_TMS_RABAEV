"""Operator consent and sender data never choose each other's identity or stock effect."""
from types import SimpleNamespace
import pytest
from pydantic import ValidationError
from fastapi import FastAPI
from fastapi.testclient import TestClient
from api.wms_api_server.app.modules.inventory.api.assembly_scale_routes import router
from api.wms_api_server.app.modules.inventory.contracts_assembly_scale import assembly_scale_service, AssemblyScaleError
from api.wms_api_server.app.modules.inventory.application.assembly_scale_post import deliver_assembly_step
from api.wms_api_server.app.modules.inventory.contracts_stock import StockPostingError
from api.wms_api_server.app.modules.inventory.infrastructure.assembly_scale import AssemblyScales
from api.wms_api_server.app.modules.platform.public import get_current_user


def context():
    return dict(eligible=True, step=dict(step_id="step1", state="READY", stock_posted=False),
        command=dict(operation_id="original.operation", actor="stored-consenting-operator",
            source=dict(case_task_id=1, case_line_id=2), metadata=dict(fact_qty="1", assembly_step_id="step1",
                assembly_consent_id="step1", automation_origin="ASSEMBLY_GATEWAY_AUTO", automation_sender="sender")))


def capture_body():
    return dict(session_id="session1", step_id="step1", capture_id="capture1", phase="AFTER", device_id="device1",
        device_policy_version=1, calibration_ref="cal1", unit="KG", basis="GROSS", preset_tare_kg="0",
        tare_mode_clear=True, quality_confirmed=True, measured_at="2026-10-15T10:00:00.000000+00:00",
        samples=[dict(offset_ms=i*500, weight_kg="1.5") for i in range(5)])


def test_auto_posts_only_the_native_stored_consent_actor_and_original_operation():
    calls = []
    def read(step, caller):
        assert (step, caller) == ("step1", "dedicated-sender")
        return context()
    def post(command):
        calls.append(command)
        return dict(operation_id=command.operation_id, fact_qty="1")
    result = deliver_assembly_step(read, post, "step1", "dedicated-sender")
    assert calls[0].actor == "stored-consenting-operator" and calls[0].operation_id == "original.operation"
    assert calls[0].command_type == "CASE_PICK_CONFIRM" and calls[0].units == ()
    assert result["step"]["state"] == "APPLIED" and result["step"]["stock_posted"] is True


def test_not_ready_and_revoked_operator_never_reach_stock_writer():
    def post(command):
        pytest.fail("Stock posting forbidden")
    assert deliver_assembly_step(lambda *args: dict(eligible=False, step=dict(state="ARMED")),
        post, "step1", "sender")["posting"] is None
    def revoked(*args):
        raise AssemblyScaleError("ASSEMBLY_ASSIGNED_OPERATOR_REQUIRED", "revoked", 403)
    with pytest.raises(AssemblyScaleError) as error:
        deliver_assembly_step(revoked, post, "step1", "sender")
    assert error.value.status == 403


@pytest.mark.parametrize("code,expected", [("RESULT_UNCERTAIN", 503), ("REQUEST_DEADLINE", 503), ("STOCK_RULE_REJECTED", 409)])
def test_post_failure_retains_original_identity_and_archived_state(code, expected):
    def post(command):
        raise StockPostingError(code, command.operation_id)
    with pytest.raises(AssemblyScaleError) as error:
        deliver_assembly_step(lambda *args: context(), post, "step1", "sender")
    assert error.value.status == expected
    assert error.value.details["operation_id"] == "original.operation"
    assert error.value.details["archive_preserved"] and error.value.details["read_before_retry"]


def test_evidence_transaction_completes_before_automatic_post_and_replay_keeps_body():
    from api.wms_api_server.app.modules.inventory.contracts_assembly_scale import AssemblyCapture
    events = []
    class Service(AssemblyScales):
        def _invoke(self, method, arguments, readonly=False):
            if method == "capture":
                events.append(("ARCHIVE_COMMITTED", arguments[0], arguments[1]))
                return dict(status="ARCHIVED", capture_id="capture1", stock_posted=False)
            assert method == "posting_request" and readonly
            return context()
    def post(command):
        assert events[-1][0] == "ARCHIVE_COMMITTED"
        return dict(operation_id=command.operation_id)
    service = Service(None, post)
    body = AssemblyCapture.model_validate(capture_body())
    first = service.capture(body, "sender")
    second = service.capture(body, "sender")
    assert events[0][1:] == events[1][1:]
    assert first["archive"] == second["archive"] and first["step"]["state"] == "APPLIED"


@pytest.fixture
def client():
    app = FastAPI()
    app.include_router(router)
    calls = []
    class Service:
        def capture(self, body, sender):
            calls.append((body.model_dump(), sender))
            return dict(archive=dict(status="ARCHIVED", stock_posted=False), step=dict(state="APPLIED"))
        def open_step(self, session, body, actor):
            calls.append((body.model_dump(), actor))
            if not body.consent_to_auto:
                raise AssemblyScaleError("ASSEMBLY_EXPLICIT_AUTO_CONSENT_REQUIRED", "consent", 409)
            return dict(state="WAITING_BEFORE", step_id=body.step_id)
    app.dependency_overrides[assembly_scale_service] = lambda: Service()
    app.dependency_overrides[get_current_user] = lambda: SimpleNamespace(username="authenticated-identity")
    with TestClient(app) as http:
        yield http, calls


def test_gateway_uses_authenticated_identity_not_business_actor_body(client):
    http, calls = client
    assert http.post("/api/inventory/assembly-scale/captures", json=capture_body()).status_code == 200
    assert calls[0][1] == "authenticated-identity"


@pytest.mark.parametrize("patch", [dict(actor="operator"), dict(gross_weight_kg="999"), dict(quality_confirmed=False),
    dict(tare_mode_clear=None), dict(quality_confirmed=1), dict(tare_mode_clear=1), dict(zero_confirmed=True), dict(phase="PICK"), dict(device_policy_version=True)])
def test_browser_mass_actor_or_wrong_capture_contract_is_rejected(client, patch):
    http, calls = client
    response = http.post("/api/inventory/assembly-scale/captures", json={**capture_body(), **patch})
    assert response.status_code == 422 and not calls


def test_auto_consent_is_not_enabled_by_default(client):
    http, calls = client
    body = dict(step_id="step1", operation_id="original.operation", case_line_id=2, quantity="1",
        scan_source_cell="source", scan_product="product", scan_container="container", expected_content_version=1)
    assert http.post("/api/inventory/assembly-scale/sessions/session1/steps", json=body).status_code == 409
    assert calls[-1][0]["consent_to_auto"] is False
    assert http.post("/api/inventory/assembly-scale/sessions/session1/steps", json={**body, "consent_to_auto": True}).status_code == 200


def test_station_requires_explicit_cumulative_tolerance():
    from api.wms_api_server.app.modules.inventory.contracts_assembly_scale import AssemblyStationPolicy
    body = dict(operation_id="POLICY.TEST", expected_version=0, confirmation_mode="AUTO",
                max_session_seconds=3600, active=True, reason="Explicit test policy")
    with pytest.raises(ValidationError):
        AssemblyStationPolicy(**body)
    assert AssemblyStationPolicy(**body, cumulative_tolerance_kg="0").cumulative_tolerance_kg == "0"
