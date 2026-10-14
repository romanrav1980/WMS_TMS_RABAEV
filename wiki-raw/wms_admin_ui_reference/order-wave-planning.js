/* Original WMS wave commands; no alternate planning or reservation writer. */
(() => {
 const el=id=>document.getElementById(id);
 let context=null,waves=[],wave=null,busy=false,epoch=0;
 const positive=n=>Number.isSafeInteger(n)&&n>0;
 const valid=v=>!!v&&['CREATE','ADD','CALCULATE','LAUNCH'].includes(v.action)&&positive(v.order)&&positive(v.warehouse)&&
   (v.action==='CREATE'?typeof v.body?.wave_code==='string'&&/^UI-[a-f0-9-]{36}$/.test(v.body.wave_code):positive(v.wave))&&
   (v.action!=='ADD'||positive(v.body?.pick_plan_id))&&(v.action!=='LAUNCH'||typeof v.body?.operation_id==='string');
 const intent=window.wmsCommandIntent.create('nicora.orderWave:',valid);
 const message=text=>{el('opWaveStatus').textContent=text;};
 const scope=()=>JSON.stringify([orderScope(),context?.order]);
 function pending(){try{return intent.read();}catch{return {value:null,raw:null};}}
 function controls(){
  const record=pending(),blocked=busy||record.raw!==null,active=context&&context.order===orderState.selectedId;
  el('opWaveRead').disabled=busy||!active;
  el('opWaveCreate').disabled=blocked||!active||!orderCan('pick_wave_create');
  el('opWaveAdd').disabled=blocked||!active||!wave||!['DRAFT','PREVIEW'].includes(wave.status)||!positive(Number(el('opWavePlan').value))||!orderCan('pick_wave_create');
  el('opWaveCalculate').disabled=blocked||!wave||!['DRAFT','PREVIEW'].includes(wave.status)||!wave.orders?.length||!orderCan('pick_wave_calculate');
  el('opWaveLaunch').disabled=blocked||!wave||wave.status!=='PREVIEW'||!orderCan('pick_wave_launch');
  el('opWaveRetry').disabled=busy||!record.value||record.value.order!==context?.order;
  el('opWaveRetry').textContent=record.value?.action==='CREATE'?'Проверить создание волны':'Продолжить сохранённое действие';
  for(const id of ['opWaveSelect','opWavePlan','opWaveName'])el(id).disabled=blocked||!active;
  el('opWaveOpen').hidden=!wave;
  if(wave)el('opWaveOpen').href='wave-replenishment.html?wave_id='+wave.pick_wave_id+'#waveExecution';
 }
 function options(id,items,empty){
  const select=el(id),before=select.value;select.replaceChildren(new Option(empty,''));
  for(const item of items)select.append(new Option(item.text,String(item.id)));
  if(items.some(x=>String(x.id)===before))select.value=before;
 }
 async function loadWaves(){
  if(!context)return;
  const identity=scope(),token=++epoch;
  const rows=await orderRequest('/api/picking/waves?ware_id='+context.warehouse+'&limit=100');
  if(identity!==scope()||token!==epoch)return;
  waves=rows;options('opWaveSelect',rows.map(w=>({id:w.pick_wave_id,text:'#'+w.pick_wave_id+' · '+w.wave_code+' · '+w.status})),'Выберите существующую волну');
  message('Показаны '+rows.length+' волн склада '+context.warehouse+(rows.length===100?' — достигнут предел списка.':'')+' Создание не выпускает задания.');
  controls();
 }
 async function loadWave(id){
  const identity=scope(),token=++epoch;
  const value=await orderRequest('/api/picking/waves/'+id);
  if(identity!==scope()||token!==epoch)return null;
  if(value.ware_id!==context.warehouse)throw Error('Волна другого склада.');
  wave=value;el('opWaveSelect').value=String(id);
  message('Волна #'+id+' · '+value.status+' · планов: '+(value.orders?.length||0)+'.');
  controls();return value;
 }
 async function send(record){
  const v=record.value;if(!context||v.order!==context.order||v.warehouse!==context.warehouse)throw Error('Выберите исходный заказ сохранённого действия.');
  const identity=scope();busy=true;controls();
  try{
   let result;
   if(v.action==='CREATE'){
    result=await orderRequest('/api/picking/waves',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(v.body)});
    if(!positive(result.pick_wave_id))throw Error('Ответ не подтверждает созданную волну.');
    const created=await orderRequest('/api/picking/waves/'+result.pick_wave_id);
    if(created.wave_code!==v.body.wave_code||created.ware_id!==v.warehouse)throw Error('Волна не соответствует сохранённой команде.');
    if(identity!==scope())return;
    intent.settle(record);await loadWaves();await loadWave(created.pick_wave_id);
   }else{
    const suffix={ADD:'plans',CALCULATE:'calculate',LAUNCH:'launch'}[v.action];
    result=await orderRequest('/api/picking/waves/'+v.wave+'/'+suffix,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(v.body)});
    if(result.pick_wave_id!==v.wave)throw Error('Ответ не подтверждает выбранную волну.');
    if(identity!==scope())return;
    intent.settle(record);await loadWave(v.wave);
   }
   if(identity===scope())message(v.action==='LAUNCH'?'Волна запущена. Откройте складское исполнение для работы с выданными заданиями.':
    v.action==='CALCULATE'?'Расчёт волны сохранён. Проверьте готовность и задания в рабочем месте волны перед запуском.':
    v.action==='ADD'?'План включён в волну. Следующее действие — расчёт волны.':'Волна создана. Включите выбранный план.');
  }catch(e){if(identity===scope())message(e.message+' Исходное действие сохранено; новый запрос не создаётся.');}
  finally{busy=false;controls();}
 }
 async function act(action){
  if(busy||pending().raw!==null||!context)return;
  const base={action,order:context.order,warehouse:context.warehouse,wave:wave?.pick_wave_id};
  if(action==='CREATE')base.body={wave_code:'UI-'+crypto.randomUUID(),wave_name:el('opWaveName').value.trim()||'Заказ '+context.order,ware_id:context.warehouse,max_customers:30};
  else if(action==='ADD')base.body={pick_plan_id:Number(el('opWavePlan').value)};
  else base.body={operation_id:'WAVE.UI:'+crypto.randomUUID()};
  await send(intent.save(base));
 }
 async function resume(){
  const record=pending(),v=record.value;
  if(busy||!v||!context||v.order!==context.order)return;
  if(v.action!=='CREATE'){
   const current=await loadWave(v.wave);if(!current)return;
   if(v.action==='ADD'&&current.orders?.some(p=>p.pick_plan_id===v.body.pick_plan_id&&p.status==='ACTIVE')){
    intent.settle(record);message('План уже включён в эту волну. Повторное добавление не требуется.');controls();return;
   }
   if(v.action==='CALCULATE'&&current.status==='PREVIEW'){
    intent.settle(record);message('Текущий расчёт волны доступен. Проверьте его перед запуском.');controls();return;
   }
   await send(record);return;
  }
  await loadWaves();
  const found=waves.filter(w=>w.wave_code===v.body.wave_code&&w.ware_id===v.warehouse);
  if(found.length!==1){message('Создание пока не подтверждено в последних100 волнах. Сохранённый код: '+v.body.wave_code+'. Новая волна автоматически не создаётся.');return;}
  const current=await loadWave(found[0].pick_wave_id);if(!current)return;
  intent.settle(record);message('Найдена созданная волна #'+current.pick_wave_id+'. Можно продолжать.');controls();
 }
 window.addEventListener('wms-order-plans-read',event=>{
  const d=event.detail;context={order:d.order.customer_order_id,warehouse:d.order.ware_id};wave=null;waves=[];++epoch;
  options('opWavePlan',d.plans.filter(p=>['PLANNED_FULL','PLANNED_PARTIAL'].includes(p.status)).map(p=>({id:p.pick_plan_id,text:'#'+p.pick_plan_id+' · '+p.total_planned_qty+' обеспечено'})),'Выберите обеспеченный план');
  options('opWaveSelect',[],'Прочитайте волны склада');
  if(el('opWavePlan').options.length===2)el('opWavePlan').selectedIndex=1;
  message(pending().raw!==null?'Есть сохранённое действие по волне. Продолжите его для исходного заказа.':'Выберите существующую волну или создайте новую для склада заказа.');controls();
 });
 function reset(){++epoch;context=null;wave=null;waves=[];options('opWaveSelect',[],'Прочитайте планы заказа');options('opWavePlan',[],'Прочитайте планы заказа');message('Сначала прочитайте планы и обеспечение заказа.');controls();}
 window.addEventListener('wms-order-context-changed',reset);window.addEventListener('wms-admin-auth-ready',reset);
 el('opWaveRead').addEventListener('click',()=>loadWaves().catch(e=>message(e.message)));
 el('opWaveSelect').addEventListener('change',()=>{wave=null;controls();const id=Number(el('opWaveSelect').value);if(positive(id))loadWave(id).catch(e=>message(e.message));});
 el('opWavePlan').addEventListener('change',controls);
 for(const [id,action]of [['opWaveCreate','CREATE'],['opWaveAdd','ADD'],['opWaveCalculate','CALCULATE'],['opWaveLaunch','LAUNCH']])el(id).addEventListener('click',()=>act(action).catch(e=>message(e.message)));
 el('opWaveRetry').addEventListener('click',()=>resume().catch(e=>message(e.message)));
 reset();
})();
