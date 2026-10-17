"""Reconciliation never calls stock posting; principals and old packet bytes stay explicit."""
from types import SimpleNamespace
import json
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from api.wms_api_server.app.modules.inventory.api.assembly_scale_routes import router as assembly_router
from api.wms_api_server.app.modules.inventory.api.assembly_recovery_routes import router
from api.wms_api_server.app.modules.inventory.contracts_assembly_scale import assembly_scale_service, AssemblyCapture
from api.wms_api_server.app.modules.inventory.contracts_assembly_recovery import AssemblyReconciliationCapture
from api.wms_api_server.app.modules.inventory.infrastructure.assembly_scale import AssemblyScales, wire
from api.wms_api_server.app.modules.platform.public import get_current_user


def packet():
    return dict(session_id="session",step_id="step",capture_id="capture",phase="RECONCILE",reconciliation_id="recon",
        device_id="device",device_policy_version=1,calibration_ref="TEST",unit="KG",basis="GROSS",preset_tare_kg="0",
        tare_mode_clear=True,quality_confirmed=True,measured_at="2026-10-15T12:00:00.000000+00:00",
        samples=[dict(offset_ms=i*500,weight_kg="0.5")for i in range(5)])


def client(service):
    app=FastAPI()
    app.include_router(assembly_router)
    app.include_router(router)
    app.dependency_overrides[get_current_user]=lambda:SimpleNamespace(username="authenticated-picker")
    app.dependency_overrides[assembly_scale_service]=lambda:service
    return TestClient(app)


@pytest.mark.parametrize("confirmation",[False,None,1,"true"])
def test_removal_requires_actual_true_boolean(confirmation):
    response=client(SimpleNamespace()).post("/api/inventory/assembly-scale/reconciliations/recon/authorize",json=dict(
        operation_id="auth",reason="Controller checked goods removal",unaccepted_goods_removed=confirmation))
    assert response.status_code==422


def test_request_and_controller_identity_are_authentication_context():
    called=[]
    service=SimpleNamespace(request_reconciliation=lambda session,body,actor:called.append((session,body.operation_id,actor))or{"state":"REQUESTED"},
        authorize_reconciliation=lambda identity,body,actor:called.append((identity,body.operation_id,actor))or{"state":"AUTHORIZED"})
    api=client(service)
    body=dict(operation_id="recon",step_id="step",expected_content_version=1,reason="Observed discrepancy")
    assert api.post("/api/inventory/assembly-scale/sessions/session/reconciliations",json=body).status_code==200
    assert api.post("/api/inventory/assembly-scale/reconciliations/recon/authorize",json=dict(operation_id="auth",reason="Independent controller review",unaccepted_goods_removed=True)).status_code==200
    assert called==[("session","recon","authenticated-picker"),("recon","auth","authenticated-picker")]
    assert api.post("/api/inventory/assembly-scale/reconciliations/recon/authorize",json=dict(operation_id="auth",reason="Independent controller review",unaccepted_goods_removed=True,controller_id="admin")).status_code==422


def test_reconcile_routes_to_metadata_only_and_keeps_immutable_ack():
    calls=[]
    def forbidden_post(command):
        raise AssertionError("Recovery must not call a goods stock writer")
    service=AssemblyScales(None,forbidden_post)
    def recover(method,args,readonly=False):
        calls.append((method,args,readonly))
        return {"status":"ARCHIVED","phase":"RECONCILE","state":"COMPLETED"}if method=="capture"else{"step":{"state":"CANCELLED"},"session":{"state":"OPEN"}}
    service._recover=recover
    response=client(service).post("/api/inventory/assembly-scale/captures",json=packet())
    assert response.status_code==200,response.text
    result=response.json()
    assert result["archive"]["state"]=="COMPLETED"and result["step"]["state"]=="CANCELLED"and result["posting"]is None
    assert calls[0][0]=="capture"and calls[0][2]is False
    assert calls[1]==("capture_state",["recon","authenticated-picker"],True)
    assert json.loads(calls[0][1][0])["reconciliation_id"]=="recon"


def test_old_before_after_canonical_model_bytes_unchanged():
    old=packet()
    old.pop("reconciliation_id")
    old["phase"]="AFTER"
    assert json.loads(wire(AssemblyCapture(**old)))==old
    assert "reconciliation_id"not in wire(AssemblyCapture(**old))
    with pytest.raises(ValueError):
        AssemblyReconciliationCapture(**old)
    response=client(SimpleNamespace()).post("/api/inventory/assembly-scale/captures",json={**old,"reconciliation_id":"recon"})
    assert response.status_code==422
