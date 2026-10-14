from pathlib import Path
import json
p=Path('wiki-raw/wms_admin_ui_reference/warehouse-tasks.js');t=p.read_text(encoding='utf-8')
t=t.replace('  initialTaskId: null,','  initialTaskId: null,\n  readEpoch: 0,')
old='  warehouseTaskState.allTasks = await warehouseTaskFetch(`/api/warehouse-tasks?${warehouseTaskParams().toString()}`);'
new='''  const token=++warehouseTaskState.readEpoch;
  const identity=JSON.stringify([warehouseTaskApiBase(),window.wmsAdminAuth?.state?.user?.username]);
  const query=warehouseTaskParams().toString();
  const tasks=await warehouseTaskFetch(`/api/warehouse-tasks?${query}`);
  if(token!==warehouseTaskState.readEpoch||query!==warehouseTaskParams().toString()||
    identity!==JSON.stringify([warehouseTaskApiBase(),window.wmsAdminAuth?.state?.user?.username]))return;
  warehouseTaskState.allTasks=tasks;'''
assert old in t;t=t.replace(old,new)
t=t.replace('  const task = warehouseTaskState.selectedTask;\n  warehouseTaskEl("warehouseTaskSelectionText")','''  const task = warehouseTaskState.selectedTask;
  const terminal=!task||["DONE","CANCELLED"].includes(task.status);
  for(const id of ["warehouseTaskAssign","warehouseTaskStart","warehouseTaskComplete","warehouseTaskCancel"]){
    warehouseTaskEl(id).disabled=terminal;
    warehouseTaskEl(id).title=terminal?"Выберите незавершённое задание":"Отправить действие серверу для проверки прав и текущего состояния";
  }
  warehouseTaskEl("warehouseTaskSelectionText")''')
t=t.replace('    row.addEventListener("click", () => selectWarehouseTask(Number(row.dataset.taskId)));','''    row.tabIndex=0;row.title="Открыть карточку задания";
    row.addEventListener("click", () => selectWarehouseTask(Number(row.dataset.taskId)));
    row.addEventListener("keydown",event=>{if(event.key==="Enter"||event.key===" "){event.preventDefault();selectWarehouseTask(Number(row.dataset.taskId));}});''')
p2=Path('wiki-raw/wms_admin_ui_reference/warehouse-tasks.html')
print(json.dumps({str(p):t,str(p2):p2.read_text(encoding='utf-8').replace('20261013-803','20261013-804')},ensure_ascii=True))
