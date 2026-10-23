"""HTTP count outcomes must agree with the shared stock coordinator recovery contract."""
from types import SimpleNamespace
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from app.modules.inventory.api import inventory_count_routes as routes
from app.modules.inventory.api.error_handlers import install_stock_error_handlers
from app.modules.inventory.contracts_observations import inventory_observations_service
from app.modules.inventory.contracts_stock import StockPostingError


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
def test_count_uses_shared_outcome(code, oracle, status, confirmed, retry, conflict):
    class Service:
        def count(self, request, actor):
            assert request.operation_id == 'COUNT.original'
            assert request.counts[0].quantity == '9007199254740993.000000001'
            assert actor == 'counter'
            raise StockPostingError(code, request.operation_id, oracle)
    app = FastAPI(); app.include_router(routes.router); install_stock_error_handlers(app)
    app.dependency_overrides[routes.get_current_user] = lambda: SimpleNamespace(username='counter')
    app.dependency_overrides[inventory_observations_service] = Service
    response = TestClient(app).post('/api/inventory/stock-posting/inventory/counts', json={
        'operation_id': 'COUNT.original', 'revision_id': 1, 'reason': 'Own error boundary test',
        'counts': [dict(uid='own-lot', cell='own-cell', article='own-article', unit='EA',
                        quantity='9007199254740993.000000001', expected_stock_version=1)]})
    assert response.status_code == status
    detail = response.json()['detail']
    assert detail['operation_id'] == 'COUNT.original'
    assert detail['outcome_confirmed'] is confirmed
    assert detail['retry_same_operation_id'] is retry
    assert detail['operation_id_conflict'] is conflict


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
def test_found_lot_uses_shared_outcome(monkeypatch, code, oracle, status, confirmed, retry, conflict):
    from app.auth import get_current_admin
    from app.modules.inventory.infrastructure import inventory_observations as subject

    class Posting:
        def post(self, command):
            assert command.command_type == 'INVENTORY_REGISTER_LOT'
            assert command.operation_id == 'FOUND.original'
            assert command.actor == 'counter'
            raise StockPostingError(code, command.operation_id, oracle)

    monkeypatch.setattr(subject, 'assert_inventory_scope', lambda *a, **k: None)
    app = FastAPI(); app.include_router(routes.router); install_stock_error_handlers(app)
    app.dependency_overrides[get_current_admin] = lambda: SimpleNamespace(username='counter', permissions={'stock_inventory_count'})
    app.dependency_overrides[inventory_observations_service] = lambda: subject.InventoryObservations(None, Posting())
    response = TestClient(app).post('/api/inventory/stock-posting/inventory/lots', json={
        'operation_id': 'FOUND.original', 'revision_id': 1, 'uid': 'own-found', 'cell': 'own-cell',
        'article': 'own-article', 'quantity': '1', 'price': '200', 'expiry_date': '2027-01-01',
        'reason': 'Own error boundary test'})
    assert response.status_code == status
    detail = response.json()['detail']
    assert detail['operation_id'] == 'FOUND.original'
    assert detail['outcome_confirmed'] is confirmed
    assert detail['retry_same_operation_id'] is retry
    assert detail['operation_id_conflict'] is conflict
