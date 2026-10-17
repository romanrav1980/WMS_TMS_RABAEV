"""HTTP identity and database scope boundary; native row filtering is tested live separately."""
from contextlib import contextmanager
from pathlib import Path
import sys
import pytest
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parents[2]/'api/wms_api_server'))
from app.modules.inventory.api import recovery_routes as routes
from app.modules.inventory.infrastructure.recovery_tasks import RecoveryTasks


class Cursor:
    def __init__(self, allowed=True):
        self.allowed = allowed
        self.calls = []
        self.description = [('WAREHOUSE_ID',), ('SHORT_ID',)]

    def execute(self, sql, **binds):
        self.calls.append((sql, binds))

    def fetchone(self):
        return (7,) if self.allowed else None

    def fetchall(self):
        return [(7, 12)]


class Gateway:
    def __init__(self, allowed=True):
        self.cursor = Cursor(allowed)
        self.transactions = 0

    @contextmanager
    def transaction(self, _):
        self.transactions += 1
        yield self.cursor


@pytest.mark.parametrize('warehouse', [None, 7])
@pytest.mark.parametrize('kind', ['inventory', 'recovery'])
def test_denial_before_document_projection(kind, warehouse):
    g = Gateway(False)
    method = getattr(RecoveryTasks(g), 'list_'+kind)
    with pytest.raises(HTTPException) as error:
        method(50, actor='role-only', ware_id=warehouse)
    assert error.value.status_code == 403
    assert len(g.cursor.calls) == 2
    assert g.cursor.calls[0][0] == 'set transaction read only'
    assert g.transactions == 1


@pytest.mark.parametrize('kind,permission,source', [
    ('inventory', 'inventory_task_view', 'it.WARE_ID'),
    ('recovery', 'case_pick_view', 'w.WARE_ID'),
])
@pytest.mark.parametrize('warehouse', [None, 7])
def test_actor_and_ware_predicates_precede_limit_even_when_ware_omitted(kind, permission, source, warehouse):
    g = Gateway()
    result = getattr(RecoveryTasks(g), 'list_'+kind)(50, actor='role-only', ware_id=warehouse)
    assert result == [{'warehouse_id': 7, 'short_id': 12}]
    sql, binds = g.cursor.calls[-1]
    assert binds['actor'] == 'role-only' and binds['ware'] == warehouse and binds['row_limit'] == 50
    assert sql.index('RRL_ACCESS_API.allowed') < sql.index('rownum<=:row_limit')
    assert source in sql and permission in sql
    assert "RRL_HAS_WRIGHT" not in sql
    if kind == 'inventory':
        assert "where ((:task_id" in sql and binds['task_id'] is None


@pytest.fixture
def client():
    class User:
        username = 'role-only'
    class Port:
        def __init__(self): self.calls = []
        def list_inventory(self, limit, task_id=None, **kwargs):
            self.calls.append(('inventory', limit, task_id, kwargs)); return []
        def list_recovery(self, limit, **kwargs):
            self.calls.append(('recovery', limit, kwargs)); return []
    app = FastAPI(); port = Port(); app.include_router(routes.router)
    app.dependency_overrides[routes.inventory_task_view] = User
    app.dependency_overrides[routes.recovery_view] = User
    app.dependency_overrides[routes.recovery_tasks_service] = lambda: port
    with TestClient(app) as c: yield c, port


def test_http_passes_identity_and_selected_warehouse(client):
    c, port = client
    assert c.get('/api/inventory/tasks?ware_id=7&task_id=9&limit=1').status_code == 200
    assert c.get('/api/inventory/recovery-shorts?ware_id=7').status_code == 200
    assert port.calls == [('inventory', 1, 9, {'actor':'role-only', 'ware_id':7}),
                          ('recovery', 50, {'actor':'role-only', 'ware_id':7})]


@pytest.mark.parametrize('query', ['ware_id=0', 'ware_id=-1', 'ware_id=1or1', 'limit=101'])
def test_invalid_http_bounds_never_reach_port(client, query):
    c, port = client
    assert c.get('/api/inventory/recovery-shorts?'+query).status_code == 422
    assert port.calls == []


def test_main_wiring_uses_identity_for_read_only_not_flat_permissions():
    # Importing the actual app catches missing composition imports too; no Oracle call.
    from app.main import app
    from app.modules.platform.public import get_current_user
    assert app.dependency_overrides[routes.inventory_task_view] is get_current_user
    assert app.dependency_overrides[routes.recovery_view] is get_current_user
