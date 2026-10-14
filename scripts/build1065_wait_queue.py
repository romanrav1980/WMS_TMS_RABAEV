from pathlib import Path
import json,re
files={}
p="api/wms_api_server/app/services/warehouse_task_service.py"
t=Path(p).read_text(encoding="utf-8");start=t.index("    def list_tasks(");end=t.index("    def assign_task(",start)
old=t[start:end]
# Extract the original bounded list query and reuse it with sparse immutable wait bindings.
sql_start=old.index('f"""')+4;sql_end=old.index('""",',sql_start)
sql=old[sql_start:sql_end]
sql=sql.replace("                       CREATED_AT,", "                       WAIT_PLAN_OPERATION_ID,WAIT_DECISION_OPERATION_ID,WAIT_ST_NUMBER,WAIT_TARGET_TT_ID,\n                       CREATED_AT,")
source="""(select wt.*,wp.PLAN_OPERATION_ID WAIT_PLAN_OPERATION_ID,wr.DECISION_OPERATION_ID WAIT_DECISION_OPERATION_ID,
                         wd.ST_NUMBER WAIT_ST_NUMBER,wd.TARGET_TT_ID WAIT_TARGET_TT_ID
                    from RRL_WAREHOUSE_TASK wt left join RRL_ST_DEFER_WAIT_PLAN wp on wp.TASK_ID=wt.TASK_ID
                    left join RRL_ST_DEFER_WAIT_RUN wr on wr.OPERATION_ID=wp.PLAN_OPERATION_ID
                    left join RRL_ST_DEFER_DECISION wd on wd.OPERATION_ID=wr.DECISION_OPERATION_ID) RRL_WAREHOUSE_TASK"""
sql=sql.replace("from RRL_WAREHOUSE_TASK\n", "from "+source+"\n",1)
method=old[:old.index("        return self.gateway.fetch_all(")]
method=method.replace("def list_tasks(", "def list(")
method=method.replace('conditions = []','conditions: list[str] = []')
method=method.replace("clamp_limit(limit)", "min(max(limit,1),500)")
method=method.replace("SOURCE_DOC_TYPE in('ST_DEFER','ST_DEFER_CASE')", "(SOURCE_DOC_TYPE in('ST_DEFER','ST_DEFER_CASE') or WAIT_PLAN_OPERATION_ID is not null)")
method += "        return self.gateway.fetch_all(_LIST_SQL.format(where_sql=where_sql),params)\n\n"
detail=old[old.index("    def get_task_or_404("):]
detail=detail.replace("def get_task_or_404(", "def get(").replace(") -> dict[str, Any]:", ") -> dict[str, Any] | None:",1)
detail=detail.replace("select t.*,", "select t.*,wp.PLAN_OPERATION_ID WAIT_PLAN_OPERATION_ID,wr.DECISION_OPERATION_ID WAIT_DECISION_OPERATION_ID,\n                   wd.ST_NUMBER WAIT_ST_NUMBER,wd.TARGET_TT_ID WAIT_TARGET_TT_ID,",1)
detail=detail.replace("from RRL_WAREHOUSE_TASK t\n", "from RRL_WAREHOUSE_TASK t left join RRL_ST_DEFER_WAIT_PLAN wp on wp.TASK_ID=t.TASK_ID\n              left join RRL_ST_DEFER_WAIT_RUN wr on wr.OPERATION_ID=wp.PLAN_OPERATION_ID\n              left join RRL_ST_DEFER_DECISION wd on wd.OPERATION_ID=wr.DECISION_OPERATION_ID\n",1)
detail=detail.replace('        if not rows:\n            raise HTTPException(status_code=404, detail="Warehouse task not found.")\n        return rows[0]', '        return rows[0] if rows else None')
new='''"""Original bounded task queue; immutable deferral binding identifies HU waiting tasks."""
from __future__ import annotations
from typing import Any
from fastapi import HTTPException

_LIST_SQL = '''+repr(sql)+'''

class TaskQueueRead:
    def __init__(self,gateway: Any) -> None:
        self.gateway=gateway

'''+method+detail
files["api/wms_api_server/app/modules/inventory/infrastructure/task_queue_read.py"]=new
signature=old[:old.index("        conditions = []")]
wrapper=signature+'''        from ..modules.inventory.public import build_task_queue_read
        return build_task_queue_read(self.gateway).list(
            status=status,task_type=task_type,task_source=task_source,assigned_to=assigned_to,
            production_order_id=production_order_id,source_doc_type=source_doc_type,source_doc_id=source_doc_id,
            limit=limit,scope_warehouse_id=scope_warehouse_id,scope_global=scope_global,queue_group=queue_group,
        )

    def get_task_or_404(self,task_id: int) -> dict[str, Any]:
        from ..modules.inventory.public import build_task_queue_read
        task=build_task_queue_read(self.gateway).get(task_id)
        if task is None:
            raise HTTPException(404,detail="Warehouse task not found.")
        return task

'''
files[p]=t[:start]+wrapper+t[end:]
p="api/wms_api_server/app/modules/inventory/public.py";t=Path(p).read_text(encoding="utf-8")
t+='''

from .infrastructure.task_queue_read import TaskQueueRead


def build_task_queue_read(gateway: Any) -> TaskQueueRead:
    return TaskQueueRead(gateway)
'''
files[p]=t
p="wiki-raw/wms_admin_ui_reference/warehouse-tasks.js";t=Path(p).read_text(encoding="utf-8")
needle='  if (task.task_type === "PUTAWAY" && ["ST_DEFER","ST_DEFER_CASE"].includes(task.source_doc_type))'
assert needle in t;t=t.replace(needle,'  if(task.wait_plan_operation_id&&task.unit_code==="HU")return "Целое HU в ожидание рейса";\n'+needle,1)
needle="  if (task.source_doc_type) parts.push("
pos=t.index(needle);t=t[:pos]+'  if(task.wait_plan_operation_id)parts.push("Ожидание СТ "+task.wait_st_number+" · рейс решения "+task.wait_target_tt_id);\n'+t[pos:]
files[p]=t
p="wiki-raw/wms_admin_ui_reference/st-deferral.js";t=Path(p).read_text(encoding="utf-8")
t=t.replace("Полный отбор плоских товарных паллет сохраняется; CASE и вложенные места требуют отдельного решения.", "Отбор сохраняется. Подготовленные CASE и целое вложенное HU перемещаются штатными заданиями; система проверяет весь исходный состав.")
files[p]=t
for p in("wiki-raw/wms_admin_ui_reference/warehouse-tasks.html","wiki-raw/wms_admin_ui_reference/transport-dispatch.html"):
 if not Path(p).exists():continue
 t=Path(p).read_text(encoding="utf-8")
 t=re.sub(r'warehouse-tasks.js\?v=[^"]+','warehouse-tasks.js?v=20261013-1065',t)
 t=re.sub(r'st-deferral.js\?v=[^"]+','st-deferral.js?v=20261013-1065',t);files[p]=t
print(json.dumps(files,ensure_ascii=True))
