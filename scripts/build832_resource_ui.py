from pathlib import Path
import json
p=Path("wiki-raw/wms_admin_ui_reference/resource-nearest.js")
s=p.read_text(encoding="utf-8")
s=s.replace('<pre></pre>', '<div class="nearest-resource-results" role="region" aria-label="Свободные ресурсы"></div>')
s=s.replace("output=panel.querySelector('pre');","output=panel.querySelector('.nearest-resource-results');")
s=s.replace("let busy=false,terminal=false;","let busy=false,terminal=false,selectedStatus=null;")
s=s.replace("busy||terminal||!valid||!auth?.hasPermission('resource_dispatch_manage');","busy||terminal||!valid||(selectedStatus!==null&&selectedStatus!=='PLANNED')||!auth?.hasPermission('resource_dispatch_manage');")
anchor=" async function action(button){"
render=""" function renderCandidates(data,mutation){
  output.replaceChildren();
  const rows=mutation?[data]:data;
  if(!Array.isArray(rows))throw Error('Неожиданный ответ списка ресурсов. Перечитайте задание.');
  if(!rows.length){output.textContent='Свободных квалифицированных ресурсов со свежей позицией сейчас нет.';return;}
  const table=document.createElement('table');table.className='nearest-resource-table';
  const head=document.createElement('thead'),headRow=document.createElement('tr');
  for(const title of ['Исполнитель','Ресурс','Техника','Последняя ячейка','Расстояние, ед. координат','Позиция подтверждена']){
   const th=document.createElement('th');th.textContent=title;headRow.appendChild(th);
  }
  head.appendChild(headRow);table.appendChild(head);
  const body=document.createElement('tbody');
  for(const item of rows){
   const row=document.createElement('tr');
   for(const value of [item.assigned_to,item.resource_id,item.equipment_id,item.last_cell,item.distance,item.last_position_at]){
    const cell=document.createElement('td');cell.textContent=String(value??'—');row.appendChild(cell);
   }
   body.appendChild(row);
  }
  table.appendChild(body);output.appendChild(table);
 }
"""
assert anchor in s;s=s.replace(anchor,render+anchor,1)
s=s.replace("output.textContent=JSON.stringify(data,null,2);","renderCandidates(data,mutation);")
s=s.replace("input.addEventListener('input',()=>{terminal=false;","input.addEventListener('input',()=>{terminal=false;selectedStatus=null;")
s=s.replace("const task=event.detail;input.value=", "const task=event.detail;selectedStatus=task?.status??null;input.value=")
s=s.replace("input.value='';output.textContent='';terminal=false;controls();","input.value='';output.textContent='';terminal=false;selectedStatus=null;controls();")
# Button hints describe server status authority.
s=s.replace("panel.querySelector('[data-action=\"dispatch-nearest\"]').disabled=", "panel.querySelector('[data-action=\"dispatch-nearest\"]').title=selectedStatus&&selectedStatus!=='PLANNED'?'Назначение доступно только для ещё не назначенного задания PLANNED':'Сервер выберет ближайший свободный квалифицированный ресурс и назначит его заданию';\n  panel.querySelector('[data-action=\"dispatch-nearest\"]').disabled=")
files={str(p):s}
p=Path("wiki-raw/wms_admin_ui_reference/warehouse-tasks.css")
files[str(p)]=p.read_text(encoding="utf-8")+"""
.warehouse-operations .nearest-resource-results{flex-basis:100%;overflow:auto}
.warehouse-operations .nearest-resource-table{width:100%;border-collapse:collapse;font-size:13px}
.warehouse-operations .nearest-resource-table th{background:#f4f7fc;color:#64758a;text-align:left;font-weight:600}
.warehouse-operations .nearest-resource-table th,.warehouse-operations .nearest-resource-table td{padding:12px;border-bottom:1px solid #e3eaf4;white-space:nowrap}
"""
p=Path("wiki-raw/wms_admin_ui_reference/warehouse-tasks.html")
files[str(p)]=p.read_text(encoding="utf-8").replace("20261013-830","20261013-832")
print(json.dumps(files,ensure_ascii=True))
