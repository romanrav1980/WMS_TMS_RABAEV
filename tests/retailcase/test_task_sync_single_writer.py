"""Sync retry cannot become another effect executor when release/proof is missing."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/"api/wms_api_server"))
import pytest
from fastapi import HTTPException
from app.services.warehouse_task_domain_sync_service import WarehouseTaskDomainSyncService

class ProofGateway:
    def __init__(self,state):self.state=state;self.reads=0
    def fetch_all(self,sql,params=None):
        self.reads+=1
        if "select STATE" in sql:return []if self.state is None else[{"state":self.state}]
        assert self.state=="ACTIVE"and "o.STATE='APPLIED'"in sql
        return []
    def execute(self,*args):raise AssertionError("Sync may not write any effect")
    def transaction(self,*args):raise AssertionError("Sync may not start an effect transaction")

@pytest.mark.parametrize("state",["PREPARED","CUTOVER",None])
def test_inactive_sync_does_not_run_an_executor(state):
    gateway=ProofGateway(state)
    with pytest.raises(HTTPException)as caught:
        WarehouseTaskDomainSyncService(gateway).retry_task_sync(829,"admin")
    assert caught.value.status_code==503 and gateway.reads==1

def test_active_sync_without_posting_cannot_repair_stock():
    gateway=ProofGateway("ACTIVE")
    with pytest.raises(HTTPException)as caught:
        WarehouseTaskDomainSyncService(gateway).retry_task_sync(829,"admin")
    assert caught.value.status_code==409
    assert caught.value.detail["code"]=="TASK_POSTING_REQUIRED"
    assert gateway.reads==2
