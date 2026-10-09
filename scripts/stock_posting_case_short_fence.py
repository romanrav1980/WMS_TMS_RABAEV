"""Prevent shortage metadata from inventing or erasing physical picked facts."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];files={}
def edit(path,old,new):
 text=files.get(path,(ROOT/path).read_text(encoding="utf-8"))
 if text.count(old)!=1:raise RuntimeError("Missing unique anchor "+path)
 files[path]=text.replace(old,new,1)
path="db/migrations/2026-10-08_stock_posting_core/142_metadata_fence.sql"
edit(path,"not in('warehouse_task_assign','warehouse_task_edit')","not in('warehouse_task_assign','warehouse_task_edit','case_pick_execute','case_pick_short_approve')")
path="api/wms_api_server/app/modules/inventory/public.py"
files[path]=(ROOT/path).read_text(encoding="utf-8")+"""

def warehouse_metadata_transaction(gateway, purpose: str, actor: str, permission: str):
    from .infrastructure.metadata_transactions import receipt_task_metadata
    return receipt_task_metadata(gateway, purpose, actor, permission)
"""
path="api/wms_api_server/app/services/case_pick_service.py"
edit(path,"""    def short_line(self, case_pick_task_id: int, line_id: int, request: CasePickLineShortRequest) -> dict[str, Any]:
        actor = request.actor or "TSD"
        line = self._line_for_update(case_pick_task_id, line_id)""","""    def short_line(self, case_pick_task_id: int, line_id: int, request: CasePickLineShortRequest) -> dict[str, Any]:
        from decimal import Decimal
        from ..modules.inventory.public import warehouse_metadata_transaction
        from ..transaction_gateway import TransactionGateway
        state = self.gateway.fetch_all("select STATE from RRL_STOCK_RELEASE where RELEASE_ID=1")
        if state and state[0]["state"] == "PREPARED":
            return self._short_line_locked(case_pick_task_id, line_id, request)
        with warehouse_metadata_transaction(self.gateway, "CASE shortage metadata", request.actor, "case_pick_execute") as cursor:
            bound = TransactionGateway(cursor)
            bound.fetch_all("select CASE_PICK_TASK_ID from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=:id for update",
                {"id": case_pick_task_id})
            rows = bound.fetch_all("select to_char(PICKED_QTY,'TM9','NLS_NUMERIC_CHARACTERS=''.,''') POSTED_QTY from RRL_CASE_PICK_LINE where CASE_PICK_TASK_ID=:task and CASE_PICK_LINE_ID=:line for update",
                {"task": case_pick_task_id, "line": line_id})
            if not rows:
                raise HTTPException(404, detail="Case line not found")
            confirmed = Decimal(str(rows[0]["posted_qty"] or "0"))
            if Decimal(str(request.picked_qty or 0)) != confirmed:
                raise HTTPException(409, detail={"code": "CASE_SHORT_PICKED_FACT_MUST_BE_POSTED",
                    "message": "Confirm actually picked quantity before reporting the remaining shortage"})
            return CasePickService(bound)._short_line_locked(case_pick_task_id, line_id, request)

    def _short_line_locked(self, case_pick_task_id: int, line_id: int, request: CasePickLineShortRequest) -> dict[str, Any]:
        actor = request.actor or "TSD"
        line = self._line_for_update(case_pick_task_id, line_id)""")
# Exact metadata quantities too; callers cannot overwrite confirmed fact with a rounded float.
edit(path,"""        planned_qty = float(line.get("planned_qty") or 0)
        picked_qty = float(request.picked_qty or 0)
        short_qty = float(request.short_qty if request.short_qty is not None else max(planned_qty - picked_qty, 0))""","""        from decimal import Decimal
        planned_qty = Decimal(str(line.get("planned_qty") or 0))
        picked_qty = Decimal(str(request.picked_qty or 0))
        short_qty = Decimal(str(request.short_qty)) if request.short_qty is not None else max(planned_qty - picked_qty, Decimal(0))
        if picked_qty < 0 or short_qty <= 0 or picked_qty + short_qty > planned_qty:
            raise HTTPException(422, detail="Invalid picked/short quantity")""")
path="api/wms_api_server/app/schemas.py"
edit(path,"""class CasePickLineShortRequest(BaseModel):
    picked_qty: float | None = Field(default=None, ge=0)
    short_qty: float | None = Field(default=None, ge=0)""","""class CasePickLineShortRequest(BaseModel):
    picked_qty: Decimal | None = Field(default=None, ge=0, max_digits=27, decimal_places=9)
    short_qty: Decimal | None = Field(default=None, ge=0, max_digits=27, decimal_places=9)""")
path="api/wms_api_server/app/modules/inventory/infrastructure/case_pick_commands.py"
edit(path,'    source = {"case_task_id": task_id, "case_line_id": line_id}',
 """    if len(json.dumps(submitted, ensure_ascii=True).encode()) > 2 * 1024 * 1024:
        raise ValueError("CASE scan payload exceeds 2 MiB")
    source = {"case_task_id": task_id, "case_line_id": line_id}""")
# Retain error information for durable frontend replay.
path="wiki-raw/wms_admin_ui_reference/case-pick-tsd.js"
text=(ROOT/path).read_text(encoding="utf-8")
files[path]=text
print(json.dumps(files,ensure_ascii=True))
