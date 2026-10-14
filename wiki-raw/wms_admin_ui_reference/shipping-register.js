(() => {
 const el=id=>document.getElementById(id),auth=()=>window.wmsAdminAuth;
 const labels={PHYSICALLY_DEPARTED:'Фактический выезд подтверждён',LOADED_NOT_DEPARTED:'Погружено, выезд не подтверждён',
  LOGICAL_SHIPPED_WITHOUT_CURRENT_LOAD_PROOF:'Прежний статус отгрузки без действующего подтверждения погрузки',
  TRIP_NOT_ASSIGNED:'Рейс не назначен',PHYSICAL_LOADING_NOT_CONFIRMED:'Фактическая погрузка не подтверждена'};
 let epoch=0,next=null;
 const scope=()=>JSON.stringify([auth().state.apiBase,auth().state.user?.username]);
 function cell(value){const td=document.createElement('td');td.textContent=String(value??'');return td;}
 function clear(){el('srRows').replaceChildren();el('srCells').replaceChildren();next=null;el('srNext').disabled=true;}
 async function load(after=0){
  const token=++epoch,identity=scope();
  try{
   const ware=Number(el('drWare').value),day=el('drDay').value;
   if(!Number.isSafeInteger(ware)||ware<1||!day)throw Error('Укажите склад и дату.');
   const q=new URLSearchParams({business_date:day,after_id:String(after),limit:'20'});
   const r=await fetch(auth().state.apiBase.replace(/\/$/,'')+'/api/finance/day-reconciliation/warehouses/'+ware+'/shipping-register?'+q,{headers:auth().headers()}),v=await r.json();
   if(token!==epoch||identity!==scope())return;
   if(!r.ok)throw Error(v.detail?.message||v.detail||'Реестр недоступен.');
   el('srRows').replaceChildren(...v.rows.map(row=>{const tr=document.createElement('tr');
    for(const value of [row.st_number,row.pallet_identifier,row.trip_id,row.address,labels[row.physical_state]||row.physical_state,row.root_uid,row.deferral_version?'Перенос, версия '+row.deferral_version:''])tr.appendChild(cell(value));tr.addEventListener('click',()=>{document.getElementById('sdSt').value=row.st_number;document.getElementById('sdSt').dispatchEvent(new Event('input'));});return tr;}));
   el('srCells').replaceChildren(...v.cells.map(row=>{const tr=document.createElement('tr');
    for(const value of [row.cell,row.positive_quantity_rows,row.unshipped_container_rows,row.unshipped_case_rows,row.occupied?'Занята':'В этих регистрах места не обнаружены'])tr.appendChild(cell(value));return tr;}));
   next=v.next_after_id;el('srNext').disabled=!v.has_more;
   el('srMessage').textContent='Строки СТ выбранной даты показаны отдельно от физических корневых мест. '+
    (v.declared_cells_occupied?'В зарегистрированных ячейках остаётся товар или контейнеры.':'В зарегистрированных ячейках занятость не обнаружена.')+
    (v.all_shipping_zone_coverage_verified?
     (v.shipping_zone_empty_confirmed?' Все ячейки каталога классифицированы опубликованной схемой; зарегистрированная грузовая зона пуста в этом снимке.':' Все ячейки каталога классифицированы; грузовая зона занята.'):
     ' Классификация ячеек неполная: '+(v.classification_coverage?.unclassified_cell_count??'?')+' без роли, '+(v.classification_coverage?.ambiguous_cell_count??'?')+' неоднозначных. Примеры: '+(v.classification_coverage?.incomplete_cell_sample||[]).join(', ')+'. Опубликуйте полную схему склада.')+
    ' Незарегистрированные физические зоны этим отчётом не проверяются; день автоматически не закрывается.';
  }catch(e){if(token===epoch&&identity===scope())el('srMessage').textContent=e.message;}
 }
 el('srLoad').addEventListener('click',()=>load());el('srNext').addEventListener('click',()=>{if(next!==null)load(next);});
 for(const id of ['drWare','drDay'])el(id).addEventListener('input',()=>{epoch++;clear();});
 window.addEventListener('wms-admin-auth-ready',()=>{epoch++;clear();el('srMessage').textContent='';});
})();
