from pathlib import Path
import json
files={}
p=Path("wiki-raw/wms_admin_ui_reference/st-deferral.js")
t=p.read_text(encoding="utf-8")
old="function pending(){const raw=localStorage.getItem(key());return raw?JSON.parse(raw):null;}"
new="""function pending(){
  const raw=localStorage.getItem(key());if(!raw)return null;
  const p=JSON.parse(raw),fields=['operation_id','st_number','target_trip_id','expected_version','source_hash','reason','reference'];
  if(!p||typeof p!=='object'||Array.isArray(p)||Object.keys(p).length!==fields.length||
   fields.some(f=>!Object.hasOwn(p,f))||typeof p.operation_id!=='string'||!p.operation_id.startsWith('STDEFER:')||
   typeof p.st_number!=='string'||!p.st_number.trim()||!Number.isSafeInteger(p.target_trip_id)||p.target_trip_id<1||
   !Number.isSafeInteger(p.expected_version)||p.expected_version<0||typeof p.source_hash!=='string'||!p.source_hash||
   typeof p.reason!=='string'||p.reason.trim().length<8||typeof p.reference!=='string'||p.reference.trim().length<8)
    throw Error('Сохранённая команда повреждена. Новая отправка заблокирована; исходник сохранён.');
  return p;
 }"""
assert old in t
t=t.replace(old,new)
t=t.replace("let p;try{p=pending();}catch{}","let p,damaged=false;try{p=pending();}catch{damaged=true;}")
t=t.replace("busy||!context||!!p||!valid","busy||!context||!!p||damaged||!valid")
t=t.replace("el(id).disabled=busy||!!p;","el(id).disabled=busy||!!p||damaged;")
t=t.replace("el('sdRetry').disabled=busy||!p;","el('sdRetry').disabled=busy||!p||damaged;")
t=t.replace("busy||!context||!!p;","busy||!context||!!p||damaged;")
t=t.replace("el('sdPending').textContent=p?","el('sdPending').textContent=damaged?'Сохранённая команда повреждена. Исходник сохранён, новая отправка заблокирована.':p?")
t=t.replace("busy=true;controls();","const requestKey=key(),requestRaw=localStorage.getItem(requestKey);\n  busy=true;controls();",1)
t=t.replace("localStorage.removeItem(key());context=null;","if(localStorage.getItem(requestKey)!==requestRaw)throw Error('Команда в другой вкладке изменилась. Её исходник сохранён.');\n   localStorage.removeItem(requestKey);context=null;")
t=t.replace("controls();\n})();","window.addEventListener('storage',event=>{if(event.key===key())controls();});\n controls();\n})();")
files[str(p)]=t
p=Path("wiki-raw/wms_admin_ui_reference/reachtruck-tsd.js");t=p.read_text(encoding="utf-8")
t=t.replace('function rtTsdOperation(task) {','function rtTsdOperation(task) {\n  if (task.task_type === "PUTAWAY" && task.source_doc_type === "ST_DEFER") return "Переместить в ожидание";')
t=t.replace('parts.push(task.source_doc_type);','parts.push(task.source_doc_type === "ST_DEFER" ? "Перенос СТ" : task.source_doc_type);')
files[str(p)]=t
p=Path("reports/retailcase/2026-10-13/index.html");t=p.read_text(encoding="utf-8")
t=t.replace("</main>","<article><h2>02 · Выбор рейса</h2><p>Период дат, район и код магазина. Выбор использует существующие рейсы ТМС.</p><p><a href=\"02-trip-picker-report.md\">Отчёт</a></p><img src=\"screenshots/04-trip-picker.png\" alt=\"Реальное окно выбора рейса\"></article></main>")
files[str(p)]=t
print(json.dumps(files,ensure_ascii=True))
