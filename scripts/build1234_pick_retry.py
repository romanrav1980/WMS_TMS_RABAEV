from pathlib import Path
import json
files={}
p=Path("wiki-raw/wms_admin_ui_reference/order-picking-workspace.js")
s=p.read_text(encoding="utf-8")
s=s.replace('el("orderPickRefresh").disabled=busy;', 'el("orderPickRefresh").disabled=busy;el("orderPickRetry").disabled=busy||!order||!saved()?.request?.operation_id||saved()?.order_id!==order.customer_order_id;')
s=s.replace('request:{customer_order_id:id,plan_strategy:', 'request:{operation_id:"PICK.CREATE.UI:"+crypto.randomUUID(),customer_order_id:id,plan_strategy:')
s=s.replace('  const raw=JSON.stringify(intent);localStorage.setItem(storageKey,raw);busy=true;controls();',
'''  const raw=JSON.stringify(intent);localStorage.setItem(storageKey,raw);
  await submit(intent,raw,storageKey,scope);
 }
 async function retry(){
  const pending=saved();
  if(busy||!order||!pending?.request?.operation_id||pending.order_id!==order.customer_order_id)return;
  const r=pending.request;
  if(r.customer_order_id!==pending.order_id||!Number.isSafeInteger(r.customer_order_id)||!["FEFO","FIFO"].includes(r.plan_strategy)||!/^PICK.CREATE.UI:[A-Za-z0-9-]+$/.test(r.operation_id))throw Error("Сохранённая команда повреждена. Повтор заблокирован.");
  await submit(pending,pending.raw,key(),orderScope());
 }
 async function submit(intent,raw,storageKey,scope){
  busy=true;controls();''')
s=s.replace('if(!Number.isSafeInteger(result.pick_plan_id)||result.pick_plan_id<1)', 'if(result.operation_id!==intent.request.operation_id||!Number.isSafeInteger(result.pick_plan_id)||result.pick_plan_id<1)')
s=s.replace('if(e.status>=400&&e.status<500&&localStorage.getItem(storageKey)===raw)', 'if(e.status>=400&&e.status<500&&e.detail?.outcome_confirmed!==false&&localStorage.getItem(storageKey)===raw)')
s=s.replace('Есть сохранённое создание плана. Перечитайте список и выберите существующий результат; автоматического повтора создания нет.', 'Есть сохранённая команда. Повтор с прежним идентификатором вернёт тот же план. Старые команды без идентификатора автоматически не повторяются.')
s=s.replace(' el("orderPickArchive").addEventListener', ' el("orderPickRetry").addEventListener("click",()=>retry().catch(e=>say(e.message)));\n el("orderPickArchive").addEventListener')
files[str(p)]=s
p=Path("wiki-raw/wms_admin_ui_reference/customer-orders.html")
s=p.read_text(encoding="utf-8")
anchor='<button id="orderPickArchive"'
assert s.count(anchor)==1
s=s.replace(anchor,'<button id="orderPickRetry" disabled title="Отправить сохранённую команду с прежним идентификатором; повтор вернёт прежний план.">Повторить сохранённую команду</button>\n'+anchor)
files[str(p)]=s

print(json.dumps(files,ensure_ascii=True))
