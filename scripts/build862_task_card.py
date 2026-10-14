from pathlib import Path
import json
files={}
p="wiki-raw/wms_admin_ui_reference/warehouse-tasks.html";s=Path(p).read_text(encoding="utf-8")
start=s.index('            <p class="task-selection-caption">')
end=s.index('            <div class="rights-summary"><span id="warehouseTaskDetailStatus">',start)
summary=s[start:end]
s=s[:start]+s[end:]
position=s.index('            <div class="rights-table-wrap warehouse-task-scroll">')
s=s[:position]+summary+s[position:]
s=s.replace('<header><h2>Карточка задания</h2></header>','<header><h2>Карточка задания</h2><a id="warehouseTaskWaveLink" hidden title="Открыть исполнение исходной волны и причины незавершения">Исполнение волны →</a></header>')
files[p]=s.replace('20261013-856','20261013-862')
p="wiki-raw/wms_admin_ui_reference/warehouse-tasks.js";s=Path(p).read_text(encoding="utf-8")
pos='  warehouseTaskEl("warehouseTaskDetailParent").textContent'
idx=s.index(pos)
s=s[:idx]+"""  const waveLink=warehouseTaskEl('warehouseTaskWaveLink');
  if(waveLink){
    const wave=Number(task?.source_doc_id);
    waveLink.hidden=!(task?.task_source==='WAVE' && Number.isSafeInteger(wave)&&wave>0 && warehouseTaskCan('pick_wave_view'));
    if(!waveLink.hidden)waveLink.href='wave-replenishment.html?wave_id='+wave+'#waveExecution';
    else waveLink.removeAttribute?.('href');
  }
"""+s[idx:]
files[p]=s
p="reports/retailcase/2026-10-13/08-partial-shared-report.md";files[p]=Path(p).read_text(encoding="utf-8")+"\n![Выполненная общая подача1097](screenshots/10-partial-shared-task.png)\n\nРеальный браузер: DONE, план/факт12 EA, остаток0, ссылка открывает карточку после загрузки.\n"
print(json.dumps(files,ensure_ascii=True))
