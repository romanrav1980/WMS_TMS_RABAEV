"""Pool HTTP outcomes preserve recovery of the original stock operation."""
from types import SimpleNamespace
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from app.modules.inventory.api import pool_routes as routes
from app.modules.inventory.api.error_handlers import install_stock_error_handlers
from app.modules.inventory.contracts_stock import StockPostingError
from app.modules.inventory.infrastructure import pool_service


@pytest.mark.parametrize('code,oracle,status,confirmed,retry,conflict', [
    ('REQUEST_DEADLINE', None, 503, False, True, False),
    ('POSTED_CONNECTION_RESET_FAILED', None, 503, False, True, False),
    ('RESULT_UNCERTAIN', None, 503, False, True, False),
    ('OPERATION_CONTENT_CONFLICT', None, 409, False, False, True),
    ('STOCK_RULE_REJECTED', 20873, 409, False, False, True),
    ('STOCK_RULE_REJECTED', 20886, 409, True, False, False),
    ('STOCK_RULE_REJECTED', 20882, 403, True, False, False),
])
def test_pool_uses_shared_outcome(monkeypatch, code, oracle, status, confirmed, retry, conflict):
    def post(self, command):
        assert command.operation_id == 'POOL.original'
        assert command.actor == 'planner'
        assert command.source == {'type': 'DEMAND_POOL', 'warehouse': 123, 'article': 'SKU'}
        raise StockPostingError(code, command.operation_id, oracle)
    monkeypatch.setattr(pool_service.StockPosting, 'post', post)
    app = FastAPI(); app.include_router(routes.router); install_stock_error_handlers(app)
    app.dependency_overrides[routes.pool_edit] = lambda: SimpleNamespace(username='planner')
    app.dependency_overrides[routes.pool_service] = lambda: pool_service.PoolService(None)
    response = TestClient(app).post('/api/inventory/soft-pools/123/SKU/allocate',
                                    json={'operation_id': 'POOL.original'})
    assert response.status_code == status
    detail = response.json()['detail']
    assert detail['operation_id'] == 'POOL.original'
    assert detail['outcome_confirmed'] is confirmed
    assert detail['retry_same_operation_id'] is retry
    assert detail['operation_id_conflict'] is conflict
