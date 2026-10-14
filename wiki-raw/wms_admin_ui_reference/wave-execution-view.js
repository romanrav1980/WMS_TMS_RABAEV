(() => {
  const reasons={
    PICKING_PENDING:'Отбор не завершён',
    CANCELLED_DEMAND_REQUIRES_RECONCILIATION:'Отменённая потребность требует решения',
    FACT_OR_APPROVED_SHORT_INCOMPLETE:'Факт и утверждённая недостача не покрывают задание',
    PHYSICAL_FULFILLMENT_OR_SHIPPING_PENDING:'Место ожидает фактической отгрузки',
    REPLENISHMENT_PENDING:'Пополнение не завершено',
    PHYSICAL_TASK_PENDING:'Физическое задание не завершено',
    CASE_CONTROL_OR_SHIPPING_PENDING:'Место ожидает контроля или отгрузки',
    CANCELLED_CASE_DEMAND_REPLAN_REQUIRED:'Пустое отменённое место: требуется решение о потребности',
    CANCELLED_CASE_STOCK_RECONCILIATION_REQUIRED:'Отменённое место содержит товар: требуется сверка',
    EMPTY_CASE_DECISION_PENDING:'Пустое место требует решения',
    ACTIVE_WAVE_HARD_REMAINS:'Остался активный резерв волны'
  };
  const kinds={PICK_TASK:'Отбор',WAREHOUSE_TASK:'Складское задание',CASE:'Место сборки',REPLENISHMENT:'Пополнение',RESERVATION:'Резерв',HARD:'Жёсткий резерв'};
  function render(panel,data) {
    const target=panel.querySelector('[data-items]');target.replaceChildren();
    const table=document.createElement('table');table.className='rights-table';
    const head=document.createElement('thead'),heading=document.createElement('tr');
    for(const name of ['Объект','Статус','Количество','Исполнитель','Следующее действие']){
      const th=document.createElement('th');th.textContent=name;heading.append(th);
    }
    head.append(heading);table.append(head);const body=document.createElement('tbody');table.append(body);
    for(const item of data.items||[]){
      const row=document.createElement('tr'),name=document.createElement('td');
      if(item.kind==='WAREHOUSE_TASK' && /^[1-9]\d*$/.test(String(item.id))){
        const a=document.createElement('a');a.href='warehouse-tasks.html?task_id='+encodeURIComponent(item.id)+'#warehouseTaskDetail';
        a.textContent=(kinds[item.kind]||item.kind)+' #'+item.id;a.title='Открыть текущее состояние и исполнение задания';name.append(a);
      }else name.textContent=(kinds[item.kind]||item.kind)+' #'+item.id;
      if(item.kind==='CASE'){
        const info=document.createElement('small');info.className='wave-execution-place';
        info.textContent=[item.carrier_identifier,item.current_cell?'Ячейка '+item.current_cell:null,
          item.case_content_version!==undefined?'Состав v'+item.case_content_version:null].filter(Boolean).join(' · ');
        name.append(info);
      }
      row.append(name);
      const reason=item.display_reason||item.reason;
      for(const value of [item.status,(item.quantity??'—')+(item.quantity_semantics==='HISTORICAL_PICKED'?' · факт отбора':''),item.actor||'—',
        (data.completed&&reason?"Историческая причина: ":"")+(reasons[reason]||reason||(data.completed?'Решение завершения сохранено':'Препятствий по объекту нет'))+
        (item.physical_stock_rows!==undefined?'; строк физического остатка: '+item.physical_stock_rows:'')]){
        const td=document.createElement('td');td.textContent=value;row.append(td);
      }
      if(item.kind==='CASE'&&/^[1-9]\d*$/.test(String(item.id))){
        const actions=row.lastChild,links=document.createElement('div');links.className='wave-execution-actions';
        if(window.wmsAdminAuth?.hasPermission('case_pick_view')){
          const picking=document.createElement('a');picking.className='wave-execution-action';
          picking.href='case-pick-tsd.html?case_task_id='+encodeURIComponent(item.id);
          picking.textContent='Открыть задание сборки';
          picking.title='Прочитать именно это задание, его строки и следующий этап; без автоматического взятия в работу';
          links.append(picking);
        }
        const composition=document.createElement('a');composition.className='wave-execution-action';
        composition.href='warehouse-hus.html?identifier='+encodeURIComponent('CASE:'+item.id)+'#huComposition';
        composition.textContent='Текущий состав';composition.title='Проверить фактическое место, партии и резерв';links.append(composition);
        if(!data.completed&&typeof item.control_identifier==='string'&&item.control_identifier&&
          window.wmsAdminAuth?.hasPermission('outgoing_pallet_check')){
          const control=document.createElement('a');control.className='wave-execution-action primary';
          control.href='warehouse-tasks.html?qc_shipment='+encodeURIComponent(item.control_identifier)+'#outgoingQuality';
          control.textContent='Открыть контроль';control.title='Предъявить текущий состав в существующем процессе контроля';links.append(control);
        }
        actions.append(links);
      }
      if(reason && !data.completed)row.className='wave-execution-blocker';
      body.append(row);
    }
    if(!(data.items||[]).length){const p=document.createElement('p');p.textContent='Объекты исполнения не найдены.';target.append(p);}
    else target.append(table);
    const demands=data.mixed_decision?.demands||data.deferred_decision?.demands||[];
    for(const demand of demands){
      const current=demand.current_planning;if(!current)continue;
      const p=document.createElement('p');p.className='wave-execution-demand';
      p.textContent='Заказ '+current.order_id+', строка '+current.line_id+': потребность для планирования '+
        current.quantity+' '+(current.unit||'')+'; отобрано '+current.picked_quantity+', резерв '+current.hard_quantity+'.';
      p.title='Незакреплённая потребность исходного заказа; не является подтверждением отгрузки';target.append(p);
    }
    panel.querySelector('[data-wave-number]').textContent='#'+data.wave_id;
    panel.querySelector('[data-wave-state]').textContent=data.status;
    panel.querySelector('[data-blockers]').textContent=data.completed?'Решение сохранено':String(data.blocking_count??0);
  }
  window.wmsWaveExecutionView={render};
})();
