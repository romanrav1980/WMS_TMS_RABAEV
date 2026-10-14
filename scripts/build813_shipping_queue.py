from pathlib import Path
import json
files={};p=Path('api/wms_api_server/app/services/warehouse_task_service.py');t=p.read_text(encoding='utf-8')
t=t.replace('        scope_global: bool = True,\n    ) -> list[dict[str, Any]]:', '        scope_global: bool = True,\n        queue_group: str | None = None,\n    ) -> list[dict[str, Any]]:',1)
t=t.replace('        where_sql = " where " + " and ".join(conditions) if conditions else ""', '''        if queue_group:
            if queue_group != "SHIPPING":
                raise HTTPException(422, detail="Unknown warehouse task queue group")
            conditions.append("(TASK_TYPE='PICKING_MOVE' or (TASK_TYPE='REPLENISHMENT' and SOURCE_DOC_TYPE='SHIPMENT'))")
        where_sql = " where " + " and ".join(conditions) if conditions else ""''',1)
files[str(p)]=t
p=Path('api/wms_api_server/app/routers/warehouse_tasks.py');t=p.read_text(encoding='utf-8').replace('from fastapi import APIRouter, Depends, HTTPException','from fastapi import APIRouter, Depends, HTTPException, Query').replace('from typing import TypeVar','from typing import TypeVar, Literal')
t=t.replace('    limit: int = 100,','    limit: int = Query(default=100, ge=1, le=500),\n    queue_group: Literal["SHIPPING"] | None = None,',1)
t=t.replace('limit=limit,scope_warehouse_id=scope.warehouse_id,scope_global=scope.global_admin,','limit=limit,scope_warehouse_id=scope.warehouse_id,scope_global=scope.global_admin,queue_group=queue_group,',1)
files[str(p)]=t
p=Path('wiki-raw/wms_admin_ui_reference/warehouse-tasks.js');t=p.read_text(encoding='utf-8')
t=t.replace('  if (sourceDoc) params.set("source_doc_id", sourceDoc);','  if (sourceDoc) params.set("source_doc_id", sourceDoc);\n  if(warehouseTaskState.preset==="shipping-zone")params.set("queue_group","SHIPPING");')
old='''  } else if (preset === "shipping-zone") {
    warehouseTaskEl("warehouseTaskType").value = "REPLENISHMENT";
    warehouseTaskEl("warehouseTaskSource").value = "WAVE";'''
new='''  } else if (preset === "shipping-zone") {
    warehouseTaskEl("warehouseTaskType").value = "";
    warehouseTaskEl("warehouseTaskSource").value = "";'''
assert old in t;t=t.replace(old,new)
t=t.replace('`Заданий: ${tasks.length}, активных: ${activeCount}`','`В выборке: ${tasks.length}, активных: ${activeCount}${warehouseTaskState.allTasks.length>=Number(warehouseTaskEl("warehouseTaskLimit").value||150)?"; достигнут лимит выдачи":""}`')
files[str(p)]=t
p=Path('wiki-raw/wms_admin_ui_reference/warehouse-tasks.html');t=p.read_text(encoding='utf-8').replace('20261013-807','20261013-813').replace('<div class="warehouse-task-kind-grid">','<p class="task-selection-caption">Сводка по текущей выборке</p>\n            <div class="warehouse-task-kind-grid">')
files[str(p)]=t
print(json.dumps(files,ensure_ascii=True))
