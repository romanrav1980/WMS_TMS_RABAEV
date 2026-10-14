from pathlib import Path
import json
files={};p=Path('wiki-raw/wms_admin_ui_reference/st-trip-picker.js');t=p.read_text(encoding='utf-8')
t=t.replace("el('tpSearch').disabled=busy;", "for(const id of ['tpFrom','tpTo','tpDistrict','tpStore'])el(id).disabled=busy;\n  el('tpSearch').disabled=busy;")
t=t.replace(" el('tpNext').addEventListener('click',()=>search(true));", """ el('tpNext').addEventListener('click',()=>search(true));
 for(const id of ['tpFrom','tpTo','tpDistrict','tpStore'])el(id).addEventListener('input',()=>{
  if(!source||busy)return;epoch++;rows=[];cursor=null;render();controls();
  el('tpMessage').textContent='Фильтры изменены. Нажмите «Найти рейсы», чтобы обновить список.';
  el('tpEmpty').textContent='Список ожидает поиска по выбранным фильтрам.';
 });""")
files[str(p)]=t
p=Path('wiki-raw/wms_admin_ui_reference/day-reconciliation.html');t=p.read_text(encoding='utf-8')
for script in ['st-trip-picker.js','st-deferral.js','st-waiting-tasks.js']:
 t=t.replace('src="'+script+'"','src="'+script+'?v=20261013-812"')
files[str(p)]=t
print(json.dumps(files,ensure_ascii=True))
