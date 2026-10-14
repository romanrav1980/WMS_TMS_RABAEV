window.dayReconDocuments=(()=>{
 const node=(tag,value)=>{const n=document.createElement(tag);n.textContent=value;return n;};
 function target(kind,id,warehouse){
  if(kind==='EVENT_OUTBOX'&&/^[1-9]\d*$/.test(id))return 'external-outbox.html?event_id='+encodeURIComponent(id);
  if(kind==='WAREHOUSE_TASK'&&/^[1-9]\d*$/.test(id))return 'warehouse-tasks.html?task_id='+encodeURIComponent(id);
  if(kind==='DELIVERY_CASE'&&/^[A-Za-z0-9_.:-]{1,100}$/.test(id))return 'store-investigations.html?case_id='+encodeURIComponent(id);
  if(kind==='LOGISTICS_EXPENSE')return 'logistics-expenses.html?warehouse_id='+warehouse+'&operation_id='+encodeURIComponent(id);
  return null;
 }
 function append(card,documents,count,warehouse){
  if(!documents?.available){card.append(node('small','Идентификаторы для этого показателя пока не возвращаются; используйте связанный реестр.'));return;}
  const details=node('details','');details.className='dr-documents';
  const ids=documents.document_ids||[];details.append(node('summary','Документы: '+ids.length+' из '+count));
  details.append(node('p',documents.scope==='CURRENT_STOCK_SNAPSHOT'?'Текущий остаток: внутренний UID паллеты и ячейка. Это не остаток на конец выбранного дня; исправление не выполняется.':documents.scope==='CURRENT_EXTERNAL_MESSAGES'?'Сообщения текущей очереди; принятие внешней системой проверяется отдельно. Порядок по идентификатору.':'Текущие незавершённые обязательства; порядок по идентификатору. Это не список только за выбранный день.'));
  const list=node('ul','');
  for(const id of ids){
   const row=node('li',''),url=target(documents.document_kind,id,warehouse);
   if(url){const a=node('a',id);a.href=url;a.title='Открыть существующий документ; проведение не выполняется';row.append(a);}
   else row.append(node('code',id));
   const stock=documents.stock_rows?.find(item=>item.document_id===id);
   if(stock)row.append(node('span',' · UID '+(stock.uid_pallet??'не указан')+' · ячейка '+(stock.cell??'не указана')+' · физически '+(stock.physical_quantity??'NULL')+' · резерв '+(stock.hard_quantity??'NULL')+' '+(stock.base_uom??'единица не указана')));
   list.append(row);
  }
  details.append(list);if(documents.has_more)details.append(node('p','Показаны первые '+documents.limit+(documents.document_kind==='STOCK_ROW'?'. Продолжение доступно в реестре конфликтов ниже.':'. Остальные документы доступны в реестре.')));
  if(documents.document_kind==='STOCK_ROW'&&['stock_quantity_invariants','physical_unit_composition'].includes(documents.metric)){
   const link=node('a','Открыть постраничный реестр конфликтов');
   link.href='day-reconciliation.html?warehouse_id='+encodeURIComponent(warehouse)+'&stock_metric='+encodeURIComponent(documents.metric)+'#stockConflicts';
   link.title='Читать текущие конфликты по50 строк; никаких исправлений запаса';details.append(link);
  }
  card.dataset.search+=' '+ids.join(' ').toLowerCase();card.append(details);
 }
 return{append};
})();