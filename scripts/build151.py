from pathlib import Path
import json
root=Path("api/wms_api_server/app");out={}
out[str(root/"modules/resources/infrastructure/workload_history.py")]='''"""Immutable original planned rows and relational replacement lineage, no writes."""
from typing import Any
from .workload_config import current_warehouse,workload_rows
from ..contracts_workload import WorkloadError

class WorkloadHistory:
    def __init__(self,gateway: Any) -> None:self.gateway=gateway
    def read(self,ware: int,plan: str,limit: int,actor: str) -> dict[str,Any]:
        with self.gateway.transaction("Planned attendance history READ ONLY snapshot")as cur:
            cur.execute("set transaction read only");current_warehouse(cur,ware,actor)
            cur.execute("""select to_char(systimestamp at time zone 'UTC',
                'YYYY-MM-DD"T"HH24:MI:SS.FF6TZH:TZM')from dual""");observed=cur.fetchone()[0]
            cur.execute("""select level DEPTH,connect_by_iscycle CYCLE_FOUND,
                a.PLAN_OPERATION_ID,a.WARE_ID,a.SITE_CODE,a.RESOURCE_ID,a.PERSON_ID,a.REASON,
                to_char(a.START_AT at time zone 'UTC','YYYY-MM-DD"T"HH24:MI:SS.FF6TZH:TZM')START_AT,
                to_char(a.FINISH_AT at time zone 'UTC','YYYY-MM-DD"T"HH24:MI:SS.FF6TZH:TZM')FINISH_AT,
                o.ACTOR PLANNED_BY,o.ACTION_KIND,
                to_char(o.CREATED_AT at time zone 'UTC','YYYY-MM-DD"T"HH24:MI:SS.FF6TZH:TZM')RECORDED_AT,
                parent.PLAN_OPERATION_ID REPLACED_PLAN_OPERATION_ID,
                cancelled.CANCEL_OPERATION_ID,cancel_op.ACTOR CANCELLED_BY,cancelled.REASON CANCEL_REASON,
                to_char(cancel_op.CREATED_AT at time zone 'UTC','YYYY-MM-DD"T"HH24:MI:SS.FF6TZH:TZM')CANCEL_RECORDED_AT
                from RRL_WORKLOAD_ATTENDANCE a join RRL_WORKLOAD_OPERATION o on o.OPERATION_ID=a.PLAN_OPERATION_ID
                left join RRL_WORKLOAD_ATTEND_CANCEL parent on parent.CANCEL_OPERATION_ID=a.PLAN_OPERATION_ID
                    and o.ACTION_KIND='REPLACE_ATTENDANCE'
                left join RRL_WORKLOAD_ATTEND_CANCEL cancelled on cancelled.PLAN_OPERATION_ID=a.PLAN_OPERATION_ID
                left join RRL_WORKLOAD_OPERATION cancel_op on cancel_op.OPERATION_ID=cancelled.CANCEL_OPERATION_ID
                where a.WARE_ID=:ware
                start with a.PLAN_OPERATION_ID=:plan and a.WARE_ID=:ware
                connect by nocycle prior parent.PLAN_OPERATION_ID=a.PLAN_OPERATION_ID
                order by level fetch first :count rows only""",ware=ware,plan=plan,count=limit+1)
            rows=workload_rows(cur)
            if not rows:raise WorkloadError("WORKLOAD_PLAN_NOT_FOUND","План этого склада не найден",404)
            if any(row["cycle_found"]for row in rows):raise WorkloadError("WORKLOAD_HISTORY_CYCLE","Нарушена история замены")
            selected=rows[:limit]
            has_more=len(rows)>limit
            next_plan=selected[-1]["replaced_plan_operation_id"]if has_more else None
            if has_more and not next_plan:raise WorkloadError("WORKLOAD_HISTORY_LINK_MISSING","Нарушена связь истории")
        return {"warehouse_id":ware,"requested_plan_operation_id":plan,"observed_at":observed,"rows":selected,
            "next_plan_operation_id":next_plan,"has_more":has_more,"stock_changed":False,
            "actual_presence_created":False,"basis":"IMMUTABLE_PLANNED_ATTENDANCE_AND_CANCELLATION",
            "starting_state_at_read":True,"frozen_daily_report":False}
'''
p=root/"modules/resources/contracts_workload.py";text=p.read_text(encoding="utf-8")
text+='''\nclass WorkloadHistoryPort(Protocol):
    def read(self,ware: int,plan: str,limit: int,actor: str) -> dict[str,Any]: ...

def workload_history_service() -> WorkloadHistoryPort:
    raise RuntimeError("Attendance history not wired")
'''
out[str(p)]=text
out[str(root/"modules/resources/api/workload_history_routes.py")]='''from typing import Any
from fastapi import APIRouter, Depends, HTTPException, Path, Query
from ...platform.public import AdminUser, require_permission
from ..contracts_workload import WorkloadHistoryPort, WorkloadError, workload_history_service

router=APIRouter(prefix="/api/resources/workload",tags=["resource-workload"])

@router.get("/warehouses/{ware_id}/attendance/{plan_id}/history")
def history(ware_id: int=Path(gt=0),plan_id: str=Path(min_length=1,max_length=100),
    limit: int=Query(25,ge=1,le=50),user: AdminUser=Depends(require_permission("resource_shift_view")),
    service: WorkloadHistoryPort=Depends(workload_history_service)) -> dict[str,Any]:
    try:return service.read(ware_id,plan_id,limit,user.username)
    except WorkloadError as exc:raise HTTPException(exc.status,{"code":exc.code,"message":str(exc)}) from exc
'''
p=root/"modules/resources/public.py";text=p.read_text(encoding="utf-8")
text+='''\nfrom .contracts_workload import WorkloadHistoryPort,workload_history_service
from .api.workload_history_routes import router as workload_history_router
from .infrastructure.workload_history import WorkloadHistory

def build_workload_history(gateway: Any) -> WorkloadHistoryPort:
    return WorkloadHistory(gateway)
'''
# existing resources/public.py already imports Any; preserve that single source.
assert "from typing import Any"in text
out[str(p)]=text
out[str(root/"workload_history_composition.py")]='''from .oracle_gateway import OracleGateway
from .modules.resources.public import WorkloadHistoryPort, build_workload_history

def attendance_history() -> WorkloadHistoryPort:
    return build_workload_history(OracleGateway())
'''
p=root/"main.py";out[str(p)]=p.read_text(encoding="utf-8")+'''
from .modules.resources.public import workload_history_router,workload_history_service
from .workload_history_composition import attendance_history
app.dependency_overrides[workload_history_service]=attendance_history
app.include_router(workload_history_router)
'''
print(json.dumps(out,ensure_ascii=True))
