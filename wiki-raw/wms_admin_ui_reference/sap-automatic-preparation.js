(() => {
 const el=id=>document.getElementById(id),auth=()=>window.wmsAdminAuth;
 const identity=()=>JSON.stringify([auth()?.state.apiBase,auth()?.state.user?.username]);
 const decimal=(v,scale)=>typeof v==='string'&&new RegExp('^\\d+(\\.\\d{1,'+scale+'})?$').test(v)&&/[1-9]/.test(v);
 const limitsValid=v=>v&&Object.keys(v).sort().join(',')==='max_goods_volume_m3,max_goods_weight_kg,max_pallets'&&
  decimal(v.max_goods_weight_kg,6)&&decimal(v.max_goods_volume_m3,9)&&Number.isSafeInteger(v.max_pallets)&&v.max_pallets>=1&&v.max_pallets<=100;
 const valid=v=>v&&Object.keys(v).sort().join(',')==='body,order_id'&&Number.isSafeInteger(v.order_id)&&v.order_id>0&&
  v.body&&Object.keys(v.body).sort().join(',')==='limits,operation_id,source_signature'&&
  typeof v.body.operation_id==='string'&&v.body.operation_id.length<=100&&/^[A-Za-z0-9_.:-]+$/.test(v.body.operation_id)&&
  /^[a-f0-9]{64}$/.test(v.body.source_signature)&&limitsValid(v.body.limits);
 const intent=window.wmsCommandIntent.create('sap-auto-preparation:',valid);
 let proposal=null,busy=false,epoch=0;
 const manualRaw=()=>localStorage.getItem('sap-st-preparation:'+identity());
 const message=value=>{el('sapAutoMessage').textContent=value;};
 function controls(){
  let record;try{record=intent.read();}catch{}
  el('sapAutoSave').disabled=busy||!proposal||!!record?.raw||!!manualRaw();
  el('sapAutoRetry').disabled=busy||!record?.value||!!manualRaw();
  el('sapAutoResolve').disabled=busy||!record?.value||!!manualRaw();
  el('sapAutoRead').disabled=busy;el('sapAutoCurrent').disabled=busy;
  el('sapAutoRecover').hidden=!record?.damaged;el('sapAutoRecover').disabled=busy;
  el('sapAutoPending').textContent=record?.damaged?'Сохранённая команда повреждена. Новая подготовка заблокирована.':
   record?.value?'Сохранён запрос '+record.value.body.operation_id+' для заказа #'+record.value.order_id+'. Повтор использует прежние параметры.':'';
 }
 function input(){
  const order_id=Number(el('sapAutoOrder').value),limits={
   max_goods_weight_kg:el('sapAutoMass').value.trim(),max_goods_volume_m3:el('sapAutoVolume').value.trim(),
   max_pallets:Number(el('sapAutoCount').value)};
  if(!Number.isSafeInteger(order_id)||order_id<1||!limitsValid(limits))throw Error('Укажите заказ, положительные пределы массы и объёма и число мест от 1 до 100.');
  return {order_id,limits};
 }
 async function api(path,body,method='POST'){
  const who=identity(),r=await fetch(auth().state.apiBase.replace(/\/$/,'')+'/api/integrations/sap/store-orders/'+path,
   {method,headers:auth().headers({'Content-Type':'application/json'}),...(method==='GET'?{}:{body:JSON.stringify(body)})});
  let v;try{v=await r.json();}catch{throw Error('Ответ не подтверждён. Сохранённый запрос остаётся.');}
  if(who!==identity())throw Error('Пользователь изменился.');
  if(!r.ok)throw Error(v.detail?.message||v.detail||'Подготовка отклонена.');
  return v;
 }
 function temperatureText(stat){return stat.temp_min_c!==undefined&&stat.temp_max_c!==undefined&&(stat.temp_min_c!==null||stat.temp_max_c!==null)?(stat.temp_min_c??'не задано')+' … '+(stat.temp_max_c??'не задано')+' °C':'Не подтверждены';}
 function display(value){return typeof value==='string'&&/^\d+\.\d+$/.test(value)?value.replace(/0+$/,'').replace(/\.$/,''):value;}
 function td(value){const t=document.createElement('td');t.textContent=String(display(value));return t;}
 async function preview(){
  const token=++epoch,who=identity();proposal=null;controls();busy=true;controls();
  try{
   const data=input(),v=await api(data.order_id+'/automatic-layout',data.limits);
   if(token!==epoch||who!==identity())return;
   if(v.customer_order_id!==data.order_id||!Array.isArray(v.pallets)||!/^[a-f0-9]{64}$/.test(v.source_signature))throw Error('Предложение не подтверждено.');
   proposal={...data,source_signature:v.source_signature,pallets:v.pallets};
   el('sapAutoRows').replaceChildren(...v.pallets.flatMap((p,i)=>p.lines.map(line=>{
    const tr=document.createElement('tr'),s=v.pallet_statistics[i];
    tr.append(td(i+1),td(s.assembly_group),td(line.articul),td(line.quantity),td(s.goods_weight_kg),td(s.goods_volume_m3),td(temperatureText(s)));return tr;
   })));
   message('Предложено мест: '+v.pallets.length+'. Целые коробки, нормы, масса, объём и известные температурные диапазоны соблюдены. Неизвестные требования требуют настройки. СТ ещё не создана. Проверьте состав перед подготовкой.');
  }catch(e){if(token===epoch&&who===identity())message(e.message);}
  finally{busy=false;controls();}
 }
 function sameRequest(a,b){
  return a?.operation_id===b.operation_id&&a?.source_signature===b.source_signature&&
   a?.limits?.max_goods_weight_kg===b.limits.max_goods_weight_kg&&
   a?.limits?.max_goods_volume_m3===b.limits.max_goods_volume_m3&&a?.limits?.max_pallets===b.limits.max_pallets;
 }
 async function send(resolve=false){
  if(busy)return;const who=identity();let record;
  try{
   if(manualRaw())throw Error('Сначала выясните исход сохранённой ручной подготовки.');
   record=intent.read();
   if(record.damaged)throw Error('Сохранённая команда повреждена. Требуется восстановление без новой подготовки.');
   if(!record.value){
    if(resolve||!proposal)throw Error('Сначала рассчитайте состав.');
    const current=input();
    if(JSON.stringify(current)!==JSON.stringify({order_id:proposal.order_id,limits:proposal.limits}))throw Error('Параметры изменились. Пересчитайте состав.');
    record=intent.save({order_id:proposal.order_id,body:{operation_id:'AUTO.ST:'+crypto.randomUUID(),
      source_signature:proposal.source_signature,limits:proposal.limits}});
   }
   const check=intent.read();if(check.raw!==record.raw||check.storageKey!==record.storageKey)throw Error('Сохранённая команда изменилась.');
  }catch(e){message(e.message);controls();return;}
  busy=true;controls();const command=record.value;
  try{
   const v=await api(command.order_id+'/prepare-st/automatic'+(resolve?'/resolve':''),command.body);
   if(who!==identity())return;
   if(resolve&&v.state==='NOT_PREPARED'){
    if(v.operation_id!==command.body.operation_id||v.customer_order_id!==command.order_id)throw Error('Исход не подтверждён.');
    intent.settle(record);proposal=null;message('Сервер после ожидания подтвердил отсутствие подготовленной СТ. Перечитайте предложение.');return;
   }
   const result=resolve?v.result:v;
   if(result?.customer_order_id!==command.order_id||result.status!=='ST_PREPARED'||!sameRequest(result.auto_request,command.body))throw Error('Результат не соответствует сохранённой команде.');
   intent.settle(record);proposal=null;assignmentLink(command.order_id);
   message('Подготовлена СТ '+result.st_number+'. Мест: '+result.pallet_identifiers.length+'. Можно назначать её в существующий рейс.');
   window.dispatchEvent(new Event('sap-auto-preparation-settled'));
  }catch(e){if(who===identity())message(e.message+' Сохранённый запрос остаётся для повтора или проверки исхода.');}
  finally{busy=false;controls();}
 }
 function assignmentLink(order){el('sapAutoAssignment').href='customer-orders.html?order_id='+encodeURIComponent(order)+'#sapAssignment';el('sapAutoAssignment').hidden=false;}
 async function readCurrent(){
  if(busy)return;const who=identity(),token=++epoch;proposal=null;busy=true;controls();
  try{
   const order=Number(el('sapAutoOrder').value);
   if(!Number.isSafeInteger(order)||order<1)throw Error('Укажите исходный заказ.');
   const source=await api(String(order),null,'GET');
   if(who!==identity()||token!==epoch)return;
   if(source.customer_order_id!==order)throw Error('Исходный заказ не подтверждён.');
   const saved=source.preparation_json;
   el('sapAutoRows').replaceChildren();
   if(!saved){message('СТ ещё не подготовлена. Укажите пределы и рассчитайте состав.');return;}
   assignmentLink(order);const statistics=saved.pallet_statistics||[];
   el('sapAutoRows').replaceChildren(...statistics.flatMap((stat,i)=>{
    const lines=saved.planned_pallets?.[i]?.lines||[{articul:'Состав в карточке заказа',quantity:'—'}];
    return lines.map(line=>{const tr=document.createElement('tr');tr.append(td(saved.pallet_identifiers[i]),td(stat.assembly_group),
     td(line.articul),td(line.quantity),td(stat.goods_weight_kg),td(stat.goods_volume_m3),td(temperatureText(stat)));return tr;});
   }));
   message('Уже подготовлена СТ '+saved.st_number+', мест: '+saved.pallet_identifiers.length+'. Сохранённый план; физический состав смотрите в карточке грузового места.');
  }catch(e){if(who===identity()&&token===epoch)message(e.message);}
  finally{busy=false;controls();}
 }
 async function recover(){
  if(busy)return;let record;const who=identity();
  try{record=intent.read();if(!record.damaged)throw Error('Повреждённой команды нет.');
   const order=Number(el('sapAutoOrder').value);
   if(!Number.isSafeInteger(order)||order<1)throw Error('Укажите исходный заказ для чтения его текущего состояния.');
   busy=true;controls();const current=await api(String(order),null,'GET');
   if(who!==identity())return;
   if(current.customer_order_id!==order)throw Error('Исходный заказ не подтверждён.');
   intent.archiveDamaged(record);proposal=null;
   message('Исходник сохранён в архиве; текущий заказ прочитан. Сверьте существующие СТ перед новым расчётом.');
  }catch(e){if(who===identity())message(e.message);}
  finally{busy=false;controls();}
 }
 function clear(){el('sapAutoAssignment').hidden=true;epoch++;proposal=null;el('sapAutoRows').replaceChildren();controls();}
 for(const id of ['sapAutoOrder','sapAutoMass','sapAutoVolume','sapAutoCount'])el(id).addEventListener('input',clear);
 el('sapAutoCurrent').addEventListener('click',readCurrent);el('sapAutoRead').addEventListener('click',preview);el('sapAutoSave').addEventListener('click',()=>send());
 el('sapAutoRetry').addEventListener('click',()=>send());el('sapAutoResolve').addEventListener('click',()=>send(true));
 el('sapAutoRecover').addEventListener('click',recover);
 window.addEventListener('sap-store-source-selected',e=>{el('sapAutoOrder').value=e.detail.order_id;clear();});
 window.addEventListener('wms-admin-auth-ready',()=>{clear();if(location.hash==='#sapAutoPreparation')requestAnimationFrame(()=>{el('sapAutoPreparation').scrollIntoView({block:'start'});if(linked)readCurrent();});});window.addEventListener('storage',controls);
 window.addEventListener('sap-manual-preparation-settled',controls);
 const linked=new URLSearchParams(location.search).get('sap_order');
 if(linked&&/^\d+$/.test(linked))el('sapAutoOrder').value=linked;
 controls();
})();
