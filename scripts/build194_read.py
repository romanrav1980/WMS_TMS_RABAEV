from pathlib import Path
import json
out={};f=Path("db/migrations/2026-10-11_ni042_weight_box_planning")
t=(f/"000_before_admission.sql").read_text(encoding="utf-8")
a=t.index(" procedure actor_scope(");b=t.index(" procedure begin_plan(",a)
t=t[:a]+""" procedure actor_scope(p_order number,p_actor varchar2)is begin RRL_PICK_PLAN_ACCESS.assert_scope(p_order,p_actor);end;
"""+t[b:]
out[str(f/"003_admission.sql")]=t
out[str(f/"apply.sql")]="@@001_access.sql\n@@002_options.sql\n@@003_admission.sql\n"
out[str(f/"rollback.sql")]="@@000_before_admission.sql\ndrop package RRL_WEIGHT_BOX_PLANNING_READ;\ndrop package RRL_PICK_PLAN_ACCESS;\n"
out["api/wms_api_server/app/modules/inventory/contracts_weighted_plan.py"]='''"""Preview actual sealed boxes for the original warehouse order row."""
from typing import Any, Protocol


class WeightedPlanPort(Protocol):
    def options(self, row: int, actor: str) -> dict[str, Any]: ...


def weighted_plan_service() -> WeightedPlanPort:
    raise RuntimeError("Weighted plan service not wired")
'''
out["api/wms_api_server/app/modules/inventory/infrastructure/weighted_planning.py"]='''"""One current read-only source for actual whole-box planning candidates."""
import oracledb
from typing import Any
from ....oracle_gateway import OracleGateway
from ...platform.public import read_oracle_json
from ..contracts_stock import StockPostingError


class WeightedPlanning:
    def __init__(self, gateway: OracleGateway) -> None:
        self.gateway = gateway

    def options(self, row: int, actor: str) -> dict[str, Any]:
        try:
            with self.gateway.transaction("Actual whole-box planning READ ONLY") as q:
                q.execute("set transaction read only")
                return read_oracle_json(q.callfunc("RRL_WEIGHT_BOX_PLANNING_READ.snapshot_json", oracledb.DB_TYPE_CLOB, [row, actor]))
        except oracledb.DatabaseError as exc:
            code = exc.args[0].code
            if code in {20881,20882,20886,20860,20868,1403,1422}:
                raise StockPostingError("WEIGHT_BOX_PLAN_SOURCE_REJECTED", None, code) from exc
            raise
'''
out["api/wms_api_server/app/modules/inventory/api/weighted_plan_routes.py"]='''"""Read current weighted whole boxes before using the existing pick planner."""
from fastapi import APIRouter, Depends, Path
from ...platform.public import AdminUser, require_permission
from ..contracts_weighted_plan import WeightedPlanPort, weighted_plan_service

router = APIRouter(prefix="/api/picking", tags=["weighted-planning"])


@router.get("/order-rows/{row}/weighted-box-options")
def weighted_box_options(row: int = Path(ge=1),
                         user: AdminUser = Depends(require_permission("pick_plan_create")),
                         service: WeightedPlanPort = Depends(weighted_plan_service)) -> dict:
    return service.options(row, user.username)
'''
p=Path("api/wms_api_server/app/modules/inventory/public.py");t=p.read_text(encoding="utf-8")
assert "weighted_plan_router"not in t
out[str(p)]=t+'''
from .contracts_weighted_plan import WeightedPlanPort, weighted_plan_service
from .api.weighted_plan_routes import router as weighted_plan_router
from .infrastructure.weighted_planning import WeightedPlanning

def build_weighted_plan() -> WeightedPlanPort:
    return WeightedPlanning(OracleGateway())
'''
p=Path("api/wms_api_server/app/main.py");t=p.read_text(encoding="utf-8")
a="app.include_router(inventory_receiving.weighted_case_router)";assert a in t
t=t.replace(a,a+"\napp.include_router(inventory_receiving.weighted_plan_router)\napp.dependency_overrides[inventory_receiving.weighted_plan_service] = inventory_receiving.build_weighted_plan")
out[str(p)]=t
out["wiki/database/retailcase_ni042_weight_box_planning_design_20261011.md"]="""# NI04.2: выбор последней целой весовой коробки
194 read-only preview of actual available physical units for original order row, before existing planner. SKU serialized weighted KG/current profiles, real net/gross/volume/source ref/GS1 label, current warehouse/pallet identifier/cell/stock version, eligibility, current original whole orderSKU demand/picked/current remaining minus unlaunched SOFT, default15/frozen cardversion. Single final-box options within tolerance versus explicit exception, no sealed splitting/no stock or reservation effect. Bounds200 orderrows/200 source lots/100 boxes.
Existing planner actor scope extracted into RRL_PICK_PLAN_ACCESS and reused before/after native planning locks; one current warehouse/right admission, not duplicate permissions policy. Native pure reader feeds typed API/customer-order UI;195 approved choice,196 existing plan/HARD exact physical selection,197 current fulfillment waiver next. No false claim of completed last-box execution.
"""
for name,line in [("wiki/index.md","- [Выбор последней целой весовой коробки: разработка](database/retailcase_ni042_weight_box_planning_design_20261011.md):194 actual candidates/current order source/native shared plan scope; admission/apply next."),
("wiki/log.md","2026-10-11:194 begins from fresh live plan-admission source/checkpoint; actual sealed weighted-box options/current original order/pct/no stock; shared planner scope extraction before/after locks.")]:
 p=Path(name);out[str(p)]=p.read_text(encoding="utf-8")+"\n"+line+"\n"
print(json.dumps(out,ensure_ascii=True))
