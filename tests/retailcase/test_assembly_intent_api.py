"""Intent cancellation cannot select another actor or claim that created work was cancelled."""
from types import SimpleNamespace
from fastapi import FastAPI
from fastapi.testclient import TestClient
from api.wms_api_server.app.modules.inventory.api.assembly_intent_routes import router
from api.wms_api_server.app.modules.inventory.contracts_assembly_intents import assembly_intent_service
from api.wms_api_server.app.modules.inventory.contracts_assembly_scale import AssemblyScaleError
from api.wms_api_server.app.modules.platform.public import get_current_user


def request_body():
    return dict(operation_id="cancel.original",kind="OPEN_STEP",session_id="session.original",reason="Correct the mistyped scan",original=dict(step_id="step.original",operation_id="pick.original",case_line_id=1,quantity="1",scan_source_cell="wrong",scan_product="SKU",scan_container="carrier",expected_content_version=2,consent_to_auto=False))


def client(service):
    app=FastAPI();app.include_router(router)
    app.dependency_overrides[get_current_user]=lambda:SimpleNamespace(username="actual.operator")
    app.dependency_overrides[assembly_intent_service]=lambda:service
    return TestClient(app)


def test_exact_original_body_is_forwarded_with_authenticated_actor():
    calls=[]
    class Owner:
        def abandon(self,body,actor):
            calls.append((body.model_dump(),actor))
            return dict(status="ABANDONED",operation_id=body.operation_id,kind=body.kind,original=body.original.model_dump(),stock_posted=False)
    body=request_body();http=client(Owner())
    assert http.post("/api/inventory/assembly-scale/abandonments",json=body).json()["stock_posted"] is False
    assert calls==[(body,"actual.operator")]


def test_browser_actor_and_malformed_original_are_rejected_before_owner():
    class Owner:
        def abandon(self,*args):
            raise AssertionError("Invalid input reached owner")
    http=client(Owner());body=request_body()
    assert http.post("/api/inventory/assembly-scale/abandonments",json={**body,"actor":"admin"}).status_code==422
    body["original"]["actor"]="admin"
    assert http.post("/api/inventory/assembly-scale/abandonments",json=body).status_code==422


def test_created_native_step_refusal_is_not_presented_as_abandoned():
    class Owner:
        def abandon(self,*args):
            raise AssemblyScaleError("ASSEMBLY_INTENT_EXISTS_READ_OR_RECONCILE_REQUIRED","Existing step requires reconciliation",409)
    result=client(Owner()).post("/api/inventory/assembly-scale/abandonments",json=request_body())
    assert result.status_code==409 and "ABANDONED" not in result.text


def test_no_fabricated_session_or_mass_for_missing_result():
    class Owner:
        def read(self,*args):
            raise AssemblyScaleError("ASSEMBLY_INTENT_NOT_FOUND","No saved result is visible",404)
    assert client(Owner()).get("/api/inventory/assembly-scale/abandonments/cancel.original").status_code==404
