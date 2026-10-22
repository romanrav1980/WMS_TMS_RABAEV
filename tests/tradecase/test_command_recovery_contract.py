"""HTTP callers must retain a possibly committed command after auth/conflict failure."""
from types import SimpleNamespace
from fastapi import FastAPI
from fastapi.testclient import TestClient
import pytest
from api.wms_api_server.app.modules.inventory.api import fullpal_shipment_routes as binding
from api.wms_api_server.app.modules.inventory.api import pallet_floor_routes as floor
from api.wms_api_server.app.modules.inventory.api import warehouse_hu_routes as hu
from api.wms_api_server.app.modules.inventory.contracts_stock import StockPostingError
from api.wms_api_server.app.modules.transport.api import loading_routes as loading
from api.wms_api_server.app.routers import case_pick as case_move
from api.wms_api_server.app.modules.inventory import public as inventory_public
from api.wms_api_server.app.modules.transport.contracts import TransportLoadingError


@pytest.mark.parametrize('area',['floor','binding','loading','hu','case_move','case_return'])
@pytest.mark.parametrize('status,message,confirmed',[(403,'CURRENT_WARE_FORBIDDEN',False),(409,'OPERATION_CONFLICT',False),(503,'RESULT_UNCERTAIN',False),(503,'STOCK_RELEASE_NOT_ACTIVE',False),(409,'INVALID_SCAN',True)])
def test_http_preserves_operation_when_prior_effect_cannot_be_disproved(area,status,message,confirmed,monkeypatch):
    operation='ORIGINAL.OPERATION'
    def rejected(*args,**kwargs):
        if area=='loading':raise TransportLoadingError('STOCK_RULE_REJECTED',message,operation,status)
        raise StockPostingError('STOCK_RELEASE_NOT_ACTIVE'if message=='STOCK_RELEASE_NOT_ACTIVE'else 'RESULT_UNCERTAIN'if status==503 else 'STOCK_RULE_REJECTED',operation,20882 if status==403 else 20886,message)
    service=SimpleNamespace(confirm=rejected,bind=rejected,load_single=rejected,command=rejected,execute=rejected)
    module,dependency,path,body={
        'floor':(floor,floor.pallet_floor_service,'/api/inventory/pallet-floor-types',dict(identifier='LEGACY_PALLET',pallet_type_id=1,expected_version=1,scan_pallet='LEGACY_PALLET',scan_cell='CELL',evidence_reference='Physical inspection')),
        'binding':(binding,binding.fullpal_shipment_service,'/api/warehouse-tasks/1/full-pallet-shipment',dict(shipment_identifier='ST',scanned_pallet='LEGACY_PALLET',expected_stock_version=1)),
        'hu':(hu,hu.warehouse_hu_service,'/api/warehouse-hus/attach',dict(identifier='PARENT',child_uid='CHILD',expected_version=1,expected_child_version=1,scan_container='PARENT',scan_child='CHILD')),
        'case_move':(case_move,None,'/api/case-pick/tasks/1/move-carrier',dict(scan_container='CASE',scanned_to_cell='EXP',expected_content_version=1)),
        'case_return':(case_move,None,'/api/case-pick/tasks/1/return-carrier',dict(scan_container='CASE',destinations={'LOT':'SOURCE'},expected_content_version=1)),
        'loading':(loading,loading.transport_loading_service,'/api/transport/loading/confirm-single',dict(identifier='ST',expected_version=1,expected_composition_signature='A'*64,scan_container='LEGACY_PALLET',scan_cell='CELL',transport_task_id=1,scan_vehicle='V',scan_dock='D',measurements=dict(origin='MANUAL_CONFIRMED',content_version=1,gross_weight_kg='10',width_m='1',depth_m='1',height_m='1'))),
    }[area]
    app=FastAPI();app.include_router(module.router)
    app.dependency_overrides[module.get_current_user]=lambda:SimpleNamespace(username='worker')
    if dependency:app.dependency_overrides[dependency]=lambda:service
    elif area=='case_return':monkeypatch.setattr(inventory_public,'return_existing_case_carrier',rejected)
    else:monkeypatch.setattr(inventory_public,'build_case_carrier_move_service',lambda:service)
    response=TestClient(app).post(path,json=dict(body,operation_id=operation))
    assert response.status_code==status
    detail=response.json()['detail'];assert detail['operation_id']==operation and detail['outcome_confirmed']is confirmed
    if not confirmed:assert detail['retry_same_operation_id']is True
    if area in {'case_move','case_return'}:assert detail['reason']==message
