/* Existing CONFIG transaction and one durable browser command, scoped to actor/API. */
(() => {
 const el=id=>document.getElementById('qs'+id),auth=()=>window.wmsAdminAuth;
 const base=()=>auth().state.apiBase.replace(/\/$/,'');
 const scope=()=>JSON.stringify(['nicora.qualityPolicy',base(),auth().state.user?.username]);
 const store=window.wmsCommandIntent.create('',v=>v&&Number.isSafeInteger(v.ware)&&v.ware>0&&v.body&&/^[A-Za-z0-9_.:-]{1,100}$/.test(v.body.operation_id)&&typeof v.body.store_addr==='string'&&['ANY','STOCK','CASE'].includes(v.body.place_category),{storageKey:scope});
 let record=null,snapshot=null,busy=false,generation=0,identity='';
 const selection=()=>JSON.stringify([el('Ware').value.trim(),el('Addr').value,el('Category').value]);
 const status=text=>{el('Status').textContent=text;};
 function controls(){
  const pending=!!record?.raw;
  document.querySelectorAll('main input,main select').forEach(n=>{n.disabled=busy||pending;});
  el('Read').disabled=busy||pending||!auth().hasPermission('warehouse_settings_view');
  el('Save').disabled=busy||pending||!snapshot||snapshot.selection!==selection()||!auth().hasPermission('warehouse_settings_edit');
  el('Retry').hidden=!record?.value;el('Retry').disabled=busy;
  el('Restart').hidden=!record?.value?.rejected;el('Restart').disabled=busy;
  el('Archive').hidden=!record?.damaged;el('Archive').disabled=busy;
 }
 async function request(path,body){
  const response=await fetch(base()+path,{method:body?'POST':'GET',headers:{...auth().headers(),...(body?{'Content-Type':'application/json'}:{})},...(body?{body:JSON.stringify(body)}:{})});
  const data=await response.json();if(!response.ok){const e=Error(typeof data.detail==='string'?data.detail:JSON.stringify(data.detail));e.confirmed=(response.status===422||data.detail?.outcome_confirmed===true)&&![401,403].includes(response.status)&&!e.message.includes('PAYLOAD_CONFLICT');throw e;}return data;
 }
 function fill(data){
  if(!data.configured)data={active:true,control_mode:'BOTH',independent:false,sample_percent:'0',exempt_whole:false,exempt_storage:false};
  el('Active').checked=Boolean(data.active);el('Mode').value=data.control_mode;el('Independent').checked=Boolean(data.independent);
  el('Sample').value=data.sample_percent;el('Whole').checked=Boolean(data.exempt_whole);el('Storage').checked=Boolean(data.exempt_storage);
 }
 async function read(){
  if(busy||record?.raw)return;const ware=Number(el('Ware').value),selected=selection(),key=scope(),stamp=++generation;
  if(!Number.isSafeInteger(ware)||ware<1||!el('Addr').value){status('Укажите склад и код магазина либо *.');return;}
  snapshot=null;busy=true;controls();
  try{const data=await request('/api/inventory/quality-policies/warehouses/'+ware+'?store_addr='+encodeURIComponent(el('Addr').value)+'&place_category='+el('Category').value);
   if(key!==scope()||stamp!==generation||selected!==selection())return;
   snapshot={...data,selection:selected};fill(data);el('Version').textContent=data.configured?'Текущая версия '+data.version+(data.active?' · правило действует':' · правило отключено'):'Адресного правила нет. Новая запись будет версией 1.';status('Правило прочитано.');
  }catch(e){if(key===scope()&&stamp===generation)status(e.message);}finally{busy=false;controls();}
 }
 async function send(){
  if(busy||!record?.value)return;const saved=record,value=saved.value,key=scope();
  if(key!==saved.storageKey||localStorage.getItem(key)!==saved.raw){status('Запрос изменился в другой вкладке. Перечитайте страницу.');return;}
  busy=true;controls();
  try{const data=await request('/api/inventory/quality-policies/warehouses/'+value.ware,value.body);
   if(scope()!==key)return;
   if(data.operation_id!==value.body.operation_id||data.warehouse_id!==value.ware||data.store_addr!==value.body.store_addr||data.place_category!==value.body.place_category||data.version!==value.body.expected_version+1||data.stock_changed!==false)throw Error('Ответ не подтверждает исходную настройку. Повторите сохранённую команду.');
   store.settle(saved);record=null;snapshot={...data,selection:selection()};fill(data);el('Version').textContent='Сохранена версия '+data.version;status('Правило сохранено. Операция '+data.operation_id);
  }catch(e){if(scope()===key&&localStorage.getItem(key)===saved.raw){
   if(e.confirmed){const value2={...value,rejected:true},raw=JSON.stringify(value2);localStorage.setItem(key,raw);if(localStorage.getItem(key)===raw)record={storageKey:key,raw,value:value2};}
   status(e.message+(e.confirmed?' Отказ подтверждён.':' Результат не подтверждён; повтор сохраняет исходную команду.'));
  }}finally{busy=false;controls();}
 }
 el('Read').onclick=read;
 el('Save').onclick=async()=>{try{
  if(busy||record?.raw||!snapshot||snapshot.selection!==selection())return;
  if(!/^(?:100(?:\.0{1,2})?|\d{1,2}(?:\.\d{1,2})?)$/.test(el('Sample').value)||el('Reason').value.trim().length<8)throw Error('Укажите процент от 0 до 100 и основание не короче восьми символов.');
  const body={operation_id:'QC.SCOPE:'+crypto.randomUUID(),expected_version:snapshot.version,store_addr:el('Addr').value,place_category:el('Category').value,active:el('Active').checked,control_mode:el('Mode').value,independent:el('Independent').checked,sample_percent:el('Sample').value,exempt_whole:el('Whole').checked,exempt_storage:el('Storage').checked,reason:el('Reason').value.trim()};
  record=store.save({ware:snapshot.warehouse_id,body});await send();
 }catch(e){status(e.message);controls();}};
 el('Retry').onclick=send;
 el('Restart').onclick=async()=>{try{if(busy||!record?.value?.rejected)return;store.settle(record);record=null;snapshot=null;await read();}catch(e){status(e.message);}controls();};
 el('Archive').onclick=async()=>{try{if(busy||!record?.damaged)return;store.archiveDamaged(record);record=null;snapshot=null;await read();}catch(e){status(e.message);}controls();};
 for(const name of ['Ware','Addr','Category'])el(name).addEventListener('input',()=>{++generation;snapshot=null;el('Version').textContent='Область изменена — перечитайте правило.';controls();});
 function changed(){const key=scope();if(key===identity)return;identity=key;++generation;snapshot=null;record=null;status('');el('Version').textContent='Сначала прочитайте правило.';
  if(auth().state.user?.username){try{record=store.read();if(record.value){el('Ware').value=record.value.ware;el('Addr').value=record.value.body.store_addr;el('Category').value=record.value.body.place_category;fill({...record.value.body,configured:true});el('Reason').value=record.value.body.reason;status('Есть сохранённая команда. Повторите её прежде новой настройки.');}else if(record.damaged)status('Повреждённый запрос сохранён. Архивируйте его перед новой настройкой.');}catch(e){record={raw:'unreadable',damaged:true};status(e.message);}}
  controls();
 }
 const initial=new URLSearchParams(location.search).get('warehouse_id');if(initial)el('Ware').value=initial;
 window.addEventListener('wms-admin-auth-ready',changed);window.addEventListener('storage',e=>{if(e.key===scope()){snapshot=null;status('Запрос изменён другой вкладкой. Перезагрузите страницу.');controls();}});changed();
})();
