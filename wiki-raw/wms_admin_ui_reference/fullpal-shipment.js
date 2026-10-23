(() => {
 const panel=document.createElement('section');panel.id='fullpalShipment';panel.className='panel fullpal-shipment-panel';
 panel.innerHTML='<h2>Связать целую паллету с подготовленной СТ</h2><p>После завершения перемещения подтвердите, какое подготовленное место исполнено этой паллетой.</p><div class="fullpal-fields"><label>Завершённое задание<input data-task type="number" min="1"></label><button data-preview type="button">Показать паллету</button><label>Скан идентификатора паллеты<input data-pallet autocomplete="off"></label><label>Скан места подготовленной СТ<input data-shipment autocomplete="off"></label></div><p data-fact></p><a data-layout hidden>Открыть укладку заказа</a><div class="fullpal-actions"><button data-bind type="button">Подтвердить связь</button><button data-archive type="button" hidden>Сохранить повреждённый запрос в архив</button><a data-control hidden>Перейти к контролю</a></div><p role="status" aria-live="polite"></p>';
 const mount=document.getElementById('warehouseTaskDetail');if(mount)mount.after(panel);else document.querySelector('main').append(panel);
 const task=panel.querySelector('[data-task]'),pallet=panel.querySelector('[data-pallet]'),shipment=panel.querySelector('[data-shipment]'),
  message=panel.querySelector('[role=status]'),bind=panel.querySelector('[data-bind]'),archive=panel.querySelector('[data-archive]');
 let snapshot=null,record=null,busy=false,generation=0,selectedTask=null;
 const base=()=>window.wmsAdminAuth.state.apiBase.replace(/\/$/,'');
 const key=()=>'wms-fullpal-binding:'+base()+':'+(window.wmsAdminAuth.state.user?.username||'');
 function valid(v){return Boolean(v&&Number.isSafeInteger(v.task)&&v.task>0&&v.body&&/^FULLPAL.BIND:[A-Za-z0-9-]+$/.test(v.body.operation_id)&&
  typeof v.body.shipment_identifier==='string'&&v.body.shipment_identifier.length>0&&v.body.shipment_identifier.length<=150&&
  typeof v.body.scanned_pallet==='string'&&v.body.scanned_pallet.length>0&&v.body.scanned_pallet.length<=150&&
  Number.isSafeInteger(v.body.expected_stock_version)&&v.body.expected_stock_version>=0);}
 function readRecord(){
  const storageKey=key(),raw=localStorage.getItem(storageKey);if(raw===null)return null;
  try{const value=JSON.parse(raw);if(!valid(value))throw Error('INVALID');return{storageKey,raw,value};}
  catch{return{storageKey,raw,damaged:true};}
 }
 function controls(){
  const eligible=selectedTask?.status==='DONE'&&selectedTask?.task_type==='PICKING_MOVE'&&selectedTask?.task_source==='WAVE';
  panel.hidden=!window.wmsAdminAuth?.hasPermission('warehouse_task_view')||Boolean(mount&&!record&&!eligible);
  const pending=record?.value,locked=busy||Boolean(record);
  for(const field of[task,pallet,shipment])field.disabled=locked;
  panel.querySelector('[data-preview]').disabled=busy||Boolean(record);
  bind.disabled=busy||record?.damaged||!window.wmsAdminAuth?.hasPermission('warehouse_task_execute')||(!pending&&!snapshot);
  bind.textContent=pending?'Повторить сохранённую связь':'Подтвердить связь';
  archive.hidden=!record?.damaged;archive.disabled=busy;
 }
 async function call(path,options={}){
  const response=await fetch(base()+path,{...options,headers:{...window.wmsAdminAuth.headers(),...(options.headers||{})}});
  const text=await response.text();let data;try{data=JSON.parse(text);}catch{throw Error('Ответ не подтверждён. Перечитайте состояние; сохранённую команду повторяйте с тем же идентификатором.');}
  if(!response.ok){const error=new Error(typeof data.detail==='string'?data.detail:JSON.stringify(data.detail||data));error.detail=data.detail;throw error;}
  return data;
 }
 async function preview(){
  if(busy||record)return;const id=Number(task.value);if(!Number.isSafeInteger(id)||id<1)throw Error('Укажите завершённое задание.');
  const current=++generation,identity=key();snapshot=null;controls();
  const data=await call('/api/warehouse-tasks/'+id+'/full-pallet-shipment');
  if(current!==generation||identity!==key()||Number(task.value)!==id)return;
  if(data.task_id!==id)throw Error('Ответ относится к другому заданию.');
  snapshot=data;panel.querySelector('[data-fact]').textContent=data.pallet_identifier+' · '+data.article+' · '+data.quantity+' '+data.base_uom+' · '+data.cell;
  const link=panel.querySelector('[data-layout]');link.hidden=!Number.isSafeInteger(data.customer_order_id);
  if(!link.hidden)link.href='customer-orders.html?order_id='+data.customer_order_id+'#preparedLayoutPanel';
  message.textContent='Отсканируйте физическую паллету и место СТ. Сервер проверит точное совпадение состава.';controls();
 }
 async function send(){
  if(busy)return;record=readRecord();if(record?.damaged){controls();throw Error('Сохранённый запрос повреждён.');}
  if(!record){
   const id=Number(task.value);if(!snapshot||snapshot.task_id!==id)throw Error('Сначала прочитайте подтверждённую паллету.');
   const value={task:id,body:{operation_id:'FULLPAL.BIND:'+crypto.randomUUID(),shipment_identifier:shipment.value.trim(),
    scanned_pallet:pallet.value.trim(),expected_stock_version:snapshot.stock_version}};
   if(!valid(value))throw Error('Укажите идентификаторы паллеты и места СТ.');
   const raw=JSON.stringify(value),storageKey=key();localStorage.setItem(storageKey,raw);
   if(localStorage.getItem(storageKey)!==raw)throw Error('Команда не сохранена.');
   record={storageKey,raw,value};
  }
  const sending=record,current=()=>key()===sending.storageKey&&localStorage.getItem(sending.storageKey)===sending.raw;
  busy=true;controls();message.textContent='Подтверждение связи…';
  try{
   const data=await call('/api/warehouse-tasks/'+sending.value.task+'/full-pallet-shipment',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(sending.value.body)});
   if(!current())return;
   if(data.operation_id!==sending.value.body.operation_id||data.warehouse_task_id!==sending.value.task||
    data.pallet_identifier!==sending.value.body.scanned_pallet||data.shipment_identifier!==sending.value.body.shipment_identifier||data.status!=='PICKED')throw Error('Ответ не подтверждает исходную связь.');
   localStorage.removeItem(sending.storageKey);record=null;snapshot=null;
   message.textContent='Паллета '+data.pallet_identifier+' связана с местом СТ '+data.shipment_identifier+': '+data.quantity+' '+data.base_uom+'.';
   const control=panel.querySelector('[data-control]');control.hidden=!window.wmsAdminAuth.hasPermission('outgoing_pallet_check');
   control.href='warehouse-tasks.html?qc_shipment='+encodeURIComponent(data.shipment_identifier)+'#outgoingQuality';
  }catch(error){
   if(current()){
    if(error.detail?.outcome_confirmed===true&&error.detail.operation_id===sending.value.body.operation_id&&!error.detail.retry_same_operation_id){localStorage.removeItem(sending.storageKey);record=null;}
    message.textContent=error.message+(record?' Сохранённая команда ожидает точного повтора.':' Перечитайте паллету после устранения причины.');
   }
  }finally{busy=false;controls();}
 }
 function rights(){
  ++generation;snapshot=null;panel.hidden=!window.wmsAdminAuth?.hasPermission('warehouse_task_view');panel.querySelector('[data-control]').hidden=true;
  record=window.wmsAdminAuth?.state.user?readRecord():null;
  if(record?.value){task.value=record.value.task;pallet.value=record.value.body.scanned_pallet;shipment.value=record.value.body.shipment_identifier;message.textContent='Сохранённая связь ожидает точного повтора.';}
  else if(record?.damaged)message.textContent='Сохранённый запрос повреждён. Новый запрос заблокирован до архивирования.';
  controls();
 }
 task.addEventListener('input',()=>{++generation;snapshot=null;controls();});
 panel.querySelector('[data-preview]').addEventListener('click',()=>preview().catch(e=>{message.textContent=e.message;controls();}));
 bind.addEventListener('click',()=>send().catch(e=>{message.textContent=e.message;controls();}));
 archive.addEventListener('click',()=>{try{if(busy||!record?.damaged||key()!==record.storageKey||localStorage.getItem(record.storageKey)!==record.raw)return;
  const name=record.storageKey+':damaged:'+crypto.randomUUID();localStorage.setItem(name,record.raw);
  if(localStorage.getItem(name)!==record.raw)throw Error('Архив не сохранён.');localStorage.removeItem(record.storageKey);record=null;message.textContent='Исходный запрос сохранён в архиве. Перечитайте паллету.';controls();
 }catch(e){message.textContent=e.message;}});
 window.addEventListener('warehouse-task-selected',event=>{selectedTask=event.detail;if(!busy&&!record){
  task.value=selectedTask?.status==='DONE'&&selectedTask?.task_type==='PICKING_MOVE'&&selectedTask?.task_source==='WAVE'?selectedTask.task_id:'';
  ++generation;snapshot=null;
 }controls();});
 window.addEventListener('storage',event=>{if(!busy&&event.key===key())rights();});
 window.addEventListener('wms-admin-auth-ready',rights);rights();
})();
