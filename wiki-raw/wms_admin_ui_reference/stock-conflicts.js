/* Current conflict registry: server keyset pages, no client-side stock repair. */
(() => {
 const panel=document.createElement('section');panel.id='stockConflicts';panel.className='panel dr-overview';
 panel.innerHTML='<h2>Конфликтные строки остатка</h2><p>Текущий запас выбранного склада. Каждая страница читается заново; изменения между страницами возможны. Остатки не исправляются.</p><label>Вид конфликта <select title="Выберите нарушенное условие"><option value="stock_quantity_invariants">Количество, резерв или базовая единица</option><option value="physical_unit_composition">Состав уникальных физических единиц</option></select></label> <button data-first title="Прочитать первые50 текущих конфликтов склада">С начала</button> <button data-next disabled title="Прочитать следующие50 после последней пары UID и ячейки">Следующая страница</button><p role="status"></p><div class="rights-table-wrap"><table class="rights-table"><thead><tr><th>UID паллеты</th><th>Ячейка</th><th>Базовая ЕИ</th><th>Физически</th><th>Жёсткий резерв</th></tr></thead><tbody></tbody></table></div>';
 document.getElementById('dayOverview').after(panel);
 const el=s=>panel.querySelector(s),ware=document.getElementById('drWare'),metric=el('select');
 const auth=()=>window.wmsAdminAuth,base=()=>auth().state.apiBase.replace(/\/$/,'');
 const scope=()=>JSON.stringify([base(),auth().state.user?.username,ware.value,metric.value]);
 let generation=0,next=null,busy=false,linked=false;
 function reset(){generation++;next=null;busy=false;el('tbody').replaceChildren();el('[data-next]').disabled=true;el('[data-first]').disabled=false;el('[role=status]').textContent='Выберите склад и начните чтение.';}
 function render(rows){
  el('tbody').replaceChildren(...rows.map(row=>{const tr=document.createElement('tr');
   for(const key of ['uid_pallet','cell','base_uom','physical_quantity','hard_quantity']){const td=document.createElement('td');td.textContent=row[key]??'NULL';tr.append(td);}return tr;}));
 }
 async function load(first){
  if(busy||!auth()?.hasPermission('transport_dispatch_view'))return;
  const warehouse=Number(ware.value);if(!Number.isSafeInteger(warehouse)||warehouse<=0){el('[role=status]').textContent='Укажите склад.';return;}
  if(first)reset();if(!first&&!next)return;
  const current=++generation,identity=scope(),params=new URLSearchParams({metric:metric.value,limit:'50'});
  if(!first)params.set('after',next);
  busy=true;el('[data-first]').disabled=el('[data-next]').disabled=true;el('[role=status]').textContent='Читаю страницу…';
  try{
   const response=await fetch(base()+'/api/finance/day-reconciliation/warehouses/'+warehouse+'/stock-conflicts?'+params,{headers:auth().headers()});
   const data=await response.json();if(current!==generation||identity!==scope())return;
   if(!response.ok)throw Error(data.detail?.message||JSON.stringify(data.detail));
   if(data.warehouse_id!==warehouse||data.metric!==metric.value||!Array.isArray(data.rows)||data.rows.length>50)throw Error('Страница не соответствует выбранному складу и виду конфликта.');
   render(data.rows);next=data.next_cursor;
   el('[role=status]').textContent='На странице: '+data.rows.length+(data.has_more?'. Есть продолжение.':'. Конец текущей выборки.');
  }catch(error){if(current===generation&&identity===scope())el('[role=status]').textContent=error.message;}
  finally{if(current===generation&&identity===scope()){busy=false;el('[data-first]').disabled=false;el('[data-next]').disabled=!next;}}
 }
 el('[data-first]').onclick=()=>load(true);el('[data-next]').onclick=()=>load(false);
 metric.addEventListener('change',reset);ware.addEventListener('input',reset);
 window.addEventListener('wms-admin-auth-ready',()=>{
  reset();panel.hidden=!auth()?.hasPermission('transport_dispatch_view');
  const requested=new URLSearchParams(location.search).get('stock_metric');
  if(!panel.hidden&&!linked&&['stock_quantity_invariants','physical_unit_composition'].includes(requested)){
   linked=true;metric.value=requested;void load(true);panel.scrollIntoView({block:'start'});
  }
 });panel.hidden=true;
})();
