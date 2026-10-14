import ast
from pathlib import Path
r=Path(__file__).resolve().parents[1]
p=r/"api/wms_api_server/app/services/case_pick_service.py"
s=p.read_text(encoding="utf-8");lines=s.splitlines(keepends=True);tree=ast.parse(s)
klass=next(node for node in tree.body if isinstance(node,ast.ClassDef)and node.name=="CasePickService")
methods={node.name:node for node in klass.body if isinstance(node,ast.FunctionDef)and node.name in("list_tasks","get_task")}
fragments=[]
for name in ("list_tasks","get_task"):
 node=methods[name];fragment="".join(lines[node.lineno-1:node.end_lineno])
 if name=="list_tasks":
  call=next(n for n in ast.walk(node)if isinstance(n,ast.Call)and isinstance(n.func,ast.Attribute)and n.func.attr=="fetch_all")
  argument=call.args[0];text=ast.get_source_segment(s,argument)
  query="".join(value.value if isinstance(value,ast.Constant)else "{where_sql}"for value in argument.values)
  fragment=fragment.replace(text,'CASE_TASK_LIST_SQL.format(where_sql=where_sql)')
  fragment=fragment.replace('        limit: int = 100,','        limit: int = 100,\n        warehouse_id: int | None = None,')
  fragment=fragment.replace('        params: dict[str, Any] = {"limit": min(max(limit, 1), 500)}','        params: dict[str, Any] = {"limit": min(max(limit, 1), 500)}\n        if warehouse_id is not None:\n            conditions.append("t.WARE_ID = :ware")\n            params["ware"] = warehouse_id')
 else:
  fragment=fragment.replace('from ..modules.inventory.public import','from ...inventory.public import')
 fragments.append(fragment)
header='"""Original CASE read model extracted; scoped API uses one current Oracle snapshot."""\nfrom typing import Any\n\nCASE_TASK_LIST_SQL = '+repr(query)+'\n\nclass LegacyCaseReads:\n    def __init__(self, gateway: Any) -> None:\n        self.gateway = gateway\n\n'
target=r/"api/wms_api_server/app/modules/resources/infrastructure/case_read_model.py"
target.write_text(header+'\n\n'.join(fragments)+'\n',encoding="utf-8")
# Descending replacement preserves line coordinates.
for name,node in sorted(methods.items(),key=lambda pair:pair[1].lineno,reverse=True):
 if name=="list_tasks":
  replacement='''    def list_tasks(self, resource_id: int | None = None, scope: str = "mine", status: str | None = None, limit: int = 100) -> list[dict[str, Any]]:
        from ..modules.resources.public import legacy_case_reads
        return legacy_case_reads(self.gateway).list_tasks(resource_id, scope, status, limit)
'''
 else:
  replacement='''    def get_task(self, case_pick_task_id: int) -> dict[str, Any] | None:
        from ..modules.resources.public import legacy_case_reads
        return legacy_case_reads(self.gateway).get_task(case_pick_task_id)
'''
 lines[node.lineno-1:node.end_lineno]=[replacement]
p.write_text("".join(lines),encoding="utf-8")
