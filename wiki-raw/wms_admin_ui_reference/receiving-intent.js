(() => {
  const marker = 'nicora.receipt.pending:';
  const validPath = /^\/api\/receiving\/supply-orders\/[^/]+\/pallets$/;
  function scope() {
    const auth = window.wmsAdminAuth;
    const actor = auth.state.user?.username || '';
    if (!actor) throw new Error('Войдите в систему.');
    return JSON.stringify([(auth.state.apiBase || 'http://127.0.0.1:8088').replace(/\/$/, ''), actor]);
  }
  const prefix = () => marker + scope() + ':';
  function canonical(value) {
    if (Array.isArray(value)) return value.map(canonical);
    if (value && typeof value === 'object') return Object.fromEntries(
      Object.keys(value).sort().map(key => [key, canonical(value[key])]));
    return value;
  }
  function material(body) {
    const copy = {...body}; delete copy.operation_id;
    return JSON.stringify(canonical(copy));
  }
  function validateRecord(raw,key){
    const value=JSON.parse(raw),body=value?.body,identifier=body?.pallet_identifier||body?.sscc;
    if(!value||!validPath.test(value.path)||typeof identifier!=='string'||!identifier.trim()||identifier.length>50
      ||typeof body.operation_id!=='string'||!/^[A-Za-z0-9_.:-]{1,100}$/.test(body.operation_id)
      ||typeof body.line_number!=='string'||!body.line_number.trim()||body.line_number.length>20
      ||!(/^[0-9]+(?:[.][0-9]{1,9})?$/.test(String(body.quantity)))||!/[1-9]/.test(String(body.quantity))
      ||typeof value.created_at!=='string'||!Number.isFinite(Date.parse(value.created_at))
      ||!Number.isSafeInteger(value.attempt_count)||value.attempt_count<1
      ||key!==prefix()+encodeURIComponent(body.operation_id)
      ||(body.units!=null&&!Array.isArray(body.units))||(body.aggregations!=null&&!Array.isArray(body.aggregations)))
      throw new Error('Проверьте идентификатор паллеты, количество, строку и исходные данные запроса.');
    return {...value,storage_key:key};
  }
  function sourceId(raw){
    try{const value=JSON.parse(raw);if(validPath.test(value?.path))return decodeURIComponent(value.path.split('/')[4]);}catch{}
    return null;
  }
  function inspect(){
    const start=prefix(),valid=[],damaged=[];
    for(let i=0;i<localStorage.length;i++){
      const key=localStorage.key(i);if(!key?.startsWith(start))continue;
      const raw=localStorage.getItem(key);
      try{valid.push(validateRecord(raw,key));}
      catch(error){damaged.push({storage_key:key,raw,source_order_id:sourceId(raw),reason:error.message});}
    }
    return {valid,damaged};
  }
  function pending(){
    const result=inspect();
    if(result.damaged.length)throw new Error('Есть повреждённый сохранённый запрос. Сверьте принятые паллеты и сохраните запрос в архив.');
    return result.valid.sort((a,b)=>a.created_at.localeCompare(b.created_at));
  }
  function damaged(){return inspect().damaged;}
  function archiveDamaged(item,snapshot){
    const identity=scope();
    if(!item?.storage_key?.startsWith(prefix())||localStorage.getItem(item.storage_key)!==item.raw)
      throw new Error('Исходный запрос изменился в другой вкладке. Перечитайте его.');
    try{validateRecord(item.raw,item.storage_key);throw new Error('VALID_RECEIPT_INTENT');}
    catch(error){if(error.message==='VALID_RECEIPT_INTENT')throw new Error('Исправный запрос повторяется исходным номером операции; архивирование не требуется.');}
    const source=snapshot?.source;
    if(snapshot?.consistent_snapshot!==true||source?.consistent_snapshot!==true||!Array.isArray(snapshot.receipts)||!source.order_id)
      throw new Error('Сначала перечитайте текущую историю принятого товара с сервера.');
    const originalSource=sourceId(item.raw);
    if(originalSource&&originalSource!==source.order_id)
      throw new Error('Выберите исходное основание SAP '+originalSource+' перед архивированием.');
    const key='nicora.receipt.archive:'+identity+':'+crypto.randomUUID();
    localStorage.setItem(key,JSON.stringify({raw:item.raw,original_key:item.storage_key,archived_at:new Date().toISOString(),
      scope:identity,source_order_id:source.order_id,source_revision:source.revision,warehouse_id:source.ware_id,
      source_state:source.receipt_state,source_lines:source.lines,
      visible_receipt_operations:snapshot.receipts.map(r=>r.operation_id),original_source_known:Boolean(originalSource)}));
    if(identity!==scope()||localStorage.getItem(item.storage_key)!==item.raw)
      throw new Error('Во время сверки запрос изменился. Архив сохранён, исходный запрос не удалён.');
    localStorage.removeItem(item.storage_key);
    window.dispatchEvent(new CustomEvent('wms-receipt-pending-changed'));
    return key;
  }
  function prepare(path, body) {
    if (!validPath.test(path)) return {path, body, scope: scope(), storage_key: null};
    const values = pending();
    let found = values.find(v => v.body.operation_id === body.operation_id);
    if (!found) {
      const matches = values.filter(v => v.path === path && v.body.sscc === body.sscc);
      if (matches.length > 1) throw new Error('Есть несколько неподтверждённых запросов этой паллеты. Выберите исходный запрос.');
      found = matches[0];
    }
    if (found && (found.path !== path || material(found.body) !== material(body)))
      throw new Error('Сначала повторите сохранённый исходный запрос приёмки. Его данные изменять нельзя.');
    if (!found && values.length >= 200) throw new Error('Завершите неподтверждённые запросы приёмки.');
    const copy = found ? JSON.parse(JSON.stringify(found.body)) : JSON.parse(JSON.stringify(body));
    const key = prefix() + encodeURIComponent(copy.operation_id);
    const record = {path, body: copy, created_at: found?.created_at || new Date().toISOString(),
      attempt_count: (found?.attempt_count || 0) + 1};
    const raw=JSON.stringify(record);
    validateRecord(raw,key);
    localStorage.setItem(key,raw);
    window.dispatchEvent(new CustomEvent('wms-receipt-pending-changed'));
    return {...record, scope: scope(), storage_key: key};
  }
  function settle(intent, status, data) {
    if (!intent.storage_key || intent.scope !== scope()) return;
    function quantity(value){
      const text=String(value??'');
      if(!/^[0-9]+(?:[.][0-9]{1,9})?$/.test(text))return null;
      const [whole,fraction='']=text.split('.');
      return whole.replace(/^0+(?=[0-9])/,'')+(fraction.replace(/0+$/,'')?'.'+fraction.replace(/0+$/,''):'');
    }
    const identifier=intent.body.pallet_identifier||intent.body.sscc;
    const successful = status >= 200 && status < 300 && data?.status==='RECEIVED'
      && data.operation_id===intent.body.operation_id && data.pallet_identifier===identifier
      && data.line_number===intent.body.line_number
      && quantity(data.quantity)!==null && quantity(data.quantity)===quantity(intent.body.quantity)
      && Number.isSafeInteger(data.task_id) && data.task_id>0;
    if(status>=200&&status<300&&!successful)
      throw new Error('Ответ не соответствует исходной приёмке. Запрос сохранён; повторите его без изменения данных.');
    const stored=localStorage.getItem(intent.storage_key);
    if(stored){
      const current=JSON.parse(stored);
      if(current.path!==intent.path||current.body?.operation_id!==intent.body.operation_id||material(current.body)!==material(intent.body))
        throw new Error('Сохранённая приёмка изменена в другой вкладке. Перечитайте исходный запрос.');
    }else return;
    const rejected = intent.attempt_count === 1 && (status === 422 ||
      (status !== 403 && data?.detail?.outcome_confirmed === true &&
        !data.detail.operation_id_conflict && data.detail.code!=="OPERATION_CONFLICT" && !data.detail.retry_same_operation_id));
    if (successful || rejected) {
      localStorage.removeItem(intent.storage_key);
      window.dispatchEvent(new CustomEvent('wms-receipt-pending-changed'));
    }
  }
  window.wmsReceiptIntent = {prepare,settle,pending,scope,damaged,archiveDamaged};
})();
