const orderState = {
  orders: [],
  selectedId: null,
  detail: null,
  fulfillment: [],
  preparations: new Map(),
  layoutOrderId: null,
};

let orderPageCursor=null,orderPageHistory=[],orderPageFilters="",orderPageBusy=false;
let orderListGeneration=0,orderDetailGeneration=0,orderBound=false,orderIdentity="";
const orderScope=()=>orderApiBase()+":"+window.wmsAdminAuth?.state?.user?.username;
const orderEl = (id) => document.getElementById(id);
const ORDER_DEFAULT_API_BASE = "http://127.0.0.1:8088";

function orderApiBase() {
  return (window.wmsAdminAuth?.state?.apiBase || ORDER_DEFAULT_API_BASE).replace(/\/$/, "");
}

function orderHeaders(extra = {}) {
  return window.wmsAdminAuth ? window.wmsAdminAuth.headers(extra) : { ...extra };
}

function orderCan(permission) {
  return window.wmsAdminAuth && window.wmsAdminAuth.hasPermission(permission);
}

async function orderRequest(path, options = {}) {
  const response = await fetch(`${orderApiBase()}${path}`, {
    ...options,
    headers: orderHeaders(options.headers || {}),
  });
  const text = await response.text();
  const payload = text ? JSON.parse(text) : null;
  if (!response.ok) {
    const error=new Error((payload && (payload.detail?.message || payload.detail?.code || payload.detail)) || `HTTP ${response.status}`);error.status=response.status;error.detail=payload?.detail;throw error;
  }
  return payload;
}

function escapeOrder(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;");
}

function orderFilters() {
  const params = new URLSearchParams();
  if (orderEl("orderStatus").value) params.set("status", orderEl("orderStatus").value);
  const orderNo = orderEl("orderNo").value.trim() || orderEl("orderSearchTop").value.trim();
  if (orderNo) params.set("order_no", orderNo);
  if (orderEl("legacyOrderId").value) params.set("legacy_order_id", orderEl("legacyOrderId").value);
  params.set("limit", orderEl("orderLimit").value || "200");
  return params;
}

function orderPagingControls(){
  orderEl("orderPagePrevious").disabled=orderPageBusy||!orderPageHistory.length;
  orderEl("orderPageNext").disabled=orderPageBusy||!orderState.orders.length||
    orderState.orders.length<Math.min(500,Math.max(1,Number(orderEl("orderLimit").value)||200));
}
async function orderPage(direction){
  if(orderPageBusy)return;
  const filters=orderFilters().toString();
  if(filters!==orderPageFilters){await loadOrders();return;}
  if(direction==="next"){
    if(!orderState.orders.length)return;
    orderPageHistory.push(orderPageCursor);
    orderPageCursor=orderState.orders.at(-1).customer_order_id;
  }else if(orderPageHistory.length){orderPageCursor=orderPageHistory.pop();}
  else return;
  await loadOrders(true);
}
async function loadOrders(keepPage=false) {
  if(keepPage!==true){orderPageCursor=null;orderPageHistory=[];}
  const params=orderFilters();orderPageFilters=params.toString();
  if(orderPageCursor!=null)params.set("before_id",String(orderPageCursor));
  orderState.orders=[];renderOrders();orderPageBusy=true;orderPagingControls();
  const serial=++orderListGeneration,scope=orderScope();
  orderEl("orderStatusText").textContent = "Загрузка...";
  try{
    const rows=await orderRequest("/api/customer-orders?"+params.toString());
    if(serial!==orderListGeneration||scope!==orderScope())return;
    orderState.orders=rows;renderOrders();
    orderEl("orderStatusText").textContent="Страница "+(orderPageHistory.length+1)+" · заказов: "+rows.length;
  }catch(error){if(serial===orderListGeneration&&scope===orderScope())orderEl("orderStatusText").textContent=error.message;}
  finally{if(serial===orderListGeneration&&scope===orderScope()){orderPageBusy=false;orderPagingControls();}}
}

function renderOrders() {
  const tbody = orderEl("orderRows");
  tbody.innerHTML = "";
  for (const order of orderState.orders) {
    const tr = document.createElement("tr");
    tr.className = orderState.selectedId === order.customer_order_id ? "selected" : "";
    tr.innerHTML = `
      <td>${order.customer_order_id ?? ""}</td>
      <td>${escapeOrder(order.order_no)}</td>
      <td>${escapeOrder(order.legacy_order_id)}</td>
      <td>${escapeOrder(order.customer_name || order.legacy_addr)}</td>
      <td>${escapeOrder(order.status)}</td>
      <td>${escapeOrder(order.shipment_date)}</td>
      <td>${escapeOrder(order.row_count)}</td>
      <td>${escapeOrder(order.order_uom_count===1&&order.unknown_uom_rows===0 ? String(order.total_order_qty_exact??order.total_order_qty)+" "+order.order_uom : "См. позиции")}</td>
    `;
    tr.tabIndex=0;tr.setAttribute("role","button");tr.setAttribute("aria-label","Открыть заказ "+(order.order_no||order.customer_order_id));
    tr.addEventListener("click",()=>loadOrderDetail(order.customer_order_id));
    tr.addEventListener("keydown",event=>{if(["Enter"," "].includes(event.key)){event.preventDefault();loadOrderDetail(order.customer_order_id);}});
    tbody.appendChild(tr);
  }
}

async function loadOrderDetail(orderId) {
  const serial=++orderDetailGeneration,scope=orderScope();
  const current=()=>serial===orderDetailGeneration&&scope===orderScope()&&orderState.selectedId===orderId;
  orderEl("sapManualEditor").hidden=false;orderEl("sapPrepareSt").disabled=true;orderEl("sapTripReviewMessage").textContent="";orderState.selectedId=orderId;orderState.detail=null;orderState.fulfillment=[];
  orderEl("orderDetails").replaceChildren();orderEl("orderLineRows").replaceChildren();orderEl("orderFulfillmentRows").replaceChildren();
  window.dispatchEvent(new CustomEvent("wms-order-context-changed"));
  try{
  orderEl("orderDetailStatus").textContent = "Загрузка...";
  const detail = await orderRequest(`/api/customer-orders/${orderId}`);
  if(!current())return;
  orderState.detail = detail;
  renderOrderHeader(orderState.detail);
  renderOrderLines();
  renderOrders();
  orderEl("orderDetailStatus").textContent = `${orderState.detail.order_no || orderId} / ${orderState.detail.status}`;
  if (orderCan("customer_fulfillment_view")) {
    const fulfillment = await orderRequest(`/api/customer-orders/${orderId}/fulfillment`);
    if(!current())return;
    orderState.fulfillment = fulfillment;
    renderFulfillment();
    if(current())await loadOrderExecution(orderId);
  } else {
    orderEl("orderFulfillmentRows").innerHTML = "";
  }
  }catch(error){if(current())orderEl("orderDetailStatus").textContent=error.message;}

}

function renderOrderHeader(detail){
  const labels={NEW:"Новый",CREATED:"Создан",PLANNED:"Подготовлен",PICKING:"В отборе",PICKED:"Собран",SHIPPED:"Отгружен",CANCELLED:"Отменён"};
  const fields=[["Заказ",detail.order_no||detail.customer_order_id],["Клиент",detail.customer_name||detail.customer_id],
    ["Дата отгрузки",detail.shipment_date||"Не задана"],["Маршрут",detail.route_id||"Не назначен"],
    ["Ворота",detail.dock_id||"Не назначены"],["Документ",labels[detail.status]||detail.status||"—"]];
  orderEl("orderDetails").replaceChildren(...fields.map(([title,value])=>{
    const box=document.createElement("div"),caption=document.createElement("small"),text=document.createElement("strong");
    box.className="order-metadata-field";caption.textContent=title;text.textContent=String(value);box.append(caption,text);return box;
  }));
}
function renderOrderLines() {
  const rows = orderState.detail?.rows || [];
  orderEl("orderLineRows").innerHTML = rows.map((row) => `
    <tr>
      <td>${escapeOrder(row.line_no)}</td>
      <td>${escapeOrder(row.articul)}</td>
      <td>${escapeOrder(row.product_name)}</td>
      <td>${escapeOrder(row.order_qty_exact??row.order_qty)}</td>
      <td>${escapeOrder(row.order_weight_exact??row.order_weight)}</td>
      <td>${escapeOrder(row.pack_count_exact??row.pack_count)}</td>
      <td>${escapeOrder(row.status)}${row.unit_code === "KG" && (orderCan("pick_plan_create") || orderCan("case_pick_short_approve")) ? '<br><button type="button" data-weight-row="' + escapeOrder(row.customer_order_row_id) + '">Целые коробки</button>' : ""}</td>
    </tr>
  `).join("");
}

function renderFulfillment() {
  orderEl("orderFulfillmentRows").innerHTML = orderState.fulfillment.map((row) => `
    <tr>
      <td>${escapeOrder(row.fulfillment_id)}</td>
      <td>${escapeOrder(row.pallet_uid || row.legacy_sborka_pallet_id)}
        ${row.case_place_current?'<br><a href="warehouse-hus.html?identifier='+encodeURIComponent(row.case_identifier)+'#huComposition">Текущий CASE '+escapeOrder(row.case_identifier)+' →</a><small class="order-case-location">Версия '+escapeOrder(row.case_current_version)+' · '+escapeOrder(row.case_current_cell)+'</small>':
          row.status==='PICKED'&&row.picked_case_task_id?'<small class="order-case-warning">Текущее размещение CASE не подтверждено</small>':''}</td>
      <td>${escapeOrder(row.address_text)}${Number.isSafeInteger(row.current_trip_id)&&row.current_trip_id>0?'<br><a href="transport-loading.html?trip_id='+row.current_trip_id+'" title="Открыть фактическую погрузку назначенного рейса.">Рейс №'+escapeOrder(row.current_trip_id)+' →</a><small class="order-case-location">'+escapeOrder(row.current_trip_condition||"Статус не задан")+' · ворота: '+escapeOrder(row.current_dock||"не назначены")+'</small>':'<small class="order-case-location">Рейс не назначен</small>'}</td>
      <td>${row.physical_composition?.length ? row.physical_composition.map(x => `${escapeOrder(x.article)}: ${escapeOrder(x.quantity)} ${escapeOrder(x.base_uom)}`).join("<br>") : escapeOrder(row.fact_qty_exact ?? row.fact_qty ?? "—")}</td>
      <td>${escapeOrder(row.fact_weight_exact ?? row.fact_weight)}</td>
      <td>${escapeOrder(({PLANNED:"Подготовлена СТ",PICKED:"Отобрано",SHIPPED:"Отгружено",CANCELLED:"Отменено"})[row.status]||row.status)}${row.picked_at ? `<br>${escapeOrder(row.picked_at)} · ${escapeOrder(row.picked_by)}` : ""}</td>
    </tr>
  `).join("");
}

async function importLegacyOrder() {
  const legacyId = orderEl("legacyImportId").value;
  if (!legacyId) throw new Error("Укажите legacy order ID");
  const created = await orderRequest(`/api/customer-orders/import-legacy/${legacyId}`, { method: "POST" });
  await loadOrders();
  await loadOrderDetail(created.customer_order_id);
}

function orderBind(id, handler) {
  orderEl(id).addEventListener("click", async () => {
    try {
      await handler();
    } catch (exc) {
      orderEl("orderStatusText").textContent = exc.message;
    }
  });
}

async function orderInit() {
  if(!window.wmsAdminAuth?.state?.user?.username)return;
  const scope=orderScope();
  if(scope===orderIdentity)return;
  orderIdentity=scope;orderListGeneration++;orderDetailGeneration++;
  orderPageCursor=null;orderPageHistory=[];orderPageFilters="";orderPageBusy=false;
  orderState.orders=[];orderState.selectedId=null;orderState.detail=null;orderState.fulfillment=[];orderState.layoutOrderId=null;orderState.preparations.clear();
  for(const id of ["orderRows","orderDetails","orderLineRows","orderFulfillmentRows","sapLayoutRows"])orderEl(id).replaceChildren();
  orderEl("sapTripReviewMessage").textContent="";orderEl("orderDetailStatus").textContent="Выберите заказ";orderEl("sapPreparationStatus").textContent="Выберите исходный заказ.";
  window.dispatchEvent(new CustomEvent("wms-order-context-changed"));
  if(!orderBound){
    orderBound=true;
    orderBind("sapLayoutLoad",loadSapLayout);orderBind("sapPrepareSt",prepareSapSt);orderBind("sapAssignSt",assignPreparedSt);orderBind("sapTripReview",reviewPreparedTrip);
    orderBind("orderPageNext",()=>orderPage("next"));orderBind("orderPagePrevious",()=>orderPage("previous"));
    orderBind("orderLoad",loadOrders);orderBind("orderRefresh",loadOrders);orderBind("legacyImport",importLegacyOrder);
    orderEl("orderSearchTop").addEventListener("keydown",event=>{if(event.key==="Enter")loadOrders();});
  }
  await loadOrders();
  if(scope!==orderScope())return;
  const initial=Number(new URLSearchParams(window.location.search).get("order_id"));
  if(Number.isSafeInteger(initial)&&initial!==0){
    await loadOrderDetail(initial);
    if(scope===orderScope()&&orderState.selectedId===initial&&window.location.hash==="#sapAssignment"){
      await loadSapLayout();
      if(scope===orderScope()&&orderState.selectedId===initial){
        orderEl("sapAssignment").open=true;orderEl("sapAssignment").scrollIntoView({block:"start"});
      }
    }
    if(scope===orderScope()&&orderState.selectedId===initial&&window.location.hash==="#orderExecution")
      document.getElementById("orderExecution")?.scrollIntoView({block:"start"});
  }
}

window.addEventListener("wms-admin-auth-ready", orderInit);

function sapLayoutRow(articul, quantity='', pallet=1) {
  const tr=document.createElement('tr');
  const article=document.createElement('td');article.textContent=articul;tr.dataset.articul=articul;
  const qty=document.createElement('input');qty.type='text';qty.inputMode='decimal';qty.value=quantity;qty.dataset.field='quantity';qty.setAttribute('aria-label','Количество');
  const number=document.createElement('input');number.type='number';number.min='1';number.max='100';number.value=pallet;number.dataset.field='pallet';number.setAttribute('aria-label','Паллета №');
  const qtyCell=document.createElement('td');qtyCell.appendChild(qty);const palletCell=document.createElement('td');palletCell.appendChild(number);
  const actions=document.createElement('td');const split=document.createElement('button');split.type='button';split.textContent='Разделить';split.onclick=()=>sapLayoutRow(articul,'',Number(number.value)+1);
  const remove=document.createElement('button');remove.type='button';remove.textContent='Убрать';remove.onclick=()=>tr.remove();actions.append(split,remove);tr.append(article,qtyCell,palletCell,actions);orderEl('sapLayoutRows').appendChild(tr);
}

async function loadSapLayout() {
  const id=orderState.selectedId,scope=orderScope(),serial=orderDetailGeneration;if(!id)throw new Error('Выберите заказ SAP.');
  const detail=await orderRequest(`/api/integrations/sap/store-orders/${id}`);
  if(orderState.selectedId!==id||scope!==orderScope()||serial!==orderDetailGeneration)return;
  orderEl('sapManualEditor').hidden=Boolean(detail.preparation_json);orderEl('sapPrepareSt').disabled=Boolean(detail.preparation_json);
  orderState.layoutOrderId=id;orderEl('sapLayoutRows').replaceChildren();
  for(const row of orderState.detail.rows)sapLayoutRow(row.articul,String(row.order_qty_exact??row.order_qty));
  if(detail.preparation_json){const result=typeof detail.preparation_json==='string'?JSON.parse(detail.preparation_json):detail.preparation_json;orderState.preparations.set(id,{result});orderEl('sapPreparationStatus').textContent=`Подготовлена СТ ${result.st_number}, мест: ${result.pallet_identifiers.length}.`;}
  else orderEl('sapPreparationStatus').textContent='Проверьте количество и номера паллет.';
}

async function prepareSapSt() {
  const auth=window.wmsAdminAuth.state,who=auth.user?.username;
  if(localStorage.getItem('sap-auto-preparation:'+auth.apiBase+':'+who)||
     localStorage.getItem('sap-st-preparation:'+JSON.stringify([auth.apiBase,who])))
    throw new Error('Сначала выясните исход сохранённой подготовки СТ; новый запрос заблокирован.');
  const id=orderState.selectedId,scope=orderScope();if(!id||id!==orderState.layoutOrderId)throw new Error('Загрузите укладку выбранного заказа.');
  const groups=new Map();
  for(const tr of orderEl('sapLayoutRows').children){const number=Number(tr.querySelector('[data-field=pallet]').value);if(!Number.isInteger(number)||number<1||number>100)throw new Error('Номер паллеты: 1–100.');if(!groups.has(number))groups.set(number,[]);groups.get(number).push({articul:tr.dataset.articul,quantity:tr.querySelector('[data-field=quantity]').value.trim()});}
  const pallets=[...groups.entries()].sort((a,b)=>a[0]-b[0]).map(([,lines])=>({lines}));
  const signature=JSON.stringify(pallets);let operation=orderState.preparations.get(id);
  if(operation?.result){orderEl('sapPreparationStatus').textContent=`Уже подготовлена СТ ${operation.result.st_number}.`;return;}
  if(!operation||operation.signature!==signature){operation={signature,operation_id:crypto.randomUUID()};orderState.preparations.set(id,operation);}
  operation.result=await orderRequest(`/api/integrations/sap/store-orders/${id}/prepare-st`,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({operation_id:operation.operation_id,pallets})});
  if(orderState.selectedId===id&&scope===orderScope()){orderEl('sapPreparationStatus').textContent=`СТ ${operation.result.st_number} подготовлена. Можно добавить её в существующий рейс.`;await loadOrderDetail(id);}
}

async function assignPreparedSt() {
  const id=orderState.selectedId,scope=orderScope();const prepared=orderState.preparations.get(id)?.result;const trip=Number(orderEl('sapTripId').value);
  if(!prepared||!Number.isSafeInteger(trip)||trip<=0)throw new Error('Подготовьте СТ и укажите существующий рейс.');
  // Existing dispatcher endpoint; no second order/trip relation.
  await orderRequest(`/api/admin/transport/tasks/${trip}/sts`,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({st_numbers:[prepared.st_number]})});
  if(orderState.selectedId===id&&scope===orderScope())orderEl('sapPreparationStatus').textContent=`СТ ${prepared.st_number} добавлена в рейс ${trip}.`;
}
if(window.wmsAdminAuth?.state?.user?.username)orderInit();

async function reviewPreparedTrip(){
 const id=orderState.selectedId,scope=orderScope(),serial=orderDetailGeneration,trip=Number(orderEl('sapTripId').value);
 const prepared=orderState.preparations.get(id)?.result;
 if(!prepared||!Number.isSafeInteger(trip)||trip<1)throw Error('Прочитайте подготовленную СТ и укажите существующий рейс.');
 orderEl('sapTripReviewMessage').textContent='Читаются текущие ограничения ТМС.';
 const result=await orderRequest('/api/transport/preflight/trips/'+trip,{method:'POST',
  headers:{'Content-Type':'application/json'},body:JSON.stringify({additional_st_numbers:[prepared.st_number]})});
 if(scope!==orderScope()||serial!==orderDetailGeneration||id!==orderState.selectedId||trip!==Number(orderEl('sapTripId').value))return;
 if(result.trip_id!==trip||result.read_only!==true||!Array.isArray(result.routes)||result.routes.length!==1)throw Error('Результат рейса не подтверждён.');
 const route=result.routes[0],capacity=route?.capacity_and_type?.result;
 const blockers=[...(route?.source_blockers||[]).map(x=>x.code),
  ...(route?.capacity_and_type?.status==='BLOCKED'?[route.capacity_and_type.code]:[])];
 const floor=capacity?.floor_capacity;
 const floorNote=floor?.status==='COMPATIBLE'?' Норматив тары: допустимые варианты '+floor.matching_variants.join(', ')+'.':
  floor?.status==='INCOMPATIBLE'?' Ни один нормативный вариант тары не подходит.':
  floor&&floor.status!=='NOT_CONFIGURED'?' Типы верхних грузовых мест или профиль тары не подтверждены.':'';
 const warnings=capacity?.warnings||[];
 const thermal=route?.temperature_requirements;
 const thermalPlanning=thermal?.planning;
 const thermalPlanningNote=thermalPlanning?(
  thermalPlanning.status==='DECLARED_CAPABILITY_COMPATIBLE'?' По текущему профилю машины достижим диапазон '+thermalPlanning.feasible_min_c+' … '+thermalPlanning.feasible_max_c+' °C. Фактическая температура ещё не подтверждена.':
  thermalPlanning.status==='VEHICLE_RANGE_INCOMPATIBLE'?' Температурные возможности машины несовместимы с товаром.':
  thermalPlanning.status==='SKU_RANGES_CONFLICT'?' Для этих товаров нет общего температурного режима.':
  ' Совместимость температурного профиля не подтверждена: '+thermalPlanning.status+'.'):'';
 const thermalNote=thermal?(
  thermal.ranges_conflict?' Температурные диапазоны товаров несовместимы.':
  thermal.all_ranges_configured?' Текущие складские диапазоны товара: от '+(thermal.common_min_c??'не задано')+' до '+(thermal.common_max_c??'не задано')+' °C.':
  ' Температурные требования части товаров не подтверждены: настройка отсутствует или некорректна.')+
  ' Режим машины: '+(thermal.vehicle_legacy_mode||'не задан')+'. Его название не подтверждает допустимый диапазон или фактическую температуру.':'';

 const labels={PLAN_ST_FOREIGN_OR_SHIPPED:'СТ уже назначена в другой рейс или отгружена',PLAN_ST_NOT_FOUND:'СТ отсутствует',PLAN_ACTIVE_UNBILLED_TRIP_REQUIRED:'Рейс закрыт или включён в счёт',PLAN_ACTIVE_VEHICLE_CAPACITY_REQUIRED:'Машина заблокирована или не заданы её вместимость и тип',PLAN_CURRENT_VEHICLE_NOT_FOUND:'Машина не найдена',PLAN_TARE_VARIANT_CAPACITY_EXCEEDED:'Состав мест превышает нормативные сочетания тары машины',PLAN_TARE_CURRENT_PLACE_TYPE_REQUIRED:'Нужны подтверждённые типы верхних мест и текущий профиль тары',PLAN_WEIGHT_CAPACITY_EXCEEDED:'Превышена допустимая масса машины',PLAN_PALLET_CAPACITY_EXCEEDED:'Превышено число мест в машине',PLAN_ADDRESS_VEHICLE_TYPE_OR_HYDRO_CONFLICT:'Тип машины или гидроборт не соответствует магазину',PLAN_ADDRESS_VEHICLE_LIMIT_EXCEEDED:'Машина превышает ограничение магазина'};
 orderEl('sapTripReviewMessage').textContent=
  (blockers.length?'Ограничения: '+blockers.map(x=>labels[x]||x).join('; '):(capacity?.validation_status==='CAPACITY_TYPE_CHECKED'?'Вместимость проверена действующими правилами ТМС.':'План требует уточнения ограничений.'))+
  (capacity?.declared_places!==undefined&&capacity?.declared_weight_kg!==undefined?' Плановых мест: '+capacity.declared_places+', масса: '+capacity.declared_weight_kg+' кг.':'')+
  (warnings.length?' '+warnings.join('; '):'') +thermalNote+thermalPlanningNote+floorNote+
  ' Назначение проверяет текущие данные повторно. Погрузка, температурный режим и разрешение выезда подтверждаются отдельно.';
}
orderEl('sapTripId').addEventListener('input',()=>{orderEl('sapTripReviewMessage').textContent='';});
