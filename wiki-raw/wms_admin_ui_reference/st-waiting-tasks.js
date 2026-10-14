(() => {
 const el=id=>document.getElementById(id),auth=()=>window.wmsAdminAuth;
 const scope=()=>JSON.stringify([auth().state.apiBase,auth().state.user?.username]);
 const key=()=> 'wms-st-waiting-tasks:'+scope();
 let busy=false,loading=false,readEpoch=0,next=null,shownDecision=null,rows=[],places=[],selectionRequired=false;
 function pending(){
  const raw=localStorage.getItem(key());if(!raw)return null;
  const body=JSON.parse(raw),keys=Object.keys(body);
  if(![2,3].includes(keys.length)||keys.some(k=>!['operation_id','decision_operation_id','root_identifier'].includes(k))||!keys.includes('operation_id')||!keys.includes('decision_operation_id')||
   (keys.includes('root_identifier')&&(typeof body.root_identifier!=='string'||!body.root_identifier.length||body.root_identifier.length>200||body.root_identifier.includes('\u0000')))||
   ![body.operation_id,body.decision_operation_id].every(v=>typeof v==='string'&&/^[A-Za-z0-9_.:-]{1,100}$/.test(v)))
   throw Error('Сохранённая команда повреждена. Не создавайте новую команду до выяснения результата исходной.');
  return {raw,body};
 }
 function controls(){
  try{
   const p=pending(),selected=el('swDecision').value.trim();
   el('swPlan').disabled=busy||loading||!!p||!selected||selected!==shownDecision||(selectionRequired&&!el('swRoot').value);el('swRoot').disabled=busy||loading||!!p;el('swRetry').disabled=busy||!p;
   el('swRecover').disabled=true;
   el('swRead').disabled=loading||!selected;el('swNext').disabled=loading||next===null||selected!==shownDecision;
   el('swPending').textContent=p?'Ожидается подтверждение команды '+p.body.operation_id+'. Повтор использует исходное решение '+p.body.decision_operation_id+'.':'';
  }catch(e){el('swPlan').disabled=true;el('swRetry').disabled=true;el('swPending').textContent=e.message;el('swRecover').disabled=busy||loading||!/^[A-Za-z0-9_.:-]{1,100}$/.test(el('swDecision').value.trim());}
 }
 function render(){
  const labels={PLANNED:'Запланировано',ASSIGNED:'Назначено',IN_PROGRESS:'В работе',DONE:'Выполнено',CANCELLED:'Отменено'};
  el('swRows').replaceChildren(...rows.map(row=>{
   const tr=document.createElement('tr');
   for(const value of [row.task_id,row.pallet_identifier,row.from_cell,row.to_cell,row.quantity+' '+row.base_uom]){
    const td=document.createElement('td');td.textContent=String(value??'');tr.appendChild(td);
   }
   tr.firstChild.className='task-id';
   const td=document.createElement('td'),badge=document.createElement('span');
   badge.className='status-pill'+(row.status==='DONE'&&row.sync_status==='SYNCED'?' done':row.status==='CANCELLED'?' cancelled':row.status==='DONE'?' pending':'');
   badge.textContent=labels[row.status]||row.status;
   if(row.status==='DONE'&&row.sync_status!=='SYNCED')badge.textContent+=' · требуется синхронизация';
   td.appendChild(badge);tr.appendChild(td);return tr;
  }));
  el('swTable').hidden=!rows.length;el('swEmpty').hidden=!!rows.length;
  el('swEmpty').textContent='Заданий для этого решения пока нет. Если товар уже в ячейке ожидания, новое перемещение не требуется.';
  el('swCount').textContent=rows.length?'Показано заданий: '+rows.length:'';
 }
 function renderPlaces(){
  const chosen=el('swRoot').value;el('swRoot').replaceChildren();
  const empty=document.createElement('option');empty.value='';empty.textContent=selectionRequired?'Выберите одно верхнее место':'По действующему составу СТ';el('swRoot').appendChild(empty);
  for(const place of places){
   const option=document.createElement('option');option.value=place.root_identifier;option.disabled=!place.available;
   const label=place.place_kind==='CASE'?'CASE':'HU';
   option.textContent=label+' '+place.root_identifier+(place.cell?' · '+place.cell:'')+
    (place.planned_task_id?' · задание #'+place.planned_task_id:!place.available?' · требуется разбор':!place.move_required?' · уже в ожидании':'');
   el('swRoot').appendChild(option);
  }
  if(places.some(p=>p.root_identifier===chosen&&p.available))el('swRoot').value=chosen;
  else if(places.length===1&&places[0].available&&selectionRequired)el('swRoot').value=places[0].root_identifier;
  el('swRootHint').textContent=selectionRequired?'Каждое верхнее место получает своё задание. Выберите место; состав и принадлежность проверит WMS.':
   'Для нескольких контейнеров выбирается конкретное место. Самостоятельные CASE можно запланировать прежним общим действием.';
 }
 async function request(path,options={}){
  const identity=scope(),response=await fetch(auth().state.apiBase.replace(/\/$/,'')+'/api/receiving/st-deferrals/waiting-tasks'+path,
   {...options,headers:auth().headers(options.headers||{})});
  const text=await response.text();let result;
  try{result=JSON.parse(text);}catch{throw Error('Ответ не подтверждён. Повторите исходную команду.');}
  if(identity!==scope())throw Error('Пользователь изменился.');
  if(!response.ok){const error=Error(result.detail?.code==='ST_WAITING_ROOT_SELECTION_REQUIRED'?'Выберите конкретное верхнее место.':result.detail?.message||'Операция не подтверждена.');error.code=result.detail?.code;throw error;}
  return result;
 }
 async function read(after=0){
  const decision=el('swDecision').value.trim(),identity=scope(),epoch=++readEpoch;
  if(!/^[A-Za-z0-9_.:-]{1,100}$/.test(decision)){el('swMessage').textContent='Выберите сохранённое решение о переносе.';return;}
  if(!after){shownDecision=null;places=[];selectionRequired=false;renderPlaces();}
  loading=true;controls();
  try{
   const result=await request('?'+new URLSearchParams({decision_operation_id:decision,after_task_id:String(after),limit:'100'}));
   if(epoch!==readEpoch||identity!==scope()||el('swDecision').value.trim()!==decision)return;
   const existing=after?rows:[];
   rows=Array.from(new Map([...existing,...result.tasks].map(row=>[row.task_id,row])).values());
   next=result.next_after_task_id;shownDecision=decision;places=result.available_places||[];selectionRequired=result.selection_required===true;renderPlaces();render();
   el('swMessage').textContent='СТ '+result.st_number+' · склад '+result.warehouse_id+' · ячейка ожидания '+(result.waiting_cell||'не настроена')+'. Статусы прочитаны из WMS.';
  }catch(e){if(epoch===readEpoch&&identity===scope())el('swMessage').textContent=e.message;}
  finally{if(epoch===readEpoch)loading=false;controls();}
 }
 async function recover(){
  if(busy||loading)return;try{pending();return;}catch{}
  const savedKey=key(),raw=localStorage.getItem(savedKey),identity=scope(),decision=el('swDecision').value.trim(),epoch=++readEpoch;
  if(!/^[A-Za-z0-9_.:-]{1,100}$/.test(decision))return;
  loading=true;controls();
  try{
   localStorage.setItem(savedKey+':archive:'+crypto.randomUUID(),raw||'');
   const result=await request('?'+new URLSearchParams({decision_operation_id:decision,limit:'100'}));
   if(epoch!==readEpoch||identity!==scope()||el('swDecision').value.trim()!==decision)return;
   if(result.decision_operation_id!==decision||!Array.isArray(result.tasks))throw Error('Неожиданный ответ WMS.');
   if(localStorage.getItem(savedKey)!==raw)throw Error('Исходник изменён другой вкладкой.');
   localStorage.removeItem(savedKey);rows=result.tasks;next=result.next_after_task_id;shownDecision=decision;places=result.available_places||[];selectionRequired=result.selection_required===true;renderPlaces();render();
   el('swMessage').textContent='Повреждённый исходник сохранён в архив. Текущие задания перечитаны. Проверьте их перед созданием нового плана; архивирование не подтверждает физическое перемещение.';
  }catch(error){if(epoch===readEpoch&&identity===scope())el('swMessage').textContent=error.message+' Создание остаётся заблокированным.';}
  finally{if(epoch===readEpoch)loading=false;controls();}
 }
 async function send(){
  if(busy)return;const identity=scope(),savedKey=key();let intent,firstAttempt=false;
  try{
   intent=pending();
   if(!intent){
    const decision=el('swDecision').value.trim();
    if(!/^[A-Za-z0-9_.:-]{1,100}$/.test(decision))throw Error('Выберите сохранённое решение о переносе СТ.');
    if(selectionRequired&&!el('swRoot').value)throw Error('Выберите конкретное верхнее место.');
    const body={operation_id:'STWAIT:'+crypto.randomUUID(),decision_operation_id:decision};
    if(el('swRoot').value)body.root_identifier=el('swRoot').value;firstAttempt=true;
    const raw=JSON.stringify(body);localStorage.setItem(savedKey,raw);intent={body,raw};
   }
  }catch(e){el('swMessage').textContent=e.message;return;}
  busy=true;controls();
  try{
   const result=await request('',{method:'POST',headers:{'Content-Type':'application/json'},body:intent.raw});
   if(identity!==scope())return;
   if(result.operation_id!==intent.body.operation_id||result.decision_operation_id!==intent.body.decision_operation_id||
    (intent.body.root_identifier&&result.root_identifier!==intent.body.root_identifier)||result.stock_changed!==false||!Array.isArray(result.tasks)||!Array.isArray(result.already_waiting))
    throw Error('Неожиданный ответ. Исходная команда сохранена.');
   if(localStorage.getItem(savedKey)!==intent.raw)throw Error('Сохранённая команда изменилась в другом окне. Результат исходной команды получен.');
   localStorage.removeItem(savedKey);el('swDecision').value=intent.body.decision_operation_id;
   await read();
   if(identity===scope())el('swMessage').textContent='Создано заданий: '+result.tasks.length+'. Уже в ячейке ожидания: '+result.already_waiting.length+
    '. Количество и резерв сохраняются. Перемещение подтверждается при выполнении задания.';
  }catch(e){
   if(identity===scope()&&firstAttempt&&e.code==='ST_WAITING_ROOT_SELECTION_REQUIRED'&&localStorage.getItem(savedKey)===intent.raw){
    localStorage.removeItem(savedKey);await read();if(identity===scope())el('swMessage').textContent='Выберите верхнее место. Новый план не был создан.';
   }else if(identity===scope())el('swMessage').textContent=e.message+' Исходную команду можно повторить.';
  }
  finally{busy=false;controls();}
 }
 function resetRows(){readEpoch++;loading=false;next=null;shownDecision=null;rows=[];places=[];selectionRequired=false;renderPlaces();el('swRows').replaceChildren();el('swTable').hidden=true;el('swEmpty').hidden=false;el('swEmpty').textContent='Выберите решение о переносе, чтобы увидеть текущие задания.';el('swCount').textContent='';}
 el('swRecover').addEventListener('click',recover);el('swPlan').addEventListener('click',send);el('swRetry').addEventListener('click',send);
 el('swRead').addEventListener('click',()=>read());el('swNext').addEventListener('click',()=>{if(next!==null)read(next);});
 el('swRoot').addEventListener('change',controls);
 el('swDecision').addEventListener('input',()=>{resetRows();controls();});
 window.addEventListener('wms-st-deferral-selected',event=>{
  if(!busy){el('swDecision').value=event.detail.operation_id;resetRows();controls();read();}
 });
 function openLinkedDecision(){
  const decision=new URLSearchParams(window.location.search).get('decision_operation_id');
  if(auth().state.user?.username&&decision&&/^[A-Za-z0-9_.:-]{1,100}$/.test(decision)){
   el('swDecision').value=decision;controls();read();
  }
 }
 window.addEventListener('wms-admin-auth-ready',()=>{el('swDecision').value='';el('swMessage').textContent='';resetRows();controls();openLinkedDecision();});
 window.addEventListener('storage',event=>{if(event.key===key())controls();});
 controls();openLinkedDecision();
})();
