(() => {
 const el=id=>document.getElementById(id),auth=()=>window.wmsAdminAuth;
 const scope=()=>JSON.stringify([auth().state.apiBase,auth().state.user?.username]);
 let context=null,epoch=0,busy=false;
 function key(){return 'wms-day-review:'+scope();}
 function pending(){const raw=localStorage.getItem(key());return raw?JSON.parse(raw):null;}
 function showPending(){let value=null;try{value=pending();}catch{}el('drReviewRetry').disabled=!value;el('drReviewResolve').disabled=!value;el('drReviewSave').disabled=!context||!!value;el('drReviewPending').textContent=value?'Сохранена команда '+value.operation_id+' для склада '+value.warehouse_id+', даты '+value.business_date+', пояса '+value.timezone_region+'. Повтор относится к этим данным.':'';}
 async function api(path,options={}){
  const identity=scope();
  const response=await fetch(auth().state.apiBase.replace(/\/$/,'')+path,{...options,headers:auth().headers(options.headers||{})});
  const raw=await response.text();let body;try{body=JSON.parse(raw);}catch{throw Error('Ответ не подтверждён. Сохранённую команду можно повторить.');}
  if(identity!==scope())throw Error('Пользователь изменился.');
  if(!response.ok)throw Error(body.detail?.message||body.detail||'Исход команды не подтверждён.');
  return body;
 }
 async function read(){
  const token=++epoch,identity=scope();context=null;showPending();
  try{
   const ware=Number(el('drWare').value),day=el('drDay').value,zone=el('drZone').value.trim();
   if(!Number.isSafeInteger(ware)||ware<1||!day||!zone)throw Error('Укажите склад, дату и часовой пояс.');
   const q=new URLSearchParams({business_date:day,timezone_region:zone});
   const result=await api('/api/finance/day-reconciliation/warehouses/'+ware+'/review-context?'+q);
   if(token!==epoch||identity!==scope())return;
   context=result;
   const open=result.report.open_items.reduce((sum,item)=>sum+item.count,0);
   el('drReviewMessage').textContent='Сверка прочитана '+result.report.read_at_utc+'. Версия журнала '+result.version+'. Открытых пунктов '+open+'. Фиксация сохраняет эти пункты.';
   showPending();
  }catch(e){if(token===epoch&&identity===scope())el('drReviewMessage').textContent=e.message;}
 }
 async function send(resolve=false){
  if(busy)return;
  const identity=scope();let command;
  try{command=pending();if(!command){
   if(resolve||!context)throw Error('Сначала прочитайте результат сверки.');
   const reason=el('drReviewReason').value.trim();if(reason.length<8)throw Error('Укажите содержательную причину фиксации.');
   command={operation_id:'DAYREVIEW:'+crypto.randomUUID(),warehouse_id:context.warehouse_id,business_date:context.business_date,
    timezone_region:context.timezone_region,expected_version:context.version,source_hash:context.source_hash,reason};
   localStorage.setItem(key(),JSON.stringify(command));
  }}catch(e){el('drReviewMessage').textContent=e.message;return;}
  busy=true;for(const id of ['drReviewSave','drReviewRetry','drReviewResolve'])el(id).disabled=true;
  try{
   const result=await api('/api/finance/day-reconciliation/reviews'+(resolve?'/resolve':''),{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(command)});
   if(identity!==scope())return;
   if(result.state==='NOT_RECORDED'&&resolve){
    localStorage.removeItem(key());context=null;
    el('drReviewMessage').textContent='После ожидания исходной команды сервер подтвердил: запись отсутствует. Можно перечитать факты и подготовить новую сверку.';
   }else if(result.state==='REVIEW_RECORDED'&&result.operation_id===command.operation_id&&result.day_closed===false){
    localStorage.removeItem(key());context=null;
    el('drReviewMessage').textContent='Сверка сохранена, версия '+result.version+'. Открытые обязательства сохранены. День не объявлен закрытым.';
   }else throw Error('Неожиданный результат: сохранённая команда остаётся для восстановления.');
  }catch(e){if(identity===scope())el('drReviewMessage').textContent=String(e.message)+' Повторите прежнюю команду или проверьте её исход.';}
  finally{busy=false;showPending();}
 }
 el('drReviewRead').addEventListener('click',read);el('drReviewSave').addEventListener('click',()=>send());
 el('drReviewRetry').addEventListener('click',()=>send());el('drReviewResolve').addEventListener('click',()=>send(true));
 for(const id of ['drWare','drDay','drZone'])el(id).addEventListener('input',()=>{epoch++;context=null;showPending();});
 window.addEventListener('wms-admin-auth-ready',()=>{epoch++;context=null;el('drReviewMessage').textContent='';el('drReviewReason').value='';showPending();});
 showPending();
})();
