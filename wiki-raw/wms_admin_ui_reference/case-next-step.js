/* Read-only next-step navigation after the existing CASE close command. */
(()=>{
 const panel=document.createElement('section');panel.className='cp-next-step';panel.hidden=true;
 document.getElementById('cpTypePanel').before(panel);
 const text=(tag,value)=>{const n=document.createElement(tag);n.textContent=value;return n;};
 function link(label,href,title){const a=text('a',label);a.href=href;a.title=title;return a;}
 function render(){
  panel.replaceChildren();const task=cpTsd.task;
  panel.hidden=!task||!['WAIT_CONTROL','CONTROL_IN_PROGRESS','CONTROLLED','READY_TO_SHIP','SHIPPED'].includes(task.status);
  if(panel.hidden)return;
  panel.append(text('h2',task.status==='SHIPPED'?'Место отгружено':'Следующий этап сборки'));
  panel.append(text('p','Идентификатор паллеты: '+(task.sscc||'CASE:'+task.case_pick_task_id)+' · состав v'+task.content_version+' · ячейка '+(task.current_cell||'не определена')));
  const actions=text('div','');actions.className='cp-next-actions';
  actions.append(link('Посмотреть фактический состав','warehouse-hus.html?identifier='+encodeURIComponent('CASE:'+task.case_pick_task_id)+'#huComposition','Прочитать текущее место и вложенный состав, без проведения'));
  if(task.status==='SHIPPED')panel.append(text('p','Отгрузка подтверждена сервером. Операция: '+(task.shipped_operation||'см. историю места')));
  else if(!task.legacy_sborka_pallet_id){
   panel.append(text('p','Сборка закрыта, но связь с подготовленной паллетой СТ ещё не подтверждена. Выберите существующую СТ перед контролем отгрузки.'));
   const a=link('Перейти к связи со СТ','#cpTsdShipmentIdentifier','Открыть существующую форму привязки. Скан и подтверждение выполняются отдельно');
   a.addEventListener('click',()=>document.getElementById('cpTsdShipmentIdentifier').focus());actions.append(a);
  }else{
   panel.append(text('p',['CONTROLLED','READY_TO_SHIP'].includes(task.status)?'Текущий статус: '+task.status+'. Перед погрузкой система повторно проверит допуск этой версии состава.':'Нужен контроль подтверждённого состава. Его выполняет уполномоченный контролёр.'));
   if(window.wmsAdminAuth?.hasPermission('outgoing_pallet_check'))actions.append(link('Открыть контроль','warehouse-tasks.html?qc_shipment='+encodeURIComponent(task.sscc||'CASE:'+task.case_pick_task_id)+'#outgoingQuality','Прочитать это место в существующем контроле; предъявление и сканы — отдельные действия'));
  }
  panel.append(actions);
 }
 window.addEventListener('wms-case-render',render);window.addEventListener('wms-admin-auth-ready',()=>{panel.hidden=true;panel.replaceChildren();});
})();