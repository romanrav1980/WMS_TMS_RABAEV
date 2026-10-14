from pathlib import Path
import json
root=Path(__file__).resolve().parents[1]
files={}
def replace(path,old,new):
 p=root/path
 s=files.get(path,p.read_text(encoding="utf-8"))
 assert old in s,path
 files[path]=s.replace(old,new,1)
replace("wiki-raw/wms_admin_ui_reference/warehouse-tasks.js",
'''  if (warehouseTaskState.selectedTask && !warehouseTaskState.tasks.some((task) => task.task_id === warehouseTaskState.selectedTask.task_id)) {
    warehouseTaskState.selectedTask = null;
  }''',
'''  if (warehouseTaskState.selectedTask) {
    warehouseTaskState.selectedTask = warehouseTaskState.tasks.find(
      task => Number(task.task_id) === Number(warehouseTaskState.selectedTask.task_id)
    ) || null;
  }''')
replace("wiki-raw/wms_admin_ui_reference/warehouse-tasks.js",
'''async function showWarehouseTaskProgress(taskId) {
  const progress = await warehouseTaskFetch(`/api/warehouse-tasks/${taskId}/progress`);
  if (Number(warehouseTaskState.selectedTask?.task_id) !== Number(taskId)) return;''',
'''async function showWarehouseTaskProgress(taskId) {
  const epoch=warehouseTaskState.readEpoch;
  const identity=JSON.stringify([warehouseTaskApiBase(),window.wmsAdminAuth?.state?.user?.username]);
  const progress = await warehouseTaskFetch(`/api/warehouse-tasks/${taskId}/progress`);
  if (epoch!==warehouseTaskState.readEpoch ||
    identity!==JSON.stringify([warehouseTaskApiBase(),window.wmsAdminAuth?.state?.user?.username]) ||
    Number(warehouseTaskState.selectedTask?.task_id) !== Number(taskId)) return;''')
replace("wiki-raw/wms_admin_ui_reference/resource-nearest.js",
'''   output.textContent=JSON.stringify(data,null,2);
   message.textContent=mutation?'Назначение подтверждено сервером. Начало и физическое выполнение — отдельные действия.':'Показаны только свободные квалифицированные ресурсы со свежей позицией.';
   if(mutation&&typeof loadWarehouseTasks==='function')await loadWarehouseTasks();''',
'''   if(mutation&&typeof loadWarehouseTasks==='function'){
    try{await loadWarehouseTasks();}
    catch(error){
     if(scope===identity()&&id===input.value){
      output.textContent=JSON.stringify(data,null,2);
      message.textContent='Назначение подтверждено сервером, но очередь не обновилась. Обновите её; повторять назначение не требуется. '+error.message;
     }
     return;
    }
   }
   if(scope!==identity()||id!==input.value)return;
   output.textContent=JSON.stringify(data,null,2);
   message.textContent=mutation?'Назначение подтверждено сервером. Начало и физическое выполнение — отдельные действия.':'Показаны только свободные квалифицированные ресурсы со свежей позицией.';''')
p=root/"wiki/requirements/nikora_delivery_v55/implementation_plan.json"
plan=json.loads(p.read_text(encoding="utf-8"))
plan["continuationStopConditions"]["deadlineMoscow"]="2026-10-13T20:00:00+03:00"
plan["continuationStopConditions"]["source"]="Latest user instruction 13Oct: continue until all sprints complete or20:00 MSK today; full commit/GitHub after actual all completion"
files[str(p.relative_to(root))]=json.dumps(plan,ensure_ascii=False,indent=2)+"\n"
p=root/"wiki/runbooks/nicora_active_work.md"
files[str(p.relative_to(root))]=("## Continuation827 — 13Oct2026\n\nLatest owner instruction supersedes18:30: continue until all sprints actually complete or20:00 MSK today17:00UTC. Current NI07.2; one implemented dev increment NI03.1, other17 not fully closed. No publication until actual completion. UI827 refresh replaces selected card from current list and guards old progress by readEpoch/identity; resource-confirmed assignment survives queue reload/error without suggesting duplicate dispatch. Focused verification pending.\n\n"+p.read_text(encoding="utf-8"))
print(json.dumps(files,ensure_ascii=True))
