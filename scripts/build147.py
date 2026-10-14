from pathlib import Path
import ast,json
out={}
p=Path("api/wms_api_server/app/services/warehouse_task_domain_sync_service.py");text=p.read_text(encoding="utf-8")
tree=ast.parse(text);cls=next(x for x in tree.body if isinstance(x,ast.ClassDef))
remove={"_run_sync","_run_sync_locked","_sync_wave_replenishment","_apply_wave_replenishment_stock_move","_sync_wave_picking_move","_sync_mes_raw_supply","_sync_mes_completion_storage","_ensure_sync_row","_mark_error","_get_sync","_get_mes_movement","_sync_key","_to_float"}
lines=text.splitlines(keepends=True)
for node in sorted((x for x in cls.body if isinstance(x,ast.FunctionDef)and x.name in remove),key=lambda x:x.lineno,reverse=True):
 del lines[node.lineno-1:node.end_lineno]
text="".join(lines)
text=text.replace("from ..schemas import MesApplyWmsRequest, MesRawTransferTaskConfirmRequest\n","").replace("from .mes_service import MesService, clamp_limit","from .mes_service import clamp_limit")
text=text.replace('''        if state and state[0]["state"] == "PREPARED":
            return None
''',"")
text=text.replace("def _explicit_sync(self, task_id: int) -> dict[str, Any] | None:","def _explicit_sync(self, task_id: int) -> dict[str, Any]:")
start=text.index("    def dispatch_after_complete(");end=text.index("    def get_task_sync(",start)
text=text[:start]+'''    def dispatch_after_complete(self, task_id: int, updated_by: str | None = None) -> dict[str, Any] | None:
        task = self._get_task(task_id)
        if not self.is_supported(task):
            return None
        return self._explicit_sync(task_id)

    def retry_task_sync(self, task_id: int, updated_by: str | None = None) -> dict[str, Any]:
        return self._explicit_sync(task_id)

'''+text[end:]
while "\n\n\n"in text:text=text.replace("\n\n\n","\n\n")
out[str(p)]=text
p=Path("api/wms_api_server/app/modules/inventory/public.py");text=p.read_text(encoding="utf-8");tree=ast.parse(text);lines=text.splitlines(keepends=True)
remove={"lock_warehouse_task_domain","apply_warehouse_task_stock_move","apply_warehouse_replenishment_reservation"}
for node in sorted((x for x in tree.body if isinstance(x,ast.FunctionDef)and x.name in remove),key=lambda x:x.lineno,reverse=True):
 del lines[node.lineno-1:node.end_lineno]
text="".join(lines)
while "\n\n\n"in text:text=text.replace("\n\n\n","\n\n")
out[str(p)]=text
print(json.dumps(out,ensure_ascii=True))
