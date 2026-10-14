(() => {
 const el=id=>document.getElementById(id),auth=()=>window.wmsAdminAuth;
 const scope=()=>JSON.stringify([auth().state.apiBase,auth().state.user?.username]);
 const dialog=el('tpDialog');let source=null,epoch=0,busy=false,cursor=null,rows=[];
 function controls(){
  for(const id of ['tpFrom','tpTo','tpDistrict','tpStore'])el(id).disabled=busy;
  el('tpSearch').disabled=busy;el('tpNext').disabled=busy||!cursor;
  el('tpSearch').textContent=busy?'Поиск...':'Найти рейсы';
 }
 function render(){
  el('tpRows').replaceChildren(...rows.map(trip=>{
   const tr=document.createElement('tr');
   const parts=trip.shipment_date.split('-'),day=new Date(Number(parts[0]),Number(parts[1])-1,Number(parts[2]));
   for(const value of ['№ '+trip.trip_id,day.toLocaleDateString('ru-RU'),trip.vehicle,
    trip.districts.join(', ')||'Не указаны',trip.stores.join(', ')||'Не указаны',trip.pallet_count]){
    const td=document.createElement('td');td.textContent=String(value??'—');tr.appendChild(td);
   }
   const action=document.createElement('td'),button=document.createElement('button');
   button.textContent='Выбрать';button.className='pick-trip-button';button.setAttribute('aria-label','Выбрать рейс '+trip.trip_id);button.title='Выбрать существующий рейс; назначение или перенос выполняются отдельно';
   button.addEventListener('click',()=>{
    if(!source||source.identity!==scope()||el(source.source_input_id||'sdSt')?.value.trim()!==source.st_number)return;
    window.dispatchEvent(new CustomEvent('wms-st-trip-selected',{detail:{st_number:source.st_number,source_hash:source.source_hash,trip}}));
    dialog.close();
   });
   action.appendChild(button);tr.appendChild(action);return tr;
  }));
  el('tpTable').hidden=!rows.length;el('tpEmpty').hidden=!!rows.length;
  el('tpCount').textContent=rows.length?'Рейсов показано: '+rows.length:'';
 }
 async function search(next=false,initial=false){
  if(!source)return;
  const current=source,token=++epoch;busy=true;controls();
  if(!next){rows=[];cursor=null;render();}
  const params=new URLSearchParams({st_number:current.st_number,limit:'50',purpose:current.purpose||'DEFER'});
  if(!initial){
   if(el('tpFrom').value)params.set('date_from',el('tpFrom').value);
   if(el('tpTo').value)params.set('date_to',el('tpTo').value);
   if(el('tpDistrict').value.trim())params.set('district',el('tpDistrict').value.trim());
   if(el('tpStore').value.trim())params.set('store_code',el('tpStore').value.trim());
  }
  if(next&&cursor)for(const [key,value]of Object.entries(cursor))params.set(key,String(value));
  el('tpMessage').textContent='Читаем существующие рейсы ТМС...';
  try{
   const response=await fetch(auth().state.apiBase.replace(/\/$/,'')+'/api/transport/st-deferrals/trip-candidates?'+params,
    {headers:auth().headers()});
   const result=await response.json();
   if(token!==epoch||current.identity!==scope()||!dialog.open)return;
   if(!response.ok)throw Error(result.detail?.message||'Не удалось получить рейсы.');
   if(current.source_hash&&result.source_hash!==current.source_hash)throw Error('Исходная СТ изменилась. Закройте окно и перечитайте СТ.');
   if(!current.source_hash)current.source_hash=result.source_hash;
   if(initial){el('tpFrom').value=result.date_from;el('tpTo').value=result.date_to;}
   el('tpFrom').min=result.minimum_date;el('tpTo').min=result.minimum_date;
   rows=Array.from(new Map([...rows,...result.rows].map(row=>[row.trip_id,row])).values());
   cursor=result.next_cursor;render();
   el('tpMessage').textContent='Рейсы не ранее '+result.minimum_date+'. Показаны спланированные рейсы до погрузки. Вместимость и условия переноса проверит WMS при сохранении.';
   el('tpEmpty').textContent='Подходящих рейсов нет. Измените период или фильтры. Новый рейс можно создать в существующей ТМС.';
  }catch(error){
   if(token===epoch&&current.identity===scope())el('tpMessage').textContent=error.message;
  }finally{if(token===epoch){busy=false;controls();}}
 }
 window.addEventListener('wms-st-trip-picker-open',event=>{
  source={...event.detail,identity:scope()};rows=[];cursor=null;
  el('tpSubtitle').textContent='Для СТ '+source.st_number;
  for(const id of ['tpFrom','tpTo','tpDistrict','tpStore'])el(id).value='';
  render();dialog.showModal();search(false,true);
 });
 el('tpClose').addEventListener('click',()=>dialog.close());
 dialog.addEventListener('close',()=>{epoch++;busy=false;source=null;controls();});
 el('tpFilters').addEventListener('submit',event=>{event.preventDefault();search();});
 el('tpNext').addEventListener('click',()=>search(true));
 for(const id of ['tpFrom','tpTo','tpDistrict','tpStore'])el(id).addEventListener('input',()=>{
  if(!source||busy)return;epoch++;rows=[];cursor=null;render();controls();
  el('tpMessage').textContent='Фильтры изменены. Нажмите «Найти рейсы», чтобы обновить список.';
  el('tpEmpty').textContent='Список ожидает поиска по выбранным фильтрам.';
 });
 window.addEventListener('wms-admin-auth-ready',()=>{if(dialog.open)dialog.close();});
})();
