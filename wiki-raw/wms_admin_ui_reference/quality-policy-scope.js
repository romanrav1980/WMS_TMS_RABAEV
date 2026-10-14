// C-0025/C-0029 (NI05.1): выбор области правила из справочников. Склад/подсклад — лёгкие опции
// /api/master-data/warehouses/options (поиск на сервере, до 100 строк, без подсчёта запасов), магазин —
// справочник /api/master-data/stores. Поля qsWare/qsAddr остаются единственным источником значения:
// выбор только записывает их и вызывает прежний сброс прочитанной версии.
(() => {
 const $=id=>document.getElementById(id),auth=()=>window.wmsAdminAuth,base=()=>auth().state.apiBase.replace(/\/$/,'');
 let wares=[],storeSerial=0,storeNext=null,timer=0,cardSerial=0,wareSerial=0,wareTimer=0;
 const known=new Map(),missing=new Set();
 const set=(id,value)=>{const n=$(id);if(n.value===value)return;n.value=value;n.dispatchEvent(new Event('input',{bubbles:true}));};
 async function get(path){const r=await fetch(base()+path,{headers:auth().headers()});let d=null;try{d=await r.json();}catch{}if(!r.ok){const e=Error(r.status===403?'нет права':typeof d?.detail==='string'?d.detail:d?.detail?.message||('HTTP '+r.status));e.status=r.status;throw e;}return d;}
 const wareLabel=w=>w.id+' · '+(w.name||'без названия')+(w.parent?' · подсклад склада '+w.parent:'');
 const toWare=r=>({id:Number(r.id),name:String(r.name??''),parent:r.parent_ware_id??null});
 function renderWares(more){
  const current=$('qsWare').value.trim();
  $('qsWareList').replaceChildren(new Option(wares.length?'Выберите склад или подсклад ('+wares.length+(more?'+':'')+')':'Ничего не найдено',''),...wares.map(w=>new Option(wareLabel(w),String(w.id))));
  $('qsWareList').value=wares.some(w=>String(w.id)===current)?current:'';
 }
 async function loadWares(){
  const note=$('qsWareNote');
  if(!auth().hasPermission('warehouse_settings_view')){note.textContent='Нет права на справочник складов — укажите номер склада вручную.';return;}
  const q=$('qsWareFind').value.trim(),mine=++wareSerial;note.textContent='Ищем в справочнике складов…';
  try{const d=await get('/api/master-data/warehouses/options?limit=100'+(q?'&q='+encodeURIComponent(q):''));if(mine!==wareSerial)return;
   wares=d.items.map(toWare).filter(w=>Number.isSafeInteger(w.id)&&w.id>0);for(const w of wares)known.set(String(w.id),w);
   note.textContent=wares.length?'Показано '+wares.length+(d.next_after?' первых — уточните поиск по номеру или названию.':'.'):'Склад не найден — проверьте запрос или введите номер вручную.';renderWares(!!d.next_after);summary();}
  catch(e){if(mine===wareSerial)note.textContent='Справочник складов недоступен ('+e.message+') — укажите номер склада вручную.';}
 }
 // Название для номера, введённого вручную или восстановленного из сохранённой команды.
 async function lookupWare(id){
  if(!/^[1-9][0-9]{0,9}$/.test(id)||known.has(id)||missing.has(id)||!auth().hasPermission('warehouse_settings_view'))return;
  try{const d=await get('/api/master-data/warehouses/options?limit=100&q='+encodeURIComponent(id));const hit=d.items.map(toWare).find(w=>String(w.id)===id);if(hit)known.set(id,hit);else missing.add(id);summary();}catch{}
 }
 function storeMode(){return document.querySelector('input[name=qsStoreMode]:checked')?.value||'ALL';}
 function applyMode(){
  const all=storeMode()==='ALL';$('qsStorePick').hidden=all;
  if(all)set('qsAddr','*');else if($('qsAddr').value==='*')set('qsAddr','');
  summary();
 }
 async function findStores(append){
  const q=$('qsStoreFind').value.trim(),mine=++storeSerial,list=$('qsStoreList');
  if(!append){storeNext=null;list.replaceChildren();}
  $('qsStoreNote').textContent='Ищем…';
  try{const d=await get('/api/master-data/stores?limit=30'+(q?'&q='+encodeURIComponent(q):'')+(append&&storeNext?'&after='+encodeURIComponent(storeNext):''));
   if(mine!==storeSerial)return;storeNext=d.next_after;
   for(const s of d.items){const o=new Option(s.addr+(s.store_code?' · код '+s.store_code:s.erp_link_count>1?' · несколько кодов ERP':'')+(s.region?' · '+s.region:'')+(s.raion?' / '+s.raion:''),s.addr);list.append(o);}
   $('qsStoreMore').hidden=!storeNext;
   $('qsStoreNote').textContent=list.options.length?'Найдено '+list.options.length+(storeNext?'+ (есть ещё)':'')+'. Выберите магазин стрелками и Enter.':'Магазин не найден. Проверьте запрос или введите точный код ниже.';
  }catch(e){if(mine===storeSerial)$('qsStoreNote').textContent=e.status===403?'Нет права на справочник магазинов — введите точный код ниже.':'Справочник магазинов недоступен ('+e.message+') — введите точный код ниже.';}
 }
 let picked='';
 async function pickStore(addr){
  if(!addr||(addr===picked&&$('qsAddr').value===addr))return;picked=addr;set('qsAddr',addr);const mine=++cardSerial;$('qsStoreCard').textContent='Читаем карточку магазина…';
  try{const c=await get('/api/master-data/stores/card?addr='+encodeURIComponent(addr));if(mine!==cardSerial||$('qsAddr').value!==addr)return;
   $('qsStoreCard').textContent=[c.erp_link_state==='AMBIGUOUS'?'Несколько связей с ERP ('+c.erp_links.length+') — код не выбран, нужна сверка':c.store_code?'Код ERP '+c.store_code:'Код ERP не сопоставлен',c.region&&('регион '+c.region+(c.raion?' / '+c.raion:'')),'приёмка '+(c.receipt_mode||'по умолчанию'),'получателей '+c.receiver_count,c.shipping_time&&('отгрузка до '+c.shipping_time)].filter(Boolean).join(' · ');}
  catch(e){if(mine===cardSerial)$('qsStoreCard').textContent=e.status===404?'Магазин не найден или удалён — сервер не примет такое правило.':'Карточка недоступна: '+e.message;}
  summary();
 }
 function summary(){
  const ware=$('qsWare').value.trim(),addr=$('qsAddr').value,cat=$('qsCategory');
  const w=known.get(ware);if(ware&&!w)lookupWare(ware);
  $('qsScope').textContent=ware?'Область: '+(w?wareLabel(w):'склад '+ware+(missing.has(ware)?' (нет в справочнике)':''))+' · '+(addr==='*'?'все магазины':addr?'магазин «'+addr+'»':'магазин не выбран')+' · '+cat.options[cat.selectedIndex].text+'.':'Область не выбрана.';
  const all=addr==='*';const radio=document.querySelector('input[name=qsStoreMode][value='+(all?'ALL':'ONE')+']');if(radio&&!radio.checked){radio.checked=true;$('qsStorePick').hidden=all;}
  if(!all&&addr&&$('qsStoreCard').dataset.addr!==addr){$('qsStoreCard').dataset.addr=addr;if(!$('qsStoreCard').textContent.startsWith('Читаем'))$('qsStoreCard').textContent='';}
  $('qsWareList').value=wares.some(x=>String(x.id)===ware)?ware:'';
 }
 // Кнопки помощника следуют блокировке основной формы (незавершённая команда, чтение).
 function mirror(){const off=$('qsWare').disabled;for(const id of ['qsStoreSearch','qsStoreMore'])$(id).disabled=off;}
 $('qsWareFind').addEventListener('input',()=>{clearTimeout(wareTimer);wareTimer=setTimeout(loadWares,300);});
 $('qsWareList').addEventListener('change',e=>{if(e.target.value)set('qsWare',e.target.value);summary();});
 document.querySelectorAll('input[name=qsStoreMode]').forEach(r=>r.addEventListener('change',applyMode));
 $('qsStoreFind').addEventListener('input',()=>{clearTimeout(timer);timer=setTimeout(()=>findStores(false),350);});
 $('qsStoreFind').addEventListener('keydown',e=>{if(e.key==='Enter'){e.preventDefault();clearTimeout(timer);findStores(false);}if(e.key==='ArrowDown'&&$('qsStoreList').options.length){e.preventDefault();$('qsStoreList').focus();}});
 $('qsStoreSearch').addEventListener('click',()=>findStores(false));$('qsStoreMore').addEventListener('click',()=>findStores(true));
 $('qsStoreList').addEventListener('change',e=>pickStore(e.target.value));
 $('qsStoreList').addEventListener('keydown',e=>{if(e.key==='Enter'){e.preventDefault();pickStore(e.target.value);}});
 for(const id of ['qsWare','qsAddr','qsCategory'])$(id).addEventListener('input',summary);$('qsCategory').addEventListener('change',summary);
 new MutationObserver(mirror).observe($('qsWare'),{attributes:true,attributeFilter:['disabled']});
 let loaded=false;function ready(){if(loaded||!auth().state.user)return;loaded=true;loadWares();setTimeout(summary,0);}
 window.addEventListener('wms-admin-auth-ready',()=>setTimeout(()=>{ready();summary();},0));setTimeout(ready,0);
})();
