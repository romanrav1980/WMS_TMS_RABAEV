from pathlib import Path
import json
p=Path('wiki-raw/wms_admin_ui_reference/warehouse-tasks.js');t=p.read_text(encoding='utf-8')
t=t.replace('  readEpoch: 0,','  readEpoch: 0,\n  confirmedBound: false,')
t=t.replace('function initWarehouseTasks() {\n  window.warehouseTaskRecovery.init(warehouseTaskFetch);','''function initWarehouseTasks() {
  warehouseTaskState.readEpoch++;
  warehouseTaskState.allTasks=[];warehouseTaskState.tasks=[];warehouseTaskState.selectedTask=null;
  renderWarehouseTasks();renderWarehouseTaskSummary();renderWarehouseTaskDetail();
  window.warehouseTaskRecovery.init(warehouseTaskFetch);
  if(!warehouseTaskState.confirmedBound){
  warehouseTaskState.confirmedBound=true;''')
needle='''    warehouseTaskEl("warehouseTaskSelectionText").textContent = message;
  });
  loadWarehouseTasks().catch(showWarehouseTaskError);
}'''
replacement='''    warehouseTaskEl("warehouseTaskSelectionText").textContent = message;
  });
  }
  loadWarehouseTasks().catch(showWarehouseTaskError);
}'''
assert needle in t;t=t.replace(needle,replacement,1)
p2=Path('wiki-raw/wms_admin_ui_reference/warehouse-tasks.html');t2=p2.read_text(encoding='utf-8').replace('20261013-813','20261013-816')
print(json.dumps({str(p):t,str(p2):t2},ensure_ascii=True))
