from pathlib import Path
import json
p="wiki-raw/wms_admin_ui_reference/receiving-intent.js";t=Path(p).read_text(encoding="utf-8")
start=t.index('  function pending()');end=t.index('  function prepare(',start)
t=t[:start]+'''  function record(raw,key){
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
      try{valid.push(record(raw,key));}
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
    try{record(item.raw,item.storage_key);throw new Error('VALID_RECEIPT_INTENT');}
    catch(error){if(error.message==='VALID_RECEIPT_INTENT')throw new Error('Исправный запрос повторяется исходным номером операции; архивирование не требуется.');}
    const source=snapshot?.source;
    if(snapshot?.consistent_snapshot!==true||source?.consistent_snapshot!==true||!Array.isArray(snapshot.receipts)||!source.order_id)
      throw new Error('Сначала перечитайте текущую историю принятого товара с сервера.');
    const originalSource=sourceId(item.raw);
    if(originalSource&&originalSource!==source.order_id)
      throw new Error('Выберите исходное основание SAP '+originalSource+' перед архивированием.');
    const key='retailcase.receipt.archive:'+identity+':'+crypto.randomUUID();
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
'''+t[end:]
needle="    localStorage.setItem(key, JSON.stringify(record));"
assert needle in t;t=t.replace(needle,"    const raw=JSON.stringify(record);\n    validateRecord(raw,key);\n    localStorage.setItem(key,raw);")
# Avoid local const record in prepare shadowing validator.
t=t.replace('  function record(raw,key){','  function validateRecord(raw,key){').replace('valid.push(record(raw,key))','valid.push(validateRecord(raw,key))').replace('try{record(item.raw,item.storage_key);','try{validateRecord(item.raw,item.storage_key);')
t=t.replace("  window.wmsReceiptIntent = {prepare, settle, pending, scope};","  window.wmsReceiptIntent = {prepare,settle,pending,scope,damaged,archiveDamaged};")
# A missing storage record cannot turn an uncorrelated success into UI confirmation.
a=t.index('    const stored=localStorage.getItem(intent.storage_key);');b=t.index('    const rejected =',a)
block=t[a:b];guard="    if(status>=200&&status<300&&!successful)\n      throw new Error('Ответ не соответствует исходной приёмке. Запрос сохранён; повторите его без изменения данных.');\n"
assert guard in block;t=t[:a]+guard+block.replace(guard,'')+t[b:]
files={p:t}
p="wiki-raw/wms_admin_ui_reference/receiving.js";t=Path(p).read_text(encoding="utf-8")
pos=t.index('  function renderPending(){')
t=t[:pos]+'''  function canConfirm(){
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
    finally{state.busy=false;el('receiptPalletFields').disabled=false;renderPending();el('receiptConfirm').disabled=!canConfirm();}
  }
'''+t[pos:]
# Render damage controls separately even when pending parser blocks.
needle='  function renderPending(){'
t=t.replace(needle,needle+"""
    try{
      const damaged=window.wmsReceiptIntent.damaged();
      el('receiptDamagedRecovery').hidden=!damaged.length;
      el('receiptDamagedSelect').replaceChildren(...damaged.map(item=>{
        const option=document.createElement('option');option.value=item.storage_key;
        option.textContent=(item.source_order_id?'Заказ '+item.source_order_id:'Источник не определён')+' · повреждённый запрос';return option;
      }));
      el('receiptRecoverDamaged').disabled=state.busy||!state.order||!damaged.length;
    }catch(error){message(error.message);}
""")
t=t.replace("}catch(error){el('receiptPendingMessage').textContent=error.message;}","}catch(error){el('receiptPendingMessage').textContent=error.message;el('receiptPendingSelect').replaceChildren();el('receiptRetryPending').disabled=true;el('receiptConfirm').disabled=true;}")
t=t.replace("if(state.busy||!state.order?.receipt_allowed||!state.line||!state.policy)return;","if(!canConfirm())return;")
t=t.replace("el('receiptConfirm').disabled=!state.order.receipt_allowed||Number(line.remaining_qty)<=0||!window.wmsAdminAuth.hasPermission('warehouse_receipt_confirm');","el('receiptConfirm').disabled=!canConfirm();")
t=t.replace("el('receiptConfirm').disabled=!state.order?.receipt_allowed||!state.line||!state.policy||Number(state.line.remaining_qty)<=0||!window.wmsAdminAuth.hasPermission('warehouse_receipt_confirm');","el('receiptConfirm').disabled=!canConfirm();")
t=t.replace("el('receiptRetryPending').addEventListener('click',retryPending);","el('receiptRetryPending').addEventListener('click',retryPending);el('receiptRecoverDamaged').addEventListener('click',recoverDamaged);")
t=t.replace("message(order.receipt_allowed?'Основание SAP открыто.","renderPending();\n      message(order.receipt_allowed?'Основание SAP открыто.")
files[p]=t
p="wiki-raw/wms_admin_ui_reference/receiving.html";t=Path(p).read_text(encoding="utf-8")
needle='<button id="receiptRetryPending" type="button" disabled>Повторить исходный запрос</button>'
assert needle in t
t=t.replace(needle,needle+'''<div id="receiptDamagedRecovery" hidden><p>Повреждённый запрос блокирует новую приёмку. Перед архивированием выберите исходный заказ и сверьте историю принятых паллет. Исходный текст сохраняется в браузере.</p><select id="receiptDamagedSelect" aria-label="Повреждённый запрос"></select><button id="receiptRecoverDamaged" type="button" disabled>Сверить историю и архивировать повреждённый запрос</button></div>''')
t=t.replace('v=20261013-930','v=20261013-938')
files[p]=t
print(json.dumps(files,ensure_ascii=True))
