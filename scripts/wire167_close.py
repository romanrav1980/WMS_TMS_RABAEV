import ast
from pathlib import Path
r=Path(__file__).resolve().parents[1]
p=r/"api/wms_api_server/app/services/case_pick_service.py"
s=p.read_text(encoding="utf-8");lines=s.splitlines(keepends=True)
klass=next(n for n in ast.parse(s).body if isinstance(n,ast.ClassDef)and n.name=="CasePickService")
nodes=[n for n in klass.body if isinstance(n,ast.FunctionDef)and n.name in("close_task","_close_task_locked")]
for node in sorted(nodes,key=lambda n:n.lineno,reverse=True):
 replacement='''    def close_task(self, case_pick_task_id: int, request: CasePickTaskActionRequest) -> dict[str, Any]:
        from ..modules.inventory.public import close_existing_case_carrier
        from ..modules.resources.public import assert_case_task_access
        return close_existing_case_carrier(self.gateway,case_pick_task_id,request,assert_case_task_access)
''' if node.name=="close_task"else""
 lines[node.lineno-1:node.end_lineno]=[replacement]
s="".join(lines)
# Scope short-report before row lock and before its saved metadata result.
a=s.index('    def short_line(');b=s.index('    def ',a+8)
part=s[a:b].replace('            bound = TransactionGateway(cursor)','            from ..modules.resources.public import assert_case_task_access\n            assert_case_task_access(cursor,case_pick_task_id,request.actor,"case_pick_execute")\n            bound = TransactionGateway(cursor)',1)
part=part.replace('            from ..modules.inventory.public import short_report_replay','            assert_case_task_access(cursor,case_pick_task_id,request.actor,"case_pick_execute")\n            from ..modules.inventory.public import short_report_replay',1)
s=s[:a]+part+s[b:]
# Current scope before returning already-REJECTED historical state.
a=s.index('    def reject_short(');b=s.index('    def ',a+8)
part=s[a:b].replace('select STATUS from RRL_CASE_PICK_SHORT','select STATUS,CASE_PICK_TASK_ID from RRL_CASE_PICK_SHORT',1)
part=part.replace('            if rows[0]["status"] == "REJECTED":','            from ..modules.resources.public import assert_case_task_access\n            assert_case_task_access(cursor,rows[0]["case_pick_task_id"],request.actor,"case_pick_short_approve")\n            if rows[0]["status"] == "REJECTED":',1)
s=s[:a]+part+s[b:]
p.write_text(s,encoding="utf-8")
p=r/"api/wms_api_server/app/modules/inventory/public.py"
p.write_text(p.read_text(encoding="utf-8")+'\nfrom .contracts_case_close import CaseCarrierCloseRequest\nfrom .infrastructure.case_carrier_close import close_case_carrier as close_existing_case_carrier\n',encoding="utf-8")
p=r/"api/wms_api_server/app/routers/case_pick.py"
s=p.read_text(encoding="utf-8").replace('from ..modules.inventory.public import CaseCarrierReturnRequest','from ..modules.inventory.public import CaseCarrierReturnRequest, CaseCarrierCloseRequest',1)
a=s.index('def close_case_pick_task');b=s.index('@router.get("/shorts")',a)
part=s[a:b].replace('request: CasePickTaskActionRequest','request: CaseCarrierCloseRequest',1)
part=part.replace('    result = CasePickService().close_task(case_pick_task_id, request)','    try:\n        result = CasePickService().close_task(case_pick_task_id, request)\n    except CaseReadError as exc:\n        raise HTTPException(exc.status, {"code": exc.code, "message": str(exc)}) from exc')
s=s[:a]+part+s[b:]
for name,endmark,statement in [
 ('def create_case_pick_short','@router.post("/tasks/{case_pick_task_id}/close-pallet")','    result = CasePickService().short_line(case_pick_task_id, line_id, request)'),
 ('def reject_case_pick_short','@router.get("/pallet-types")','    return {"case_pick_short_id": short_id, **CasePickService().reject_short(short_id, request)}')]:
 a=s.index(name);b=s.index(endmark,a);part=s[a:b]
 if 'result = 'in statement:
  replacement='    try:\n    '+statement+'\n    except CaseReadError as exc:\n        raise HTTPException(exc.status, {"code": exc.code, "message": str(exc)}) from exc'
 else:
  replacement='    try:\n    '+statement+'\n    except CaseReadError as exc:\n        raise HTTPException(exc.status, {"code": exc.code, "message": str(exc)}) from exc'
 assert statement in part
 part=part.replace(statement,replacement,1);s=s[:a]+part+s[b:]
p.write_text(s,encoding="utf-8")
