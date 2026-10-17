"""Deny before projections; one snapshot; HTTP identity and task bounds."""
from contextlib import contextmanager
from pathlib import Path
from types import SimpleNamespace
import sys
import oracledb
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'api/wms_api_server'))
from app.modules.inventory.infrastructure.inventory_lot_reads import inventory_lots
from app.modules.inventory.infrastructure.recovery_tasks import RecoveryTasks
from app.modules.inventory.contracts_observations import InventoryObservationError
from app.modules.inventory.api import inventory_count_routes as counts,recovery_routes as queues
from app.modules.platform.public import get_current_user


def rejection(code):
    return oracledb.DatabaseError(SimpleNamespace(code=code))


class Cursor:
    def __init__(self,denied=False):
        self.calls=[];self.denied=denied;self.description=[];self.rows=[]
    def callproc(self,name,args):
        self.calls.append((name,args))
        if self.denied:raise rejection(20882)
    def execute(self,sql,*args,**kwargs):
        self.calls.append((sql,kwargs or args))
        if 'RRL_REMAINS' in sql:
            self.description=[(v,)for v in ['LOT_UID','ARTICLE','CELL','UNIT']]
            self.rows=[('L','A','C','EA')]
        elif 'RRL_SKU_RECEIPT_PROFILE'in sql:
            self.description=[(v,)for v in ['ARTICUL','SYSTEM_CODE','PROFILE_CODE']]
            self.rows=[('A','CRPT','X')]
        elif 'it.INVENTORY_TASK_ID=:task_id'in sql:
            self.description=[('INVENTORY_TASK_ID',),('ASSIGNED_TO',)];self.rows=[(8,'auditor')]
    def fetchall(self):return self.rows


class Gateway:
    def __init__(self,denied=False):self.cursor=Cursor(denied);self.transactions=0
    @contextmanager
    def transaction(self,purpose):
        self.transactions+=1;yield self.cursor


def test_lots_authority_and_profiles_share_one_read_snapshot():
    gateway=Gateway();result=inventory_lots(gateway,4,'C','A','auditor',8)
    assert gateway.transactions==1
    assert gateway.cursor.calls[0][0]=='set transaction read only'
    assert gateway.cursor.calls[1]==('RRL_INVENTORY_TASK_ACCESS.assert_read',['auditor',4,None,8,'C','A'])
    assert result['lots']==[dict(uid='L',article='A',cell='C',unit='EA',marking_profiles=[dict(system_code='CRPT',profile_code='X')])]
    assert 'fetch first 201 rows only'in gateway.cursor.calls[2][0]


def test_denied_scope_never_reads_lots_or_profiles():
    gateway=Gateway(True)
    with pytest.raises(InventoryObservationError)as error:inventory_lots(gateway,4,'FOREIGN','A','auditor',8)
    assert error.value.status==403 and len(gateway.cursor.calls)==2


def test_claim_uses_native_owner_then_returns_inside_same_uow():
    gateway=Gateway();result=RecoveryTasks(gateway).claim_inventory(8,'auditor')
    assert gateway.transactions==1 and gateway.cursor.calls[0]==('RRL_INVENTORY_TASK_ACCESS.claim_task',[8,'auditor'])
    assert result==dict(inventory_task_id=8,assigned_to='auditor')
    assert not any('update RRL_INVENTORY_TASK'in c[0]for c in gateway.cursor.calls)


def test_claim_denial_never_reads_foreign_projection():
    from fastapi import HTTPException
    gateway=Gateway(True)
    with pytest.raises(HTTPException)as error:RecoveryTasks(gateway).claim_inventory(8,'auditor')
    assert error.value.status_code==403 and len(gateway.cursor.calls)==1


def test_http_reads_and_count_use_identity_and_forward_task():
    calls=[]
    class Port:
        def lots(self,*args,**kwargs):calls.append((args,kwargs));return {}
        def count(self,request,actor):calls.append((request.inventory_task_id,actor));return {}
    app=FastAPI();app.include_router(counts.router)
    app.dependency_overrides[get_current_user]=lambda:SimpleNamespace(username='auditor')
    app.dependency_overrides[counts.inventory_observations_service]=lambda:Port()
    with TestClient(app)as client:
        assert client.get('/api/inventory/stock-posting/inventory/4/lots?cell=C&article=A&inventory_task_id=8').status_code==200
        assert client.post('/api/inventory/stock-posting/inventory/counts',json=dict(operation_id='O',revision_id=4,reason='Test',inventory_task_id=8,counts=[])).status_code==200
    assert calls==[((4,'C','A','auditor'),dict(task_id=8)),(8,'auditor')]


@pytest.mark.parametrize('task',['0','-1','invalid'])
def test_http_claim_rejects_bad_task_before_owner(task):
    app=FastAPI();app.include_router(queues.router)
    app.dependency_overrides[queues.inventory_task_execute]=lambda:SimpleNamespace(username='auditor')
    app.dependency_overrides[queues.recovery_tasks_service]=lambda:None
    with TestClient(app)as client:assert client.post('/api/inventory/tasks/'+task+'/claim').status_code==422


def test_actual_claim_composition_uses_identity():
    from app.main import app
    assert app.dependency_overrides[queues.inventory_task_execute]is get_current_user
