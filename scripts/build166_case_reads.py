import ast
from pathlib import Path
r=Path(__file__).resolve().parents[1]
p=r/"api/wms_api_server/app/modules/resources/infrastructure/case_scoped_reads.py"
s=p.read_text(encoding="utf-8")
s=s.replace('def task_scope(cur: Any, task: int, actor: str) -> None:\n    actor_scope(cur, actor)\n    try:',
 '''def native_task_scope(cur: Any, task: int, actor: str, permission: str) -> None:
    try:''')
s=s.replace('[task, actor, "case_pick_view", None]','[task, actor, permission, None]',1)
a=s.index('\n\nclass ScopedCaseReads')
s=s[:a]+'''\n\ndef task_scope(cur: Any, task: int, actor: str) -> None:
    actor_scope(cur, actor)
    native_task_scope(cur, task, actor, "case_pick_view")
'''+s[a:]
s+='''

    def shorts(self, actor: str, status: str | None, limit: int) -> list[dict[str, Any]]:
        if not 1 <= limit <= 500:
            raise CaseReadError("CASE_LIST_SCOPE_INVALID", "Предел должен быть1–500", 422)
        with self.gateway.transaction("Current CASE shortages READ ONLY snapshot") as cur:
            if not getattr(self.gateway, "transaction_bound", False):
                cur.execute("set transaction read only")
            ware, global_admin = actor_scope(cur, actor)
            return LegacyCaseReads(TransactionGateway(cur)).list_shorts(status, limit, None if global_admin else ware)
'''
p.write_text(s,encoding="utf-8")
p=r/"api/wms_api_server/app/modules/resources/public.py"
p.write_text(p.read_text(encoding="utf-8")+'from .infrastructure.case_scoped_reads import native_task_scope as assert_case_task_access\n',encoding="utf-8")
p=r/"api/wms_api_server/app/modules/resources/contracts_case_read.py"
s=p.read_text(encoding="utf-8").replace('    def task(self, task: int, actor: str) -> dict[str, Any]: ...','    def task(self, task: int, actor: str) -> dict[str, Any]: ...\n    def shorts(self, actor: str, status: str | None, limit: int) -> list[dict[str, Any]]: ...')
p.write_text(s,encoding="utf-8")
p=r/"api/wms_api_server/app/services/case_pick_service.py"
s=p.read_text(encoding="utf-8");lines=s.splitlines(keepends=True)
klass=next(n for n in ast.parse(s).body if isinstance(n,ast.ClassDef)and n.name=="CasePickService")
node=next(n for n in klass.body if isinstance(n,ast.FunctionDef)and n.name=="list_shorts")
fragment="".join(lines[node.lineno-1:node.end_lineno])
fragment=fragment.replace('limit: int = 200)','limit: int = 200, warehouse_id: int | None = None)')
fragment=fragment.replace('        conditions = []','''        conditions = []
        if warehouse_id is not None:
            conditions.append("exists(select 1 from RRL_CASE_PICK_TASK ct where ct.CASE_PICK_TASK_ID=s.CASE_PICK_TASK_ID and ct.WARE_ID=:ware)")''',1)
fragment=fragment.replace('        if status:','        if warehouse_id is not None:\n            params["ware"] = warehouse_id\n        if status:',1)
target=r/"api/wms_api_server/app/modules/resources/infrastructure/case_read_model.py"
target.write_text(target.read_text(encoding="utf-8")+'\n'+fragment+'\n',encoding="utf-8")
lines[node.lineno-1:node.end_lineno]=['''    def list_shorts(self, status: str | None = None, limit: int = 200) -> list[dict[str, Any]]:
        from ..modules.resources.public import legacy_case_reads
        return legacy_case_reads(self.gateway).list_shorts(status, limit)
''']
p.write_text("".join(lines),encoding="utf-8")
p=r/"api/wms_api_server/app/modules/inventory/infrastructure/case_task_services.py"
s=p.read_text(encoding="utf-8").replace('    def marking_policy(self,task: int,line: int) -> dict[str,Any]:\n        return case_pick_policy(self.gateway,task,line)',
 '''    def marking_policy(self,task: int,line: int,actor: str) -> dict[str,Any]:
        from ...resources.public import assert_case_task_access
        from ....transaction_gateway import TransactionGateway
        with self.gateway.transaction("Current CASE marking policy READ ONLY snapshot") as cur:
            cur.execute("set transaction read only")
            assert_case_task_access(cur,task,actor,"case_pick_execute")
            return case_pick_policy(TransactionGateway(cur),task,line)''')
p.write_text(s,encoding="utf-8")
p=r/"api/wms_api_server/app/routers/case_pick.py"
s=p.read_text(encoding="utf-8")
s=s.replace('build_case_task_services().marking_policy(case_pick_task_id, line_id)','build_case_task_services().marking_policy(case_pick_task_id, line_id, user.username)')
a=s.index('def case_line_marking_policy');b=s.index('@router.post("/tasks/{case_pick_task_id}/lines/{line_id}/confirm")',a)
part=s[a:b].replace('    except LookupError as exc:','    except CaseReadError as exc:\n        raise HTTPException(exc.status, {"code": exc.code, "message": str(exc)}) from exc\n    except LookupError as exc:',1)
s=s[:a]+part+s[b:]
a=s.index('def list_case_pick_shorts');b=s.index('@router.post("/shorts/{short_id}/approve")',a)
s=s[:a]+'''def list_case_pick_shorts(
    status: str | None = None, limit: int = 200,
    user: AdminUser = Depends(require_permission(CASE_PICK_VIEW_PERMISSION)),
    service: CaseReadPort = Depends(case_read_service),
) -> list[dict]:
    try:
        return service.shorts(user.username, status, limit)
    except CaseReadError as exc:
        raise HTTPException(exc.status, {"code": exc.code, "message": str(exc)}) from exc


'''+s[b:]
p.write_text(s,encoding="utf-8")
