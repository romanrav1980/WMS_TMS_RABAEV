from pathlib import Path
import ast,json,re,textwrap
out={};root=Path("api/wms_api_server/app")
out[str(root/"modules/inventory/infrastructure/release_boundary.py")]='''"""Authoritative current release fence; never opts out to a legacy effect executor."""
from typing import Any
from ..contracts_stock import StockPostingError

def require_active_release(gateway: Any,operation_id: str|None=None) -> None:
    rows=gateway.fetch_all("select STATE from RRL_STOCK_RELEASE where RELEASE_ID=1")
    if not rows or rows[0]["state"]!="ACTIVE":
        raise StockPostingError("STOCK_RELEASE_NOT_ACTIVE",operation_id or "")
'''
names=["case_pick_commands","case_short_commands","document_reservation_commands","reservation_commands","wave_commands",
 "mes_commands","mes_release_commands","mes_supply_commands","mes_task_commands","terminal_quality_commands"]
pattern=re.compile(r'    (?:state|rows) = gateway.fetch_all\("select STATE from RRL_STOCK_RELEASE where RELEASE_ID=1"\)\n    if (?:state|rows) and (?:state|rows)\[0\]\["state"\] == "PREPARED":\n        return (?:None|False)\n')
for name in names:
 p=root/f"modules/inventory/infrastructure/{name}.py";text=p.read_text(encoding="utf-8")
 assert len(pattern.findall(text))==1,name
 operation="None"if name in{"document_reservation_commands","wave_commands"}else'request.operation_id'
 text=pattern.sub(f"    require_active_release(gateway,{operation})\n",text)
 text=text.replace("from .stock_posting_uow import StockPosting","from .stock_posting_uow import StockPosting\nfrom .release_boundary import require_active_release")
 out[str(p)]=text
p=root/"modules/inventory/public.py";text=p.read_text(encoding="utf-8")
text+="\nfrom .infrastructure.release_boundary import require_active_release as require_active_stock_release\n"
text+="from .infrastructure.mes_commands import apply_mes_movements as apply_existing_mes_movements\n"
text+="from .infrastructure.mes_release_commands import release_supply as release_existing_mes_supply\n"
text+="from .infrastructure.reservation_commands import post_reservation as post_existing_reservation\n"
out[str(p)]=text
def native_only(text,names):
 tree=ast.parse(text);cls=next(x for x in tree.body if isinstance(x,ast.ClassDef));lines=text.splitlines(keepends=True)
 changes=[]
 for fn in cls.body:
  if not isinstance(fn,ast.FunctionDef)or fn.name not in names:continue
  node=next((n for n in fn.body if isinstance(n,ast.If)and isinstance(n.test,ast.Compare)and isinstance(n.test.ops[0],ast.IsNot)and isinstance(n.test.comparators[0],ast.Constant)and n.test.comparators[0].value is None),None)
  assert node and not node.orelse and isinstance(node.body[-1],ast.Return),fn.name
  prefix="".join(lines[fn.lineno-1:node.lineno-1])
  if isinstance(node.test.left,ast.Call):prefix+="        "+ast.unparse(node.test.left)+"\n"
  branch="".join(lines[node.body[0].lineno-1:node.body[-1].end_lineno])
  branch="".join(line[4:]if line.startswith("    ")else line for line in branch.splitlines(keepends=True))
  changes.append((fn.lineno-1,fn.end_lineno,prefix+branch))
 for start,end,value in sorted(changes,reverse=True):lines[start:end]=[value]
 return "".join(lines)
p=root/"services/case_pick_service.py";text=p.read_text(encoding="utf-8")
text=native_only(text,{"confirm_line","approve_short"})
for call in["_short_line_locked(case_pick_task_id, line_id, request)","_close_task_locked(case_pick_task_id, request)","_reject_short_locked(short_id, request)"]:
 needle='''        state = self.gateway.fetch_all("select STATE from RRL_STOCK_RELEASE where RELEASE_ID=1")
        if state and state[0]["state"] == "PREPARED":
            return self.'''+call+"\n"
 assert text.count(needle)==1,call
 text=text.replace(needle,"")
out[str(p)]=text
p=root/"services/mes_service.py";text=p.read_text(encoding="utf-8")
text=native_only(text,{"apply_wms","calculate_raw_supply","release_to_production","confirm_raw_transfer_task","cancel_raw_transfer_task"})
text=text.replace("from ..modules.inventory.infrastructure.mes_commands import apply_mes_movements","from ..modules.inventory.public import apply_existing_mes_movements as apply_mes_movements")
text=text.replace("from ..modules.inventory.infrastructure.mes_release_commands import release_supply","from ..modules.inventory.public import release_existing_mes_supply as release_supply")
start=text.index("    def _assert_legacy_reservation_builder(");end=text.index("    def _create_soft_raw_reservation(",start)
text=text[:start]+'''    def _assert_legacy_reservation_builder(self) -> None:
        raise HTTPException(409, detail={"code": "MES_RESERVATION_POSTING_REQUIRED"})

'''+text[end:]
out[str(p)]=text
p=root/"services/stock_reservation_service.py";text=p.read_text(encoding="utf-8")
text=native_only(text,{"create_reservation","promote_to_hard","release_reservation","consume_reservation","cancel_reservation"})
text=text.replace("from ..modules.inventory.infrastructure.reservation_commands import post_reservation","from ..modules.inventory.public import post_existing_reservation as post_reservation")
out[str(p)]=text
p=root/"services/picking_service.py";text=p.read_text(encoding="utf-8")
text=text.replace("from ..modules.inventory.contracts_stock import StockCommand, StockPostingError","from ..modules.inventory.public import StockCommand, StockPostingError")
text=text.replace("from ..modules.inventory.infrastructure.stock_posting_uow import StockPosting","from ..modules.inventory.public import StockPosting")
needle='''        state = self.gateway.fetch_all("select STATE from RRL_STOCK_RELEASE where RELEASE_ID=1")
        if state and state[0]["state"] == "PREPARED":
            return False
'''
assert text.count(needle)==1
text=text.replace(needle,'''        from ..modules.inventory.public import require_active_stock_release
        require_active_stock_release(self.gateway,request.operation_id)
''')
tree=ast.parse(text);cls=next(x for x in tree.body if isinstance(x,ast.ClassDef))
fn=next(x for x in cls.body if isinstance(x,ast.FunctionDef)and x.name=="complete_wave_pick_task")
node=next(x for x in fn.body if isinstance(x,ast.If)and "PREPARED"in ast.unparse(x.test))
lines=text.splitlines(keepends=True)
# Keep signature and actor; replace release escape with active-only fence and native body.
prefix="".join(lines[fn.lineno-1:node.lineno-2])
assert "release ="not in prefix
branch="".join(lines[node.body[0].lineno-1:node.body[-1].end_lineno])
branch="".join(line[4:]if line.startswith("    ")else line for line in branch.splitlines(keepends=True))
replacement=prefix+'''        from ..modules.inventory.public import require_active_stock_release
        require_active_stock_release(self.gateway,request.operation_id)
'''+branch
replacement=replacement.replace("from ..modules.inventory.infrastructure.task_completion import complete_existing_task","from ..modules.inventory.public import complete_existing_warehouse_task as complete_existing_task")
lines[fn.lineno-1:fn.end_lineno]=[replacement]
text="".join(lines)
# Closed old private direct balance helper remains unreachable but cannot be enabled by PREPARED.
start=text.index("    def _apply_case_pick_stock_fact(");end=text.index("\n    def ",start+5)
text=text[:start]+'''    def _apply_case_pick_stock_fact(self, task: dict[str, Any], fact_qty: float) -> None:
        raise HTTPException(409, detail={"code": "CASE_PICK_CONFIRM_REQUIRED"})
'''+text[end:]
out[str(p)]=text
for p,text in out.items():ast.parse(text)
print(json.dumps(out,ensure_ascii=True))
