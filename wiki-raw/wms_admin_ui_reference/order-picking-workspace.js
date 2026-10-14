(() => {
 const el=id=>document.getElementById(id);
 let epoch=0,busy=false,plans=[],order=null;
 const key=()=>JSON.stringify(["retailcase.orderPickCreate",orderApiBase(),window.wmsAdminAuth.state.user?.username]);
 function saved(){const raw=localStorage.getItem(key());if(!raw)return null;try{return {...JSON.parse(raw),raw};}catch{return {damaged:true,raw};}}
 function say(text){el("orderPickStatus").textContent=text;}
 function controls(){el("orderPickReceiving").hidden=!order||!Number.isSafeInteger(order.ware_id);el("orderPickCreate").disabled=busy||!order||!!saved();el("orderPickRefresh").disabled=busy;el("orderPickRetry").disabled=busy||!order||!saved()?.request?.operation_id||saved()?.order_id!==order.customer_order_id;el("orderPickArchive").disabled=busy||!saved()?.confirmed_rejection;}
 async function read(){
  const id=orderState.selectedId,scope=orderScope(),token=++epoch;order=null;plans=[];el("orderPickRows").replaceChildren();controls();
  if(!id||!orderCan("pick_plan_view"))return;
  const [detail,list]=await Promise.all([orderRequest("/api/customer-orders/"+id),orderRequest("/api/picking/plans?customer_order_id="+id+"&limit=100")]);
  if(token!==epoch||scope!==orderScope()||id!==orderState.selectedId)return;
  order=detail;plans=list.filter(p=>p.customer_order_id===id);
  window.dispatchEvent(new CustomEvent("wms-order-plans-read",{detail:{order:detail,plans}}));
  el("orderPickReceiving").href="receiving.html?warehouse_id="+encodeURIComponent(detail.ware_id);
  el("orderPickWaves").href="wave-replenishment.html?ware_id="+encodeURIComponent(detail.ware_id);
  for(const p of plans){
   const tr=document.createElement("tr");
   for(const value of[p.pick_plan_id,({NO_STOCK:"Ожидается товар",PLANNED_FULL:"Обеспечен полностью",PLANNED_PARTIAL:"Обеспечен частично",CANCELLED:"Отменён",DRAFT:"Подготовка"})[p.status]||p.status,p.total_order_qty,p.total_planned_qty,p.total_shortage_qty,p.task_count,p.active_reservation_count]){
    const td=document.createElement("td");td.textContent=String(value??"—");tr.append(td);
   }
   const action=document.createElement("td");
   if(p.status==="NO_STOCK"&&Number(p.task_count)===0&&Number(p.active_reservation_count)===0&&orderCan("pick_plan_cancel")){
    const button=document.createElement("button");button.textContent="Отменить пустой план";button.title="Отменить план без выданных заданий и резервов, чтобы после поступления товара пересчитать обеспечение.";
    button.addEventListener("click",()=>cancelEmpty(p).catch(e=>say(e.message)));action.append(button);
   }
   tr.append(action);
   el("orderPickRows").append(tr);
  }
  const pending=saved();
  say(pending?"Есть сохранённая команда. Повтор с прежним идентификатором вернёт тот же план. Старые команды без идентификатора автоматически не повторяются.":plans.some(p=>p.status==="NO_STOCK")?"Товар пока не обеспечен. Потребность сохранена; складские задания не выданы. После приёмки отмените пустой план и пересчитайте обеспечение.":plans.length?"Показаны существующие планы. Для продолжения используйте действующий план и рабочее место волн.":"Планов нет. Создание использует текущий запас и прежний складской планировщик.");
  controls();
 }
 async function create(){
  if(busy||saved()||!order)return;
  const active=plans.filter(p=>!["CANCELLED","FAILED"].includes(p.status));
  if(plans.length>=100){say("Достигнут предел списка планов. Создание заблокировано; уточните существующие планы.");return;}
  if(active.length){say("У заказа уже есть план "+active.map(p=>p.pick_plan_id).join(", ")+". Продолжите его; новый план не создаётся.");return;}
  const id=order.customer_order_id,scope=orderScope(),storageKey=key();
  const intent={order_id:id,before_ids:plans.map(p=>p.pick_plan_id),request:{operation_id:"PICK.CREATE.UI:"+crypto.randomUUID(),customer_order_id:id,plan_strategy:el("orderPickStrategy").value}};
  const raw=JSON.stringify(intent);localStorage.setItem(storageKey,raw);
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
  busy=true;controls();
  try{
   const result=await orderRequest("/api/picking/plans",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(intent.request)});
   if(scope!==orderScope()||localStorage.getItem(storageKey)!==raw)return;
   if(result.operation_id!==intent.request.operation_id||!Number.isSafeInteger(result.pick_plan_id)||result.pick_plan_id<1)throw Error("Ответ не подтверждает созданный план.");
   localStorage.removeItem(storageKey);
   await read();say("Сохранён план "+result.pick_plan_id+". Обеспечение и недостача показаны по текущему результату.");
  }catch(e){
   if(scope===orderScope()){if(e.status>=400&&e.status<500&&e.detail?.outcome_confirmed!==false&&localStorage.getItem(storageKey)===raw)localStorage.setItem(storageKey,JSON.stringify({...intent,confirmed_rejection:true}));say(e.message+". Создание сохранено. Перечитайте существующие планы перед дальнейшими действиями.");}
  }finally{busy=false;controls();}
 }
 async function cancelEmpty(plan){
  if(busy||saved()||!order||plan.customer_order_id!==order.customer_order_id)return;
  busy=true;controls();const identity=orderScope(),orderId=order.customer_order_id;
  try{
   await orderRequest("/api/picking/plans/"+plan.pick_plan_id+"/cancel",{method:"POST",headers:{"Content-Type":"application/json"},body:"{}"});
   if(identity===orderScope()&&orderState.selectedId===orderId){await read();say("Пустой план отменён. После приёмки товара можно создать актуальное обеспечение.");}
  }catch(e){if(identity===orderScope())say(e.message+". Перечитайте состояние плана; автоматического повторного создания нет.");}
  finally{busy=false;controls();}
 }
 async function archive(){
  const pending=saved();if(busy||!pending?.confirmed_rejection||!order)return;
  if(pending.order_id!==order.customer_order_id)throw Error("Выберите исходный заказ сохранённого отказа.");
  const storageKey=key(),scope=orderScope();await read();
  if(scope!==orderScope()||localStorage.getItem(storageKey)!==pending.raw)return;
  const archiveKey=storageKey+":archive:"+crypto.randomUUID();
  localStorage.setItem(archiveKey,pending.raw);
  if(localStorage.getItem(archiveKey)!==pending.raw)throw Error("Архив не сохранён.");
  localStorage.removeItem(storageKey);say("Исходный запрос сохранён в архиве. Используйте показанный существующий план или исправьте причину отказа.");controls();
 }
 window.addEventListener("wms-order-context-changed",()=>{++epoch;order=null;plans=[];el("orderPickRows").replaceChildren();say("Выберите заказ и прочитайте его планы.");controls();});
 window.addEventListener("wms-admin-auth-ready",()=>{++epoch;order=null;controls();});
 el("orderPickRefresh").addEventListener("click",()=>read().catch(e=>say(e.message)));
 el("orderPickCreate").addEventListener("click",()=>create().catch(e=>say(e.message)));
 el("orderPickRetry").addEventListener("click",()=>retry().catch(e=>say(e.message)));
 el("orderPickArchive").addEventListener("click",()=>archive().catch(e=>say(e.message)));
})();
