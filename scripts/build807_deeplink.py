from pathlib import Path
import json
p=Path('wiki-raw/wms_admin_ui_reference/warehouse-tasks.js');t=p.read_text(encoding='utf-8')
old='''  if (warehouseTaskState.initialTaskId && !warehouseTaskState.selectedTask) {
    warehouseTaskState.selectedTask = warehouseTaskState.tasks.find((task) => Number(task.task_id) === warehouseTaskState.initialTaskId) || null;
  }
'''
assert old in t;t=t.replace(old,'')
needle='  renderWarehouseTasks();\n  renderWarehouseTaskSummary();\n  renderWarehouseTaskDetail();\n}'
new='''  if(warehouseTaskState.initialTaskId){
    const id=warehouseTaskState.initialTaskId;
    const linked=warehouseTaskState.tasks.find(task=>Number(task.task_id)===id)||await warehouseTaskFetch(`/api/warehouse-tasks/${id}`);
    if(token!==warehouseTaskState.readEpoch||identity!==JSON.stringify([warehouseTaskApiBase(),window.wmsAdminAuth?.state?.user?.username]))return;
    warehouseTaskState.initialTaskId=null;warehouseTaskState.selectedTask=linked;
  }
'''+needle
assert needle in t;t=t.replace(needle,new,1)
p2=Path('wiki-raw/wms_admin_ui_reference/warehouse-tasks.html');t2=p2.read_text(encoding='utf-8').replace('20261013-804','20261013-807')
print(json.dumps({str(p):t,str(p2):t2},ensure_ascii=True))
