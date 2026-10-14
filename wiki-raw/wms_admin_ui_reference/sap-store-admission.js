(() => {
  const el=id=>document.getElementById(id);let epoch=0;
  const labels={ACCEPTED:'Допущен',PENDING_LATE:'Ожидает решения: поздний заказ',
    PENDING_CALENDAR:'Ожидает решения: календарь',REJECTED:'Отказ ERP'};
  function scope(){const a=window.wmsAdminAuth;return JSON.stringify([a.state.apiBase,a.state.user?.username]);}
  async function api(path,options={}){
    const before=scope(),base=(window.wmsAdminAuth.state.apiBase||'http://127.0.0.1:8088').replace(/\/$/,'');
    const r=await fetch(base+path,{...options,headers:window.wmsAdminAuth.headers(options.headers||{})}),body=await r.json();
    if(before!==scope())throw new Error('Пользователь изменился. Перечитайте источник.');
    if(!r.ok)throw new Error(typeof body.detail==='string'?body.detail:JSON.stringify(body.detail||body));
    return body;
  }
  const preparationLabels={
    ALREADY_PREPARED_USE_SAVED_RESULT:'СТ уже подготовлена',
    SOURCE_NOT_ADMITTED:'Нет разрешения ERP',
    SOURCE_OPERATIONAL_STATE_FROZEN:'Исполнение уже началось',
    LEGACY_ADDRESS_MISSING:'Не задан адрес прежней СТ',
    CURRENT_CALENDAR_CLOSED:'Магазин закрыт для доставки в эту дату',
    CURRENT_CALENDAR_ZONE_CHANGED:'Изменился часовой пояс календаря',
    PICKING_DEADLINE_PASSED:'Истёк срок завершения отбора',
    LEGACY_ARTICLE_NOT_UNIQUE:'Нет однозначной карточки товара',
    SOURCE_PICKING_CELL_MISSING:'Не назначена ячейка отбора этого склада',
    PACKAGING_MASS_DIMENSIONS_REQUIRED:'Не заданы вложенность, масса или размеры коробки',
    LEGACY_ROUNDING_CHANGES_SOURCE_QUANTITY:'Округление коробок изменяет исходное количество',
    WHOLE_PACKAGING_LAYOUT_REQUIRED:'Для прежней СТ требуется целое число коробок',
    SOURCE_BASE_UNIT_AMBIGUOUS:'У строк товара разные базовые единицы',
    SOURCE_DEMAND_EMPTY:'Исходный заказ пуст'
  };
  function cell(value){const td=document.createElement('td');td.textContent=String(value??'');return td;}
  async function detail(id){
    const token=++epoch;
    try{
      const value=await api('/api/integrations/sap/store-orders/'+id);if(token!==epoch)return;
      const readiness=await api('/api/integrations/sap/store-orders/'+id+'/preparation-readiness');if(token!==epoch)return;
      const last=value.admission_decision?.last_decision;
      el('sapAdmissionDetail').textContent=`Заказ #${id}: ${labels[value.admission_status]||value.admission_status}.
        Первичный импорт: ${labels[value.result_json.admission_status]||value.result_json.admission_status}.
        Версия решения: ${value.admission_decision?.version||0}.`+
        (last?` Решение ${last.decision_id}: ${last.reason}; ${last.reference}.`:'');
      el('sapPreparationReadiness').textContent=readiness.already_prepared?'СТ уже подготовлена. Используйте сохранённый результат.':readiness.ready_for_operator_layout?'Параметры готовы к операторской укладке. При подтверждении система проверит их снова.':'Подготовка СТ требует исправления: '+[...readiness.blockers.map(code=>preparationLabels[code]||code),...readiness.lines.flatMap(line=>line.blockers.map(code=>line.articul+': '+(preparationLabels[code]||code)))].join('; ');
      window.dispatchEvent(new CustomEvent('sap-store-source-selected',{detail:{order_id:id}}));
      el('sapAdmissionHash').value=value.content_hash;
      el('sapAdmissionDemand').replaceChildren(...value.demand_json.Lines.map(line=>{
        const tr=document.createElement('tr');tr.appendChild(cell(line.material));tr.appendChild(cell(line.quantity));tr.appendChild(cell(line.unit));return tr;
      }));
    }catch(e){if(token===epoch)el('sapAdmissionDetail').textContent=e.message;}
  }
  async function list(){
    const token=++epoch,w=el('sapAdmissionWare').value.trim();
    try{
      const values=await api('/api/integrations/sap/store-orders'+(w?'?warehouse_id='+encodeURIComponent(w):''));if(token!==epoch)return;
      el('sapAdmissionRows').replaceChildren(...values.map(value=>{
        const tr=document.createElement('tr');
        for(const v of [value.order_number,value.ware_id,value.store_code,value.delivery_date,labels[value.admission_status]||value.admission_status,value.status])tr.appendChild(cell(v));
        tr.addEventListener('click',()=>detail(value.customer_order_id));return tr;
      }));
      el('sapAdmissionDetail').textContent=values.length?'Выберите источник для просмотра решения и исходной потребности.':'Нет источников в доступном складе.';
      el('sapAdmissionDemand').replaceChildren();el('sapAdmissionHash').value='';el('sapPreparationReadiness').textContent='';
    }catch(e){if(token===epoch)el('sapAdmissionDetail').textContent=e.message;}
  }
  async function importDecision(){
    const file=el('sapAdmissionXml').files?.[0];if(!file)return;
    if(file.size>4*1024*1024){el('sapAdmissionImportMessage').textContent='XML превышает 4 МиБ.';return;}
    const button=el('sapAdmissionImport');button.disabled=true;
    try{
      const result=await api('/api/integrations/sap/store-decisions',{method:'POST',headers:{'Content-Type':'application/xml'},body:await file.arrayBuffer()});
      el('sapAdmissionImportMessage').textContent=`Решение ${result.decision_id} сохранено: ${labels[result.admission_status]||result.admission_status}. Потребность и остатки не изменены.`;
    }catch(e){el('sapAdmissionImportMessage').textContent=e.message+' При потере ответа повторите тот же исходный XML.';}
    finally{button.disabled=false;}
  }
  window.addEventListener('wms-admin-auth-ready',()=>{epoch++;el('sapAdmissionRows').replaceChildren();el('sapAdmissionDemand').replaceChildren();el('sapAdmissionHash').value='';el('sapPreparationReadiness').textContent='';el('sapAdmissionDetail').textContent='Обновите список источников.';});
  el('sapAdmissionRefresh').addEventListener('click',list);el('sapAdmissionImport').addEventListener('click',importDecision);
})();
