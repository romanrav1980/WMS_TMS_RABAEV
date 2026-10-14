import ast
from pathlib import Path
r=Path(__file__).resolve().parents[1]
p=r/"api/wms_api_server/app/modules/resources/infrastructure/case_read_model.py"
s=p.read_text(encoding="utf-8");node=next(n for n in ast.parse(s).body if isinstance(n,ast.Assign))
old=ast.get_source_segment(s,node)
s=s.replace(old,'CASE_TASK_LIST_SQL = """'+node.value.value+'"""')
p.write_text(s,encoding="utf-8")
p=r/"api/wms_api_server/app/modules/resources/public.py"
s=p.read_text(encoding="utf-8")+'''
from .contracts_case_read import CaseReadPort, CaseReadError, case_read_service
from .infrastructure.case_scoped_reads import ScopedCaseReads
from .infrastructure.case_read_model import LegacyCaseReads


def legacy_case_reads(gateway: Any) -> LegacyCaseReads:
    return LegacyCaseReads(gateway)
'''
p.write_text(s,encoding="utf-8")
p=r/"api/wms_api_server/app/routers/case_pick.py"
s=p.read_text(encoding="utf-8")
s='from ..modules.resources.public import CaseReadPort, CaseReadError, case_read_service\n'+s
a=s.index('def list_case_pick_tasks(');b=s.index('@router.post("/tasks/{case_pick_task_id}/claim")',a)
s=s[:a]+'''def list_case_pick_tasks(
    resource_id: int | None = None, scope: str = "mine", status: str | None = None, limit: int = 100,
    user: AdminUser = Depends(require_permission(CASE_PICK_VIEW_PERMISSION)),
    service: CaseReadPort = Depends(case_read_service),
) -> list[dict]:
    try:
        return service.tasks(user.username, resource_id, scope, status, limit)
    except CaseReadError as exc:
        raise HTTPException(exc.status, {"code": exc.code, "message": str(exc)}) from exc


@router.get("/tasks/{case_pick_task_id}")
def get_case_pick_task(
    case_pick_task_id: int,
    user: AdminUser = Depends(require_permission(CASE_PICK_VIEW_PERMISSION)),
    service: CaseReadPort = Depends(case_read_service),
) -> dict:
    try:
        return service.task(case_pick_task_id, user.username)
    except CaseReadError as exc:
        raise HTTPException(exc.status, {"code": exc.code, "message": str(exc)}) from exc


'''+s[b:]
p.write_text(s,encoding="utf-8")
p=r/"api/wms_api_server/app/main.py"
p.write_text(p.read_text(encoding="utf-8")+'''
from .modules.resources.public import case_read_service
from .case_read_composition import scoped_case_reads
app.dependency_overrides[case_read_service] = scoped_case_reads
''',encoding="utf-8")
