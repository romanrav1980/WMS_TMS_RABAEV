(() => {
 const el=id=>document.getElementById(id),auth=()=>window.wmsAdminAuth;
 const scope=()=>JSON.stringify([auth().state.apiBase,auth().state.user?.username]),key=()=> 'wms-warehouse-depot:'+scope();
 let context=null,epoch=0,busy=false;
 function pending(){const raw=localStorage.getItem(key());return raw?JSON.parse(raw):null;}
 function controls(){let p;try{p=pending();}catch{}el('wdSave').disabled=busy||!context||!!p;for(const id of ['wdRetry','wdResolve'])el(id).disabled=busy||!p;
  el('wdPending').textContent=p?'Сохранена команда '+p.operation_id+' для склада '+p.warehouse_id+'. Повтор относится к этому адресу.':'';}
 async function api(path,options={}){
  const identity=scope(),r=await fetch(auth().state.apiBase.replace(/\/$/,'')+'/api/transport/warehouse-depots'+path,{...options,headers:auth().headers(options.headers||{})});
  let value;try{value=await r.json();}catch{throw Error('Ответ не подтверждён. Сохранённую команду можно повторить.');}
  if(identity!==scope())throw Error('Пользователь изменился.');
  if(!r.ok)throw Error(value.detail?.message||value.detail||'Операция не подтверждена.');return value;
 }
 async function read(){
  const token=++epoch,identity=scope();context=null;controls();
  try{
   const ware=Number(el('wdWare').value);if(!Number.isSafeInteger(ware)||ware<1)throw Error('Укажите склад.');
   const v=await api('/'+ware);if(token!==epoch||identity!==scope())return;context=v;el('wdAddress').value=v.depot_address||'';
   el('wdMessage').textContent='Версия '+v.version+'. '+(v.configured?'Адрес отправления '+v.depot_address+'; координаты '+v.latitude+', '+v.longitude+'.':'Адрес отправления не настроен или отсутствуют координаты.')+' Физическое соответствие адресу требует проверки.';controls();
  }catch(e){if(token===epoch&&identity===scope())el('wdMessage').textContent=e.message;}
 }
 async function send(resolve=false){
  if(busy)return;const identity=scope();let command;
  try{
   command=pending();if(!command){
    if(resolve||!context)throw Error('Прочитайте настройки склада.');
    const reason=el('wdReason').value.trim();if(reason.length<8)throw Error('Укажите основание изменения.');
    command={operation_id:'WAREDEPOT:'+crypto.randomUUID(),warehouse_id:context.warehouse_id,expected_version:context.version,
     depot_address:el('wdAddress').value.trim()||null,reason};
    localStorage.setItem(key(),JSON.stringify(command));
   }
  }catch(e){el('wdMessage').textContent=e.message;return;}
  busy=true;controls();
  try{
   const v=await api(resolve?'/resolve':'',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(command)});
   if(identity!==scope())return;
   if(resolve&&v.state==='NOT_RECORDED'&&v.operation_id===command.operation_id){
    localStorage.removeItem(key());context=null;el('wdMessage').textContent='После ожидания исходной команды сервер подтвердил: запись отсутствует. Перечитайте настройки.';return;
   }
   const result=resolve?v.result:v;
   if(result.operation_id!==command.operation_id||result.stock_changed!==false)throw Error('Неожиданный исход. Сохранённая команда остаётся.');
   localStorage.removeItem(key());context=null;
   el('wdMessage').textContent='Адрес отправления сохранён, версия '+result.version+'. Существующие плановые решения требуют пересмотра при изменении источника.';
  }catch(e){if(identity===scope())el('wdMessage').textContent=e.message+' Повторите исходную команду или проверьте её исход.';}
  finally{busy=false;controls();}
 }
 el('wdRead').addEventListener('click',read);el('wdSave').addEventListener('click',()=>send());
 el('wdRetry').addEventListener('click',()=>send());el('wdResolve').addEventListener('click',()=>send(true));
 function clear(){epoch++;context=null;el('wdMessage').textContent='';controls();}
 el('wdWare').addEventListener('input',clear);window.addEventListener('wms-admin-auth-ready',clear);
 window.addEventListener('warehouse-depot-selected',e=>{el('wdWare').value=e.detail.warehouse_id;clear();});
 controls();
})();
