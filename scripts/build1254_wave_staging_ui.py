import json
from pathlib import Path
p=Path("wiki-raw/wms_admin_ui_reference/wave-replenishment.js");s=p.read_text(encoding="utf-8")
old='+ `<td><span class="task-badge ${waveStatusClass(warehouseStatus)}">${escapeWaveRepHtml(warehouseStatus)}</span><small>${escapeWaveRepHtml(task.warehouse_task_id || "")}</small></td>`'
new='+ `<td><span class="task-badge ${waveStatusClass(warehouseStatus)}">${escapeWaveRepHtml(warehouseStatus)}</span>${Number.isSafeInteger(task.warehouse_task_id)&&task.warehouse_task_id>0 ? `<a class="wave-execution-action" href="warehouse-tasks.html?task_id=${task.warehouse_task_id}#warehouseTaskDetail">Выполнить задание #${task.warehouse_task_id}</a>` : ""}</td>`'
assert old in s;s=s.replace(old,new)
s=s.replace('Нет full-pallet строк для грузовой зоны','Нет заданий целых паллет для грузовой зоны')
s=s.replace('detail:{wave_id:waveId}}));\n  await loadWaveReplenishmentTasks();','detail:{wave_id:wave.pick_wave_id}}));\n  await loadWaveReplenishmentTasks();')
a=s.index('async function runStagingRelease()');b=s.index('async function loadPickFaces()',a)
s=s[:a]+'''async function runStagingRelease() {
  const wave=waveReplenishmentState.selectedWave,button=waveRepEl("waveStagingRelease");
  if(!wave||button.disabled)throw new Error("Выберите волну и дождитесь завершения запроса");
  if(!waveRepCan("pick_wave_launch"))throw new Error("Нет права pick_wave_launch");
  const toCell=waveRepEl("waveStagingToCell").value.trim();
  if(!toCell)throw new Error("Укажите грузовую зону");
  const identity=waveRepIdentity(),epoch=waveReplenishmentState.selectionEpoch;
  const current=()=>identity===waveRepIdentity()&&epoch===waveReplenishmentState.selectionEpoch&&waveReplenishmentState.selectedWave?.pick_wave_id===wave.pick_wave_id;
  button.disabled=true;
  waveRepEl("waveReplenishmentDetailStatus").textContent="Выпуск задач в грузовую зону…";
  try{
    const result=await waveRepFetch('/api/picking/waves/'+wave.pick_wave_id+'/staging/release',{
      method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({to_cell:toCell})});
    if(!current())return;
    if(result.pick_wave_id!==wave.pick_wave_id||result.status!=="RELEASED")throw new Error("Ответ не подтверждает выбранную волну");
    await loadWaveStagingTasks();
    if(current())waveRepEl("waveReplenishmentDetailStatus").textContent="В грузовую зону выпущено: "+(result.released_count||0)+". Откройте задания ниже; повтор с тем же адресом не создаёт дубли.";
  }catch(error){
    if(current())waveRepEl("waveReplenishmentDetailStatus").textContent=error.message+". Перечитайте задания перед повтором; сохраняйте прежний адрес назначения.";
  }finally{button.disabled=!waveRepCan("pick_wave_launch");}
}

'''+s[b:]
print(json.dumps({str(p):s}))
