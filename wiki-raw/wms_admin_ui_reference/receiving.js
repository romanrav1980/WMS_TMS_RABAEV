(() => {
  const el = id => document.getElementById(id);
  const state = {order:null,line:null,policy:null,readEpoch:0,listEpoch:0,units:new Map(),unitQuantities:new Map(),replanOperations:new Map(),closeOperations:new Map(),reopenOperations:new Map(),aggregations:[],operation:crypto.randomUUID(),label:null,busy:false};
  const message = text => {el('receiptMessage').textContent=text;};
  const formDraft=window.wmsReceiptFormDraft.create({fields:window.wmsReceiptFormState.fields,busy:()=>state.busy,
    capture:()=>window.wmsReceiptFormState.capture(state),valid:(data,policy)=>window.wmsReceiptFormState.valid(data,policy),
    apply:data=>window.wmsReceiptFormState.apply(data,state,updateScanMode,renderCodes),
    reset:()=>{resetPallet();if(state.order&&state.line&&state.policy)formDraft.mount(state.order,state.line,state.policy);}});
  function updateLabelAvailability(){
    el('receiptIssueLabel').disabled=!(state.order?.receipt_allowed&&state.line&&state.policy&&!state.busy&&Number(state.line.remaining_qty)>0);
  }
  updateLabelAvailability();
  async function api(path, body, method) {
    const base=(window.wmsAdminAuth.state.apiBase||'http://127.0.0.1:8088').replace(/\/$/,'');
    const scope=window.wmsReceiptIntent.scope();
    const intent=body?window.wmsReceiptIntent.prepare(path,body):null;
    if(intent?.storage_key)formDraft.submitted(intent);
    const response=await fetch(base+path,{method:method||(body?'POST':'GET'),headers:window.wmsAdminAuth.headers(body?{'Content-Type':'application/json'}:{}),body:body?JSON.stringify(intent.body):undefined});
    const responseText=await response.text();
    let data;
    try{data=JSON.parse(responseText);}catch{
      throw new Error(body?'Сервер не подтвердил результат. Исходная команда сохранена; повторите её без изменения данных.':'Сервер не вернул данные. Повторите чтение.');
    }
    if(scope!==window.wmsReceiptIntent.scope())throw new Error('Пользователь или сервер изменился. Перечитайте данные.');
    if(intent)window.wmsReceiptIntent.settle(intent,response.status,data);
    if(!response.ok) throw new Error(typeof data.detail==='string'?data.detail:JSON.stringify(data.detail||data));
    return data;
  }
  function row(values,selection) {
    const tr=document.createElement('tr');
    for(const value of values){const td=document.createElement('td');td.textContent=String(value??'');tr.appendChild(td);}
    if(selection){
      tr.dataset.receiptSelectable='true';tr.dataset.orderId=selection.order_id;
      if(selection.line_number!=null){tr.dataset.lineNumber=selection.line_number;tr.dataset.articul=selection.articul;}
      tr.tabIndex=0;tr.title=selection.line_number!=null?'Выбрать товарную позицию':'Выбрать заказ SAP';
      const action=document.createElement('td'),button=document.createElement('button');
      button.type='button';button.textContent='Выбрать';button.className='receipt-select-button';
      action.appendChild(button);tr.appendChild(action);
    }
    return tr;
  }
  function bindSelection(id){
    const container=el(id);
    const select=event=>{
      const selected=event.target?.closest('tr[data-receipt-selectable]');
      if(!selected||!container.contains(selected))return;
      if(event.type==='keydown'){
        if(event.key!=='Enter'&&event.key!==' ')return;
        event.preventDefault();
      }
      const data=selected.dataset;
      if(data.lineNumber!=null)void selectLine({line_number:data.lineNumber,articul:data.articul},data.orderId);
      else void selectOrder(data.orderId);
    };
    container.addEventListener('click',select);container.addEventListener('keydown',select);
  }
  bindSelection('receiptOrders');bindSelection('receiptLines');
  const sourceDocument = new URLSearchParams(location.search).get('receipt_document_id');
  const sourceQuery=new URLSearchParams(location.search);
  const linkedWarehouse=sourceQuery.get('warehouse_id');
  if(linkedWarehouse&&/^[1-9][0-9]*$/.test(linkedWarehouse)&&Number.isSafeInteger(Number(linkedWarehouse)))
    el('receiptWarehouse').value=linkedWarehouse;
  const sourceOrder=sourceQuery.get('supply_order_id')||sourceQuery.get('order_id');
  const sourceLine=sourceQuery.get('line_number');
  let sourceOpened=false,sourceLineOpened=false;
  async function loadOrders() {
    if(state.busy){message('Дождитесь подтверждения текущей паллеты.');return;}
    const token=++state.listEpoch;
    try {
      const w=el('receiptWarehouse').value;
      const orders=await api('/api/integrations/sap/supply-orders'+(w?'?warehouse_id='+encodeURIComponent(w):''));
      if(token!==state.listEpoch)return;
      el('receiptOrders').replaceChildren(...orders.map(o=>row([o.order_number,o.ware_id,o.revision,o.receive_cell],{order_id:o.order_id})));
      message(orders.length?'Выберите заказ SAP.':'Заказов SAP нет. Ожидается файл от шлюза.');
      if(sourceOrder && !sourceOpened){
        if(sourceDocument||sourceOrder.length>100||(sourceQuery.get('supply_order_id')&&sourceQuery.get('order_id')&&sourceQuery.get('supply_order_id')!==sourceQuery.get('order_id')))throw new Error('Укажите одно корректное основание поставки.');
        sourceOpened=true;await selectOrder(sourceOrder);
      }
      if(sourceDocument && !sourceOpened){
        if(!/^[1-9][0-9]*$/.test(sourceDocument))throw new Error('Некорректный номер накладной.');
        const selected=await api('/api/integrations/sap/supply-orders/by-receipt-document/'+encodeURIComponent(sourceDocument));
        if(token!==state.listEpoch)return;
        sourceOpened=true;await selectOrder(selected.order_id);

      }
    }catch(error){if(token===state.listEpoch)message(error.message);}
  }
  async function selectOrder(id,confirmedRefresh=false) {
    if(state.busy&&!confirmedRefresh){message('Дождитесь подтверждения текущей паллеты.');return;}
    const token=++state.readEpoch;
    state.order=null;state.line=null;state.policy=null;el('receiptConfirm').disabled=true;updateLabelAvailability();
    el('receiptLines').replaceChildren();el('receiptOrderTitle').textContent='Загрузка заказа…';
    window.dispatchEvent(new CustomEvent("wms-receipt-selection-reset"));
    try {
      const order=await api('/api/integrations/sap/supply-orders/'+encodeURIComponent(id));if(token!==state.readEpoch)return;state.order=order;window.dispatchEvent(new CustomEvent("wms-receipt-selected", {detail:order}));
      el('receiptOrderTitle').textContent=`Заказ ${order.order_number}; склад ${order.ware_id}`;
      el('receiptLines').replaceChildren(...order.lines.map(l=>row([l.line_number,l.articul,l.name,l.planned_qty,l.accepted_qty,l.remaining_qty,l.suggested_pallet_count??'Укажите укладку'],{order_id:order.order_id,line_number:l.line_number,articul:l.articul})));
      renderPending();
      message(order.receipt_allowed?'Основание SAP открыто. Выберите товар для приёмки.':'Приёмка этого основания закрыта. Доступен просмотр истории.');
      if(sourceLine&&!sourceLineOpened&&(!sourceOrder||order.order_id===sourceOrder)){
        const requested=sourceLine.length<=100?order.lines.find(line=>String(line.line_number)===sourceLine):null;
        if(!requested)throw new Error('Позиция из ссылки не найдена в текущем заказе. Выберите строку в таблице.');
        sourceLineOpened=true;await selectLine(requested,order.order_id,confirmedRefresh);
      }else if(order.lines.length===1)await selectLine(order.lines[0],order.order_id,confirmedRefresh);
      return true;
    }catch(error){if(token===state.readEpoch)message(error.message);}
  }
  async function selectLine(line,expectedOrderId=state.order?.order_id,confirmedRefresh=false) {
    if(state.busy&&!confirmedRefresh){message('Дождитесь подтверждения текущей паллеты.');return;}
    if(!state.order||state.order.order_id!==expectedOrderId){message('Перечитайте выбранный заказ SAP.');return;}
    const currentLine=state.order.lines.find(item=>String(item.line_number)===String(line.line_number)&&item.articul===line.articul);
    if(!currentLine){message('Выбранная строка изменилась. Перечитайте заказ SAP.');return;}
    line=currentLine;
    const token=++state.readEpoch,currentOrder=state.order;
    state.line=line;state.policy=null;el('receiptConfirm').disabled=true;updateLabelAvailability();
    window.dispatchEvent(new CustomEvent("wms-receipt-line-selected",{detail:line}));
    for(const row of el('receiptLines').children)row.dataset.selected=row.firstElementChild?.textContent===String(line.line_number)?'true':'false';
    message('Загрузка правил приёмки для строки '+line.line_number+'…');
    resetPallet();
    try {
      const policy=await api('/api/finished-goods/skus/'+encodeURIComponent(line.articul)+'/receiving-policy');
      if(token!==state.readEpoch||state.order!==currentOrder||state.line!==line)return;
      if(!policy.configured)throw new Error('Сначала сохраните настройки приёмки и маркировки в карточке товара.');

      state.policy=policy;window.dispatchEvent(new CustomEvent('wms-receipt-policy-selected',{detail:{articul:line.articul,policy}}));el('receiptMarking').hidden=!policy.marking_required;
      el('receiptBarcode').disabled=policy.marking_required;
      el('receiptQuantity').value=line.suggested_pallet_quantity||line.remaining_qty;
      el('receiptSuggestion').textContent=`Осталось ${line.remaining_qty} ${line.base_uom}. Предложено ${line.suggested_pallet_count??'не задано'} паллет; норма ${line.norma_ukladki||'не задана'}. Можно изменить количество на этой паллете.`;
      el('receiptProfile').replaceChildren(...policy.profiles.map((p,i)=>{const o=document.createElement('option');o.value=String(i);o.textContent=`${p.system_code} / ${p.profile_code}`;return o;}));
      updateScanMode();el('receiptConfirm').disabled=!canConfirm();updateLabelAvailability();formDraft.mount(state.order,line,policy);
      message(currentOrder.receipt_allowed
        ?`Выбрана строка ${line.line_number}: ${line.articul}, ${line.name}`
        :`Выбрана строка ${line.line_number}. Основание закрыто; доступен просмотр правил и истории.`);
    }catch(error){if(token===state.readEpoch&&state.order===currentOrder)message(error.message);}
  }
  function resetPallet(){formDraft.begin();state.operation=crypto.randomUUID();state.label=null;el('receiptZpl').disabled=true;el('receiptConfirmLabel').disabled=true;el('receiptPrintedScan').value='';el('receiptLabelMessage').textContent='';state.units.clear();state.unitQuantities.clear();state.aggregations=[];for(const id of ['receiptSscc','receiptBarcode','receiptMarkCode'])el(id).value='';renderCodes();updateLabelAvailability();}
  function updateScanMode() {
    const p=state.policy?.profiles[Number(el('receiptProfile').value)];
    const modes=p?.scan_mode==='UNIT_OR_AGGREGATION'?['UNIT','BOX','PALLET']:p?[p.scan_mode]:[];
    el('receiptScanMode').replaceChildren(...modes.map(m=>{const o=document.createElement('option');o.value=m;o.textContent={UNIT:'Единица товара',BOX:'Коробка',PALLET:'Паллета'}[m];return o;}));
  }
  function addCode() {
    try {
      assertScansEditable();
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
  function assertScansEditable(){
    if(state.busy)throw new Error('Дождитесь ответа на текущую команду.');
    if(window.wmsReceiptIntent.damaged().length)throw new Error('Сначала восстановите повреждённый запрос. Сканы не изменены.');
    const pallet=el('receiptSscc').value.trim();
    if(window.wmsReceiptIntent.pending().some(item=>item.body.operation_id===state.operation||(pallet&&item.body.sscc===pallet)))
      throw new Error('Этот набор уже отправлялся. Повторите исходный запрос без изменения сканов.');
  }
  function removeCode(selection){
    try{
      assertScansEditable();
      if(selection.unit_id!==undefined){
        const codes=state.units.get(selection.unit_id),index=codes?.indexOf(selection.scan)??-1;
        if(index<0)return;
        el('receiptUnitQuantity').value=state.unitQuantities.get(selection.unit_id)||'';
        codes.splice(index,1);
        if(!codes.length){state.units.delete(selection.unit_id);state.unitQuantities.delete(selection.unit_id);}
        el('receiptUnit').value=selection.unit_id;
      }else{
        const index=state.aggregations.indexOf(selection.scan);if(index<0)return;state.aggregations.splice(index,1);
      }
      const profile=state.policy?.profiles.findIndex(p=>p.system_code===selection.scan.system_code&&p.profile_code===selection.scan.profile_code);
      if(profile>=0){el('receiptProfile').value=String(profile);updateScanMode();el('receiptScanMode').value=selection.unit_id!==undefined?'UNIT':selection.scan.level;}
      renderCodes();message('Ошибочный скан убран из формы. Остальные сканы сохранены; количество паллеты не изменено. Пересканируйте нужный код.');el('receiptMarkCode').focus();
    }catch(error){message(error.message);}
  }
  function renderCodes(){
    window.wmsReceiptScanList.render(el('receiptCodes'),state.units,state.aggregations,removeCode);
    el('receiptCodeCount').textContent=`Единиц со сканированиями: ${state.units.size}; агрегаций: ${state.aggregations.length}`;
    formDraft.save();
  }
  async function confirm(){
    if(!canConfirm())return;
    try{formDraft.assertPostable();}catch(error){message(error.message);return;}let failed=false;
    state.busy=true;el('receiptConfirm').disabled=true;el('receiptPalletFields').disabled=true;
    const body={operation_id:state.operation,line_number:state.line.line_number,sscc:el('receiptSscc').value.trim(),quantity:el('receiptQuantity').value,
      product_barcode:state.policy.marking_required?null:el('receiptBarcode').value.trim(),supplier_batch:el('receiptBatch').value.trim(),expiry_date:el('receiptExpiry').value,
      produced_date:el('receiptProduced').value||null,gross_weight:el('receiptWeight').value||null,pallet_height:el('receiptHeight').value||null,pallet_height_m:el('receiptHeightM').value||null,volume_m3:el('receiptVolume').value||null,
      units:Array.from(state.units,([unit_id,codes])=>({unit_id,codes,quantity:state.unitQuantities.get(unit_id)||null})),aggregations:state.aggregations};
    try {
      const result=await api(`/api/receiving/supply-orders/${encodeURIComponent(state.order.order_id)}/pallets`,body);
      const text=`Паллета ${result.pallet_identifier} принята: ${result.quantity}. Задание ${result.task_id}: ${result.receive_cell} → ${result.putaway_cell}.`;
      const id=state.order.order_id;resetPallet();await selectOrder(id,true);message(text);
    }catch(error){failed=true;message(error.message+' При повторе без изменения данных используется тот же номер операции.');}
    finally {state.busy=false;if(failed)formDraft.save();el('receiptPalletFields').disabled=false;if(!state.order&&window.wmsAdminAuth.state.user)void loadOrders();el('receiptConfirm').disabled=!canConfirm();updateLabelAvailability();}
  }
  window.addEventListener('wms-admin-auth-ready',()=>{state.readEpoch++;state.listEpoch++;state.order=null;state.line=null;state.policy=null;sourceOpened=false;sourceLineOpened=false;resetPallet();renderPending();loadOrders();});
  if(window.wmsAdminAuth.state.user){renderPending();loadOrders();}
  el('receiptRefresh').addEventListener('click',loadOrders);el('receiptNew').addEventListener('click',()=>{if(formDraft.archiveCurrent()){resetPallet();if(state.order&&state.line&&state.policy)formDraft.mount(state.order,state.line,state.policy);}});
  el('receiptProfile').addEventListener('change',updateScanMode);el('receiptAddCode').addEventListener('click',addCode);
  el('receiptMarkCode').addEventListener('keydown',e=>{if(e.key==='Enter'){e.preventDefault();addCode();}});
  el('receiptClearCodes').addEventListener('click',()=>{try{assertScansEditable();state.units.clear();state.unitQuantities.clear();state.aggregations=[];renderCodes();}catch(error){message(error.message);}});
  el('receiptConfirm').addEventListener('click',confirm);
  function warehouse(){const id=el('receiptWarehouse').value||state.order?.ware_id;if(!id)throw new Error('Укажите склад или выберите заказ.');return id;}
  async function issueLabel(){
    if(!state.order?.receipt_allowed||!state.line||!state.policy||Number(state.line.remaining_qty)<=0){message('Для выпуска этикетки выберите открытое основание и позицию с остатком приёмки.');return;}
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
    finally{updateLabelAvailability();}
  }
  async function downloadZpl(){try{if(!state.label)return;const response=await fetch(window.wmsAdminAuth.state.apiBase+`/api/receiving/labels/${state.label.label_id}?format=zpl&dpi=${el('receiptPrinterDpi').value}`,{headers:window.wmsAdminAuth.headers()});if(!response.ok)throw new Error('Ошибка ZPL.');const url=URL.createObjectURL(await response.blob()),a=document.createElement('a');a.href=url;a.download=`sscc-${state.label.sscc}.zpl`;a.click();setTimeout(()=>URL.revokeObjectURL(url),10000);}catch(error){message(error.message);}}
  async function confirmPrinted(){try{if(!state.label)return;await api(`/api/receiving/labels/${state.label.label_id}/confirm`,{scanned_sscc:el('receiptPrintedScan').value});el('receiptLabelMessage').textContent='Наклеенная этикетка подтверждена. Можно принять паллету.';}catch(error){message(error.message);}}
  async function loadSettings(){try{const v=await api(`/api/receiving/warehouses/${warehouse()}/settings`);for(const [id,key] of [['receiptDeferWaitCell','defer_wait_cell'],['receiptQcSamplePercent','outgoing_qc_sample_percent'],['receiptQcMode','outgoing_qc_mode'],['receiptHuHeightUnit','hu_cell_height_unit'],['receiptGs1Prefix','company_prefix'],['receiptSsccExtension','extension_digit'],['receiptPlacementMetric','placement_metric'],['receiptCoordinateUnit','coordinate_unit_m'],['receiptTruckSpeed','reachtruck_mps'],['receiptLiftSpeed','lift_mps']])el(id).value=v[key]??'';el('receiptQcIndependent').checked=Boolean(v.outgoing_qc_independent);el('receiptSettingsMessage').textContent='Настройки загружены.';}catch(error){message(error.message);}}
  async function saveSettings(){try{await api(`/api/receiving/warehouses/${warehouse()}/settings`,{defer_wait_cell:el('receiptDeferWaitCell').value.trim()||null,outgoing_qc_sample_percent:el('receiptQcSamplePercent').value,outgoing_qc_mode:el('receiptQcMode').value||null,outgoing_qc_independent:el('receiptQcIndependent').checked,hu_cell_height_unit:el('receiptHuHeightUnit').value||null,company_prefix:el('receiptGs1Prefix').value.trim()||null,extension_digit:Number(el('receiptSsccExtension').value),placement_metric:el('receiptPlacementMetric').value,coordinate_unit_m:el('receiptCoordinateUnit').value,reachtruck_mps:el('receiptTruckSpeed').value,lift_mps:el('receiptLiftSpeed').value},'PUT');el('receiptSettingsMessage').textContent='Настройки склада сохранены.';}catch(error){message(error.message);}}
  async function saveSkuRule(){try{if(!state.line)throw new Error('Выберите товар.');await api(`/api/receiving/warehouses/${warehouse()}/skus/${encodeURIComponent(state.line.articul)}/placement-rule`,{pick_cell:el('receiptPickCell').value.trim(),temp_min:el('receiptSkuTempMin').value||null,temp_max:el('receiptSkuTempMax').value||null,min_shelf_days:Number(el('receiptMinShelf').value),source_pick_mode:el('receiptSourcePickMode').value,allow_pick_batch_mix:el('receiptAllowBatchMix').checked},'PUT');el('receiptSettingsMessage').textContent='Правило товара сохранено.';}catch(error){message(error.message);}}
  async function saveCellRule(){try{const c=el('receiptStorageCell').value.trim();if(!c)throw new Error('Укажите ячейку хранения.');await api(`/api/receiving/warehouses/${warehouse()}/cells/${encodeURIComponent(c)}/placement-rule`,{temp_min:el('receiptCellTempMin').value||null,temp_max:el('receiptCellTempMax').value||null,pick_cell:el('receiptPickCell').value.trim()||null,travel_sec:el('receiptTravelSeconds').value||null,basis:el('receiptTravelBasis').value},'PUT');el('receiptSettingsMessage').textContent='Правило ячейки сохранено.';}catch(error){message(error.message);}}
  async function closeSupply(){try{if(!state.order)throw new Error('Выберите заказ.');const id=state.order.order_id,reason=el('receiptCloseReason').value.trim();const v=await api(`/api/receiving/supply-orders/${encodeURIComponent(id)}/close`,{operation_id:state.closeOperations.get(id)||rememberOperation(state.closeOperations,id),reason});await selectOrder(id);message('Приёмка закрыта. Недостача: '+v.lines.filter(l=>Number(l.shortage)>0).map(l=>`${l.material}: ${l.shortage}`).join(', '));}catch(error){message(error.message);}}
  async function exchange(){try{const events=await api('/api/integrations/sap/receipt-events');const names={PENDING:'Ожидает отправки',EXPORTED:'Передано шлюзу',ACKNOWLEDGED:'Принято SAP',REJECTED:'Отклонено SAP',ERROR:'Ошибка'};const kinds={PALLET_RECEIVED:'Приёмка',PALLET_PUTAWAY:'Размещение',SUPPLY_RECONCILED:'Сверка поставки',PUTAWAY_REPLANNED:'Переназначение адреса',SUPPLY_REOPEN_REQUESTED:'Повторное открытие поставки',PUTAWAY_CANCELLED:'Отмена размещения'};el('receiptExchangeRows').replaceChildren(...events.map(e=>{const tr=row([e.order_number,e.pallet_identifier,kinds[e.event_type]||e.event_type,names[e.status]||e.status,e.external_document_id||'']);const td=document.createElement('td');if(['ERROR','REJECTED','EXPORTED'].includes(e.status)&&window.wmsAdminAuth.hasPermission('sap_supply_import')){const b=document.createElement('button');b.textContent='Повторить отправку';b.addEventListener('click',async()=>{try{await api(`/api/integrations/sap/receipt-events/${encodeURIComponent(e.event_id)}/retry`,{});await exchange();}catch(error){message(error.message);}});td.appendChild(b);}tr.appendChild(td);return tr;}));}catch(error){message(error.message);}}
  async function replan(){try{const key=JSON.stringify(['receiptReplanTask','receiptReplanPallet','receiptReplanCell','receiptReplanReason'].map(id=>el(id).value));const v=await api(`/api/receiving/putaway/${el('receiptReplanTask').value}/replan`,{operation_id:state.replanOperations.get(key)||rememberOperation(state.replanOperations,key),scanned_pallet:el('receiptReplanPallet').value,scanned_from_cell:el('receiptReplanCell').value,reason:el('receiptReplanReason').value});message(`Задание ${v.task_id}: новый адрес ${v.placement.cell}. Количество к размещению: ${v.current_task_quantity ?? 'по заданию'}.`);}catch(error){message(error.message);}}
  el('receiptIssueLabel').addEventListener('click',issueLabel);el('receiptZpl').addEventListener('click',downloadZpl);el('receiptConfirmLabel').addEventListener('click',confirmPrinted);
  el('receiptPrintedScan').addEventListener('keydown',e=>{if(e.key==='Enter'){e.preventDefault();confirmPrinted();}});
  el('receiptLoadSettings').addEventListener('click',loadSettings);el('receiptSaveSettings').addEventListener('click',saveSettings);el('receiptSaveSkuRule').addEventListener('click',saveSkuRule);el('receiptSaveCellRule').addEventListener('click',saveCellRule);el('receiptCloseSupply').addEventListener('click',closeSupply);el('receiptRefreshExchange').addEventListener('click',exchange);el('receiptReplan').addEventListener('click',replan);
  function canConfirm(){
    try{return !state.busy&&Boolean(state.order?.receipt_allowed&&state.line&&state.policy)
      &&Number(state.line.remaining_qty)>0&&window.wmsAdminAuth.hasPermission('warehouse_receipt_confirm')
      &&window.wmsReceiptIntent.damaged().length===0;}catch{return false;}
  }
  async function recoverDamaged(){
    if(state.busy||!state.order)return;
    const captured=window.wmsReceiptIntent.damaged().find(v=>v.storage_key===el('receiptDamagedSelect').value);
    if(!captured)return;
    const order=state.order,identity=window.wmsReceiptIntent.scope(),token=++state.readEpoch;
    state.busy=true;el('receiptPalletFields').disabled=true;
    try{
      const snapshot=await window.wmsReceiptHistory.load(order.order_id);
      if(token!==state.readEpoch||state.order!==order||identity!==window.wmsReceiptIntent.scope())
        throw new Error('Основание или пользователь изменились. Повторите сверку.');
      window.wmsReceiptIntent.archiveDamaged(captured,snapshot);
      resetPallet();await selectOrder(order.order_id,true);
      message('Повреждённый запрос сохранён в архиве. Сверьте историю паллет; новое подтверждение выполняется только для фактически новой паллеты.');
    }catch(error){message(error.message);}
    finally{state.busy=false;el('receiptPalletFields').disabled=false;renderPending();el('receiptConfirm').disabled=!canConfirm();updateLabelAvailability();}
  }
  function renderPending(){
    try{
      const damaged=window.wmsReceiptIntent.damaged();
      el('receiptDamagedRecovery').hidden=!damaged.length;
      el('receiptDamagedSelect').replaceChildren(...damaged.map(item=>{
        const option=document.createElement('option');option.value=item.storage_key;
        option.textContent=(item.source_order_id?'Заказ '+item.source_order_id:'Источник не определён')+' · повреждённый запрос';return option;
      }));
      el('receiptRecoverDamaged').disabled=state.busy||!state.order||!damaged.length;
    }catch(error){message(error.message);}

    try{
      const values=window.wmsReceiptIntent.pending();
      el('receiptPendingSelect').replaceChildren(...values.map(value=>{
        const option=document.createElement('option');option.value=value.body.operation_id;
        option.textContent=`${value.body.sscc}: ${value.body.quantity} · ${value.body.operation_id}`;return option;
      }));
      el('receiptPendingMessage').textContent=values.length?`Неподтверждённых запросов: ${values.length}. Повторите исходный запрос.`:'Неподтверждённых запросов нет.';
      el('receiptRetryPending').disabled=!values.length;
    }catch(error){el('receiptPendingMessage').textContent=error.message;el('receiptPendingSelect').replaceChildren();el('receiptRetryPending').disabled=true;el('receiptConfirm').disabled=true;}
  }
  async function retryPending(){
    if(state.busy)return;
    if(state.label||state.units.size||state.aggregations.length){message('Сначала завершите или отложите текущую вводимую паллету.');return;}
    const saved=window.wmsReceiptIntent.pending().find(value=>value.body.operation_id===el('receiptPendingSelect').value);
    if(!saved)return;
    state.busy=true;el('receiptRetryPending').disabled=true;el('receiptPalletFields').disabled=true;
    try{
      const result=await api(saved.path,saved.body);
      const orderId=decodeURIComponent(saved.path.split('/')[4]);
      resetPallet();await selectOrder(orderId,true);
      message(`Подтверждён исходный результат приёмки: паллета ${result.pallet_identifier}, количество ${result.quantity}, задание ${result.task_id}.`);
    }catch(error){message(error.message+' Проверьте список неподтверждённых запросов.');}
    finally{state.busy=false;el('receiptPalletFields').disabled=false;renderPending();if(!state.order&&window.wmsAdminAuth.state.user)void loadOrders();updateLabelAvailability();}
  }
  window.addEventListener('wms-receipt-pending-changed',renderPending);
  el('receiptRetryPending').addEventListener('click',retryPending);el('receiptRecoverDamaged').addEventListener('click',recoverDamaged);
  window.addEventListener('wms-receipt-layout-quantity',event=>{
    try{
      const value=event.detail;
      if(!state.order||!state.line||value.order_id!==state.order.order_id||value.line_number!==state.line.line_number)
        throw new Error('Выберите актуальные заказ и строку, затем перечитайте предложение.');
      if(state.busy||state.label||state.units.size||state.aggregations.length)
        throw new Error('Количество из предложения выбирается до этикетки и сканирования кодов.');
      const pending=window.wmsReceiptIntent.pending();
      if(pending.some(v=>v.body.operation_id===state.operation||v.body.sscc===el('receiptSscc').value.trim()))
        throw new Error('Сначала повторите исходный неподтверждённый запрос этой паллеты.');
      el('receiptQuantity').value=value.quantity;
      message('Количество выбранной паллеты: '+value.quantity+'. Укажите фактические партию, срок и идентификатор; подтвердите приёмку после сканирования.');
    }catch(error){message(error.message);}
  });
  function rememberOperation(map,id){const op=crypto.randomUUID();map.set(id,op);return op;}
  async function reopenSupply(){try{if(!state.order)throw new Error('Выберите заказ.');const id=state.order.order_id;await api(`/api/receiving/supply-orders/${encodeURIComponent(id)}/reopen`,{operation_id:state.reopenOperations.get(id)||rememberOperation(state.reopenOperations,id),reason:el('receiptCloseReason').value.trim()});state.closeOperations.delete(id);await selectOrder(id);message('Запрошено повторное открытие. Приёмка возобновится после новой версии заказа SAP.');}catch(error){message(error.message);}}
  async function loadSkuRule(){try{const line=state.line;if(!line)throw new Error('Выберите товар.');const v=await api(`/api/receiving/warehouses/${warehouse()}/skus/${encodeURIComponent(line.articul)}/placement-rule`);if(state.line!==line)return;for(const [id,key] of [['receiptPickCell','pick_cell'],['receiptSkuTempMin','temp_min'],['receiptSkuTempMax','temp_max'],['receiptMinShelf','min_shelf_days'],['receiptSourcePickMode','source_pick_mode']])el(id).value=v[key]??(key==='min_shelf_days'?0:key==='source_pick_mode'?'AFTER_PUTAWAY':'');el('receiptAllowBatchMix').checked=Number(v.allow_pick_batch_mix||0)===1;el('receiptSettingsMessage').textContent=v.configured===false?'Правило товара ещё не задано.':'Правило товара загружено.';}catch(error){message(error.message);}}
  async function loadCellRule(){try{const c=el('receiptStorageCell').value.trim();if(!c)throw new Error('Укажите ячейку хранения.');const v=await api(`/api/receiving/warehouses/${warehouse()}/cells/${encodeURIComponent(c)}/placement-rule`);el('receiptCellTempMin').value=v.temp_min??'';el('receiptCellTempMax').value=v.temp_max??'';el('receiptSettingsMessage').textContent='Температурное правило ячейки загружено.';}catch(error){message(error.message);}}
  el('receiptReopenSupply').addEventListener('click',reopenSupply);el('receiptLoadSkuRule').addEventListener('click',loadSkuRule);el('receiptLoadCellRule').addEventListener('click',loadCellRule);
})();