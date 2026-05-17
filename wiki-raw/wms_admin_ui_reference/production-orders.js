const mesState = {
  orders: [],
  selectedOrder: null,
};

const mesEl = (id) => document.getElementById(id);

function mesApiBase() {
  return mesEl("mesBase").value.replace(/\/$/, "");
}

function mesHeaders(extra = {}) {
  if (!window.wmsAdminAuth) return { ...extra };
  return window.wmsAdminAuth.headers(extra);
}

function mesCan(permission) {
  return window.wmsAdminAuth && window.wmsAdminAuth.hasPermission(permission);
}

function mesCurrentUser() {
  return window.wmsAdminAuth?.state?.user?.username || "admin";
}

function mesFilters() {
  const params = new URLSearchParams();
  const target = mesEl("mesTargetFilter").value.trim() || mesEl("mesSearch").value.trim();
  if (target) params.set("target_articul", target);
  if (mesEl("mesStatusFilter").value) params.set("status", mesEl("mesStatusFilter").value);
  params.set("limit", mesEl("mesLimit").value || "100");
  return params;
}

async function mesLoadOrders() {
  mesEl("mesStatusText").textContent = "Загрузка...";
  const response = await fetch(`${mesApiBase()}/api/mes/production-orders?${mesFilters().toString()}`, {
    headers: mesHeaders(),
  });
  if (!response.ok) throw new Error(`MES HTTP ${response.status}`);
  mesState.orders = await response.json();
  renderMesOrders();
  mesEl("mesStatusText").textContent = `Заказов: ${mesState.orders.length}`;
}

function renderMesOrders() {
  const tbody = mesEl("mesOrderRows");
  tbody.innerHTML = "";
  for (const order of mesState.orders) {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td>${order.production_order_id ?? ""}</td>
      <td>${escapeMes(order.order_no ?? "")}</td>
      <td>${escapeMes(order.target_articul ?? "")}</td>
      <td>${escapeMes(order.status ?? "")}</td>
      <td>${order.planned_qty ?? ""} ${escapeMes(order.unit_code ?? "")}</td>
      <td>${order.fact_qty ?? ""}</td>
      <td>${order.prod_batch_id ?? ""}</td>
    `;
    tr.addEventListener("click", () => loadMesOrder(order.production_order_id));
    tbody.appendChild(tr);
  }
}

async function loadMesOrder(orderId) {
  mesEl("mesDetailStatus").textContent = "Загрузка...";
  const response = await fetch(`${mesApiBase()}/api/mes/production-orders/${orderId}`, {
    headers: mesHeaders(),
  });
  const result = await response.json();
  if (!response.ok) throw new Error(result.detail || `MES detail HTTP ${response.status}`);
  mesState.selectedOrder = result;
  mesEl("mesDetailStatus").textContent = `${result.order_no} / ${result.status}`;
  mesEl("mesDetails").textContent = JSON.stringify({
    production_order_id: result.production_order_id,
    order_no: result.order_no,
    bom_id: result.bom_id,
    target_articul: result.target_articul,
    planned_qty: result.planned_qty,
    fact_qty: result.fact_qty,
    unit_code: result.unit_code,
    status: result.status,
    prod_batch_id: result.prod_batch_id,
  }, null, 2);
  renderMesMovements(result.movements || []);
  mesEl("mesGenealogy").textContent = "";
}

function renderMesMovements(movements) {
  const tbody = mesEl("mesMovementRows");
  tbody.innerHTML = "";
  for (const movement of movements) {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td>${movement.movement_id ?? ""}</td>
      <td>${escapeMes(movement.movement_type ?? "")}</td>
      <td>${escapeMes(movement.status ?? "")}</td>
      <td>${escapeMes(movement.uid_pallet ?? "")}</td>
      <td>${escapeMes(movement.source_location ?? "")}</td>
      <td>${escapeMes(movement.target_location ?? "")}</td>
      <td>${movement.quantity ?? ""} ${escapeMes(movement.unit_code ?? "")}</td>
      <td>${escapeMes(movement.last_error ?? "")}</td>
    `;
    tbody.appendChild(tr);
  }
}

async function createMesOrder() {
  if (!mesCan("mes_production_edit")) throw new Error("Нет права mes_production_edit");
  const body = {
    order_no: mesEl("mesNewOrderNo").value.trim(),
    bom_id: mesEl("mesNewBomId").value ? Number(mesEl("mesNewBomId").value) : null,
    target_articul: mesEl("mesNewTarget").value.trim(),
    planned_qty: Number(mesEl("mesNewQty").value),
    unit_code: mesEl("mesNewUnit").value.trim() || "KG",
    production_line: mesEl("mesNewLine").value.trim() || null,
    created_by: mesCurrentUser(),
  };
  const response = await fetch(`${mesApiBase()}/api/mes/production-orders`, {
    method: "POST",
    headers: mesHeaders({ "Content-Type": "application/json" }),
    body: JSON.stringify(body),
  });
  const result = await response.json();
  if (!response.ok) throw new Error(result.detail || `Create MES order HTTP ${response.status}`);
  await mesLoadOrders();
  await loadMesOrder(result.id);
}

async function issueMesRaw() {
  if (!mesState.selectedOrder) throw new Error("Выберите заказ");
  if (!mesCan("mes_production_edit")) throw new Error("Нет права mes_production_edit");
  const body = {
    uid_pallet: mesEl("mesRawPallet").value.trim() || null,
    raw_articul: mesEl("mesRawArticul").value.trim() || null,
    quantity: Number(mesEl("mesRawQty").value),
    unit_code: mesState.selectedOrder.unit_code || "KG",
    source_location: mesEl("mesRawFrom").value.trim() || null,
    production_location: mesEl("mesRawTo").value.trim() || "MES_PROD",
    created_by: mesCurrentUser(),
  };
  const response = await fetch(`${mesApiBase()}/api/mes/production-orders/${mesState.selectedOrder.production_order_id}/issue-raw`, {
    method: "POST",
    headers: mesHeaders({ "Content-Type": "application/json" }),
    body: JSON.stringify(body),
  });
  const result = await response.json();
  if (!response.ok) throw new Error(result.detail || `Issue raw HTTP ${response.status}`);
  await loadMesOrder(mesState.selectedOrder.production_order_id);
}

async function completeMesOrder() {
  if (!mesState.selectedOrder) throw new Error("Выберите заказ");
  if (!mesCan("mes_production_complete")) throw new Error("Нет права mes_production_complete");
  const qty = Number(mesEl("mesFactQty").value);
  const body = {
    prod_batch_no: mesEl("mesLotNo").value.trim() || null,
    fact_qty: qty,
    unit_code: mesState.selectedOrder.unit_code || "KG",
    pallets: [{
      uid_pallet: mesEl("mesFgPallet").value.trim(),
      pallet_no: 1,
      quantity: qty,
      sscc: mesEl("mesFgSscc").value.trim() || null,
    }],
    idempotency_key: `${mesState.selectedOrder.order_no}:complete`,
    created_by: mesCurrentUser(),
  };
  const response = await fetch(`${mesApiBase()}/api/mes/production-orders/${mesState.selectedOrder.production_order_id}/complete`, {
    method: "POST",
    headers: mesHeaders({ "Content-Type": "application/json" }),
    body: JSON.stringify(body),
  });
  const result = await response.json();
  if (!response.ok) throw new Error(result.detail || `Complete HTTP ${response.status}`);
  await loadMesOrder(mesState.selectedOrder.production_order_id);
}

async function applyMesWms() {
  if (!mesState.selectedOrder) throw new Error("Выберите заказ");
  if (!mesCan("mes_wms_bridge_apply")) throw new Error("Нет права mes_wms_bridge_apply");
  const response = await fetch(`${mesApiBase()}/api/mes/production-orders/${mesState.selectedOrder.production_order_id}/apply-wms`, {
    method: "POST",
    headers: mesHeaders({ "Content-Type": "application/json" }),
    body: JSON.stringify({ applied_by: mesCurrentUser() }),
  });
  const result = await response.json();
  if (!response.ok) throw new Error(result.detail || `Apply WMS HTTP ${response.status}`);
  await loadMesOrder(mesState.selectedOrder.production_order_id);
}

async function loadMesGenealogy() {
  if (!mesState.selectedOrder) throw new Error("Выберите заказ");
  const response = await fetch(`${mesApiBase()}/api/mes/production-orders/${mesState.selectedOrder.production_order_id}/genealogy`, {
    headers: mesHeaders(),
  });
  const result = await response.json();
  if (!response.ok) throw new Error(result.detail || `Genealogy HTTP ${response.status}`);
  mesEl("mesGenealogy").textContent = JSON.stringify({
    order: {
      production_order_id: result.order?.production_order_id,
      order_no: result.order?.order_no,
      status: result.order?.status,
      prod_batch_id: result.order?.prod_batch_id,
      target_articul: result.order?.target_articul,
    },
    raw_usage: result.raw_usage || [],
    pallets: result.pallets || [],
  }, null, 2);
}

function fillMesDemoFields() {
  const suffix = new Date().toISOString().replace(/[-:TZ.]/g, "").slice(0, 14);
  mesEl("mesNewOrderNo").value = `MES-DEMO-${suffix}`;
  mesEl("mesNewTarget").value = "FG-DEMO-PETFOOD";
  mesEl("mesNewQty").value = "100";
  mesEl("mesNewUnit").value = "KG";
  mesEl("mesNewLine").value = "LINE-1";
  mesEl("mesRawPallet").value = `RAW-DEMO-${suffix}`;
  mesEl("mesRawArticul").value = "RM-MEAT-BEEF-FROZ-01";
  mesEl("mesRawQty").value = "50";
  mesEl("mesRawFrom").value = "RM-A01-01";
  mesEl("mesRawTo").value = "MES_PROD";
  mesEl("mesLotNo").value = `LOT-DEMO-${suffix}`;
  mesEl("mesFactQty").value = "100";
  mesEl("mesFgPallet").value = `FG-DEMO-${suffix}`;
  mesEl("mesFgSscc").value = `0000000000${suffix}`.slice(-18);
}

function initMes() {
  if (!mesEl("mesRefresh")) return;
  if (window.wmsAdminAuth && !window.wmsAdminAuth.hasPermission("mes_production_view")) return;
  mesEl("mesRefresh").addEventListener("click", () => mesLoadOrders().catch(showMesError));
  mesEl("mesLoad").addEventListener("click", () => mesLoadOrders().catch(showMesError));
  mesEl("mesCreateOrder").addEventListener("click", () => createMesOrder().catch(showMesError));
  mesEl("mesFillDemo").addEventListener("click", () => fillMesDemoFields());
  mesEl("mesIssueRaw").addEventListener("click", () => issueMesRaw().catch(showMesError));
  mesEl("mesCompleteOrder").addEventListener("click", () => completeMesOrder().catch(showMesError));
  mesEl("mesApplyWms").addEventListener("click", () => applyMesWms().catch(showMesError));
  mesEl("mesLoadGenealogy").addEventListener("click", () => loadMesGenealogy().catch(showMesError));
  for (const id of ["mesStatusFilter", "mesTargetFilter", "mesLimit"]) {
    mesEl(id).addEventListener("change", () => mesLoadOrders().catch(showMesError));
  }
  mesLoadOrders().catch(showMesError);
}

function showMesError(error) {
  mesEl("mesStatusText").textContent = `Ошибка: ${error.message}`;
  mesEl("mesDetailStatus").textContent = `Ошибка: ${error.message}`;
}

function escapeMes(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;");
}

if (window.wmsAdminAuth && window.wmsAdminAuth.state.user) {
  initMes();
} else {
  window.addEventListener("wms-admin-auth-ready", initMes, { once: true });
}
