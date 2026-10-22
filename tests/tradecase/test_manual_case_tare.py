"""Manual input stays distinct from device packets and retains uncertain commands."""
from types import SimpleNamespace
from contextlib import contextmanager
import oracledb
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from api.wms_api_server.app.modules.inventory.api import warehouse_scale_routes as routes
from api.wms_api_server.app.modules.inventory.contracts_warehouse_scale import WarehouseScaleError

BODY=dict(operation_id="MANUAL.ORIGINAL",expected_content_version=2,scan_container="SSCC",tare_weight_kg="0.1",measurement_ref="Record1")


def client(command):
    app=FastAPI();app.include_router(routes.router)
    app.dependency_overrides[routes.get_current_user]=lambda:SimpleNamespace(username="worker")
    app.dependency_overrides[routes.warehouse_scale_service]=lambda:SimpleNamespace(manual_tare=command)
    return TestClient(app)


def test_manual_tare_has_no_device_packet_or_stock_command():
    calls=[]
    def record(*args):calls.append(args);return dict(operation_id=args[1].operation_id,origin="MANUAL_CONFIRMED",stock_changed=False)
    response=client(record).post("/api/inventory/warehouse-scales/tasks/1/manual-empty-tare",json=BODY)
    assert response.status_code==200 and response.json()["stock_changed"]is False
    assert calls[0][0]==1 and calls[0][1].model_dump()==BODY and calls[0][2]=="worker"


@pytest.mark.parametrize("status,message",[(403,"CURRENT_OWNER_FORBIDDEN"),(409,"MANUAL_TARE_OPERATION_CONFLICT"),(503,"OUTCOME_UNCERTAIN")])
def test_unknown_or_forbidden_replay_keeps_original_operation(status,message):
    def rejected(*args):raise WarehouseScaleError("REJECTED",message,status)
    r=client(rejected).post("/api/inventory/warehouse-scales/tasks/1/manual-empty-tare",json=BODY)
    assert r.status_code==status
    assert r.json()["detail"]["operation_id"]==BODY["operation_id"]
    assert r.json()["detail"]["outcome_confirmed"]is False
    assert r.json()["detail"]["retry_same_operation_id"]is True
    assert "retry_same_capture"not in r.json()["detail"]


@pytest.mark.parametrize("extra",[{"device_id":"X"},{"capture_key":"X"},{"expected_content_version":True},{"tare_weight_kg":"NaN"},{"tare_weight_kg":"-1"}])
def test_manual_packet_cannot_be_substituted_for_electronic_capture(extra):
    def unexpected(*args):pytest.fail("Invalid input reached Oracle")
    assert client(unexpected).post("/api/inventory/warehouse-scales/tasks/1/manual-empty-tare",json={**BODY,**extra}).status_code==422


def test_closed_release_does_not_disprove_a_prior_manual_measurement():
    from api.wms_api_server.app.modules.inventory.infrastructure.warehouse_scales import scale_error
    error=oracledb.DatabaseError(SimpleNamespace(code=20860,message="TASK_METADATA_RELEASE_CLOSED"))
    assert scale_error(error).status==503


def test_closed_release_keeps_label_outcome_unknown_before_cached_lookup():
    from api.wms_api_server.app.modules.inventory.infrastructure.case_labels import CaseLabels
    from api.wms_api_server.app.modules.inventory.contracts_stock import StockPostingError
    class Cursor:
        def var(self,*args):return None
        def callproc(self,name,args=None):
            if name.endswith("clear_plan"):return
            raise oracledb.DatabaseError(SimpleNamespace(code=20860,message="TASK_METADATA_RELEASE_CLOSED"))
    class Gateway:
        @contextmanager
        def transaction(self,purpose):yield Cursor()
    with pytest.raises(StockPostingError)as error:
        CaseLabels(Gateway())._command("RRL_CASE_SSCC_API.issue",1,"{}","worker","ORIGINAL")
    assert error.value.code=="RESULT_UNCERTAIN"and error.value.operation_id=="ORIGINAL"
