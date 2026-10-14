// Existing task family is the authority for quantities and the next task.
(() => {
 const node=(tag,text,cls)=>{const n=document.createElement(tag);n.textContent=text;if(cls)n.className=cls;return n;};
 const statuses={PLANNED:'Запланировано',ASSIGNED:'Назначено',IN_PROGRESS:'В работе',DONE:'Выполнено',CANCELLED:'Отменено',ERROR:'Ошибка'};
 function container(){
  let panel=document.getElementById('warehouseTaskFamily');
  if(!panel){panel=node('section','','wt-family');panel.id='warehouseTaskFamily';panel.setAttribute('aria-label','Цепочка исполнения задания');document.getElementById('warehouseTaskDetail').append(panel);}
  return panel;
 }
 function clear(){const panel=document.getElementById('warehouseTaskFamily');if(panel){panel.replaceChildren();panel.hidden=true;}}
 function link(id,label){const a=node('a',label);a.href='warehouse-tasks.html?task_id='+encodeURIComponent(id)+'#warehouseTaskDetail';a.title='Прочитать актуальное задание; назначение и проведение автоматически не выполняются';return a;}
 function render(progress,selected){
  const panel=container();panel.hidden=false;panel.replaceChildren(node('h3','Цепочка исполнения #'+progress.root_task_id));
  panel.append(node('p','Подтверждено: '+progress.confirmed_quantity+' · осталось в активных заданиях: '+progress.remaining_quantity+' '+(progress.unit_code||''),'wt-family-total'));
  panel.append(node('p','Факт суммируется только по выполненным этапам. Отменённые этапы не считаются выполненными. Количества исходного задания и его продолжений не складываются повторно.','wt-family-note'));
  if(progress.next_task_id)panel.append(link(progress.next_task_id,'Открыть следующее задание #'+progress.next_task_id));
  else panel.append(node('p',progress.status==='CANCELLED'?'Активных продолжений нет. В цепочке есть отменённые этапы — это не подтверждение полного исполнения.':'Активных продолжений нет; факты этапов приведены ниже.'));
  if(['HU','CASE','PALLET'].includes(progress.unit_code))panel.append(node('p','Количество указано в грузовых местах '+progress.unit_code+', а не в единицах товара.','wt-family-note'));
  const list=node('div','','wt-family-list');
  const rows=[...(progress.tasks||[])].sort((a,b)=>Number(a.task_id)-Number(b.task_id));
  for(const row of rows){
   const card=node('article','','wt-family-step'+(Number(row.task_id)===Number(selected)?' is-selected':''));card.dataset.taskId=String(row.task_id);
   const head=node('div','','wt-family-head');head.append(link(row.task_id,'#'+row.task_id),node('strong',statuses[row.status]||row.status));card.append(head);
   card.append(node('p',row.parent_task_id?'Продолжение задания #'+row.parent_task_id:'Исходное задание'));
   card.append(node('p',(row.from_cell||'—')+' → '+(row.to_cell||'—')));
   card.append(node('p','Задано этапу: '+(row.quantity??'—')+' '+(row.unit_code||'')+' · подтверждённый факт: '+(row.status==='DONE'?(row.fact_quantity??'не указан'):'не подтверждён')));
   card.append(node('p','Исполнитель: '+(row.assigned_to||'не назначен')+(row.equipment_id?' · техника '+row.equipment_id:'')));
   if(row.uid_pallet||row.sscc)card.append(node('p','Идентификатор паллеты: '+(row.uid_pallet||row.sscc)));
   if(row.status==='ERROR')card.append(node('p','Откройте задание для причины отказа и разрешённого продолжения.','wt-family-note'));
   list.append(card);
  }
  panel.append(list);
 }
 window.warehouseTaskFamily={render,clear};
 window.addEventListener('warehouse-task-selected',clear);
 window.addEventListener('wms-admin-auth-ready',clear);
})();