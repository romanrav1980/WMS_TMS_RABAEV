"""Bulk scans select the existing native writer with a server-owned action marker."""
from types import SimpleNamespace
from copy import deepcopy
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from api.wms_api_server.app.modules.transport.api import loading_routes as routes
from api.wms_api_server.app.modules.transport.contracts import TransportLoadingError


BODY=dict(operation_id='BULK.ORIGINAL',identifier='BOX.LEGACY',expected_version=3,
          scan_container='BOX.LEGACY',scan_cell='EXPEDITION',transport_task_id=1,
          scan_vehicle='TRUCK',scan_dock='DOCK',measurements=dict(origin='MANUAL_CONFIRMED',
          content_version=3,gross_weight_kg='10',width_m='0.4',depth_m='0.5',height_m='0.5'))


def client(load):
    app=FastAPI();app.include_router(routes.router)
    app.dependency_overrides[routes.get_current_user]=lambda:SimpleNamespace(username='worker')
    app.dependency_overrides[routes.transport_loading_service]=lambda:SimpleNamespace(load=load)
    return TestClient(app)


def test_whole_and_bulk_keep_same_transport_measurements_and_different_immutable_actions():
    calls=[]
    def load(*args):calls.append(args);return dict(operation_id=args[0],status='LOADED')
    api=client(load);original=deepcopy(BODY)
    assert api.post('/api/transport/loading/confirm',json=BODY).status_code==200
    assert api.post('/api/transport/loading/confirm-bulk-box',json=BODY).status_code==200
    assert BODY==original and calls[0][0:2]==calls[1][0:2]==('BULK.ORIGINAL','BOX.LEGACY')
    before,after=calls[0][2],calls[1][2]
    assert after.pop('bulk_box_scan')is True and before==after
    assert before['loading_context']==dict(transport_task_id=1,scan_vehicle='TRUCK',scan_dock='DOCK',measurements=BODY['measurements'])
    assert calls[0][3]==calls[1][3]=='worker'


@pytest.mark.parametrize('status,code',[(403,'CURRENT_OWNER_FORBIDDEN'),(409,'OPERATION_CONFLICT'),(503,'RESULT_UNCERTAIN')])
def test_bulk_failure_keeps_original_operation_and_unknown_outcome(status,code):
    def rejected(*args):raise TransportLoadingError('STOCK_RULE_REJECTED',code,args[0],status)
    response=client(rejected).post('/api/transport/loading/confirm-bulk-box',json=BODY)
    assert response.status_code==status
    detail=response.json()['detail'];assert detail['operation_id']==BODY['operation_id']
    assert detail['outcome_confirmed']is False and detail['retry_same_operation_id']is True


def test_client_cannot_override_the_native_action_marker():
    def never(*args):pytest.fail('Malformed action marker reached the writer')
    assert client(never).post('/api/transport/loading/confirm-bulk-box',json=dict(BODY,bulk_box_scan=False)).status_code==422
