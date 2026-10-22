(() => {
 const el=id=>document.getElementById(id),auth=()=>window.wmsAdminAuth;
 const scope=()=>JSON.stringify([auth().state.apiBase,auth().state.user?.username]);
 let context=null,epoch=0,busy=false,next=null;
 const key=()=> 'wms-st-deferral:'+scope();
 function showSummary(v){
  const panel=el('sdOverview');panel.hidden=!v;
  if(!v){panel.replaceChildren();return;}
  const prepared=v.physical_preparation,waiting=prepared&&!prepared.physical_move_required;
  const cards=[['Текущий рейс',String(v.source_trip_id)],['Дата отгрузки',v.source_trip.shipment_date],
   ['Паллет в СТ',String(v.members.length)],['Состояние товара',prepared?(waiting?'В ячейке ожидания':'Отобран, требуется перемещение'):'Отбор ещё не завершён']];
  panel.replaceChildren(...cards.map(([label,value],index)=>{
   const card=document.createElement('div');card.className='summary-card'+(index===3&&waiting?' is-ready':'');
   const title=document.createElement('span'),text=document.createElement('strong');title.textContent=label;text.textContent=value;
   card.append(title,text);return card;
  }));
 }
 function clearTrip(){el('sdTarget').value='';el('sdSelectedTrip').textContent='';}
 function pending(){
  const raw=localStorage.getItem(key());if(!raw)return null;
  const p=JSON.parse(raw),fields=['operation_id','st_number','target_trip_id','expected_version','source_hash','reason','reference'];
  if(!p||typeof p!=='object'||Array.isArray(p)||Object.keys(p).length!==fields.length||
   fields.some(f=>!Object.hasOwn(p,f))||typeof p.operation_id!=='string'||!/^STDEFER:[A-Za-z0-9_.:-]{1,92}$/.test(p.operation_id)||
   typeof p.st_number!=='string'||!p.st_number.trim()||p.st_number.length>100||!Number.isSafeInteger(p.target_trip_id)||p.target_trip_id<1||
   !Number.isSafeInteger(p.expected_version)||p.expected_version<0||typeof p.source_hash!=='string'||!/^[a-f0-9]{64}$/.test(p.source_hash)||
   typeof p.reason!=='string'||p.reason.trim().length<8||p.reason.length>500||typeof p.reference!=='string'||p.reference.trim().length<8||p.reference.length>500)
    throw Error('Сохранённая команда повреждена. Новая отправка заблокирована; исходник сохранён.');
  return p;
 }
 function controls(){let p,damaged=false;try{p=pending();}catch{damaged=true;}const target=Number(el('sdTarget').value),valid=Number.isSafeInteger(target)&&target>0&&el('sdReason').value.trim().length>=8&&el('sdReference').value.trim().length>=8;el('sdSave').disabled=busy||!context||!!p||damaged||!valid;for(const id of ['sdTarget','sdReason','sdReference'])el(id).disabled=busy||!!p||damaged;el('sdRetry').disabled=busy||!p||damaged;el('sdPickTrip').disabled=busy||!context||!!p||damaged;
  el('sdRecover').disabled=busy||!damaged||!el('sdSt').value.trim();
  el('sdPending').textContent=damaged?'Сохранённая команда повреждена. Исходник сохранён, новая отправка заблокирована.':p?'Сохранена команда '+p.operation_id+': СТ '+p.st_number+', целевой рейс '+p.target_trip_id+'. Повтор использует эти данные.':'';}
 async function recover(){
  if(busy)return;try{pending();return;}catch{}
  const identity=scope(),storageKey=key(),raw=localStorage.getItem(storageKey),st=el('sdSt').value.trim(),token=++epoch;
  if(!st)return;busy=true;context=null;clearTrip();showSummary(null);controls();
  try{
   localStorage.setItem(storageKey+':archive:'+crypto.randomUUID(),raw||'');
   const value=await api('/context?'+new URLSearchParams({st_number:st}));
   if(identity!==scope()||token!==epoch||st!==el('sdSt').value.trim())return;
   if(localStorage.getItem(storageKey)!==raw)throw Error('Команда изменена другой вкладкой. Исходник сохранён.');
   localStorage.removeItem(storageKey);context=value;showSummary(value);
   el('sdMessage').textContent='Повреждённый исходник сохранён в архив. Текущее состояние СТ перечитано. Перед новой командой проверьте историю переносов.';
  }catch(error){if(identity===scope()&&token===epoch)el('sdMessage').textContent=error.message+' Новая отправка остаётся заблокированной.';}
  finally{busy=false;controls();}
 }
 async function api(path,options={}) {
  const identity=scope(),r=await fetch(auth().state.apiBase.replace(/\/$/,'')+'/api/transport/st-deferrals'+path,
   {...options,headers:auth().headers(options.headers||{})});
  const text=await r.text();let v;try{v=JSON.parse(text);}catch{throw Error('Ответ не подтверждён. Повторите сохранённую команду.');}
  if(identity!==scope())throw Error('Пользователь изменился.');
  if(!r.ok)throw Error(v.detail?.message||v.detail||'Операция не подтверждена.');return v;
 }
 async function read(){
  const token=++epoch,identity=scope();context=null;clearTrip();showSummary(null);controls();
  try{const v=await api('/context?'+new URLSearchParams({st_number:el('sdSt').value.trim()}));
   if(token!==epoch||identity!==scope())return;context=v;showSummary(v);
   el('sdMessage').textContent='СТ '+v.st_number+', склад '+v.warehouse_id+', рейс '+v.source_trip_id+', версия '+v.version+
    ', паллет '+v.members.length+'. Исходная дата рейса '+v.source_trip.shipment_date+'. Перенос разрешается только до погрузки. Отбор сохраняется. Собранный товар и контейнеры с вложениями перемещаются складскими заданиями; система проверяет весь исходный состав.';if(v.physical_preparation)el('sdMessage').textContent+=v.physical_preparation.physical_move_required?' Товар уже отобран: перенос рейса не перемещает его. Создайте штатное складское задание в зону ожидания.':' Отобранный товар уже находится в настроенной ячейке ожидания; повторное перемещение не требуется.';controls();
  }catch(e){if(token===epoch&&identity===scope())el('sdMessage').textContent=e.message;}
 }
 async function send(){
  if(busy)return;const identity=scope();let command;
  try{command=pending();if(!command){
   if(!context)throw Error('Прочитайте исходную СТ.');
   const target=Number(el('sdTarget').value),reason=el('sdReason').value.trim(),reference=el('sdReference').value.trim();
   if(!Number.isSafeInteger(target)||target<1||reason.length<8||reference.length<8)throw Error('Укажите существующий рейс, причину и ссылку на решение (не менее 8 символов).');
   command={operation_id:'STDEFER:'+crypto.randomUUID(),st_number:context.st_number,target_trip_id:target,
    expected_version:context.version,source_hash:context.source_hash,reason,reference};
   localStorage.setItem(key(),JSON.stringify(command));
  }}catch(e){el('sdMessage').textContent=e.message;return;}
  const requestKey=key(),requestRaw=localStorage.getItem(requestKey);
  busy=true;controls();
  try{const result=await api('',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(command)});
   if(identity!==scope())return;
   if(result.operation_id!==command.operation_id||result.stock_changed!==false)throw Error('Неожиданный результат. Сохранённая команда остаётся.');
   if(localStorage.getItem(requestKey)!==requestRaw)throw Error('Команда в другой вкладке изменилась. Её исходник сохранён.');
   window.dispatchEvent(new CustomEvent('wms-st-deferral-selected',{detail:result}));
   localStorage.removeItem(requestKey);context=null;showSummary(null);
   el('sdMessage').textContent='Перенос сохранён: '+result.source_trip_id+' → '+result.target_trip_id+
    '. Исходная дата '+result.original_shipping_date+', новая дата '+result.target_shipping_date+
    '. Объём заказа сохранён. Физическая отгрузка не подтверждена.';
  }catch(e){if(identity===scope())el('sdMessage').textContent=e.message+' Сохранённую команду можно повторить.';}
  finally{busy=false;controls();}
 }
 async function history(after=0){
  const token=++epoch,identity=scope();
  try{const v=await api('/history?'+new URLSearchParams({st_number:el('sdSt').value.trim(),after_version:String(after)}));
   if(token!==epoch||identity!==scope())return;
   el('sdHistoryRows').replaceChildren(...v.rows.map(row=>{const tr=document.createElement('tr');
    for(const value of [row.version,row.source_trip_id,row.target_trip_id,row.original_shipping_date,row.target_shipping_date,row.reason,row.reference,row.actor]){
     const td=document.createElement('td');td.textContent=String(value??'');tr.appendChild(td);}
     const action=document.createElement('td'),button=document.createElement('button');
     button.textContent='Задания ожидания';
     button.addEventListener('click',()=>window.dispatchEvent(new CustomEvent('wms-st-deferral-selected',{detail:row})));
     action.appendChild(button);tr.appendChild(action);return tr;}));
   next=v.next_after_version;el('sdHistoryNext').disabled=!v.has_more;
  }catch(e){if(token===epoch&&identity===scope())el('sdMessage').textContent=e.message;}
 }
 el('sdRecover').addEventListener('click',recover);el('sdRead').addEventListener('click',read);el('sdSave').addEventListener('click',send);el('sdRetry').addEventListener('click',send);
 el('sdHistory').addEventListener('click',()=>history());el('sdHistoryNext').addEventListener('click',()=>{if(next!==null)history(next);});
 el('sdSt').addEventListener('input',()=>{epoch++;context=null;clearTrip();showSummary(null);next=null;el('sdHistoryRows').replaceChildren();el('sdHistoryNext').disabled=true;controls();});
 el('sdPickTrip').addEventListener('click',()=>{
  if(context&&!busy)window.dispatchEvent(new CustomEvent('wms-st-trip-picker-open',{detail:{st_number:context.st_number,source_hash:context.source_hash}}));
 });
 window.addEventListener('wms-st-trip-selected',event=>{
  const v=event.detail;
  if(!context||busy||context.st_number!==v.st_number||context.source_hash!==v.source_hash)return;
  el('sdTarget').value=String(v.trip.trip_id);
  el('sdSelectedTrip').textContent=v.trip.shipment_date+' · '+v.trip.vehicle+' · '+(v.trip.districts.join(', ')||'Район не указан');
  controls();
 });
 for(const id of ['sdTarget','sdReason','sdReference'])el(id).addEventListener('input',controls);
 window.addEventListener('wms-admin-auth-ready',()=>{epoch++;context=null;clearTrip();showSummary(null);next=null;el('sdHistoryRows').replaceChildren();el('sdMessage').textContent='';controls();});
 window.addEventListener('storage',event=>{if(event.key===key())controls();});
 controls();
})();
