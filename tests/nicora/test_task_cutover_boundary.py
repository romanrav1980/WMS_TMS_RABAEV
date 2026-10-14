"""The inactive release must never run a legacy physical completion."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/"api/wms_api_server"))
import pytest
from fastapi import HTTPException
from app.modules.inventory.infrastructure.task_completion import complete_existing_task
from app.schemas import WarehouseTaskStatusRequest

class InactiveGateway:
    def __init__(self, state): self.state=state
    def fetch_all(self, sql, params=None):
        assert sql == "select STATE from RRL_STOCK_RELEASE where RELEASE_ID=1"
        return [] if self.state is None else [{"state":self.state}]
    def transaction(self, *args):
        raise AssertionError("Legacy completion may not start")

@pytest.mark.parametrize("state",["PREPARED","CUTOVER",None])
def test_completion_is_closed_until_single_writer_is_active(state):
    with pytest.raises(HTTPException) as caught:
        complete_existing_task(InactiveGateway(state),1,WarehouseTaskStatusRequest(updated_by="admin"),"admin")
    assert caught.value.status_code==503
    assert caught.value.detail=="STOCK_RELEASE_NOT_ACTIVE"
