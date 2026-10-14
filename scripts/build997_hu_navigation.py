from pathlib import Path
import json
read=lambda p:Path(p).read_text(encoding="utf-8")
files={}
p="wiki-raw/wms_admin_ui_reference/warehouse-tasks.js"
v=read(p)
needle='  const waveLink=warehouseTaskEl(\'warehouseTaskWaveLink\');'
assert needle in v
v=v.replace(needle,'''  const huLink=warehouseTaskEl("warehouseTaskHuLink");
  if(huLink){
    const identifier=task?.uid_pallet||task?.sscc;
    huLink.hidden=!(task?.unit_code==="HU"&&identifier&&warehouseTaskCan("warehouse_task_view"));
    if(!huLink.hidden)huLink.href="warehouse-hus.html?identifier="+encodeURIComponent(identifier)+"#huComposition";
    else huLink.removeAttribute("href");
  }
'''+needle,1)
v=v.replace('if(caseNote)caseNote.hidden=task?.source_doc_type!=="ST_DEFER_CASE";','''if(caseNote){
    const hu=task?.unit_code==="HU";
    caseNote.hidden=!(hu||task?.source_doc_type==="ST_DEFER_CASE");
    caseNote.textContent=hu
      ?"Перемещается одно грузовое место HU со всеми вложениями. Количество мест не равно количеству товара. Ссылка «Текущий состав HU» показывает состав сейчас; после распаковки он может отличаться от состава при выполнении задания."
      :"Перемещается одно готовое грузовое место CASE целиком. Товарные количества и резервы каждой партии сохраняются; «1 CASE» означает число мест, а не одну единицу товара.";
  }''',1)
v=v.replace('function qtyModeText(task) {','function qtyModeText(task) {\n  if(task.unit_code==="HU")return "HU · одно место";',1)
files[p]=v
p="wiki-raw/wms_admin_ui_reference/warehouse-tasks.html"
v=read(p).replace('</a></header>','</a> <a id="warehouseTaskHuLink" hidden>Текущий состав HU →</a></header>',1)
v=v.replace('warehouse-tasks.js?v=20261013-969','warehouse-tasks.js?v=20261013-997')
files[p]=v
p="wiki-raw/wms_admin_ui_reference/warehouse-hus.js"
v=read(p)
v=v.replace('  let view=null,pending=null,busy=false,generation=0,identity="";','''  let view=null,pending=null,busy=false,generation=0,identity="";
  const requestedIdentifier=new URLSearchParams(window.location.search).get("identifier")||"";''',1)
v=v.replace('link.href="warehouse-tasks.html";','link.href="warehouse-tasks.html?task_id="+encodeURIComponent(data.task_id)+"#warehouseTaskDetail";',1)
needle='    controls();\n  }\n  window.addEventListener("wms-admin-auth-ready",auth);auth();'
assert needle in v
v=v.replace(needle,'''    if(!pending&&requestedIdentifier)el("huIdentifier").value=requestedIdentifier;
    controls();
    if(!pending&&requestedIdentifier)load();
  }
  window.addEventListener("wms-admin-auth-ready",auth);auth();''',1)
files[p]=v
p="wiki-raw/wms_admin_ui_reference/warehouse-hus.html"
files[p]=read(p).replace('<section class="panel"><label>Идентификатор','<section id="huComposition" class="panel"><label>Идентификатор',1).replace('<div id="huSummary"></div>','<p class="subtle">Показан текущий состав места. Отгруженное место показывает сохранённый состав на момент отгрузки.</p><div id="huSummary"></div>',1).replace('warehouse-hus.js"></script>','warehouse-hus.js?v=20261013-997"></script>',1)
print(json.dumps(files,ensure_ascii=True))
