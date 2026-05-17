const rawSupplyState = {
  orders: [],
  selectedOrder: null,
  supply: null,
  tasks: [],
  shortages: [],
};

const rawSupplyEl = (id) => document.getElementById(id);

function rawSupplyApiBase() {
  return (window.wmsAdminAuth?.state?.apiBase || "http://127.0.0.1:8088").replace(/\/$/, "");
}

function rawSupplyHeaders(extra = {}) {
  if (!window.wmsAdminAuth) return { ...extra };
  return window.wmsAdminAuth.headers(extra);
}

function rawSupplyCan(permission) {
  return window.wmsAdminAuth && window.wmsAdminAuth.hasPermission(permission);
}

function rawSupplyUser() {
  return window.wmsAdminAuth?.state?.user?.username || "admin";
}

async function rawSupplyFetch(path, options = {}) {
  const response = await fetch(`${rawSupplyApiBase()}${path}`, {
    ...options,
    headers: rawSupplyHeaders(options.headers || {}),
  });
  const text = await response.text();
  const body = text ? JSON.parse(text) : {};
  if (!response.ok) {
    const detail = body.detail?.message || body.detail || body.message || `HTTP ${response.status}`;
    throw new Error(typeof detail === "string" ? detail : JSON.stringify(detail));
  }
  return body;
}

function rawSupplyOrderParams() {
  const params = new URLSearchParams();
  const target = rawSupplyEl("rawSupplyTarget").value.trim() || rawSupplyEl("rawSupplySearch").value.trim();
  const status = rawSupplyEl("rawSupplyOrderStatus").value;
  if (target) params.set("target_articul", target);
  if (status) params.set("status", status);
  params.set("limit", rawSupplyEl("rawSupplyOrderLimit").value || "100");
  return params;
}

function rawSupplyTaskParams(selectedOnly = false) {
  const params = new URLSearchParams();
  const status = rawSupplyEl("rawSupplyTaskStatus").value;
  if (selectedOnly && rawSupplyState.selectedOrder) {
    params.set("production_order_id", rawSupplyState.selectedOrder.production_order_id);
  }
  if (status) params.set("status", status);
  params.set("limit", rawSupplyEl("rawSupplyTaskLimit").value || "100");
  return params;
}

function rawSupplyShortageParams(selectedOnly = false) {
  const params = new URLSearchParams();
  const status = rawSupplyEl("rawSupplyShortageStatus").value;
  const rawArticul = rawSupplyEl("rawSupplyShortageArticul").value.trim();
  if (selectedOnly && rawSupplyState.selectedOrder) {
    params.set("production_order_id", rawSupplyState.selectedOrder.production_order_id);
  }
  if (status) params.set("status", status);
  if (rawArticul) params.set("raw_articul", rawArticul);
  params.set("limit", rawSupplyEl("rawSupplyShortageLimit").value || "100");
  return params;
}

async function loadRawSupplyOrders() {
  rawSupplyEl("rawSupplyOrderStatusText").textContent = "Загрузка...";
  rawSupplyState.orders = await rawSupplyFetch(`/api/mes/production-orders?${rawSupplyOrderParams().toString()}`);
  renderRawSupplyOrders();
  rawSupplyEl("rawSupplyOrderStatusText").textContent = `Заказов: ${rawSupplyState.orders.length}`;
}

async function loadRawSupplyOrder(orderId) {
  rawSupplyEl("rawSupplyDetailStatus").textContent = "Загрузка...";
  rawSupplyState.selectedOrder = await rawSupplyFetch(`/api/mes/production-orders/${orderId}`);
  rawSupplyEl("rawSupplyDetailStatus").textContent = `${rawSupplyState.selectedOrder.order_no} / ${rawSupplyState.selectedOrder.status}`;
  await loadSelectedRawSupply();
}

async function loadSelectedRawSupply() {
  if (!rawSupplyState.selectedOrder) {
    renderRawSupply(null);
    return;
  }
  rawSupplyState.supply = await rawSupplyFetch(`/api/mes/production-orders/${rawSupplyState.selectedOrder.production_order_id}/raw-supply`);
  renderRawSupply(rawSupplyState.supply);
}

async function calculateRawSupply() {
  if (!rawSupplyState.selectedOrder) throw new Error("Выберите производственный заказ");
  if (!rawSupplyCan("mes_raw_supply_calculate")) throw new Error("Нет права mes_raw_supply_calculate");
  const result = await rawSupplyFetch(`/api/mes/production-orders/${rawSupplyState.selectedOrder.production_order_id}/raw-supply/calculate`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ calculated_by: rawSupplyUser() }),
  });
  rawSupplyEl("rawSupplyOrderStatusText").textContent =
    `Расчет: потребность ${result.demand_count}, кандидаты ${result.candidate_count}, дефицит ${result.shortage_count}`;
  await loadSelectedRawSupply();
  await loadRawSupplyShortages(true);
}

async function releaseRawSupply() {
  if (!rawSupplyState.selectedOrder) throw new Error("Выберите производственный заказ");
  if (!rawSupplyCan("mes_raw_transfer_create")) throw new Error("Нет права mes_raw_transfer_create");
  const result = await rawSupplyFetch(`/api/mes/production-orders/${rawSupplyState.selectedOrder.production_order_id}/release-to-production`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      to_ware_id: rawSupplyEl("rawSupplyToWare").value ? Number(rawSupplyEl("rawSupplyToWare").value) : null,
      to_cell: rawSupplyEl("rawSupplyToCell").value.trim() || "MES_PROD",
      allow_partial: Number(rawSupplyEl("rawSupplyAllowPartial").value || 0),
      created_by: rawSupplyUser(),
    }),
  });
  rawSupplyEl("rawSupplyOrderStatusText").textContent = `Создано задач: ${result.created_task_count}`;
  await loadSelectedRawSupply();
  await Promise.all([loadRawSupplyTasks(true), loadRawSupplyShortages(true)]);
}

async function loadRawSupplyTasks(selectedOnly = false) {
  rawSupplyState.tasks = await rawSupplyFetch(`/api/mes/raw-transfer-tasks?${rawSupplyTaskParams(selectedOnly).toString()}`);
  renderRawSupplyTasks(rawSupplyState.tasks);
}

async function loadRawSupplyShortages(selectedOnly = false) {
  rawSupplyState.shortages = await rawSupplyFetch(`/api/mes/raw-shortages?${rawSupplyShortageParams(selectedOnly).toString()}`);
  renderRawSupplyShortages(rawSupplyState.shortages);
}

async function confirmRawSupplyTask(taskId) {
  if (!rawSupplyCan("mes_raw_transfer_confirm")) throw new Error("Нет права mes_raw_transfer_confirm");
  await rawSupplyFetch(`/api/mes/raw-transfer-tasks/${taskId}/confirm`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ confirmed_by: rawSupplyUser() }),
  });
  await afterRawSupplyTaskAction();
}

async function cancelRawSupplyTask(taskId) {
  if (!rawSupplyCan("mes_raw_transfer_cancel")) throw new Error("Нет права mes_raw_transfer_cancel");
  await rawSupplyFetch(`/api/mes/raw-transfer-tasks/${taskId}/cancel`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ reason: "Отмена из админки снабжения", cancelled_by: rawSupplyUser() }),
  });
  await afterRawSupplyTaskAction();
}

async function afterRawSupplyTaskAction() {
  await Promise.all([
    rawSupplyState.selectedOrder ? loadSelectedRawSupply() : Promise.resolve(),
    loadRawSupplyTasks(Boolean(rawSupplyState.selectedOrder)),
  ]);
}

function renderRawSupplyOrders() {
  const tbody = rawSupplyEl("rawSupplyOrderRows");
  tbody.innerHTML = "";
  for (const order of rawSupplyState.orders) {
    const tr = document.createElement("tr");
    if (rawSupplyState.selectedOrder?.production_order_id === order.production_order_id) tr.classList.add("selected");
    tr.innerHTML = `
      <td>${order.production_order_id ?? ""}</td>
      <td>${escapeRawSupply(order.order_no ?? "")}</td>
      <td>${escapeRawSupply(order.target_articul ?? "")}</td>
      <td>${escapeRawSupply(order.status ?? "")}</td>
      <td>${formatRawSupplyNumber(order.planned_qty)} ${escapeRawSupply(order.unit_code ?? "")}</td>
      <td>${formatRawSupplyNumber(order.fact_qty)}</td>
    `;
    tr.addEventListener("click", () => loadRawSupplyOrder(order.production_order_id).catch(showRawSupplyError));
    tbody.appendChild(tr);
  }
}

function renderRawSupply(supply) {
  renderRawSupplyDemands(supply?.demands || []);
  renderRawSupplyCandidates(supply?.candidates || []);
  renderRawSupplyReservations(supply?.reservations || []);
  renderRawSupplyTasks(supply?.tasks || []);
  renderRawSupplyShortages(supply?.shortages || []);
  rawSupplyEl("rawSupplyKpiDemand").textContent = String(supply?.demands?.length || 0);
  rawSupplyEl("rawSupplyKpiCandidate").textContent = String(supply?.candidates?.length || 0);
  rawSupplyEl("rawSupplyKpiShortage").textContent = String((supply?.shortages || []).filter((row) => row.status === "OPEN").length);
  rawSupplyEl("rawSupplyKpiTask").textContent = String(supply?.tasks?.length || 0);
}

function renderRawSupplyDemands(rows) {
  const tbody = rawSupplyEl("rawSupplyDemandRows");
  tbody.innerHTML = "";
  for (const row of rows) {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td>${escapeRawSupply(row.raw_articul ?? "")}</td>
      <td>${formatRawSupplyNumber(row.required_qty)} ${escapeRawSupply(row.unit_code ?? "")}</td>
      <td>${formatRawSupplyNumber(row.issued_qty)}</td>
      <td>${formatRawSupplyNumber(row.open_qty)}</td>
      <td>${row.soft_reservation_id ?? ""}</td>
      <td>${escapeRawSupply(row.status ?? "")}</td>
    `;
    tbody.appendChild(tr);
  }
}

function renderRawSupplyCandidates(rows) {
  const tbody = rawSupplyEl("rawSupplyCandidateRows");
  tbody.innerHTML = "";
  for (const row of rows) {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td>${escapeRawSupply(row.raw_articul ?? "")}</td>
      <td>${escapeRawSupply(row.uid_pallet ?? "")}</td>
      <td>${escapeRawSupply(row.from_ware_id ?? "")}</td>
      <td>${escapeRawSupply(row.from_cell ?? "")}</td>
      <td>${formatRawSupplyNumber(row.available_qty)}</td>
      <td>${formatRawSupplyNumber(row.suggested_qty)}</td>
      <td>${escapeRawSupply(row.quality_status ?? "")}</td>
    `;
    tbody.appendChild(tr);
  }
}

function renderRawSupplyShortages(rows) {
  const tbody = rawSupplyEl("rawSupplyShortageRows");
  tbody.innerHTML = "";
  for (const row of rows) {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td>${escapeRawSupply(row.order_no ?? row.production_order_id ?? "")}</td>
      <td>${escapeRawSupply(row.raw_articul ?? "")}</td>
      <td>${formatRawSupplyNumber(row.required_qty)}</td>
      <td>${formatRawSupplyNumber(row.available_qty)}</td>
      <td>${formatRawSupplyNumber(row.shortage_qty)}</td>
      <td>${escapeRawSupply(row.status ?? "")}</td>
    `;
    if (row.production_order_id) {
      tr.addEventListener("click", () => loadRawSupplyOrder(row.production_order_id).catch(showRawSupplyError));
    }
    tbody.appendChild(tr);
  }
}

function renderRawSupplyReservations(rows) {
  const tbody = rawSupplyEl("rawSupplyReservationRows");
  tbody.innerHTML = "";
  for (const row of rows) {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td>${row.reservation_id ?? ""}</td>
      <td>${escapeRawSupply(row.reservation_kind ?? "")}</td>
      <td>${escapeRawSupply(row.articul ?? "")}</td>
      <td>${formatRawSupplyNumber(row.qty)} ${escapeRawSupply(row.unit_code ?? "")}</td>
      <td>${escapeRawSupply(row.ware_id ?? "")}</td>
      <td>${escapeRawSupply(row.cell ?? "")}</td>
      <td>${escapeRawSupply(row.uid_pallet ?? "")}</td>
      <td>${escapeRawSupply(row.status ?? "")}</td>
    `;
    tbody.appendChild(tr);
  }
}

function renderRawSupplyTasks(rows) {
  const tbody = rawSupplyEl("rawSupplyTaskRows");
  tbody.innerHTML = "";
  for (const task of rows) {
    const canConfirm = ["PLANNED", "IN_PROGRESS"].includes(task.task_status) && rawSupplyCan("mes_raw_transfer_confirm");
    const canCancel = !["DONE", "CANCELLED"].includes(task.task_status) && rawSupplyCan("mes_raw_transfer_cancel");
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td>${task.task_id ?? ""}</td>
      <td>${task.production_order_id ?? ""}</td>
      <td>${escapeRawSupply(task.raw_articul ?? "")}</td>
      <td>${escapeRawSupply(task.uid_pallet ?? "")}</td>
      <td>${escapeRawSupply(task.from_cell ?? "")}</td>
      <td>${escapeRawSupply(task.to_cell ?? "")}</td>
      <td>${formatRawSupplyNumber(task.task_qty)} ${escapeRawSupply(task.unit_code ?? "")}</td>
      <td>${escapeRawSupply(task.task_status ?? "")}</td>
      <td>
        ${canConfirm ? `<button type="button" data-action="confirm" data-task-id="${task.task_id}">Принять</button>` : ""}
        ${canCancel ? `<button type="button" data-action="cancel" data-task-id="${task.task_id}">Отменить</button>` : ""}
      </td>
    `;
    tr.querySelector("[data-action='confirm']")?.addEventListener("click", () => confirmRawSupplyTask(task.task_id).catch(showRawSupplyError));
    tr.querySelector("[data-action='cancel']")?.addEventListener("click", () => cancelRawSupplyTask(task.task_id).catch(showRawSupplyError));
    tbody.appendChild(tr);
  }
}

function showRawSupplyError(error) {
  console.error(error);
  rawSupplyEl("rawSupplyOrderStatusText").textContent = error.message || String(error);
}

function escapeRawSupply(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;");
}

function formatRawSupplyNumber(value) {
  if (value === null || value === undefined || value === "") return "";
  const number = Number(value);
  if (!Number.isFinite(number)) return escapeRawSupply(value);
  return number.toLocaleString("ru-RU", { maximumFractionDigits: 3 });
}

function initRawSupplyPage() {
  if (!rawSupplyEl("rawSupplyRefresh")) return;
  if (window.wmsAdminAuth && !window.wmsAdminAuth.hasPermission("mes_raw_supply_view")) return;
  rawSupplyEl("rawSupplyRefresh").addEventListener("click", () => {
    Promise.all([loadRawSupplyOrders(), loadRawSupplyTasks(false), loadRawSupplyShortages(false)]).catch(showRawSupplyError);
  });
  rawSupplyEl("rawSupplyLoadOrders").addEventListener("click", () => loadRawSupplyOrders().catch(showRawSupplyError));
  rawSupplyEl("rawSupplyLoadTasks").addEventListener("click", () => loadRawSupplyTasks(Boolean(rawSupplyState.selectedOrder)).catch(showRawSupplyError));
  rawSupplyEl("rawSupplyLoadShortages").addEventListener("click", () => loadRawSupplyShortages(Boolean(rawSupplyState.selectedOrder)).catch(showRawSupplyError));
  rawSupplyEl("rawSupplyCalculate").addEventListener("click", () => calculateRawSupply().catch(showRawSupplyError));
  rawSupplyEl("rawSupplyRelease").addEventListener("click", () => releaseRawSupply().catch(showRawSupplyError));
  rawSupplyEl("rawSupplySearch").addEventListener("keydown", (event) => {
    if (event.key === "Enter") loadRawSupplyOrders().catch(showRawSupplyError);
  });
  Promise.all([loadRawSupplyOrders(), loadRawSupplyTasks(false), loadRawSupplyShortages(false)]).catch(showRawSupplyError);
}

document.addEventListener("DOMContentLoaded", initRawSupplyPage);
