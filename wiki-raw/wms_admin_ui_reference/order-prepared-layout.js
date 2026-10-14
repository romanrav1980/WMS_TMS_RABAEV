(() => {
 const el=id=>document.getElementById(id),panel=el('preparedLayoutPanel');
 const valid=v=>Boolean(v&&Number.isSafeInteger(v.order)&&v.order>0&&v.body&&Number.isSafeInteger(v.body.row_id)&&v.body.row_id>0&&
  Number.isSafeInteger(v.body.target_shipment_id)&&v.body.target_shipment_id>0&&typeof v.body.reason==='string'&&v.body.reason.trim()&&v.body.reason.length<=500&&
  /^[A-F0-9]{64}$/.test(v.body.expected_signature)&&/^ST.LAYOUT:[A-Za-z0-9-]+$/.test(v.body.operation_id));
 const intent=window.wmsCommandIntent.create('nicora.preparedLayout:',valid);
 let snapshot=null,rows=[],busy=false,epoch=0,record=null,order=null;
 const say=text=>el('plStatus').textContent=text;
 function scope(){return intent.scope();}
 function controls(){
  const pending=record?.value,damaged=record?.damaged;
  el('plMove').disabled=busy||damaged||!orderCan('outgoing_pallet_edit')||(!pending&&!snapshot)||Boolean(pending&&pending.order!==order);
  el('plMove').textContent=pending?'Повторить сохранённый перенос':'Подтвердить перенос строки';
  for(const id of ['plRow','plTarget','plReason','plPreview'])el(id).disabled=busy||Boolean(pending)||damaged||!order||!rows.some(r=>r.fulfillment_status==='PLANNED');
  el('plRead').disabled=busy;el('plArchive').hidden=!damaged&&!pending?.confirmed_rejection;el('plArchive').disabled=busy;
 }
 function table(target,items){
  target.replaceChildren();for(const r of items){const tr=document.createElement('tr');
   for(const text of[r.pallet_identifier??r.pallet,r.article,r.quantity,r.unit,r.packs,r.weight]){
    const td=document.createElement('td');td.textContent=String(text??'—');tr.append(td);
   }target.append(tr);
  }
 }
 function invalidate(){++epoch;snapshot=null;el('plComparison').hidden=true;controls();}
 function chooseTargets(){
  invalidate();const source=rows.find(r=>r.row_id===Number(el('plRow').value));
  el('plTarget').replaceChildren();
  for(const item of new Map(rows.filter(r=>r.fulfillment_status==='PLANNED').map(r=>[r.shipment_id,r])).values()){
   if(item.shipment_id===source?.shipment_id)continue;
   const option=document.createElement('option');option.value=item.shipment_id;option.textContent=item.pallet_identifier;el('plTarget').append(option);
  }
 }
 async function read(){
  if(busy)return;invalidate();rows=[];order=orderState.selectedId||null;record=intent.read();controls();
  if(!order){say('Выберите заказ.');return;}
  const token=epoch,identity=scope(),id=order;
  const data=await orderRequest('/api/customer-orders/'+id+'/prepared-layout');
  if(token!==epoch||identity!==scope()||id!==orderState.selectedId)return;
  rows=data.rows;table(el('plCurrentRows'),rows);el('plRow').replaceChildren();
  for(const item of rows.filter(r=>r.row_id&&r.fulfillment_status==='PLANNED')){
   const option=document.createElement('option');option.value=item.row_id;
   option.textContent=item.pallet_identifier+' · '+item.article+' · '+item.quantity+' '+item.unit;el('plRow').append(option);
  }
  chooseTargets();
  if(data.truncated){order=null;say('Более200 строк. Перенос заблокирован для неполной выборки.');}
  else say(record?.damaged?'Сохранённый запрос повреждён; сначала сохраните его в архив.':record?.value?'Есть сохранённый перенос для заказа '+record.value.order+'. Повтор использует исходные параметры.':!rows.some(r=>r.fulfillment_status==='PLANNED')?'Все места уже исполняются или отгружены. Изменение плановой укладки недоступно.':'Текущая плановая укладка. Перенос строки сохраняет общее количество, массу и коробки; физическое перемещение выполняется складским заданием.');
  controls();
 }
 async function preview(){
  if(busy||record?.raw||!order)return;
  const token=++epoch,identity=scope(),id=order;const body={row_id:Number(el('plRow').value),target_shipment_id:Number(el('plTarget').value)};
  snapshot=null;controls();
  const data=await orderRequest('/api/customer-orders/'+id+'/prepared-layout/preview',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)});
  if(token!==epoch||identity!==scope()||id!==orderState.selectedId)return;
  if(data.order_id!==id||data.row_id!==body.row_id||data.target_shipment_id!==body.target_shipment_id||!/^[A-F0-9]{64}$/.test(data.signature))throw Error('Ответ не соответствует выбранному переносу.');
  snapshot=data;table(el('plBeforeRows'),data.before);table(el('plAfterRows'),data.after);el('plComparison').hidden=false;
  say('Проверьте состав до и после. Места СТ '+data.st_number+' и назначение рейса '+(data.trip_id||'—')+' сохраняются.');controls();
 }
 async function send(){
  if(busy||record?.damaged||!orderCan('outgoing_pallet_edit'))return;
  if(!record?.value){
   if(!snapshot||snapshot.order_id!==order)return;
   const reason=el('plReason').value.trim();if(!reason)throw Error('Укажите причину изменения укладки.');
   record=intent.save({order,body:{operation_id:'ST.LAYOUT:'+crypto.randomUUID(),row_id:snapshot.row_id,
    target_shipment_id:snapshot.target_shipment_id,expected_signature:snapshot.signature,reason}});
  }
  if(record.value.order!==order)throw Error('Вернитесь к исходному заказу сохранённого переноса.');
  const sending=record,identity=scope();if(localStorage.getItem(sending.storageKey)!==sending.raw)throw Error('Запрос изменился в другой вкладке.');
  const current=()=>identity===scope()&&localStorage.getItem(sending.storageKey)===sending.raw;
  busy=true;controls();
  try{
   const result=await orderRequest('/api/customer-orders/'+sending.value.order+'/prepared-layout/move-row',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(sending.value.body)});
   if(!current())return;
   if(result.operation_id!==sending.value.body.operation_id||result.order_id!==sending.value.order||result.status!=='APPLIED'||result.stock_changed!==false)throw Error('Ответ не подтверждает перенос.');
   intent.settle(sending);record=null;snapshot=null;busy=false;await read();say('Укладка изменена. Общий товар сохранён; теперь свяжите фактические паллеты с подготовленными местами.');
   window.dispatchEvent(new CustomEvent('wms-prepared-layout-confirmed',{detail:result}));
  }catch(error){
   if(current()){
    if(error.detail?.outcome_confirmed===true){
     const value={...sending.value,confirmed_rejection:true};localStorage.setItem(sending.storageKey,JSON.stringify(value));record=intent.read();
    }
    say(error.message+'. Исходная команда сохранена; неопределённый результат повторяется с тем же идентификатором.');
   }
  }finally{busy=false;controls();}
 }
 async function archive(){
  if(busy||(!record?.damaged&&!record?.value?.confirmed_rejection))return;
  if(record.damaged)intent.archiveDamaged(record);
  else{const archive=record.storageKey+':rejected:'+crypto.randomUUID();localStorage.setItem(archive,record.raw);
   if(localStorage.getItem(archive)!==record.raw)throw Error('Архив не сохранён.');intent.settle(record);}
  record=null;await read();
 }
 function reset(){invalidate();order=null;rows=[];table(el('plCurrentRows'),[]);say('Перечитайте укладку выбранного заказа.');controls();}
 for(const [id,action]of [['plRead',read],['plPreview',preview],['plMove',send],['plArchive',archive]])el(id).addEventListener('click',()=>action().catch(e=>say(e.message)));
 el('plRow').addEventListener('change',chooseTargets);el('plTarget').addEventListener('change',invalidate);
 window.addEventListener('wms-order-context-changed',reset);
 window.addEventListener('wms-admin-auth-ready',()=>{reset();panel.hidden=!orderCan('customer_order_view');record=window.wmsAdminAuth?.state.user?intent.read():null;controls();});
 controls();
})();
