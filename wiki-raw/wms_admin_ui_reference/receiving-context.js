(() => {
  const root=document.getElementById('receiptContext');
  let order=null,line=null,policy=null;
  const text=(selector,value)=>{root.querySelector(selector).textContent=value??'—';};
  function render(){
    text('[data-order]',order?order.order_number:'Выберите заказ SAP');
    text('[data-warehouse]',order?'Склад '+order.ware_id+' · зона '+(order.receive_cell||'не задана'):'Основание приёмки не выбрано');
    text('[data-version]',order?'Редакция '+order.revision+' · формат '+(order.gateway_contract_version||1):'—');
    text('[data-article]',line?line.articul+' · '+(line.name||''):'Выберите товар');
    text('[data-remaining]',line?(order?.receipt_allowed?'К приёмке ':'Остаток по заказу: ')+line.remaining_qty+' '+line.base_uom:'—');
    text('[data-accepted]',line?(order?.receipt_state==='REVERSED'?'Принято ранее ':'Принято ')+line.accepted_qty+' из '+line.planned_qty+' '+line.base_uom:'—');
    text('[data-scanning]',!policy?'Правила товара ещё не загружены':policy.marking_required?'Уникальные коды маркировки':'ШК штуки или коробки');
    const modes={UNIT:'QR единицы',BOX:'агрегация коробки',PALLET:'агрегация паллеты',UNIT_OR_AGGREGATION:'QR единицы или известная агрегация'};
    text('[data-profiles]',policy?.marking_required?(policy.profiles||[]).map(p=>p.system_code+' / '+p.profile_code+': '+(modes[p.scan_mode]||p.scan_mode)).join('; '):
      policy?'Идентификатор паллеты, партия, срок и фактическое количество':'Способ приёмки определяется карточкой товара');
    const statuses={OPEN:'Открыта приёмка',COMPLETE:'Количество принято полностью',REVERSED:'Поступление сторнировано',RECONCILED:'Приёмка закрыта со сверкой',LEGACY_CLOSED:'Закрыто старым процессом'};
    text('[data-source-status]',order?(statuses[order.receipt_state]||'Статус требует проверки'):'Выберите основание');
    root.dataset.ready=order&&line&&policy?'true':'false';
  }
  window.addEventListener('wms-receipt-selected',event=>{order=event.detail;line=null;policy=null;render();});
  window.addEventListener('wms-receipt-line-selected',event=>{line=event.detail;policy=null;render();});
  window.addEventListener('wms-receipt-policy-selected',event=>{
    if(line?.articul!==event.detail?.articul)return;
    policy=event.detail.policy;render();
  });
  function reset(){order=null;line=null;policy=null;render();}
  window.addEventListener('wms-receipt-selection-reset',reset);
  window.addEventListener('wms-admin-auth-ready',reset);render();
})();
