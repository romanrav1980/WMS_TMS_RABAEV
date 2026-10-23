from copy import deepcopy
from hashlib import sha256
import pytest
from pydantic import ValidationError
from api.wms_api_server.app.modules.inventory.contracts_trade_stock import TradeMarkConfirmation,TradeCellPolicy,TradeOwnerGrant
from api.wms_api_server.app.modules.inventory.contracts_trade_planning import TradeOrderBind
from api.wms_api_server.app.modules.integrations.contracts_tradecase import TradeEnvelope
from api.wms_api_server.app.modules.integrations.infrastructure.tradecase_documents import OracleTradecaseDocuments,canonical

def confirmation():
    return dict(operation_id='op',skm_id='L4',external_event_id='biz1',expected_site_version=1,occurred_at='2026-10-19T11:00:00+03:00',items=[dict(physical_unit_key='a'*64,expected_attribute_version=1,verdict='VALID')])

@pytest.mark.parametrize('change',['duplicate','naive','reason','version'])
def test_rejects_unsafe_external_confirmation(change):
    value=confirmation()
    if change=='duplicate':value['items']*=2
    elif change=='naive':value['occurred_at']='2026-10-19T11:00:00'
    elif change=='reason':value['items'][0]['verdict']='REJECTED'
    else:value['expected_site_version']=True
    with pytest.raises(ValidationError):TradeMarkConfirmation.model_validate(value)

def test_rejects_ambiguous_native_line_binding():
    with pytest.raises(ValidationError):TradeOrderBind.model_validate(dict(operation_id='op',expected_order_version=1,customer_order_id=1,lines=[dict(line_id='a',customer_order_row_id=2),dict(line_id='b',customer_order_row_id=2)]))

def test_pick_range_requires_owner():
    with pytest.raises(ValidationError):TradeCellPolicy.model_validate(dict(operation_id='op',expected_version=0,zone_kind='PICK',reason='Configure range'))

def test_operating_grant_requires_visibility():
    with pytest.raises(ValidationError):TradeOwnerGrant.model_validate(dict(operation_id='op',expected_version=0,username='u',owner_id='SNS',can_view=False,can_operate=True,reason='Grant test operation'))

class Capture(OracleTradecaseDocuments):
    def _command(self,procedure,warehouse_id,actor,value):return value

def test_optional_mapping_preserves_unchanged_older_business_hash():
    original=dict(schema_version=1,event_id='e1',source_id='SAP',warehouse_id=1,document_id='A',version=1,occurred_at='2026-10-19T11:00:00+03:00',payload=dict(entity_type='SKU',title='A',base_uom='EA',units_per_box=10,permitted_mrc=['200'],active=True))
    result=Capture(None).receive(TradeEnvelope.model_validate(original),'admin')
    expected={key:original[key]for key in('schema_version','source_id','warehouse_id','document_id','version','payload')}
    assert result['business_hash']==sha256(canonical(expected).encode()).hexdigest()
    assert 'wms_article_id'not in result['payload']


@pytest.mark.parametrize('code,oracle,status,confirmed,retry,conflict', [
    ('REQUEST_DEADLINE', None, 503, False, True, False),
    ('LOCK_RETRY_EXHAUSTED', None, 503, False, True, False),
    ('CONNECTION_UNUSABLE', None, 503, False, True, False),
    ('RESULT_UNCERTAIN', None, 503, False, True, False),
    ('POSTED_CONNECTION_RESET_FAILED', None, 503, False, True, False),
    ('OPERATION_CONTENT_CONFLICT', None, 409, False, False, True),
    ('STOCK_RULE_REJECTED', 20873, 409, False, False, True),
    ('STOCK_RULE_REJECTED', 20886, 409, True, False, False),
    ('STOCK_RULE_REJECTED', 20882, 403, True, False, False),
])
def test_sort_keeps_posting_recovery_outcome(monkeypatch, code, oracle, status, confirmed, retry, conflict):
    from types import SimpleNamespace
    from fastapi import FastAPI
    from fastapi.testclient import TestClient
    from api.wms_api_server.app.modules.inventory.api import trade_stock_routes as routes
    from api.wms_api_server.app.modules.inventory.api.error_handlers import install_stock_error_handlers
    from api.wms_api_server.app.modules.inventory.contracts_stock import StockPostingError
    from api.wms_api_server.app.modules.inventory.infrastructure import trade_sort
    from api.wms_api_server.app.modules.inventory.infrastructure.trade_stock import OracleTradeStock

    class Gateway:
        def fetch_all(self, sql, params):
            return [{'ok': 1}] if 'RRL_ACCESS_API.allowed' in sql else []

    class Posting:
        def post(self, command):
            assert command.command_type == 'INTERNAL_MOVE'
            assert command.operation_id == 'SORT.original'
            assert command.actor == 'sorter'
            assert command.units == ('A' * 64,)
            raise StockPostingError(code, command.operation_id, oracle, 'CURRENT_SORT_RULE')

    monkeypatch.setattr(trade_sort, 'resolve', lambda *a: (('A' * 64,), '1', 'EA'))
    monkeypatch.setattr(trade_sort, 'StockPosting', Posting)
    app = FastAPI(); app.include_router(routes.router); install_stock_error_handlers(app)
    app.dependency_overrides[routes.get_current_user] = lambda: SimpleNamespace(username='sorter')
    app.dependency_overrides[routes.trade_stock_service] = lambda: OracleTradeStock(Gateway())
    response = TestClient(app).post('/api/tradecase/warehouses/1/stock/sort', json={
        'operation_id': 'SORT.original', 'source_pallet': 'OWN', 'source_cell': 'FROM',
        'target_cell': 'TO', 'scans': [{'system_code': 'CRPT', 'profile_code': 'TOBACCO', 'code': 'own-code'}]})
    assert response.status_code == status
    detail = response.json()['detail']
    assert detail['operation_id'] == 'SORT.original'
    assert detail['outcome_confirmed'] is confirmed
    assert detail['retry_same_operation_id'] is retry
    assert detail['operation_id_conflict'] is conflict
    assert detail['reason'] == 'CURRENT_SORT_RULE'
