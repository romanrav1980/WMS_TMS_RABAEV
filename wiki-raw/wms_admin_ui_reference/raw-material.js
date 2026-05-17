const rawState = {
  skus: [],
  warehouses: [],
  selectedSku: null,
  selectedWarehouses: new Set(),
};

const rawEl = (id) => document.getElementById(id);

function rawApiBase() {
  return (window.wmsAdminAuth?.state?.apiBase || "http://127.0.0.1:8088").replace(/\/$/, "");
}

function rawHeaders(extra = {}) {
  if (!window.wmsAdminAuth) return { ...extra };
  return window.wmsAdminAuth.headers(extra);
}

function rawCan(permission) {
  return window.wmsAdminAuth && window.wmsAdminAuth.hasPermission(permission);
}

function rawUser() {
  return window.wmsAdminAuth?.state?.user?.username || "admin";
}

function rawSkuParams() {
  const params = new URLSearchParams();
  const search = rawEl("rawSkuSearch").value.trim() || rawEl("rawSearchTop").value.trim();
  if (search) params.set("search", search);
  if (rawEl("rawOnlyWithStock").value) params.set("only_with_stock", rawEl("rawOnlyWithStock").value);
  params.set("limit", rawEl("rawSkuLimit").value || "200");
  return params;
}

function rawRemainParams() {
  const params = new URLSearchParams();
  const articul = rawEl("rawRemainArticul").value.trim();
  const cell = rawEl("rawRemainCell").value.trim();
  const batch = rawEl("rawRemainBatch").value.trim();
  const quality = rawEl("rawRemainQuality").value;
  const selectedWarehouses = Array.from(rawState.selectedWarehouses);
  if (articul) params.set("articul", articul);
  if (cell) params.set("cell", cell);
  if (batch) params.set("batch_no", batch);
  if (quality) params.set("quality_status", quality);
  if (selectedWarehouses.length === 1) params.set("ware_id", selectedWarehouses[0]);
  if (selectedWarehouses.length > 1) params.set("ware_ids", selectedWarehouses.join(","));
  params.set("only_available", rawEl("rawRemainAvailable").value || "1");
  params.set("limit", rawEl("rawRemainLimit").value || "500");
  return params;
}

async function loadRawSkus() {
  rawEl("rawSkuStatus").textContent = "Загрузка...";
  const response = await fetch(`${rawApiBase()}/api/raw-material/skus?${rawSkuParams().toString()}`, {
    headers: rawHeaders(),
  });
  if (!response.ok) throw new Error(`SKU HTTP ${response.status}`);
  rawState.skus = await response.json();
  renderRawSkus();
  rawEl("rawSkuStatus").textContent = `SKU: ${rawState.skus.length}`;
}

async function loadRawWarehouses() {
  rawEl("rawWarehouseStatus").textContent = "Загрузка...";
  const response = await fetch(`${rawApiBase()}/api/raw-material/warehouses?limit=200`, {
    headers: rawHeaders(),
  });
  if (!response.ok) throw new Error(`Warehouses HTTP ${response.status}`);
  rawState.warehouses = await response.json();
  if (rawState.selectedWarehouses.size === 0) {
    for (const warehouse of rawState.warehouses) rawState.selectedWarehouses.add(String(warehouse.id));
  }
  renderRawWarehouses();
  rawEl("rawWarehouseStatus").textContent = `Складов: ${rawState.warehouses.length}`;
}

async function loadRawRemains() {
  if (!rawCan("raw_material_stock_view")) {
    rawEl("rawRemainStatus").textContent = "Нет права просмотра остатков";
    return;
  }
  rawEl("rawRemainStatus").textContent = "Загрузка...";
  const params = rawRemainParams();
  const response = await fetch(`${rawApiBase()}/api/raw-material/remains?${params.toString()}`, {
    headers: rawHeaders(),
  });
  if (!response.ok) throw new Error(`Remains HTTP ${response.status}`);
  const rows = await response.json();
  renderRawRemains(rows);
  rawEl("rawRemainStatus").textContent = `Строк остатков: ${rows.length}`;
}

async function refreshRawPage() {
  await Promise.all([loadRawSkus(), loadRawWarehouses()]);
  await loadRawRemains();
}

function renderRawSkus() {
  const tbody = rawEl("rawSkuRows");
  tbody.innerHTML = "";
  for (const sku of rawState.skus) {
    const tr = document.createElement("tr");
    if (rawState.selectedSku?.articul === sku.articul) tr.classList.add("selected");
    tr.innerHTML = `
      <td>${escapeRaw(sku.articul ?? "")}</td>
      <td>${escapeRaw(sku.name ?? "")}</td>
      <td>${escapeRaw(sku.raw_group ?? "")}</td>
      <td>${formatNumber(sku.total_remain)}</td>
      <td>${formatNumber(sku.pallet_count)}</td>
    `;
    tr.addEventListener("click", () => selectRawSku(sku));
    tbody.appendChild(tr);
  }
}

function renderRawWarehouses() {
  const tbody = rawEl("rawWarehouseRows");
  tbody.innerHTML = "";
  for (const warehouse of rawState.warehouses) {
    const id = String(warehouse.id);
    const tr = document.createElement("tr");
    if (rawState.selectedWarehouses.has(id)) tr.classList.add("selected");
    tr.innerHTML = `
      <td><input type="checkbox" ${rawState.selectedWarehouses.has(id) ? "checked" : ""} /></td>
      <td>${escapeRaw(id)}</td>
      <td>${escapeRaw(warehouse.name ?? "")}</td>
      <td>${formatNumber(warehouse.total_remain)}</td>
      <td>${formatNumber(warehouse.sku_count)}</td>
    `;
    tr.addEventListener("click", (event) => {
      event.preventDefault();
      toggleRawWarehouse(id);
    });
    tbody.appendChild(tr);
  }
}

function renderRawRemains(rows) {
  const tbody = rawEl("rawRemainRows");
  tbody.innerHTML = "";
  for (const row of rows) {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td>${escapeRaw(row.ware_name ?? row.ware_id ?? "")}</td>
      <td>${escapeRaw(row.cell ?? "")}</td>
      <td>${escapeRaw(row.uid_pallet ?? "")}</td>
      <td>${escapeRaw(row.sscc ?? "")}</td>
      <td>${escapeRaw(row.articul ?? "")}</td>
      <td>${escapeRaw(row.articul_name ?? "")}</td>
      <td>${escapeRaw(row.raw_batch_no ?? "")}</td>
      <td>${escapeRaw(row.mercury_vsd_uuid ?? "")}</td>
      <td>${formatDate(row.expiry_date)}</td>
      <td>${formatNumber(row.qty)}</td>
      <td>${formatNumber(row.reserved_qty)}</td>
      <td>${formatNumber(row.available_qty)}</td>
      <td>${escapeRaw(row.quality_status ?? "")}</td>
    `;
    tbody.appendChild(tr);
  }
}

function selectRawSku(sku) {
  rawState.selectedSku = sku;
  rawEl("rawSkuDetail").textContent = `${sku.articul} / ${sku.name || ""}`;
  rawEl("rawRemainArticul").value = sku.articul || "";
  rawEl("rawEditIsRaw").value = String(Number(sku.is_raw_material ?? 1));
  rawEl("rawEditGroup").value = sku.raw_group || "";
  rawEl("rawEditMercury").value = String(Number(sku.mercury_required ?? 0));
  rawEl("rawEditLot").value = String(Number(sku.lot_required ?? 1));
  rawEl("rawEditExpiry").value = String(Number(sku.expiry_required ?? 1));
  rawEl("rawEditMinQty").value = sku.min_stock_qty ?? "";
  rawEl("rawEditTargetQty").value = sku.target_stock_qty ?? "";
  rawEl("rawEditComment").value = sku.technologist_comment || "";
  renderRawSkus();
  loadRawRemains().catch(showRawError);
}

function toggleRawWarehouse(id) {
  if (rawState.selectedWarehouses.has(id)) {
    rawState.selectedWarehouses.delete(id);
  } else {
    rawState.selectedWarehouses.add(id);
  }
  renderRawWarehouses();
  loadRawRemains().catch(showRawError);
}

async function saveRawSku() {
  if (!rawState.selectedSku) throw new Error("Выберите сырье");
  if (!rawCan("raw_material_edit")) throw new Error("Нет права редактирования сырья");
  const body = {
    is_raw_material: Number(rawEl("rawEditIsRaw").value),
    raw_group: rawEl("rawEditGroup").value.trim() || null,
    mercury_required: Number(rawEl("rawEditMercury").value),
    lot_required: Number(rawEl("rawEditLot").value),
    expiry_required: Number(rawEl("rawEditExpiry").value),
    min_stock_qty: rawEl("rawEditMinQty").value ? Number(rawEl("rawEditMinQty").value) : null,
    target_stock_qty: rawEl("rawEditTargetQty").value ? Number(rawEl("rawEditTargetQty").value) : null,
    technologist_comment: rawEl("rawEditComment").value.trim() || null,
    active: 1,
    updated_by: rawUser(),
  };
  const response = await fetch(`${rawApiBase()}/api/raw-material/skus/${encodeURIComponent(rawState.selectedSku.articul)}`, {
    method: "PATCH",
    headers: rawHeaders({ "Content-Type": "application/json" }),
    body: JSON.stringify(body),
  });
  const result = await response.json();
  if (!response.ok) throw new Error(result.detail || `Save SKU HTTP ${response.status}`);
  await loadRawSkus();
  const updated = rawState.skus.find((sku) => sku.articul === rawState.selectedSku.articul);
  if (updated) selectRawSku(updated);
}

function initRawMaterial() {
  if (!rawEl("rawRefresh")) return;
  if (window.wmsAdminAuth && !window.wmsAdminAuth.hasPermission("raw_material_view")) return;

  rawEl("rawRefresh").addEventListener("click", () => refreshRawPage().catch(showRawError));
  rawEl("rawLoadSkus").addEventListener("click", () => loadRawSkus().catch(showRawError));
  rawEl("rawLoadRemains").addEventListener("click", () => loadRawRemains().catch(showRawError));
  rawEl("rawSaveSku").addEventListener("click", () => saveRawSku().catch(showRawError));
  rawEl("rawSearchTop").addEventListener("input", () => loadRawSkus().catch(showRawError));
  for (const id of ["rawOnlyWithStock", "rawSkuLimit"]) {
    rawEl(id).addEventListener("change", () => loadRawSkus().catch(showRawError));
  }
  for (const id of ["rawRemainQuality", "rawRemainAvailable", "rawRemainLimit"]) {
    rawEl(id).addEventListener("change", () => loadRawRemains().catch(showRawError));
  }
  for (const id of ["rawRemainArticul", "rawRemainCell", "rawRemainBatch"]) {
    rawEl(id).addEventListener("keydown", (event) => {
      if (event.key === "Enter") loadRawRemains().catch(showRawError);
    });
  }
  refreshRawPage().catch(showRawError);
}

function showRawError(error) {
  const message = `Ошибка: ${error.message}`;
  rawEl("rawSkuStatus").textContent = message;
  rawEl("rawWarehouseStatus").textContent = message;
  rawEl("rawRemainStatus").textContent = message;
}

function escapeRaw(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;");
}

function formatNumber(value) {
  if (value === null || value === undefined || value === "") return "";
  const number = Number(value);
  if (!Number.isFinite(number)) return escapeRaw(value);
  return new Intl.NumberFormat("ru-RU", { maximumFractionDigits: 3 }).format(number);
}

function formatDate(value) {
  if (!value) return "";
  return String(value).slice(0, 10);
}

if (window.wmsAdminAuth && window.wmsAdminAuth.state.user) {
  initRawMaterial();
} else {
  window.addEventListener("wms-admin-auth-ready", initRawMaterial, { once: true });
}
