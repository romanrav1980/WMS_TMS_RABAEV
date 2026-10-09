const orderState = {
  orders: [],
  selectedId: null,
  detail: null,
  fulfillment: [],
  preparations: new Map(),
  layoutOrderId: null,
};

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
    throw new Error((payload && payload.detail) || `HTTP ${response.status}`);
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

async function loadOrders() {
  orderEl("orderStatusText").textContent = "Загрузка...";
  orderState.orders = await orderRequest(`/api/customer-orders?${orderFilters().toString()}`);
  renderOrders();
  orderEl("orderStatusText").textContent = `Заказов: ${orderState.orders.length}`;
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
      <td>${escapeOrder(order.total_order_qty)}</td>
    `;
    tr.addEventListener("click", () => loadOrderDetail(order.customer_order_id));
    tbody.appendChild(tr);
  }
}

async function loadOrderDetail(orderId) {
  orderState.selectedId = orderId;
  orderEl("orderDetailStatus").textContent = "Загрузка...";
  orderState.detail = await orderRequest(`/api/customer-orders/${orderId}`);
  orderEl("orderDetails").textContent = JSON.stringify({
    customer_order_id: orderState.detail.customer_order_id,
    legacy_order_id: orderState.detail.legacy_order_id,
    order_no: orderState.detail.order_no,
    status: orderState.detail.status,
    customer_id: orderState.detail.customer_id,
    customer_name: orderState.detail.customer_name,
    shipment_date: orderState.detail.shipment_date,
    route_id: orderState.detail.route_id,
    dock_id: orderState.detail.dock_id,
  }, null, 2);
  renderOrderLines();
  renderOrders();
  orderEl("orderDetailStatus").textContent = `${orderState.detail.order_no || orderId} / ${orderState.detail.status}`;
  if (orderCan("customer_fulfillment_view")) {
    orderState.fulfillment = await orderRequest(`/api/customer-orders/${orderId}/fulfillment`);
    renderFulfillment();
  } else {
    orderEl("orderFulfillmentRows").innerHTML = "";
  }
}

function renderOrderLines() {
  const rows = orderState.detail?.rows || [];
  orderEl("orderLineRows").innerHTML = rows.map((row) => `
    <tr>
      <td>${escapeOrder(row.line_no)}</td>
      <td>${escapeOrder(row.articul)}</td>
      <td>${escapeOrder(row.product_name)}</td>
      <td>${escapeOrder(row.order_qty)}</td>
      <td>${escapeOrder(row.order_weight)}</td>
      <td>${escapeOrder(row.pack_count)}</td>
      <td>${escapeOrder(row.status)}</td>
    </tr>
  `).join("");
}

function renderFulfillment() {
  orderEl("orderFulfillmentRows").innerHTML = orderState.fulfillment.map((row) => `
    <tr>
      <td>${escapeOrder(row.fulfillment_id)}</td>
      <td>${escapeOrder(row.pallet_uid || row.legacy_sborka_pallet_id)}</td>
      <td>${escapeOrder(row.address_text)}</td>
      <td>${escapeOrder(row.fact_qty)}</td>
      <td>${escapeOrder(row.fact_weight)}</td>
      <td>${escapeOrder(row.status)}</td>
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
  orderBind('sapLayoutLoad', loadSapLayout);
  orderBind('sapPrepareSt', prepareSapSt);
  orderBind('sapAssignSt', assignPreparedSt);
  orderBind("orderLoad", loadOrders);
  orderBind("orderRefresh", loadOrders);
  orderBind("legacyImport", importLegacyOrder);
  orderEl("orderSearchTop").addEventListener("keydown", (event) => {
    if (event.key === "Enter") loadOrders();
  });
  await loadOrders();
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
  const id=orderState.selectedId;if(!id)throw new Error('Выберите заказ SAP.');
  const detail=await orderRequest(`/api/integrations/sap/store-orders/${id}`);
  if(orderState.selectedId!==id)return;
  orderState.layoutOrderId=id;orderEl('sapLayoutRows').replaceChildren();
  for(const row of orderState.detail.rows)sapLayoutRow(row.articul,String(row.order_qty));
  if(detail.preparation_json){const result=typeof detail.preparation_json==='string'?JSON.parse(detail.preparation_json):detail.preparation_json;orderState.preparations.set(id,{result});orderEl('sapPreparationStatus').textContent=`Подготовлена СТ ${result.st_number}.`;}
  else orderEl('sapPreparationStatus').textContent='Проверьте количество и номера паллет.';
}

async function prepareSapSt() {
  const id=orderState.selectedId;if(!id||id!==orderState.layoutOrderId)throw new Error('Загрузите укладку выбранного заказа.');
  const groups=new Map();
  for(const tr of orderEl('sapLayoutRows').children){const number=Number(tr.querySelector('[data-field=pallet]').value);if(!Number.isInteger(number)||number<1||number>100)throw new Error('Номер паллеты: 1–100.');if(!groups.has(number))groups.set(number,[]);groups.get(number).push({articul:tr.dataset.articul,quantity:tr.querySelector('[data-field=quantity]').value.trim()});}
  const pallets=[...groups.entries()].sort((a,b)=>a[0]-b[0]).map(([,lines])=>({lines}));
  const signature=JSON.stringify(pallets);let operation=orderState.preparations.get(id);
  if(operation?.result){orderEl('sapPreparationStatus').textContent=`Уже подготовлена СТ ${operation.result.st_number}.`;return;}
  if(!operation||operation.signature!==signature){operation={signature,operation_id:crypto.randomUUID()};orderState.preparations.set(id,operation);}
  operation.result=await orderRequest(`/api/integrations/sap/store-orders/${id}/prepare-st`,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({operation_id:operation.operation_id,pallets})});
  if(orderState.selectedId===id){orderEl('sapPreparationStatus').textContent=`СТ ${operation.result.st_number} подготовлена. Можно добавить её в существующий рейс.`;await loadOrderDetail(id);}
}

async function assignPreparedSt() {
  const id=orderState.selectedId;const prepared=orderState.preparations.get(id)?.result;const trip=Number(orderEl('sapTripId').value);
  if(!prepared||!Number.isSafeInteger(trip)||trip<=0)throw new Error('Подготовьте СТ и укажите существующий рейс.');
  // Existing dispatcher endpoint; no second order/trip relation.
  await orderRequest(`/api/admin/transport/tasks/${trip}/sts`,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({st_numbers:[prepared.st_number]})});
  if(orderState.selectedId===id)orderEl('sapPreparationStatus').textContent=`СТ ${prepared.st_number} добавлена в рейс ${trip}.`;
}