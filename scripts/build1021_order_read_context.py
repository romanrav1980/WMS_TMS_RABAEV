from pathlib import Path
import json
read=lambda p:Path(p).read_text(encoding="utf-8");files={}
p="wiki-raw/wms_admin_ui_reference/customer-orders.js";v=read(p)
v=v.replace('const orderEl = (id)', 'let orderListGeneration=0,orderDetailGeneration=0,orderBound=false,orderIdentity="";\nconst orderScope=()=>orderApiBase()+":"+window.wmsAdminAuth?.state?.user?.username;\nconst orderEl = (id)',1)
start=v.index('async function loadOrders()');end=v.index('\nfunction renderOrders()',start)
v=v[:start]+'''async function loadOrders() {
  const serial=++orderListGeneration,scope=orderScope();
  orderEl("orderStatusText").textContent = "Загрузка...";
  try{
    const rows=await orderRequest("/api/customer-orders?"+orderFilters().toString());
    if(serial!==orderListGeneration||scope!==orderScope())return;
    orderState.orders=rows;renderOrders();
    orderEl("orderStatusText").textContent="Заказов: "+rows.length;
  }catch(error){if(serial===orderListGeneration&&scope===orderScope())orderEl("orderStatusText").textContent=error.message;}
}
'''+v[end:]
v=v.replace('tr.addEventListener("click", () => loadOrderDetail(order.customer_order_id));','''tr.tabIndex=0;tr.setAttribute("role","button");tr.setAttribute("aria-label","Открыть заказ "+(order.order_no||order.customer_order_id));
    tr.addEventListener("click",()=>loadOrderDetail(order.customer_order_id));
    tr.addEventListener("keydown",event=>{if(["Enter"," "].includes(event.key)){event.preventDefault();loadOrderDetail(order.customer_order_id);}});''',1)
start=v.index('async function loadOrderDetail(orderId)');end=v.index('\nfunction renderOrderLines()',start)
old=v[start:end]
old=old.replace('  orderState.selectedId = orderId;','''  const serial=++orderDetailGeneration,scope=orderScope();
  const current=()=>serial===orderDetailGeneration&&scope===orderScope()&&orderState.selectedId===orderId;
  orderState.selectedId=orderId;orderState.detail=null;orderState.fulfillment=[];
  orderEl("orderDetails").replaceChildren();orderEl("orderLineRows").replaceChildren();orderEl("orderFulfillmentRows").replaceChildren();
  window.dispatchEvent(new CustomEvent("wms-order-context-changed"));
  try{''',1)
old=old.replace('if (orderState.selectedId !== orderId) return;','if(!current())return;')
old=old.replace('    await loadOrderExecution(orderId);','    if(current())await loadOrderExecution(orderId);',1)
endclose=old.rfind('\n}')
old=old[:endclose]+'''
  }catch(error){if(current())orderEl("orderDetailStatus").textContent=error.message;}
'''+old[endclose:]
v=v[:start]+old+v[end:]
start=v.index('async function orderInit()');end=v.index('\nwindow.addEventListener("wms-admin-auth-ready", orderInit);',start)
v=v[:start]+'''async function orderInit() {
  if(!window.wmsAdminAuth?.state?.user?.username)return;
  const scope=orderScope();
  if(scope===orderIdentity)return;
  orderIdentity=scope;orderListGeneration++;orderDetailGeneration++;
  orderState.orders=[];orderState.selectedId=null;orderState.detail=null;orderState.fulfillment=[];orderState.layoutOrderId=null;orderState.preparations.clear();
  for(const id of ["orderRows","orderDetails","orderLineRows","orderFulfillmentRows","sapLayoutRows"])orderEl(id).replaceChildren();
  orderEl("orderDetailStatus").textContent="Выберите заказ";orderEl("sapPreparationStatus").textContent="Выберите исходный заказ.";
  window.dispatchEvent(new CustomEvent("wms-order-context-changed"));
  if(!orderBound){
    orderBound=true;
    orderBind("sapLayoutLoad",loadSapLayout);orderBind("sapPrepareSt",prepareSapSt);orderBind("sapAssignSt",assignPreparedSt);
    orderBind("orderLoad",loadOrders);orderBind("orderRefresh",loadOrders);orderBind("legacyImport",importLegacyOrder);
    orderEl("orderSearchTop").addEventListener("keydown",event=>{if(event.key==="Enter")loadOrders();});
  }
  await loadOrders();
  if(scope!==orderScope())return;
  const initial=Number(new URLSearchParams(window.location.search).get("order_id"));
  if(Number.isSafeInteger(initial)&&initial>0){
    await loadOrderDetail(initial);
    if(scope===orderScope()&&orderState.selectedId===initial&&window.location.hash==="#orderExecution")
      document.getElementById("orderExecution")?.scrollIntoView({block:"start"});
  }
}
'''+v[end:]
v=v.replace("  const id=orderState.selectedId;if(!id)throw new Error('Выберите заказ SAP.');","  const id=orderState.selectedId,scope=orderScope(),serial=orderDetailGeneration;if(!id)throw new Error('Выберите заказ SAP.');",1)
v=v.replace("  if(orderState.selectedId!==id)return;","  if(orderState.selectedId!==id||scope!==orderScope()||serial!==orderDetailGeneration)return;",1)
v=v.replace("  const id=orderState.selectedId;if(!id||id!==orderState.layoutOrderId)","  const id=orderState.selectedId,scope=orderScope();if(!id||id!==orderState.layoutOrderId)",1)
v=v.replace("  if(orderState.selectedId===id){orderEl('sapPreparationStatus')","  if(orderState.selectedId===id&&scope===orderScope()){orderEl('sapPreparationStatus')",1)
v=v.replace("  const id=orderState.selectedId;const prepared=","  const id=orderState.selectedId,scope=orderScope();const prepared=",1)
v=v.replace("  if(orderState.selectedId===id)orderEl('sapPreparationStatus')","  if(orderState.selectedId===id&&scope===orderScope())orderEl('sapPreparationStatus')",1)
files[p]=v
p="wiki-raw/wms_admin_ui_reference/order-execution.js";v=read(p).replace('window.addEventListener("wms-admin-auth-ready",resetOrderExecution);','window.addEventListener("wms-admin-auth-ready",resetOrderExecution);\nwindow.addEventListener("wms-order-context-changed",resetOrderExecution);',1);files[p]=v
p="wiki-raw/wms_admin_ui_reference/order-delivery.js";v=read(p)
needle='window.addEventListener("wms-admin-auth-ready",()=>{';assert v.count(needle)==1
v=v.replace(needle,'function resetOrderDelivery(){',1)
assert v.rstrip().endswith('});')
v=v.rstrip()[:-3]+'}\nwindow.addEventListener("wms-admin-auth-ready",resetOrderDelivery);\nwindow.addEventListener("wms-order-context-changed",resetOrderDelivery);\n';files[p]=v
p="wiki-raw/wms_admin_ui_reference/customer-orders.html";v=read(p).replace('<h3>Фактическое исполнение','<h3 id="orderExecution">Фактическое исполнение',1).replace('src="customer-orders.js"','src="customer-orders.js?v=20261013-1021"').replace('src="order-delivery.js"','src="order-delivery.js?v=20261013-1021"').replace('order-execution.js?v=20261013-1015','order-execution.js?v=20261013-1021')
files[p]=v
print(json.dumps(files,ensure_ascii=True))
