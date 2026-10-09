import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/"api/wms_api_server"))
from decimal import Decimal
import pytest
from fastapi import HTTPException
from app.schemas import PickTaskCompleteRequest
from app.services.picking_service import PickingService
from app.modules.inventory.infrastructure import task_completion


class Gateway:
    def __init__(self, task_ids, kind="FULL_PALLET"):
        self.task_ids = task_ids
        self.kind = kind

    def fetch_all(self, sql, params=None):
        if "RRL_STOCK_RELEASE" in sql:
            return [{"state": "ACTIVE"}]
        if "left join RRL_CASE_PICK_LINE" in sql:
            return [{"task_type": self.kind}]
        if "RRL_WAREHOUSE_TASK x" in sql:
            return [{"task_id": value} for value in self.task_ids]
        raise AssertionError("Unexpected legacy path: "+sql)

    def execute(self, *args, **kwargs):
        raise AssertionError("A separate metadata completion must never precede posting")


def test_full_pallet_confirmation_preserves_exact_fact_and_retry_id(monkeypatch):
    calls=[]
    def complete(gateway, task_id, request, actor):
        calls.append((task_id,request,actor))
        return {"status": "DONE", "operation_id":request.operation_id}
    monkeypatch.setattr(task_completion,"complete_existing_task",complete)
    service=PickingService(Gateway([17]))
    request=PickTaskCompleteRequest(fact_qty="9007199254740993.000000001",
        operation_id="wave-retry",completed_by="operator",scanned_pallet="legacy-17",
        scanned_from_cell="RACK1",scanned_to_cell="STAGE1")
    result=service.complete_wave_pick_task(8,9,request)
    assert result["operation_id"]=="wave-retry"
    task,posted,actor=calls[0]
    assert task==17 and actor=="operator"
    assert posted.fact_qty==Decimal("9007199254740993.000000001")
    assert posted.scanned_pallet=="legacy-17"
    assert posted.scanned_from_cell=="RACK1" and posted.scanned_to_cell=="STAGE1"


@pytest.mark.parametrize("tasks",[[],[17,18]])
def test_missing_or_ambiguous_physical_task_never_completes_pick(tasks):
    with pytest.raises(HTTPException) as error:
        PickingService(Gateway(tasks)).complete_wave_pick_task(8,9,PickTaskCompleteRequest())
    assert error.value.detail["code"]=="WAVE_STAGING_TASK_REQUIRED"
