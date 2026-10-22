// Профиль магазина (C-0029): GET/PUT /api/master-data/stores/profile. Одна версия покрывает все параметры и окна.
// Окна: «не задано» (UNCONFIGURED) или полная неделя (WEEKLY, явный часовой пояс, день без интервалов — закрыт).
// Команда сохраняется до отправки, повтор — тем же operation_id/body, успех — после сверки ответа.
(() => {
 const auth=()=>window.wmsAdminAuth,base=()=>auth().state.apiBase.replace(/\/$/,'');
 const DAYS=['Пн','Вт','Ср','Чт','Пт','Сб','Вс'],MAX_DAY=8,MAX_WEEK=56;
 const scope=()=>JSON.stringify(['retailcase.storeProfile',base(),auth().state.user?.username]);
 const valid=v=>v&&typeof v.body?.store_addr==='string'&&/^[A-Za-z0-9_.:-]{1,100}$/.test(v.body?.operation_id||'')&&Number.isSafeInteger(v.body.expected_version);
 const store=window.wmsCommandIntent.create('',valid,{storageKey:scope,invalid:'Некорректная команда профиля.'});
 let state=null;
 const h=(tag,props={},...kids)=>{const n=document.createElement(tag);for(const[k,v]of Object.entries(props)){if(v==null)continue;if(k==='class')n.className=v;else if(k==='text')n.textContent=v;else if(k in n&&typeof v!=='string')n[k]=v;else n.setAttribute(k,v);}n.append(...kids.filter(Boolean));return n;};
 const minutes=t=>{const m=/^(\d{2}):(\d{2})$/.exec(t.trim());if(!m)return null;const v=Number(m[1])*60+Number(m[2]);return (Number(m[1])<24&&Number(m[2])<60)||t.trim()==='24:00'?v:null;};
 const hhmm=v=>String(Math.floor(v/60)).padStart(2,'0')+':'+String(v%60).padStart(2,'0');
 function tri(name,label,value,title){const s=h('select',{name,title});for(const [v,t] of [['','не задано'],['1','да'],['0','нет']])s.append(new Option(t,v));s.value=value==null?'':value?'1':'0';return h('label',{},label,s);}
 function num(name,label,value,min,title){return h('label',{},label,h('input',{name,inputmode:'numeric',value:value??'',placeholder:'не задано',title:title||('целое число от '+min)}));}
 function pick(name,label,value,options){const s=h('select',{name});s.append(new Option('не задано',''));for(const[v,t] of options)s.append(new Option(t,v));s.value=value||'';return h('label',{},label,s);}
 function intervalRow(day,from,to){const row=h('div',{class:'sd-interval'});
  row.append(h('input',{'aria-label':DAYS[day-1]+' с',placeholder:'08:00',value:from!=null?hhmm(from):'','data-role':'from'}),h('span',{text:'—'}),h('input',{'aria-label':DAYS[day-1]+' до',placeholder:'20:00',value:to!=null?hhmm(to):'','data-role':'to'}));
  const del=h('button',{type:'button',text:'Убрать','aria-label':'Убрать интервал '+DAYS[day-1]});del.addEventListener('click',()=>{row.remove();refreshDay(day);});row.append(del);return row;}
 function refreshDay(day){const box=state.form.querySelector('[data-day="'+day+'"]'),list=box.querySelector('.sd-intervals');const n=list.querySelectorAll('.sd-interval').length;
  list.querySelector('.sd-closed')?.remove();if(!n)list.prepend(h('span',{class:'sd-closed',text:'закрыто'}));box.querySelector('[data-add]').disabled=n>=MAX_DAY||state.locked;}
 function week(windows){const w=h('div',{class:'sd-week','aria-label':'Недельное расписание приёма'});
  for(let d=1;d<=7;d++){const list=h('div',{class:'sd-intervals'}),add=h('button',{type:'button',text:'+ интервал','data-add':'1','aria-label':'Добавить интервал '+DAYS[d-1]});
   for(const x of windows.filter(x=>x.weekday===d))list.append(intervalRow(d,x.from_minute,x.to_minute));
   const box=h('div',{class:'sd-day','data-day':String(d)},h('b',{text:DAYS[d-1]}),list,add);add.addEventListener('click',()=>{list.append(intervalRow(d,null,null));refreshDay(d);});w.append(box);}
  return w;}
 function collect(){const f=state.form,val=n=>f.elements[n].value.trim(),flag=n=>val(n)===''?null:val(n)==='1',int=n=>{const v=val(n);if(v==='')return null;if(!/^\d{1,6}$/.test(v))throw Error('«'+f.elements[n].closest('label').firstChild.textContent+'»: целое число.');return Number(v);};
  const mode=f.querySelector('input[name=mode]:checked').value,windows=[];
  if(mode==='WEEKLY')for(let d=1;d<=7;d++)for(const row of f.querySelectorAll('[data-day="'+d+'"] .sd-interval')){const a=minutes(row.querySelector('[data-role=from]').value),b=minutes(row.querySelector('[data-role=to]').value);
   if(a==null||b==null||a>=b)throw Error(DAYS[d-1]+': интервал в формате ЧЧ:ММ, начало раньше конца (конец суток — 24:00).');windows.push({weekday:d,from_minute:a,to_minute:b});}
  if(windows.length>MAX_WEEK)throw Error('Не более '+MAX_WEEK+' интервалов в неделю.');
  const zone=val('timezone_region')||null;if(mode==='WEEKLY'&&!zone)throw Error('Для недельного расписания укажите часовой пояс магазина явно (например, Europe/Moscow).');
  const result={receiving_window_mode:mode,timezone_region:zone,backroom_flag:flag('backroom_flag'),backroom_pallets:int('backroom_pallets'),backroom_rolls:int('backroom_rolls'),unattended_drop_flag:flag('unattended_drop_flag'),
   storage_temp_class:val('storage_temp_class')||null,ramp_flag:flag('ramp_flag'),ramp_height_mm:int('ramp_height_mm'),max_vehicle_outer_height_mm:int('max_vehicle_outer_height_mm'),max_vehicle_outer_length_mm:int('max_vehicle_outer_length_mm'),
   default_unload_method:val('default_unload_method')||null,loader_required:flag('loader_required'),access_note:val('access_note')||null,windows};
  const rules=state.deliveryRules;if(rules?.status==='KNOWN'){
   const duration=val('unload_norm_min')===''?null:Number(val('unload_norm_min')),strict=flag('window_strict');
   if(duration!==(rules.unload_norm_min==null?null:Number(rules.unload_norm_min))){result.unload_norm_min=int('unload_norm_min');if(result.unload_norm_min!=null&&(result.unload_norm_min<1||result.unload_norm_min>1440))throw Error('Норма разгрузки: от 1 до 1440 минут.');}
   if(strict!==rules.window_strict)result.window_strict=strict;
   if('unload_norm_min'in result||'window_strict'in result)result.expected_delivery_rules_hash=rules.source_hash;
  }else if(val('unload_norm_min')||val('window_strict'))throw Error('Правила доставки не прочитаны. Перечитайте карточку.');
  return result;}
 function status(text){const node=state.host.querySelector('#sdProfileStatus');if(node)node.textContent=text;}
 function lock(){const busy=state.busy,rec=state.record,pending=!!rec?.raw;state.locked=busy||pending||!state.installed||!auth().hasPermission('warehouse_settings_edit');if(!state.form||!state.host.contains(state.form))return;
  state.form.querySelectorAll('input,select,textarea,button').forEach(n=>{n.disabled=state.locked;});for(let d=1;d<=7;d++)refreshDay(d);
  const q=id=>state.host.querySelector(id);q('#sdSave').disabled=state.locked;q('#sdRetry').hidden=!rec?.value||rec.value.rejected;q('#sdRetry').disabled=busy;
  q('#sdRestart').hidden=!rec?.value?.rejected;q('#sdArchive').hidden=!rec?.damaged;q('#sdWeekly').hidden=state.form.querySelector('input[name=mode]:checked')?.value!=='WEEKLY';}
 async function call(body){const r=await fetch(base()+'/api/master-data/stores/profile'+(body?'':'?addr='+encodeURIComponent(state.addr)),{method:body?'PUT':'GET',headers:auth().headers(body?{'Content-Type':'application/json'}:{}),...(body?{body:JSON.stringify(body)}:{})});
  let d=null;try{d=await r.json();}catch{}if(!r.ok){const e=Error(typeof d?.detail==='string'?d.detail:d?.detail?.message||JSON.stringify(d?.detail)||('HTTP '+r.status));e.confirmed=d?.detail?.outcome_confirmed===true;e.status=r.status;throw e;}return d;}
 async function send(){const rec=state.record;if(state.busy||!rec?.value)return;const v=rec.value;state.busy=true;lock();
  try{const d=await call(v.body);
   if(d.operation_id!==v.body.operation_id||d.store_addr!==v.body.store_addr||d.version!==v.body.expected_version+1||d.stock_changed!==false)throw Object.assign(Error('Ответ не подтверждает сохранённую команду. Повторите её.'),{confirmed:false});
   store.settle(rec);state.record=null;const text='Профиль сохранён: версия '+d.version+', операция '+d.operation_id+'.';state.busy=false;await load();status(text);return;
  }catch(e){if(e.confirmed){const value={...v,rejected:true},raw=JSON.stringify(value);try{localStorage.setItem(rec.storageKey,raw);if(localStorage.getItem(rec.storageKey)===raw)state.record={...rec,raw,value};}catch{}}
   status(e.message+(e.confirmed?' Отказ подтверждён сервером — исправьте данные.':' Результат не подтверждён: повторите ту же команду.'));}
  finally{state.busy=false;lock();}}
 function render(data){const p=data.profile||{},host=state.host;state.deliveryRules=data.delivery_rules;
  const rules={...(data.delivery_rules||{}),...('unload_norm_min'in p?{unload_norm_min:p.unload_norm_min}:{}),...('window_strict'in p?{window_strict:p.window_strict}:{})};
  const mode=h('div',{class:'sd-radio',role:'radiogroup','aria-label':'Режим окон приёма'});
  for(const[v,t] of [['UNCONFIGURED','Окна не заданы'],['WEEKLY','Недельное расписание']]){const r=h('input',{type:'radio',name:'mode',value:v});r.checked=(p.receiving_window_mode||'UNCONFIGURED')===v;r.addEventListener('change',lock);mode.append(h('label',{},r,t));}
  const form=h('form',{autocomplete:'off'},h('h3',{text:'Окна приёма товара'}),mode,
   h('div',{id:'sdWeekly'},h('label',{},'Часовой пояс магазина (IANA)',h('input',{name:'timezone_region',value:p.timezone_region||'',placeholder:'Europe/Moscow',title:'Обязателен для недельного расписания; проверяется по каталогу Oracle'})),
    h('p',{class:'sd-note',text:'День без интервалов — закрыт. Интервалы [с, до) без пересечений, до 8 в день; ночной приём — двумя днями.'}),week(data.windows||[])),
   h('h3',{text:'Подсобка'}),h('div',{class:'sd-grid'},tri('backroom_flag','Подсобка есть',p.backroom_flag),num('backroom_pallets','Вместимость, паллет',p.backroom_pallets,0),num('backroom_rolls','Вместимость, ролл-кейджей',p.backroom_rolls,0),
    tri('unattended_drop_flag','Можно оставить без получателя',p.unattended_drop_flag,'Справочно: не отменяет подтверждение приёмки и маркировки'),pick('storage_temp_class','Температура хранения',p.storage_temp_class,[['AMBIENT','обычная'],['CHILLED','охлаждение'],['FROZEN','заморозка']])),
   h('h3',{text:'Подъезд и разгрузка'}),h('div',{class:'sd-grid'},num('unload_norm_min','Норма разгрузки, мин',rules.unload_norm_min,1,'Укажите от 1 до 1440 минут. Расчёт маршрута использует норму для обслуживания точки.'),
    tri('window_strict','Строгое окно доставки',rules.window_strict,'Строгое окно блокирует подтверждение маршрута при опоздании; нестрогое показывает предупреждение.'),
    tri('ramp_flag','Рампа есть',p.ramp_flag),num('ramp_height_mm','Высота рампы, мм',p.ramp_height_mm,0),
    num('max_vehicle_outer_height_mm','Макс. внешняя высота ТС, мм',p.max_vehicle_outer_height_mm,1,'Внешний габарит машины, не высота кузова; пусто — ограничение не задано'),
    num('max_vehicle_outer_length_mm','Макс. внешняя длина ТС, мм',p.max_vehicle_outer_length_mm,1,'Внешний габарит машины, не длина кузова; пусто — ограничение не задано'),
    pick('default_unload_method','Способ разгрузки',p.default_unload_method,[['PALLET','паллетой'],['ROLL_CAGE','ролл-кейджем'],['MANUAL','вручную']]),tri('loader_required','Нужен грузчик',p.loader_required)),
   h('label',{},'Примечание о подъезде',h('textarea',{name:'access_note',maxlength:'1000',rows:'2',placeholder:'без телефонов и кодов доступа',value:p.access_note||''})),
   h('label',{},'Основание изменения',h('input',{name:'reason',maxlength:'1000',placeholder:'не короче 8 символов'})));
  form.elements.access_note.value=p.access_note||'';
  const actions=h('div',{class:'sd-actions'},h('button',{type:'button',id:'sdSave',class:'sd-primary',text:'Сохранить профиль'}),h('button',{type:'button',id:'sdRetry',text:'Повторить сохранение',hidden:true}),
   h('button',{type:'button',id:'sdRestart',text:'Исправить после отказа',hidden:true}),h('button',{type:'button',id:'sdArchive',text:'Архивировать повреждённую команду',hidden:true}));
  const head=h('p',{class:'sd-note',text:!data.installed?'Профиль ещё не установлен в базе: таблицы ожидают применения миграции. Поля показаны только для просмотра.':data.configured?'Версия профиля '+data.version+' · изменил '+(data.updated_by||'—')+' · '+(data.updated_at||''):'Профиль не заполнен. Первая запись будет версией 1.'});
  host.replaceChildren(h('h3',{text:'Профиль магазина'}),head,form,actions,h('p',{id:'sdProfileStatus',role:'status','aria-live':'polite'}));state.form=form;
  host.querySelector('#sdSave').addEventListener('click',save);host.querySelector('#sdRetry').addEventListener('click',send);
  host.querySelector('#sdRestart').addEventListener('click',async()=>{try{store.settle(state.record);state.record=null;await load();}catch(e){status(e.message);}});
  host.querySelector('#sdArchive').addEventListener('click',async()=>{try{store.archiveDamaged(state.record);state.record=null;await load();}catch(e){status(e.message);}});
  lock();}
 async function save(){try{if(state.locked)return;const reason=state.form.elements.reason.value.trim();if(reason.length<8)throw Error('Укажите основание не короче 8 символов.');
   const body={operation_id:'STORE.PROFILE:'+crypto.randomUUID(),store_addr:state.addr,expected_version:state.version,reason,...collect()};
   state.record=store.save({body});await send();}catch(e){status(e.message);lock();}}
 async function load(){const addr=state.addr;state.busy=true;
  try{const d=await call();if(!state.isCurrent()||state.addr!==addr)return;state.version=d.version;state.installed=d.installed!==false;
   let rec=null;try{rec=store.read();}catch{rec={raw:'unreadable',damaged:true};}state.record=rec?.raw?rec:null;
   const pendingHere=rec?.value&&rec.value.body.store_addr===addr;
   render(pendingHere?{...d,profile:{...rec.value.body},windows:rec.value.body.windows}:d);
   if(rec?.value&&!pendingHere)status('Есть незавершённая команда профиля другого магазина: «'+rec.value.body.store_addr+'». Откройте его и повторите команду.');
   else if(pendingHere)status('Есть сохранённая команда этого магазина. Повторите её прежде новой правки.');else if(rec?.damaged)status('Сохранённая команда повреждена. Архивируйте её перед новой правкой.');
  }catch(e){state.host.replaceChildren(h('p',{class:'sd-note',text:'Профиль не прочитан: '+e.message}));}finally{state.busy=false;if(state.form&&state.host.contains(state.form))lock();}}
 window.StoreProfileForm={open(host,addr,isCurrent){state={host,addr,isCurrent,busy:false,record:null,version:0,installed:false,locked:true,form:null};host.hidden=false;host.replaceChildren(h('p',{class:'sd-note',text:'Читаем профиль…'}));load();}};
})();
