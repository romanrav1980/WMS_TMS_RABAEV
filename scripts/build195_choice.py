from pathlib import Path
import json
out={};f=Path("db/migrations/2026-10-11_ni042_weight_box_choice")
t=(f/"000_before_reader.sql").read_text(encoding="utf-8")
t=t.replace("snapshot_json(p_row number,p_actor varchar2)","snapshot_json(p_row number,p_actor varchar2,p_permission varchar2 default 'pick_plan_create')")
t=t.replace("  RRL_PICK_PLAN_ACCESS.assert_scope(o.CUSTOMER_ORDER_ID,p_actor);","  if p_permission is null or p_permission not in('pick_plan_create','case_pick_short_approve')then raise_application_error(-20882,'WEIGHT_BOX_PREVIEW_PERMISSION_REQUIRED');end if;\n  RRL_PICK_PLAN_ACCESS.assert_scope(o.CUSTOMER_ORDER_ID,p_actor,p_permission);")
out[str(f/"003_reader.sql")]=t
p=f/"002_api.sql";t=p.read_text(encoding="utf-8").replace("snapshot_json(row_id,p_actor)","snapshot_json(row_id,p_actor,'case_pick_short_approve')");out[str(p)]=t
out[str(f/"apply.sql")]="@@001_schema.sql\n@@003_reader.sql\n@@002_api.sql\n@@004_guard.sql\n"
out[str(f/"rollback.sql")]="""declare n number;begin select count(*)into n from RRL_PICK_WEIGHT_CHOICE;if n>0 then raise_application_error(-20863,'WEIGHT_CHOICE_RETAIN_ARCHIVE_FORWARD_REPAIR');end if;end;
/
@@000_before_reader.sql
drop trigger RRL_WEIGHT_CHOICE_GUARD;
drop context RRL_WEIGHT_CHOICE_CTX;
drop package RRL_WEIGHT_BOX_CHOICE_API;
drop table RRL_PICK_WEIGHT_CHOICE;
"""
p=Path("api/wms_api_server/app/modules/inventory/contracts_weighted_plan.py");t=p.read_text(encoding="utf-8").replace("from typing import Any, Protocol","from typing import Any, Protocol, Literal\nfrom pydantic import BaseModel, Field, ConfigDict")
t=t.replace("class WeightedPlanPort(Protocol):",'''class WeightedBoxChoiceRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    choice_id: str = Field(min_length=1, max_length=100, pattern=r"^[A-Za-z0-9_.:-]+$")
    customer_order_row_id: int = Field(ge=1, strict=True)
    physical_unit_key: str = Field(pattern=r"^[A-F0-9]{64}$")
    weighted_box_barcode: str = Field(min_length=1, max_length=512)
    source_signature: str = Field(pattern=r"^[A-F0-9]{64}$")
    choice_mode: Literal["WITHIN_TOLERANCE", "LAST_WHOLE_BOX"]
    reason: str = Field(min_length=3, max_length=1000)


class WeightedChoiceCancelRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    reason: str = Field(min_length=3, max_length=1000)


class WeightedPlanPort(Protocol):
    def approval_options(self, row: int, actor: str) -> dict[str, Any]: ...
    def approve(self, body: WeightedBoxChoiceRequest, actor: str) -> dict[str, Any]: ...
    def cancel(self, choice: str, reason: str, actor: str) -> dict[str, Any]: ...''')
out[str(p)]=t
p=Path("api/wms_api_server/app/modules/inventory/infrastructure/weighted_planning.py");t=p.read_text(encoding="utf-8")
t=t.replace("import oracledb","import oracledb\nimport json",1).replace("import read_oracle_json","import read_oracle_json, stock_configuration_transaction")
t=t.replace("from ..contracts_stock import StockPostingError","from ..contracts_stock import StockPostingError\nfrom ..contracts_weighted_plan import WeightedBoxChoiceRequest")
t=t.replace("    def options(self, row: int, actor: str) -> dict[str, Any]:","    def options(self, row: int, actor: str) -> dict[str, Any]:\n        return self._options(row, actor, \"pick_plan_create\")\n\n    def approval_options(self, row: int, actor: str) -> dict[str, Any]:\n        return self._options(row, actor, \"case_pick_short_approve\")\n\n    def _options(self, row: int, actor: str, permission: str) -> dict[str, Any]:")
t=t.replace("[row, actor]))","[row, actor, permission]))")
t+='''
    def approve(self, body: WeightedBoxChoiceRequest, actor: str) -> dict[str, Any]:
        wire = json.dumps(body.model_dump(mode="json"), ensure_ascii=True, sort_keys=True, separators=(",", ":"))
        try:
            with stock_configuration_transaction(self.gateway, "Approve final whole weighted box", actor, "case_pick_short_approve") as q:
                inp, out = q.var(oracledb.DB_TYPE_CLOB), q.var(oracledb.DB_TYPE_CLOB)
                inp.setvalue(0, wire)
                q.callproc("RRL_WEIGHT_BOX_CHOICE_API.approve_request", [inp, actor, out])
                return read_oracle_json(out.getvalue())
        except oracledb.DatabaseError as exc:
            raise choice_error(exc, body.choice_id) from exc

    def cancel(self, choice: str, reason: str, actor: str) -> dict[str, Any]:
        try:
            with stock_configuration_transaction(self.gateway, "Cancel unused weighted box choice", actor, "case_pick_short_approve") as q:
                out = q.var(oracledb.DB_TYPE_CLOB)
                q.callproc("RRL_WEIGHT_BOX_CHOICE_API.cancel_choice", [choice, actor, reason, out])
                return read_oracle_json(out.getvalue())
        except oracledb.DatabaseError as exc:
            raise choice_error(exc, choice) from exc


def choice_error(exc: oracledb.DatabaseError, choice: str) -> StockPostingError:
    code = exc.args[0].code
    kind = ("OPERATION_CONTENT_CONFLICT" if code == 20873 else
            "RESULT_UNCERTAIN" if not (20800 <= code <= 20999 or code in {1, 1403, 1422}) else
            "WEIGHT_BOX_CHOICE_REJECTED")
    return StockPostingError(kind, choice, code, str(exc).split("\\n", 1)[0])
'''
out[str(p)]=t
p=Path("api/wms_api_server/app/modules/inventory/api/weighted_plan_routes.py");t=p.read_text(encoding="utf-8")
t=t.replace("import WeightedPlanPort,","import WeightedPlanPort, WeightedBoxChoiceRequest, WeightedChoiceCancelRequest,")
t+='''
@router.get("/order-rows/{row}/weighted-box-approval-preview")
def weighted_box_approval_preview(row: int = Path(ge=1),
                         user: AdminUser = Depends(require_permission("case_pick_short_approve")),
                         service: WeightedPlanPort = Depends(weighted_plan_service)) -> dict:
    return service.approval_options(row, user.username)


@router.post("/weighted-box-choices")
def approve_weighted_box(body: WeightedBoxChoiceRequest,
                         user: AdminUser = Depends(require_permission("case_pick_short_approve")),
                         service: WeightedPlanPort = Depends(weighted_plan_service)) -> dict:
    return service.approve(body, user.username)


@router.post("/weighted-box-choices/{choice}/cancel")
def cancel_weighted_box(choice: str, body: WeightedChoiceCancelRequest,
                         user: AdminUser = Depends(require_permission("case_pick_short_approve")),
                         service: WeightedPlanPort = Depends(weighted_plan_service)) -> dict:
    return service.cancel(choice, body.reason, user.username)
'''
out[str(p)]=t
out["wiki/database/retailcase_ni042_weight_box_choice_design_20261011.md"]="""# NI04.2: согласованный выбор последней коробки
195 additive immutable approved choice archive, existing CONFIG metadata transaction only/no P/H or stock writer. Scoped approval-only versus pick-plan creation roles separate via shared native reader permission; source signature/current physical unit/raw GS1 identity/net+gross+volume/current policy/stock/current order captured; WITHIN_TOLERANCE versus explicit LAST_WHOLE_BOX reason. Exact request+actor replay; unique active per original order row and physical box; cancellation retains original source/history. No real ACK/no marked split.
196 existing native planner consumes approved choice inside old plan creation/SOFT transaction with current source/locks;197 exact physical HARD pin;198 actual fulfillment/cancellation-aware demand. Until then archive approval is not stock/plan fulfillment. No second allocator.
"""
for name,line in [("wiki/index.md","- [Согласованный выбор последней коробки: разработка](database/retailcase_ni042_weight_box_choice_design_20261011.md):195 immutable current selected box/role-separated approval/source replay/no stock; existing plan use next."),
("wiki/log.md","2026-10-11:195 begins from fresh original194 pure reader/checkpoint; additive immutable choice/current source signature/GS1/exact box/metadata approval-only permission/unique active/cancel history; no quantity effect.")]:
 p=Path(name);out[str(p)]=p.read_text(encoding="utf-8")+"\n"+line+"\n"
print(json.dumps(out,ensure_ascii=True))
