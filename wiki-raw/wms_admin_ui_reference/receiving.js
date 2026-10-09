(() => {
  const el = id => document.getElementById(id);
  const state = {order:null,line:null,policy:null,units:new Map(),unitQuantities:new Map(),replanOperations:new Map(),closeOperations:new Map(),reopenOperations:new Map(),aggregations:[],operation:crypto.randomUUID(),label:null,busy:false};
  const message = text => {el('receiptMessage').textContent=text;};
  async function api(path, body, method) {
    const base=(window.wmsAdminAuth.state.apiBase||'http://127.0.0.1:8088').replace(/\/$/,'');
    const response=await fetch(base+path,{method:method||(body?'POST':'GET'),headers:window.wmsAdminAuth.headers(body?{'Content-Type':'application/json'}:{}),body:body?JSON.stringify(body):undefined});
    const data=await response.json();
    if(!response.ok) throw new Error(typeof data.detail==='string'?data.detail:JSON.stringify(data.detail||data));
    return data;
  }
  function row(values,onClick) {
    const tr=document.createElement('tr');
    for(const value of values){const td=document.createElement('td');td.textContent=String(value??'');tr.appendChild(td);}
    if(onClick)tr.addEventListener('click',onClick);
    return tr;
  }
  const sourceDocument = new URLSearchParams(location.search).get('receipt_document_id');
  let sourceOpened = false;
  async function loadOrders() {
    try {
      const w=el('receiptWarehouse').value;
      const orders=await api('/api/integrations/sap/supply-orders'+(w?'?warehouse_id='+encodeURIComponent(w):''));
      el('receiptOrders').replaceChildren(...orders.map(o=>row([o.order_number,o.ware_id,o.revision,o.receive_cell],()=>selectOrder(o.order_id))));
      message(orders.length?'Выберите заказ SAP.':'Заказов SAP нет. Ожидается файл от шлюза.');
      if(sourceDocument && !sourceOpened){
        if(!/^[1-9][0-9]*$/.test(sourceDocument))throw new Error('Некорректный номер накладной.');
        const selected=await api('/api/integrations/sap/supply-orders/by-receipt-document/'+encodeURIComponent(sourceDocument));
        sourceOpened=true;await selectOrder(selected.order_id);
        message('Открыта поставка выбранной накладной. Приёмка — по паллетам и сканированию; размещение — через задания.');
      }
    }catch(error){message(error.message);}
  }
  async function selectOrder(id) {
    state.line=null;state.policy=null;el('receiptConfirm').disabled=true;
    try {
      const order=await api('/api/integrations/sap/supply-orders/'+encodeURIComponent(id));state.order=order;window.dispatchEvent(new CustomEvent("wms-receipt-selected", {detail:order}));
      el('receiptOrderTitle').textContent=`Заказ ${order.order_number}; склад ${order.ware_id}`;
      el('receiptLines').replaceChildren(...order.lines.map(l=>row([l.line_number,l.articul,l.name,l.planned_qty,l.accepted_qty,l.remaining_qty,l.suggested_pallet_count??'Укажите укладку'],()=>selectLine(l))));
    }catch(error){message(error.message);}
  }
  async function selectLine(line) {
    state.line=line;state.policy=null;el('receiptConfirm').disabled=true;
    resetPallet();
    try {
      const policy=await api('/api/finished-goods/skus/'+encodeURIComponent(line.articul)+'/receiving-policy');
      if(state.line!==line)return;
      if(!policy.configured)throw new Error('Сначала сохраните настройки приёмки и маркировки в карточке товара.');
      state.policy=policy;el('receiptMarking').hidden=!policy.marking_required;
      el('receiptBarcode').disabled=policy.marking_required;
      el('receiptQuantity').value=line.suggested_pallet_quantity||line.remaining_qty;
      el('receiptSuggestion').textContent=`Осталось ${line.remaining_qty} ${line.base_uom}. Предложено ${line.suggested_pallet_count??'не задано'} паллет; норма ${line.norma_ukladki||'не задана'}. Можно изменить количество на этой паллете.`;
      el('receiptProfile').replaceChildren(...policy.profiles.map((p,i)=>{const o=document.createElement('option');o.value=String(i);o.textContent=`${p.system_code} / ${p.profile_code}`;return o;}));
      updateScanMode();el('receiptConfirm').disabled=Number(line.remaining_qty)<=0||!window.wmsAdminAuth.hasPermission('warehouse_receipt_confirm');
      message(`Приёмка: ${line.articul}, ${line.name}`);
    }catch(error){message(error.message);}
  }
  function resetPallet(){state.operation=crypto.randomUUID();state.label=null;el('receiptZpl').disabled=true;el('receiptConfirmLabel').disabled=true;el('receiptPrintedScan').value='';el('receiptLabelMessage').textContent='';state.units.clear();state.unitQuantities.clear();state.aggregations=[];for(const id of ['receiptSscc','receiptBarcode','receiptMarkCode'])el(id).value='';renderCodes();}
  function updateScanMode() {
    const p=state.policy?.profiles[Number(el('receiptProfile').value)];
    const modes=p?.scan_mode==='UNIT_OR_AGGREGATION'?['UNIT','BOX','PALLET']:p?[p.scan_mode]:[];
    el('receiptScanMode').replaceChildren(...modes.map(m=>{const o=document.createElement('option');o.value=m;o.textContent={UNIT:'Единица товара',BOX:'Коробка',PALLET:'Паллета'}[m];return o;}));
  }
  function addCode() {
    try {
      const p=state.policy?.profiles[Number(el('receiptProfile').value)],code=el('receiptMarkCode').value,kind=el('receiptScanMode').value;
      if(!p||!code)throw new Error('Выберите профиль и отсканируйте код.');
      const entry={system_code:p.system_code,profile_code:p.profile_code,code};
      if(kind==='UNIT'){
        const id=el('receiptUnit').value.trim();if(!id)throw new Error('Укажите номер физической единицы.');
        const codes=state.units.get(id)||[];
        if(codes.some(c=>c.system_code===p.system_code&&c.profile_code===p.profile_code))throw new Error('Этот профиль единицы уже отсканирован.');
        codes.push(entry);state.units.set(id,codes);state.unitQuantities.set(id,el('receiptUnitQuantity').value||null);
        const required=state.policy.profiles.filter(q=>['UNIT','UNIT_OR_AGGREGATION'].includes(q.scan_mode));
        if(codes.length===required.length&&/^\d+$/.test(id))el('receiptUnit').value=String(Number(id)+1);
      }else state.aggregations.push({...entry,level:kind});
      el('receiptMarkCode').value='';renderCodes();el('receiptMarkCode').focus();
    }catch(error){message(error.message);}
  }
  function renderCodes(){
    const lines=[];
    for(const [id,codes] of state.units)for(const c of codes)lines.push(`Единица ${id}: ${c.system_code} / ${c.profile_code} — ${c.code}`);
    for(const c of state.aggregations)lines.push(`${c.level==='BOX'?'Коробка':'Паллета'}: ${c.system_code} / ${c.profile_code} — ${c.code}`);
    el('receiptCodes').replaceChildren(...lines.map(t=>{const li=document.createElement('li');li.textContent=t;return li;}));
    el('receiptCodeCount').textContent=`Единиц со сканированиями: ${state.units.size}; агрегаций: ${state.aggregations.length}`;
  }
  async function confirm(){
    if(state.busy||!state.order||!state.line||!state.policy)return;
    state.busy=true;el('receiptConfirm').disabled=true;
    const body={operation_id:state.operation,line_number:state.line.line_number,sscc:el('receiptSscc').value.trim(),quantity:el('receiptQuantity').value,
      product_barcode:state.policy.marking_required?null:el('receiptBarcode').value.trim(),supplier_batch:el('receiptBatch').value.trim(),expiry_date:el('receiptExpiry').value,
      produced_date:el('receiptProduced').value||null,gross_weight:el('receiptWeight').value||null,pallet_height:el('receiptHeight').value||null,pallet_height_m:el('receiptHeightM').value||null,volume_m3:el('receiptVolume').value||null,
      units:Array.from(state.units,([unit_id,codes])=>({unit_id,codes,quantity:state.unitQuantities.get(unit_id)||null})),aggregations:state.aggregations};
    try {
      const result=await api(`/api/receiving/supply-orders/${encodeURIComponent(state.order.order_id)}/pallets`,body);
      const text=`Паллета ${result.pallet_identifier} принята: ${result.quantity}. Задание ${result.task_id}: ${result.receive_cell} → ${result.putaway_cell}.`;
      const id=state.order.order_id;resetPallet();await selectOrder(id);message(text);
    }catch(error){message(error.message+' При повторе без изменения данных используется тот же номер операции.');}
    finally {state.busy=false;el('receiptConfirm').disabled=!state.line||!state.policy||!window.wmsAdminAuth.hasPermission('warehouse_receipt_confirm');}
  }
  window.addEventListener('wms-admin-auth-ready',loadOrders);
  if(window.wmsAdminAuth.state.user)loadOrders();
  el('receiptRefresh').addEventListener('click',loadOrders);el('receiptNew').addEventListener('click',resetPallet);
  el('receiptProfile').addEventListener('change',updateScanMode);el('receiptAddCode').addEventListener('click',addCode);
  el('receiptMarkCode').addEventListener('keydown',e=>{if(e.key==='Enter'){e.preventDefault();addCode();}});
  el('receiptClearCodes').addEventListener('click',()=>{state.units.clear();state.unitQuantities.clear();state.aggregations=[];renderCodes();});
  el('receiptConfirm').addEventListener('click',confirm);
  function warehouse(){const id=el('receiptWarehouse').value||state.order?.ware_id;if(!id)throw new Error('Укажите склад или выберите заказ.');return id;}
  async function issueLabel(){
    if(!state.order||!state.line){message('Выберите заказ и товар.');return;}
    const printWindow=window.open('about:blank','_blank');
    el('receiptIssueLabel').disabled=true;
    try{
      const body={operation_id:state.operation+'-label',line_number:state.line.line_number,quantity:el('receiptQuantity').value,supplier_batch:el('receiptBatch').value.trim(),expiry_date:el('receiptExpiry').value};
      const label=await api(`/api/receiving/supply-orders/${encodeURIComponent(state.order.order_id)}/labels`,body);
      state.label=label;el('receiptSscc').value=label.sscc;el('receiptZpl').disabled=false;el('receiptConfirmLabel').disabled=false;
      el('receiptLabelMessage').textContent=`SSCC ${label.sscc}. Напечатайте и наклейте этикетку, затем отсканируйте её в поле подтверждения.`;
      const response=await fetch(window.wmsAdminAuth.state.apiBase+`/api/receiving/labels/${label.label_id}`,{headers:window.wmsAdminAuth.headers()});
      if(!response.ok)throw new Error('Ошибка формирования этикетки.');
      const url=URL.createObjectURL(await response.blob());if(printWindow)printWindow.location=url;else{const a=document.createElement('a');a.href=url;a.target='_blank';a.textContent='Открыть этикетку';el('receiptLabelMessage').appendChild(a);}
      setTimeout(()=>URL.revokeObjectURL(url),300000);
    }catch(error){if(printWindow)printWindow.close();message(error.message);}
    finally{el('receiptIssueLabel').disabled=false;}
  }
  async function downloadZpl(){try{if(!state.label)return;const response=await fetch(window.wmsAdminAuth.state.apiBase+`/api/receiving/labels/${state.label.label_id}?format=zpl&dpi=${el('receiptPrinterDpi').value}`,{headers:window.wmsAdminAuth.headers()});if(!response.ok)throw new Error('Ошибка ZPL.');const url=URL.createObjectURL(await response.blob()),a=document.createElement('a');a.href=url;a.download=`sscc-${state.label.sscc}.zpl`;a.click();setTimeout(()=>URL.revokeObjectURL(url),10000);}catch(error){message(error.message);}}
  async function confirmPrinted(){try{if(!state.label)return;await api(`/api/receiving/labels/${state.label.label_id}/confirm`,{scanned_sscc:el('receiptPrintedScan').value});el('receiptLabelMessage').textContent='Наклеенная этикетка подтверждена. Можно принять паллету.';}catch(error){message(error.message);}}
  async function loadSettings(){try{const v=await api(`/api/receiving/warehouses/${warehouse()}/settings`);for(const [id,key] of [['receiptGs1Prefix','company_prefix'],['receiptSsccExtension','extension_digit'],['receiptPlacementMetric','placement_metric'],['receiptCoordinateUnit','coordinate_unit_m'],['receiptTruckSpeed','reachtruck_mps'],['receiptLiftSpeed','lift_mps']])el(id).value=v[key]??'';el('receiptSettingsMessage').textContent='Настройки загружены.';}catch(error){message(error.message);}}
  async function saveSettings(){try{await api(`/api/receiving/warehouses/${warehouse()}/settings`,{company_prefix:el('receiptGs1Prefix').value.trim()||null,extension_digit:Number(el('receiptSsccExtension').value),placement_metric:el('receiptPlacementMetric').value,coordinate_unit_m:el('receiptCoordinateUnit').value,reachtruck_mps:el('receiptTruckSpeed').value,lift_mps:el('receiptLiftSpeed').value},'PUT');el('receiptSettingsMessage').textContent='Настройки склада сохранены.';}catch(error){message(error.message);}}
  async function saveSkuRule(){try{if(!state.line)throw new Error('Выберите товар.');await api(`/api/receiving/warehouses/${warehouse()}/skus/${encodeURIComponent(state.line.articul)}/placement-rule`,{pick_cell:el('receiptPickCell').value.trim(),temp_min:el('receiptSkuTempMin').value||null,temp_max:el('receiptSkuTempMax').value||null,min_shelf_days:Number(el('receiptMinShelf').value)},'PUT');el('receiptSettingsMessage').textContent='Правило товара сохранено.';}catch(error){message(error.message);}}
  async function saveCellRule(){try{const c=el('receiptStorageCell').value.trim();if(!c)throw new Error('Укажите ячейку хранения.');await api(`/api/receiving/warehouses/${warehouse()}/cells/${encodeURIComponent(c)}/placement-rule`,{temp_min:el('receiptCellTempMin').value||null,temp_max:el('receiptCellTempMax').value||null,pick_cell:el('receiptPickCell').value.trim()||null,travel_sec:el('receiptTravelSeconds').value||null,basis:el('receiptTravelBasis').value},'PUT');el('receiptSettingsMessage').textContent='Правило ячейки сохранено.';}catch(error){message(error.message);}}
  async function closeSupply(){try{if(!state.order)throw new Error('Выберите заказ.');const id=state.order.order_id,reason=el('receiptCloseReason').value.trim();const v=await api(`/api/receiving/supply-orders/${encodeURIComponent(id)}/close`,{operation_id:state.closeOperations.get(id)||rememberOperation(state.closeOperations,id),reason});await selectOrder(id);message('Приёмка закрыта. Недостача: '+v.lines.filter(l=>Number(l.shortage)>0).map(l=>`${l.material}: ${l.shortage}`).join(', '));}catch(error){message(error.message);}}
  async function exchange(){try{const events=await api('/api/integrations/sap/receipt-events');const names={PENDING:'Ожидает отправки',EXPORTED:'Передано шлюзу',ACKNOWLEDGED:'Принято SAP',REJECTED:'Отклонено SAP',ERROR:'Ошибка'};const kinds={PALLET_RECEIVED:'Приёмка',PALLET_PUTAWAY:'Размещение',SUPPLY_RECONCILED:'Сверка поставки',PUTAWAY_REPLANNED:'Переназначение адреса',SUPPLY_REOPEN_REQUESTED:'Повторное открытие поставки',PUTAWAY_CANCELLED:'Отмена размещения'};el('receiptExchangeRows').replaceChildren(...events.map(e=>{const tr=row([e.order_number,e.pallet_identifier,kinds[e.event_type]||e.event_type,names[e.status]||e.status,e.external_document_id||'']);const td=document.createElement('td');if(['ERROR','REJECTED','EXPORTED'].includes(e.status)&&window.wmsAdminAuth.hasPermission('sap_supply_import')){const b=document.createElement('button');b.textContent='Повторить отправку';b.addEventListener('click',async()=>{try{await api(`/api/integrations/sap/receipt-events/${encodeURIComponent(e.event_id)}/retry`,{});await exchange();}catch(error){message(error.message);}});td.appendChild(b);}tr.appendChild(td);return tr;}));}catch(error){message(error.message);}}
  async function replan(){try{const key=JSON.stringify(['receiptReplanTask','receiptReplanPallet','receiptReplanCell','receiptReplanReason'].map(id=>el(id).value));const v=await api(`/api/receiving/putaway/${el('receiptReplanTask').value}/replan`,{operation_id:state.replanOperations.get(key)||rememberOperation(state.replanOperations,key),scanned_pallet:el('receiptReplanPallet').value,scanned_from_cell:el('receiptReplanCell').value,reason:el('receiptReplanReason').value});message(`Задание ${v.task_id}: новый адрес ${v.placement.cell}.`);}catch(error){message(error.message);}}
  el('receiptIssueLabel').addEventListener('click',issueLabel);el('receiptZpl').addEventListener('click',downloadZpl);el('receiptConfirmLabel').addEventListener('click',confirmPrinted);
  el('receiptPrintedScan').addEventListener('keydown',e=>{if(e.key==='Enter'){e.preventDefault();confirmPrinted();}});
  el('receiptLoadSettings').addEventListener('click',loadSettings);el('receiptSaveSettings').addEventListener('click',saveSettings);el('receiptSaveSkuRule').addEventListener('click',saveSkuRule);el('receiptSaveCellRule').addEventListener('click',saveCellRule);el('receiptCloseSupply').addEventListener('click',closeSupply);el('receiptRefreshExchange').addEventListener('click',exchange);el('receiptReplan').addEventListener('click',replan);
  function rememberOperation(map,id){const op=crypto.randomUUID();map.set(id,op);return op;}
  async function reopenSupply(){try{if(!state.order)throw new Error('Выберите заказ.');const id=state.order.order_id;await api(`/api/receiving/supply-orders/${encodeURIComponent(id)}/reopen`,{operation_id:state.reopenOperations.get(id)||rememberOperation(state.reopenOperations,id),reason:el('receiptCloseReason').value.trim()});state.closeOperations.delete(id);await selectOrder(id);message('Запрошено повторное открытие. Приёмка возобновится после новой версии заказа SAP.');}catch(error){message(error.message);}}
  async function loadSkuRule(){try{const line=state.line;if(!line)throw new Error('Выберите товар.');const v=await api(`/api/receiving/warehouses/${warehouse()}/skus/${encodeURIComponent(line.articul)}/placement-rule`);if(state.line!==line)return;for(const [id,key] of [['receiptPickCell','pick_cell'],['receiptSkuTempMin','temp_min'],['receiptSkuTempMax','temp_max'],['receiptMinShelf','min_shelf_days']])el(id).value=v[key]??(key==='min_shelf_days'?0:'');el('receiptSettingsMessage').textContent=v.configured===false?'Правило товара ещё не задано.':'Правило товара загружено.';}catch(error){message(error.message);}}
  async function loadCellRule(){try{const c=el('receiptStorageCell').value.trim();if(!c)throw new Error('Укажите ячейку хранения.');const v=await api(`/api/receiving/warehouses/${warehouse()}/cells/${encodeURIComponent(c)}/placement-rule`);el('receiptCellTempMin').value=v.temp_min??'';el('receiptCellTempMax').value=v.temp_max??'';el('receiptSettingsMessage').textContent='Температурное правило ячейки загружено.';}catch(error){message(error.message);}}
  el('receiptReopenSupply').addEventListener('click',reopenSupply);el('receiptLoadSkuRule').addEventListener('click',loadSkuRule);el('receiptLoadCellRule').addEventListener('click',loadCellRule);
})();