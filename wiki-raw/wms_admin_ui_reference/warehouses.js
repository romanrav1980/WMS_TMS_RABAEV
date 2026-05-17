const warehouseState = {
  warehouses: [],
  selected: null,
};

const whEl = (id) => document.getElementById(id);

function whApiBase() {
  return whEl("warehouseBase").value.replace(/\/$/, "");
}

function whHeaders(extra = {}) {
  if (!window.wmsAdminAuth) return { ...extra };
  return window.wmsAdminAuth.headers(extra);
}

function whCan(permission) {
  return window.wmsAdminAuth && window.wmsAdminAuth.hasPermission(permission);
}

function whFilters() {
  const params = new URLSearchParams();
  if (whEl("warehouseRoleFilter").value) params.set("role", whEl("warehouseRoleFilter").value);
  if (whEl("warehouseMesFilter").value !== "") params.set("mes_enabled", whEl("warehouseMesFilter").value);
  params.set("limit", whEl("warehouseLimit").value || "200");
  return params;
}

async function loadWarehouses() {
  whEl("warehouseStatusText").textContent = "Загрузка...";
  const response = await fetch(`${whApiBase()}/api/admin/warehouses?${whFilters().toString()}`, {
    headers: whHeaders(),
  });
  if (!response.ok) throw new Error(`Warehouses HTTP ${response.status}`);
  const rows = await response.json();
  const search = whEl("warehouseSearch").value.trim().toLowerCase();
  warehouseState.warehouses = search
    ? rows.filter((row) => JSON.stringify(row).toLowerCase().includes(search))
    : rows;
  renderWarehouses();
  whEl("warehouseStatusText").textContent = `Складов: ${warehouseState.warehouses.length}`;
}

function renderWarehouses() {
  const tbody = whEl("warehouseRows");
  tbody.innerHTML = "";
  for (const warehouse of warehouseState.warehouses) {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td>${warehouse.id ?? ""}</td>
      <td>${escapeWh(warehouse.name ?? "")}</td>
      <td>${escapeWh(formatWarehouseRoles(warehouse))}</td>
      <td>${Number(warehouse.mes_enabled || 0) === 1 ? "Да" : "Нет"}</td>
      <td>${escapeWh(warehouse.default_receive_cell ?? "")}</td>
      <td>${escapeWh(warehouse.default_issue_cell ?? "")}</td>
      <td>${warehouse.cell_count ?? 0}</td>
      <td>${warehouse.pallet_count ?? 0}</td>
      <td>${warehouse.total_remain ?? 0}</td>
    `;
    tr.addEventListener("click", () => selectWarehouse(warehouse));
    tbody.appendChild(tr);
  }
}

function selectWarehouse(warehouse) {
  warehouseState.selected = warehouse;
  whEl("warehouseDetailStatus").textContent = `${warehouse.id} / ${warehouse.name}`;
  whEl("warehouseDetails").textContent = JSON.stringify(warehouse, null, 2);
  whEl("warehouseEditMes").value = String(Number(warehouse.mes_enabled || 0));
  whEl("warehouseFlagRaw").checked = Number(warehouse.flag_raw_material || 0) === 1;
  whEl("warehouseFlagProduction").checked = Number(warehouse.flag_production || 0) === 1;
  whEl("warehouseFlagBuffer").checked = Number(warehouse.flag_production_buffer || 0) === 1;
  whEl("warehouseFlagFg").checked = Number(warehouse.flag_finished_goods || 0) === 1;
  whEl("warehouseEditReceive").value = warehouse.default_receive_cell || "";
  whEl("warehouseEditIssue").value = warehouse.default_issue_cell || "";
  whEl("warehouseEditComment").value = warehouse.ware_comment || "";
}

async function saveWarehouse() {
  if (!warehouseState.selected) throw new Error("Выберите склад");
  if (!whCan("warehouse_settings_edit")) throw new Error("Нет права warehouse_settings_edit");
  const body = {
    flag_raw_material: whEl("warehouseFlagRaw").checked ? 1 : 0,
    flag_production: whEl("warehouseFlagProduction").checked ? 1 : 0,
    flag_production_buffer: whEl("warehouseFlagBuffer").checked ? 1 : 0,
    flag_finished_goods: whEl("warehouseFlagFg").checked ? 1 : 0,
    mes_enabled: Number(whEl("warehouseEditMes").value),
    default_receive_cell: whEl("warehouseEditReceive").value.trim() || null,
    default_issue_cell: whEl("warehouseEditIssue").value.trim() || null,
    ware_comment: whEl("warehouseEditComment").value.trim() || null,
  };
  const response = await fetch(`${whApiBase()}/api/admin/warehouses/${warehouseState.selected.id}`, {
    method: "PATCH",
    headers: whHeaders({ "Content-Type": "application/json" }),
    body: JSON.stringify(body),
  });
  const result = await response.json();
  if (!response.ok) throw new Error(result.detail || `Save warehouse HTTP ${response.status}`);
  await loadWarehouses();
  const updated = warehouseState.warehouses.find((row) => row.id === warehouseState.selected.id);
  if (updated) selectWarehouse(updated);
}

function initWarehouses() {
  if (!whEl("warehouseRefresh")) return;
  if (window.wmsAdminAuth && !window.wmsAdminAuth.hasPermission("warehouse_settings_view")) return;
  whEl("warehouseRefresh").addEventListener("click", () => loadWarehouses().catch(showWarehouseError));
  whEl("warehouseLoad").addEventListener("click", () => loadWarehouses().catch(showWarehouseError));
  whEl("warehouseSave").addEventListener("click", () => saveWarehouse().catch(showWarehouseError));
  for (const id of ["warehouseRoleFilter", "warehouseMesFilter", "warehouseLimit"]) {
    whEl(id).addEventListener("change", () => loadWarehouses().catch(showWarehouseError));
  }
  whEl("warehouseSearch").addEventListener("input", () => renderWarehouses());
  loadWarehouses().catch(showWarehouseError);
}

function showWarehouseError(error) {
  whEl("warehouseStatusText").textContent = `Ошибка: ${error.message}`;
  whEl("warehouseDetailStatus").textContent = `Ошибка: ${error.message}`;
}

function escapeWh(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;");
}

function formatWarehouseRoles(warehouse) {
  const roles = [];
  if (Number(warehouse.flag_raw_material || 0) === 1) roles.push("RAW");
  if (Number(warehouse.flag_production || 0) === 1) roles.push("PROD");
  if (Number(warehouse.flag_production_buffer || 0) === 1) roles.push("BUFFER");
  if (Number(warehouse.flag_finished_goods || 0) === 1) roles.push("FG");
  return roles.length ? roles.join(", ") : "GENERAL";
}

if (window.wmsAdminAuth && window.wmsAdminAuth.state.user) {
  initWarehouses();
} else {
  window.addEventListener("wms-admin-auth-ready", initWarehouses, { once: true });
}
