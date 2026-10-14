// Справочник магазинов (C-0029): поиск /api/master-data/stores и карточка /stores/card — только чтение.
// Профиль магазина редактирует store-profile-form.js (window.StoreProfileForm).
(() => {
 const $=id=>document.getElementById(id),auth=()=>window.wmsAdminAuth,base=()=>auth().state.apiBase.replace(/\/$/,'');
 let next=null,serial=0,cardSerial=0,timer=0,selected='',identity='';
 async function get(path){const r=await fetch(base()+path,{headers:auth().headers()});let d=null;try{d=await r.json();}catch{}
  if(!r.ok){const e=Error(r.status===403?'Нет права на справочник магазинов.':r.status===404?'Магазин не найден или удалён.':typeof d?.detail==='string'?d.detail:d?.detail?.message||('HTTP '+r.status));e.status=r.status;throw e;}return d;}
 function h(tag,cls,text){const n=document.createElement(tag);if(cls)n.className=cls;if(text!=null)n.textContent=text;return n;}
 const fact=(k,v)=>{const d=h('div');d.append(h('dt',null,k),h('dd',null,v==null||v===''?'—':String(v)));return d;};
 const yes=v=>v==null?null:Number(v)?'да':'нет';
 async function search(append){
  const q=$('sdQuery').value.trim(),mine=++serial;if(!append){next=null;$('sdList').replaceChildren();}
  $('sdSearchNote').textContent='Ищем…';
  try{const d=await get('/api/master-data/stores?limit=30'+(q?'&q='+encodeURIComponent(q):'')+(append&&next?'&after='+encodeURIComponent(next):''));
   if(mine!==serial)return;next=d.next_after;
   for(const s of d.items){const li=h('li'),b=h('button','sd-item');b.type='button';b.dataset.addr=s.addr;b.setAttribute('aria-current',String(s.addr===selected));
    b.append(h('strong',null,s.addr),h('small',null,[s.store_code?'код '+s.store_code:s.erp_link_count>1?'несколько кодов ERP':'без кода ERP',s.region,s.raion].filter(Boolean).join(' · ')));
    b.addEventListener('click',()=>open(s.addr));li.append(b);$('sdList').append(li);}
   $('sdMore').hidden=!next;const n=$('sdList').children.length;
   $('sdSearchNote').textContent=n?'Показано '+n+(next?', есть ещё':'')+'.':'Ничего не найдено.';
  }catch(e){if(mine===serial)$('sdSearchNote').textContent=e.message;}
 }
 function section(title,rows){const s=h('section');s.append(h('h3',null,title));const dl=h('dl','sd-facts');for(const [k,v] of rows)dl.append(fact(k,v));s.append(dl);return s;}
 function render(c){
  const parts=[
   section('Адрес и логистика',[['Адрес',c.addr],['Регион / район',[c.region,c.raion].filter(Boolean).join(' / ')||null],['Направление',c.napr],['Тип ТС',c.transport_type],['Макс. тоннаж, т',c.max_vehicle_tons],['Стол-лифт',yes(c.stol)],['Норма разгрузки, мин',c.unload_norm_min],['Строгое окно (TW_STRICT)',yes(c.tw_strict)],['Отгрузка со склада до',c.shipping_time],['Срок, дн.',c.lead_time],['Ворота по умолчанию',c.dock_default],['Координаты',c.latitude!=null&&c.longitude!=null?c.latitude+', '+c.longitude:null],['Геозона, м',c.geo_fence_radius_m]]),
   section('Приёмка и тара',[['Режим приёмки',c.receipt_mode||'по умолчанию'],['Версия политики',c.receipt_policy_version],['Получателей назначено',c.receiver_count],['Возврат тары',c.tare_return_mode?c.tare_return_mode+(c.tare_return_days!=null?' · '+c.tare_return_days+' дн.':'')+(c.tare_timezone?' · '+c.tare_timezone:''):null]]),
   section('ERP',[['Связь',c.erp_link_state==='AMBIGUOUS'?'несколько связей — нужна сверка':c.erp_link_state==='SINGLE'?'одна':'нет'],['Код магазина',c.store_code],['Название',c.store_name],['GLN',c.gln],['EDI',c.edi_id]])];
  if(c.erp_link_state==='AMBIGUOUS'){const w=h('p','sd-warn','Связи ERP: '+c.erp_links.map(l=>l.store_code).join(', ')+'. Код не выбран автоматически.');parts.push(w);}
  const cal=h('section');cal.append(h('h3',null,'Календарь поставок SAP (склады, доступные вам)'));
  cal.append(c.delivery_calendars.length?h('p',null,c.delivery_calendars.map(x=>'склад '+x.ware_id+': дни '+x.delivery_weekdays+(Number(x.allow_same_day)?' · в тот же день':'')).join('; ')):h('p','sd-note','Нет календаря по доступным складам.'));
  parts.push(cal);$('sdCard').replaceChildren(...parts);
 }
 async function open(addr){
  selected=addr;document.querySelectorAll('.sd-item').forEach(b=>b.setAttribute('aria-current',String(b.dataset.addr===addr)));
  const mine=++cardSerial;$('sdCardNote').textContent='Читаем карточку…';$('sdCard').replaceChildren();$('sdProfile').hidden=true;
  try{const c=await get('/api/master-data/stores/card?addr='+encodeURIComponent(addr));if(mine!==cardSerial)return;
   $('sdCardNote').textContent='';render(c);
   try{const u=new URL(location.href);u.searchParams.set('addr',addr);history.replaceState(history.state,'',u);}catch{}
   window.StoreProfileForm.open($('sdProfile'),addr,()=>mine===cardSerial&&selected===addr);
  }catch(e){if(mine===cardSerial)$('sdCardNote').textContent=e.message;}
 }
 $('sdQuery').addEventListener('input',()=>{clearTimeout(timer);timer=setTimeout(()=>search(false),300);});
 $('sdQuery').addEventListener('keydown',e=>{if(e.key==='Enter'){clearTimeout(timer);search(false);}});
 $('sdMore').addEventListener('click',()=>search(true));
 function changed(){const key=base()+':'+(auth().state.user?.username||'');if(!auth().state.user||identity===key)return;identity=key;selected='';
  $('sdCard').replaceChildren();$('sdProfile').hidden=true;search(false);const addr=new URLSearchParams(location.search).get('addr');if(addr)open(addr);}
 window.addEventListener('wms-admin-auth-ready',changed);setTimeout(changed,0);
})();
