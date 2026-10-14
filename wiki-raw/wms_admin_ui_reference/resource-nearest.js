(() => {
 const panel=document.createElement('section');panel.className='panel';
 panel.innerHTML='<h2>Назначить ближайший свободный ресурс</h2><label>ID задания <input type="number" min="1"></label><button data-action="candidates">Показать кандидатов</button><button data-action="dispatch-nearest">Назначить ближайшего</button><p role="status">Выберите задание. Для назначения требуется свободный квалифицированный ресурс со свежей позицией.</p><div class="nearest-resource-results" role="region" aria-label="Свободные ресурсы"></div>';
 (document.querySelector('main')||document.body).prepend(panel);
 const input=panel.querySelector('input'),message=panel.querySelector('p'),output=panel.querySelector('.nearest-resource-results');
 let busy=false,terminal=false,selectedStatus=null;
 const identity=()=>JSON.stringify([window.wmsAdminAuth?.state.apiBase,window.wmsAdminAuth?.state.user?.username]);
 function controls(){
  const auth=window.wmsAdminAuth,valid=/^[1-9][0-9]*$/.test(input.value)&&Number.isSafeInteger(Number(input.value));
  panel.hidden=!auth?.hasPermission('resource_management_view');input.disabled=busy;
  panel.querySelector('[data-action="candidates"]').disabled=busy||terminal||!valid;
  panel.querySelector('[data-action="dispatch-nearest"]').title=selectedStatus&&selectedStatus!=='PLANNED'?'Назначение доступно только для ещё не назначенного задания PLANNED':'Сервер выберет ближайший свободный квалифицированный ресурс и назначит его заданию';
  panel.querySelector('[data-action="dispatch-nearest"]').disabled=busy||terminal||!valid||(selectedStatus!==null&&selectedStatus!=='PLANNED')||!auth?.hasPermission('resource_dispatch_manage');
 }
 function renderCandidates(data,mutation){
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
 async function action(button){
  if(busy||button.disabled)return;const id=input.value,scope=identity(),mutation=button.dataset.action==='dispatch-nearest';
  busy=true;controls();
  try{
   const auth=window.wmsAdminAuth;
   const response=await fetch(auth.state.apiBase.replace(/\/$/,'')+'/api/resources/warehouse-tasks/'+id+'/'+button.dataset.action,{method:mutation?'POST':'GET',headers:auth.headers()});
   const data=await response.json();if(scope!==identity()||id!==input.value)return;
   if(!response.ok)throw Error(typeof data.detail==='string'?data.detail:JSON.stringify(data.detail||data));
   if(mutation&&typeof loadWarehouseTasks==='function'){
    try{await loadWarehouseTasks();}
    catch(error){
     if(scope===identity()&&id===input.value){
      renderCandidates(data,mutation);
      message.textContent='Назначение подтверждено сервером, но очередь не обновилась. Обновите её; повторять назначение не требуется. '+error.message;
     }
     return;
    }
   }
   if(scope!==identity()||id!==input.value)return;
   renderCandidates(data,mutation);
   message.textContent=mutation?'Назначение подтверждено сервером. Начало и физическое выполнение — отдельные действия.':'Показаны только свободные квалифицированные ресурсы со свежей позицией.';
  }catch(error){if(scope===identity()&&id===input.value)message.textContent=error.message+(mutation?' Перед повторным назначением перечитайте текущее задание.':'');}
  finally{busy=false;controls();}
 }
 input.addEventListener('input',()=>{terminal=false;selectedStatus=null;output.textContent='';controls();});
 panel.querySelectorAll('button').forEach(button=>button.addEventListener('click',()=>action(button)));
 window.addEventListener('warehouse-task-selected',event=>{
  const task=event.detail;selectedStatus=task?.status??null;input.value=task?String(task.task_id):'';terminal=!!task&&['DONE','CANCELLED'].includes(task.status);
  output.textContent='';message.textContent=terminal?'Задание завершено: назначение ресурса недоступно.':'Расстояние считается по координатам ячеек. Требуется подтверждённая позиция не старше 5 минут.';controls();
 });
 window.addEventListener('wms-admin-auth-ready',()=>{input.value='';output.textContent='';terminal=false;selectedStatus=null;controls();});controls();
})();
