const orderState = {
  orders: [],
  selectedId: null,
  detail: null,
  fulfillment: [],
};

const orderEl = (id) => document.getElementById(id);

function orderApiBase() {
  return orderEl("orderBase").value.replace(/\/$/, "");
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
  orderEl("orderBase").value = window.wmsAdminAuth?.state?.apiBase || orderEl("orderBase").value;
  orderBind("orderLoad", loadOrders);
  orderBind("orderRefresh", loadOrders);
  orderBind("legacyImport", importLegacyOrder);
  orderEl("orderSearchTop").addEventListener("keydown", (event) => {
    if (event.key === "Enter") loadOrders();
  });
  await loadOrders();
}

window.addEventListener("wms-admin-auth-ready", orderInit);
