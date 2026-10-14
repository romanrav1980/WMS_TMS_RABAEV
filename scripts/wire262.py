from pathlib import Path
import json
out={}
p=Path("wiki-raw/wms_admin_ui_reference/receiving.js");s=p.read_text(encoding="utf-8")
old="""    const response=await fetch(base+path,{method:method||(body?'POST':'GET'),headers:window.wmsAdminAuth.headers(body?{'Content-Type':'application/json'}:{}),body:body?JSON.stringify(body):undefined});
    const data=await response.json();
    if(!response.ok) throw new Error(typeof data.detail==='string'?data.detail:JSON.stringify(data.detail||data));
    return data;"""
new="""    const scope=window.wmsReceiptIntent.scope();
    const intent=body?window.wmsReceiptIntent.prepare(path,body):null;
    const response=await fetch(base+path,{method:method||(body?'POST':'GET'),headers:window.wmsAdminAuth.headers(body?{'Content-Type':'application/json'}:{}),body:body?JSON.stringify(intent.body):undefined});
    const data=await response.json();
    if(scope!==window.wmsReceiptIntent.scope())throw new Error('Пользователь или сервер изменился. Перечитайте данные.');
    if(intent)window.wmsReceiptIntent.settle(intent,response.status,data);
    if(!response.ok) throw new Error(typeof data.detail==='string'?data.detail:JSON.stringify(data.detail||data));
    return data;"""
assert old in s;s=s.replace(old,new)
s=s.replace("  window.addEventListener('wms-admin-auth-ready',loadOrders);","""  window.addEventListener('wms-admin-auth-ready',()=>{state.order=null;state.line=null;state.policy=null;resetPallet();renderPending();loadOrders();});""")
s=s.replace("  if(window.wmsAdminAuth.state.user)loadOrders();","""  if(window.wmsAdminAuth.state.user){renderPending();loadOrders();}""")
s=s.replace("  function rememberOperation(map,id){",'''  function renderPending(){
    try{
      const values=window.wmsReceiptIntent.pending();
      el('receiptPendingSelect').replaceChildren(...values.map(value=>{
        const option=document.createElement('option');option.value=value.body.operation_id;
        option.textContent=`${value.body.sscc}: ${value.body.quantity} · ${value.body.operation_id}`;return option;
      }));
      el('receiptPendingMessage').textContent=values.length?`Неподтверждённых запросов: ${values.length}. Повторите исходный запрос.`:'Неподтверждённых запросов нет.';
      el('receiptRetryPending').disabled=!values.length;
    }catch(error){el('receiptPendingMessage').textContent=error.message;}
  }
  async function retryPending(){
    if(state.busy)return;
    if(state.label||state.units.size||state.aggregations.length){message('Сначала завершите или отложите текущую вводимую паллету.');return;}
    const saved=window.wmsReceiptIntent.pending().find(value=>value.body.operation_id===el('receiptPendingSelect').value);
    if(!saved)return;
    state.busy=true;el('receiptRetryPending').disabled=true;
    try{
      const result=await api(saved.path,saved.body);
      const orderId=decodeURIComponent(saved.path.split('/')[4]);
      resetPallet();await selectOrder(orderId);
      message(`Приёмка подтверждена: паллета ${result.pallet_identifier}, количество ${result.quantity}, задание ${result.task_id}.`);
    }catch(error){message(error.message+' Исходный запрос сохранён до подтверждения.');}
    finally{state.busy=false;renderPending();}
  }
  window.addEventListener('wms-receipt-pending-changed',renderPending);
  el('receiptRetryPending').addEventListener('click',retryPending);
  function rememberOperation(map,id){''')
out[str(p)]=s
p=Path("wiki-raw/wms_admin_ui_reference/receiving.html");s=p.read_text(encoding="utf-8")
s=s.replace('<section aria-label="План укладки поставки">','''<section aria-label="Восстановление приёмки">
<h3>Неподтверждённая приёмка</h3><p id="receiptPendingMessage" role="status"></p>
<select id="receiptPendingSelect" aria-label="Исходный запрос приёмки"></select>
<button id="receiptRetryPending" type="button" disabled>Повторить исходный запрос</button>
<p>При потере ответа сохраняются исходные количество, партия, срок и коды. Новая товарная приёмка при повторе не создаётся.</p>
</section>
<section aria-label="План укладки поставки">''')
s=s.replace('<script src="receiving-layout.js"></script>','<script src="receiving-intent.js"></script><script src="receiving-layout.js"></script>');out[str(p)]=s
p=Path("wiki-raw/wms_admin_ui_reference/receiving-layout.js");s=p.read_text(encoding="utf-8").replace("order = event.detail; line = null; epoch++;","order = event.detail; line = null; epoch++; el('receiptLayoutPreview').disabled=false;").replace("line = event.detail; epoch++;","line = event.detail; epoch++; el('receiptLayoutPreview').disabled=false;")
s=s.replace("  async function preview() {","  window.addEventListener('wms-admin-auth-ready',()=>{order=null;line=null;epoch++;el('receiptLayoutRows').replaceChildren();el('receiptLayoutPreview').disabled=false;message('Выберите заказ и строку.');});\n  async function preview() {")
out[str(p)]=s
print(json.dumps(out,ensure_ascii=True))
