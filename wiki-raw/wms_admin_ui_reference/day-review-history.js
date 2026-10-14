(() => {
 const el=id=>document.getElementById(id),auth=()=>window.wmsAdminAuth;
 let epoch=0,next=null;const scope=()=>JSON.stringify([auth().state.apiBase,auth().state.user?.username]);
 const labels={shipping_register_page_incomplete:'Реестр СТ показан частично',shipping_declared_cells_occupied:'Занятые зарегистрированные ячейки грузовой зоны',shipping_members_not_departed_in_page:'Строки СТ без подтверждённого выезда на показанной странице',external_erp_ack_pending:'Ответ ERP ожидается',regulatory_ack_not_reconciled:'Государственный ответ не сверён',
  regulatory_stock_source_unverified:'Не подтверждена исходная проводка государственного сообщения',
  stock_quantity_invariants:'Нарушение количества или резерва',physical_unit_composition:'Расхождение состава физических единиц',
  open_warehouse_tasks:'Незавершённые складские задания',delivery_discrepancies:'Расхождения доставки',
  interwarehouse_receipt_pending:'Межскладская приёмка не завершена',interwarehouse_placement_pending:'Межскладское размещение не завершено',
  interwarehouse_onward_pending:'Второе межскладское плечо не подготовлено',interwarehouse_custody_pending:'Ответственность первого плеча не снята',
  interwarehouse_unload_pending:'Межскладская выгрузка не подтверждена',return_placement_pending:'Возврат не размещён',
  supplier_handover_pending:'Передача поставщику не подтверждена',disposal_pending:'Брак ожидает утилизации',
  tare_offers_unaccepted:'Тара не принята',tare_loss_unresolved:'Недостача тары без решения',
  expense_approval_pending:'Расходы ожидают решения',expense_allocation_pending:'Расходы не распределены'};
 async function api(path){const identity=scope(),r=await fetch(auth().state.apiBase.replace(/\/$/,'')+path,{headers:auth().headers()}),v=await r.json();
  if(identity!==scope())throw Error('Пользователь изменился.');
  if(!r.ok)throw Error(v.detail?.message||v.detail||'Журнал недоступен.');return v;}
 function td(text){const node=document.createElement('td');node.textContent=String(text??'');return node;}
 function paragraph(text){const node=document.createElement('p');node.textContent=text;return node;}
 function clear(){el('drReviewHistoryRows').replaceChildren();el('drReviewHistoryDetail').replaceChildren();next=null;el('drReviewHistoryNext').disabled=true;}
 async function detail(op){const token=++epoch;
  try{const v=await api('/api/finance/day-reconciliation/reviews/'+encodeURIComponent(op));if(token!==epoch)return;
   el('drReviewHistoryDetail').replaceChildren(paragraph('Склад '+v.warehouse_id+', дата '+v.business_date+', пояс '+v.timezone_region+'. Версия '+v.version+'.'),
    paragraph('Факты рассмотрены '+v.captured_at+'; запись '+v.recorded_at+'. '+v.actor+': '+v.reason),
    paragraph('Запас на момент сверки:'),
    ...v.report.stock.by_base_uom.map(row=>paragraph(row.base_uom+': физически '+row.physical_quantity+', резерв '+row.hard_quantity)),
    paragraph('Открытые обязательства на момент сверки:'),
    ...v.report.open_items.map(row=>paragraph((labels[row.code]||row.code)+': '+row.count)),
    paragraph('Запись сверки сохраняет открытые обязательства. Закрытие дня и внешнее подтверждение не объявлены.'));
   window.dispatchEvent(new CustomEvent("wms-day-review-selected",{detail:{operation_id:op}}));
  }catch(e){if(token===epoch)el('drReviewHistoryMessage').textContent=e.message;}}
 async function load(after=0){const token=++epoch;
  try{const ware=Number(el('drWare').value),day=el('drDay').value,zone=el('drZone').value.trim();
   if(!Number.isSafeInteger(ware)||ware<1||!day||!zone)throw Error('Укажите склад, дату и часовой пояс.');
   const q=new URLSearchParams({business_date:day,timezone_region:zone,after_version:String(after),limit:'20'});
   const v=await api('/api/finance/day-reconciliation/reviews/warehouses/'+ware+'/history?'+q);if(token!==epoch)return;
   el('drReviewHistoryRows').replaceChildren(...v.rows.map(row=>{const tr=document.createElement('tr');
    for(const value of [row.version,row.captured_at,row.actor,row.reason])tr.appendChild(td(value));
    tr.addEventListener('click',()=>detail(row.operation_id));return tr;}));
   next=v.next_after_version;el('drReviewHistoryNext').disabled=!v.has_more;
   el('drReviewHistoryMessage').textContent=v.rows.length?'Выберите запись для просмотра сохранённых обязательств.':'Записей сверки ещё нет.';
   el('drReviewHistoryDetail').replaceChildren();
  }catch(e){if(token===epoch)el('drReviewHistoryMessage').textContent=e.message;}}
 el('drReviewHistoryLoad').addEventListener('click',()=>load());
 el('drReviewHistoryNext').addEventListener('click',()=>{if(next!==null)load(next);});
 for(const id of ['drWare','drDay','drZone'])el(id).addEventListener('input',()=>{epoch++;clear();});
 window.addEventListener('wms-admin-auth-ready',()=>{epoch++;clear();el('drReviewHistoryMessage').textContent='';});
})();
