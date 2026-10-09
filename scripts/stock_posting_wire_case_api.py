"""Emit existing CASE API bridge and immutable, exact request fields."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];files={}
def edit(path,old,new):
 text=files.get(path,(ROOT/path).read_text(encoding="utf-8"))
 if text.count(old)!=1:raise RuntimeError("Missing unique anchor "+path)
 files[path]=text.replace(old,new,1)
path="api/wms_api_server/app/schemas.py"
edit(path,"""class CasePickLineConfirmRequest(BaseModel):
    fact_qty: float | None = Field(default=None, ge=0)""","""class CasePickUnitScan(BaseModel):
    system_code: str = Field(min_length=1, max_length=40)
    profile_code: str = Field(min_length=1, max_length=60)
    code: str = Field(min_length=1, max_length=4000)


class CasePickLineConfirmRequest(BaseModel):
    fact_qty: Decimal | None = Field(default=None, ge=0, max_digits=27, decimal_places=9)
    operation_id: str | None = Field(default=None, min_length=1, max_length=100)
    unit_keys: list[str] = Field(default_factory=list, max_length=10000)
    unit_scans: list[CasePickUnitScan] = Field(default_factory=list, max_length=10000)""")
path="api/wms_api_server/app/modules/inventory/public.py"
text=(ROOT/path).read_text(encoding="utf-8")
files[path]=text+"""

def post_existing_case_pick(gateway, task_id: int, line_id: int, request):
    from .infrastructure.case_pick_commands import post_case_pick
    return post_case_pick(gateway, task_id, line_id, request)
"""
path="api/wms_api_server/app/services/case_pick_service.py"
edit(path,"""        actor = request.actor or "TSD"
        line = self._line_for_update(case_pick_task_id, line_id)
        if request.offline_event_id and self._offline_event_exists(request.offline_event_id):
            return {"status": line.get("status"), "idempotent": True}
        self._validate_line_scan(line, request)""","""        from ..modules.inventory.public import post_existing_case_pick
        from ..modules.inventory.contracts_stock import StockPostingError
        try:
            posted = post_existing_case_pick(self.gateway, case_pick_task_id, line_id, request)
        except ValueError as exc:
            raise HTTPException(422, detail={"code": "CASE_COMMAND_INVALID", "message": str(exc)}) from exc
        except StockPostingError as exc:
            uncertain = exc.code in {"RESULT_UNCERTAIN", "REQUEST_DEADLINE", "CONNECTION_UNUSABLE", "LOCK_RETRY_EXHAUSTED", "STOCK_RELEASE_NOT_ACTIVE"}
            raise HTTPException(503 if uncertain else 409, detail={"code": exc.code,
                "operation_id": exc.operation_id, "oracle_code": exc.oracle_code,
                "outcome_confirmed": not uncertain, "retry_same_operation_id": uncertain}) from exc
        if posted is not None:
            return posted
        actor = request.actor or "TSD"
        line = self._line_for_update(case_pick_task_id, line_id)
        if request.offline_event_id and self._offline_event_exists(request.offline_event_id):
            return {"status": line.get("status"), "idempotent": True}
        self._validate_line_scan(line, request)""")
path="api/wms_api_server/app/routers/case_pick.py"
text=(ROOT/path).read_text(encoding="utf-8")
files[path]=text.replace("request.actor = request.actor or user.username","request.actor = user.username")
path="db/migrations/2026-10-08_stock_posting_core/160_case_pick_command.sql"
edit(path,"if n!=1 then raise_application_error(-20886,'CASE_PRODUCT_SCAN_CONFLICT');end if;",
 "if n!=1 and d.get_array('units').get_size=0 then raise_application_error(-20886,'CASE_PRODUCT_SCAN_CONFLICT');end if;")
edit(path,"a json_array_t;chunks json_array_t:=json_array_t();x json_object_t;",
 "a json_array_t;chunks json_array_t:=json_array_t();x json_object_t;selected_wire clob;")
edit(path,"  for sr in(select sr.RESERVATION_ID,",
 "  selected_wire:=d.get_array('units').to_clob;\n  for sr in(select sr.RESERVATION_ID,")
edit(path,"   q:=least(remaining,sr.BASE_QTY);remaining:=remaining-q;",
 """   if d.get_array('units').get_size>0 then
    select nvl(sum(u.BASE_QTY),0) into q from RRL_WMS_RECEIPT_UNIT u
     join json_table(selected_wire,'$[*]' columns(K varchar2(64) path '$'))j on j.K=u.PHYSICAL_UNIT_KEY
     where u.CURRENT_UID=sr.UID_PALLET and u.CURRENT_CELL=v_cell and u.HARD_RESERVATION_ID=sr.RESERVATION_ID and u.STOCK_STATUS!='ISSUED';
    if q=0 then continue;end if;
    if q>remaining or q>sr.BASE_QTY then raise_application_error(-20884,'CASE_SCANNED_UNIT_QUANTITY_CONFLICT');end if;
   else q:=least(remaining,sr.BASE_QTY);end if;
   remaining:=remaining-q;""")
print(json.dumps(files,ensure_ascii=True))
