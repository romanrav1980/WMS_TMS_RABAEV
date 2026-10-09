"""Reuse the existing warehouse physical task for full-pallet wave confirmation."""
import json
from pathlib import Path
out={}
p=Path("api/wms_api_server/app/schemas.py");s=p.read_text(encoding="utf-8")
start=s.index("class PickTaskCompleteRequest(BaseModel):");end=s.index("\n\nclass ",start+1)
part=s[start:end]
assert "fact_qty: float | None" in part
part=part.replace("fact_qty: float | None = Field(default=None, ge=0)","fact_qty: Decimal | None = Field(default=None, ge=0, allow_inf_nan=False)")
part+="\n    operation_id: str | None = Field(default=None, min_length=1, max_length=100)\n"
s=s[:start]+part+s[end:];out[str(p)]=s
p=Path("api/wms_api_server/app/services/picking_service.py");s=p.read_text(encoding="utf-8")
needle='            if types and types[0]["task_type"] == "CASE_PICK":'
assert s.count(needle)==1
endmarker='        rows = self.gateway.fetch_all(\n            """\n            select wt.PICK_WAVE_TASK_ID,'
start=s.index(needle);end=s.index(endmarker,start)
bridge="""            if not types or types[0]["task_type"] != "FULL_PALLET":
                raise HTTPException(409, detail={"code": "PHYSICAL_WAVE_TASK_REQUIRED"})
            physical_tasks = self.gateway.fetch_all(
                "select x.TASK_ID from RRL_WAREHOUSE_TASK x "
                "join RRL_PICK_WAVE_TASK wt on wt.PICK_WAVE_TASK_ID=x.SOURCE_TASK_ID "
                "where wt.PICK_WAVE_ID=:wave and wt.PICK_TASK_ID=:pick "
                "and x.TASK_SOURCE='WAVE' and x.SOURCE_DOC_TYPE='PICK_WAVE' "
                "and x.SOURCE_DOC_ID=:wave and x.TASK_TYPE='PICKING_MOVE' "
                "and x.STATUS<>'CANCELLED' fetch first 2 rows only",
                {"wave": pick_wave_id, "pick": pick_task_id})
            if len(physical_tasks) != 1:
                raise HTTPException(409, detail={"code": "WAVE_STAGING_TASK_REQUIRED",
                    "message": "Release the existing full-pallet staging task before physical confirmation"})
            from ..modules.inventory.infrastructure.task_completion import complete_existing_task
            from ..schemas import WarehouseTaskStatusRequest
            task_id = physical_tasks[0]["task_id"]
            result = complete_existing_task(self.gateway, task_id, WarehouseTaskStatusRequest(
                fact_qty=request.fact_qty, scanned_pallet=request.scanned_pallet,
                scanned_from_cell=request.scanned_from_cell, scanned_to_cell=request.scanned_to_cell,
                operation_id=request.operation_id), actor)
            return {**result, "pick_wave_id": pick_wave_id, "pick_task_id": pick_task_id,
                    "released_minimax_count": 0}
"""
s=s[:end]+bridge+s[end:];out[str(p)]=s
print(json.dumps(out,ensure_ascii=True))
