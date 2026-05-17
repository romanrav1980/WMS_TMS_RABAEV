const fgState = {
  skus: [],
  warehouses: [],
  selectedSku: null,
  selectedWarehouses: new Set(),
};

const fgEl = (id) => document.getElementById(id);

function fgApiBase() {
  return (window.wmsAdminAuth?.state?.apiBase || "http://127.0.0.1:8088").replace(/\/$/, "");
}

function fgHeaders(extra = {}) {
  if (!window.wmsAdminAuth) return { ...extra };
  return window.wmsAdminAuth.headers(extra);
}

function fgCan(permission) {
  return window.wmsAdminAuth && window.wmsAdminAuth.hasPermission(permission);
}

function fgUser() {
  return window.wmsAdminAuth?.state?.user?.username || "admin";
}

function fgSkuParams() {
  const params = new URLSearchParams();
  const search = fgEl("fgSkuSearch").value.trim() || fgEl("fgSearchTop").value.trim();
  if (search) params.set("search", search);
  if (fgEl("fgOnlyWithStock").value) params.set("only_with_stock", fgEl("fgOnlyWithStock").value);
  params.set("limit", fgEl("fgSkuLimit").value || "200");
  return params;
}

function fgBatchParams() {
  const params = new URLSearchParams();
  if (fgEl("fgBatchArticul").value.trim()) params.set("articul", fgEl("fgBatchArticul").value.trim());
  if (fgEl("fgBatchNo").value.trim()) params.set("batch_no", fgEl("fgBatchNo").value.trim());
  if (fgEl("fgBatchQuality").value) params.set("quality_status", fgEl("fgBatchQuality").value);
  params.set("limit", fgEl("fgBatchLimit").value || "200");
  return params;
}

function fgRemainParams() {
  const params = new URLSearchParams();
  const selectedWarehouses = Array.from(fgState.selectedWarehouses);
  if (fgEl("fgRemainArticul").value.trim()) params.set("articul", fgEl("fgRemainArticul").value.trim());
  if (fgEl("fgRemainBatch").value.trim()) params.set("prod_batch_no", fgEl("fgRemainBatch").value.trim());
  if (fgEl("fgRemainCell").value.trim()) params.set("cell", fgEl("fgRemainCell").value.trim());
  if (fgEl("fgRemainQuality").value) params.set("quality_status", fgEl("fgRemainQuality").value);
  if (selectedWarehouses.length === 1) params.set("ware_id", selectedWarehouses[0]);
  if (selectedWarehouses.length > 1) params.set("ware_ids", selectedWarehouses.join(","));
  params.set("only_available", fgEl("fgRemainAvailable").value || "1");
  params.set("limit", fgEl("fgRemainLimit").value || "500");
  return params;
}

async function loadFgSkus() {
  fgEl("fgSkuStatus").textContent = "Загрузка...";
  const response = await fetch(`${fgApiBase()}/api/finished-goods/skus?${fgSkuParams().toString()}`, {
    headers: fgHeaders(),
  });
  if (!response.ok) throw new Error(`SKU HTTP ${response.status}`);
  fgState.skus = await response.json();
  renderFgSkus();
  fgEl("fgSkuStatus").textContent = `SKU: ${fgState.skus.length}`;
}

async function loadFgWarehouses() {
  fgEl("fgWarehouseStatus").textContent = "Загрузка...";
  const response = await fetch(`${fgApiBase()}/api/finished-goods/warehouses?limit=200`, {
    headers: fgHeaders(),
  });
  if (!response.ok) throw new Error(`Warehouses HTTP ${response.status}`);
  fgState.warehouses = await response.json();
  if (fgState.selectedWarehouses.size === 0) {
    for (const warehouse of fgState.warehouses) fgState.selectedWarehouses.add(String(warehouse.id));
  }
  renderFgWarehouses();
  fgEl("fgWarehouseStatus").textContent = `Складов: ${fgState.warehouses.length}`;
}

async function loadFgBatches() {
  if (!fgCan("finished_goods_batch_view")) {
    fgEl("fgBatchStatus").textContent = "Нет права просмотра партий";
    return;
  }
  fgEl("fgBatchStatus").textContent = "Загрузка...";
  const response = await fetch(`${fgApiBase()}/api/finished-goods/batches?${fgBatchParams().toString()}`, {
    headers: fgHeaders(),
  });
  if (!response.ok) throw new Error(`Batches HTTP ${response.status}`);
  const rows = await response.json();
  renderFgBatches(rows);
  fgEl("fgBatchStatus").textContent = `Партий: ${rows.length}`;
}

async function loadFgRemains() {
  if (!fgCan("finished_goods_stock_view")) {
    fgEl("fgRemainStatus").textContent = "Нет права просмотра остатков";
    return;
  }
  fgEl("fgRemainStatus").textContent = "Загрузка...";
  const response = await fetch(`${fgApiBase()}/api/finished-goods/remains?${fgRemainParams().toString()}`, {
    headers: fgHeaders(),
  });
  if (!response.ok) throw new Error(`Remains HTTP ${response.status}`);
  const rows = await response.json();
  renderFgRemains(rows);
  fgEl("fgRemainStatus").textContent = `Строк остатков: ${rows.length}`;
}

async function refreshFgPage() {
  await Promise.all([loadFgSkus(), loadFgWarehouses()]);
  await Promise.all([loadFgBatches(), loadFgRemains()]);
}

function renderFgSkus() {
  const tbody = fgEl("fgSkuRows");
  tbody.innerHTML = "";
  for (const sku of fgState.skus) {
    const tr = document.createElement("tr");
    if (fgState.selectedSku?.articul === sku.articul) tr.classList.add("selected");
    tr.innerHTML = `
      <td>${escapeFg(sku.articul ?? "")}</td>
      <td>${escapeFg(sku.name ?? "")}</td>
      <td>${escapeFg(sku.gtin ?? "")}</td>
      <td>${Number(sku.crpt_required || 0) === 1 ? "Да" : "Нет"}</td>
      <td>${formatFgNumber(sku.total_remain)}</td>
      <td>${formatFgNumber(sku.pallet_count)}</td>
    `;
    tr.addEventListener("click", () => selectFgSku(sku));
    tbody.appendChild(tr);
  }
}

function renderFgWarehouses() {
  const tbody = fgEl("fgWarehouseRows");
  tbody.innerHTML = "";
  for (const warehouse of fgState.warehouses) {
    const id = String(warehouse.id);
    const tr = document.createElement("tr");
    if (fgState.selectedWarehouses.has(id)) tr.classList.add("selected");
    tr.innerHTML = `
      <td><input type="checkbox" ${fgState.selectedWarehouses.has(id) ? "checked" : ""} /></td>
      <td>${escapeFg(id)}</td>
      <td>${escapeFg(warehouse.name ?? "")}</td>
      <td>${escapeFg(warehouse.warehouse_role ?? "")}</td>
      <td>${formatFgNumber(warehouse.total_remain)}</td>
      <td>${formatFgNumber(warehouse.sku_count)}</td>
    `;
    tr.addEventListener("click", (event) => {
      event.preventDefault();
      toggleFgWarehouse(id);
    });
    tbody.appendChild(tr);
  }
}

function renderFgBatches(rows) {
  const tbody = fgEl("fgBatchRows");
  tbody.innerHTML = "";
  for (const row of rows) {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td>${escapeFg(row.prod_batch_id ?? "")}</td>
      <td>${escapeFg(row.prod_batch_no ?? "")}</td>
      <td>${escapeFg(row.articul ?? "")}</td>
      <td>${escapeFg(row.gtin ?? "")}</td>
      <td>${formatFgNumber(row.total_quantity)}</td>
      <td>${formatFgDate(row.expiry_date_to ?? row.expiry_date_from)}</td>
      <td>${escapeFg(row.quality_status ?? "")}</td>
      <td>${Number(row.is_planning_allowed || 0) === 1 ? "Да" : "Нет"}</td>
      <td>${escapeFg(row.crpt_status ?? "")}</td>
      <td>${formatFgNumber(row.pallet_count)}</td>
    `;
    tbody.appendChild(tr);
  }
}

function renderFgRemains(rows) {
  const tbody = fgEl("fgRemainRows");
  tbody.innerHTML = "";
  for (const row of rows) {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td>${escapeFg(row.ware_name ?? row.ware_id ?? "")}</td>
      <td>${escapeFg(row.cell ?? "")}</td>
      <td>${escapeFg(row.uid_pallet ?? "")}</td>
      <td>${escapeFg(row.sscc ?? "")}</td>
      <td>${escapeFg(row.articul ?? "")}</td>
      <td>${escapeFg(row.prod_batch_no ?? "")}</td>
      <td>${formatFgDate(row.expiry_date)}</td>
      <td>${formatFgNumber(row.qty)}</td>
      <td>${formatFgNumber(row.available_qty)}</td>
      <td>${escapeFg(row.quality_status ?? "")}</td>
      <td>${escapeFg(row.crpt_status ?? "")}</td>
      <td>${escapeFg(row.aggregation_status ?? "")}</td>
    `;
    tbody.appendChild(tr);
  }
}

function selectFgSku(sku) {
  fgState.selectedSku = sku;
  fgEl("fgSkuDetail").textContent = `${sku.articul} / ${sku.name || ""}`;
  fgEl("fgBatchArticul").value = sku.articul || "";
  fgEl("fgRemainArticul").value = sku.articul || "";
  fgEl("fgEditIsFinished").value = String(Number(sku.is_finished_goods ?? 1));
  fgEl("fgEditGroup").value = sku.product_group || "";
  fgEl("fgEditGtin").value = sku.gtin || "";
  fgEl("fgEditCrpt").value = String(Number(sku.crpt_required ?? 0));
  fgEl("fgEditAggregation").value = String(Number(sku.aggregation_required ?? 0));
  fgEl("fgEditSscc").value = String(Number(sku.sscc_required ?? 1));
  fgEl("fgEditLabel").value = String(Number(sku.pallet_label_required ?? 1));
  fgEl("fgEditQualityHold").value = String(Number(sku.quality_hold_required ?? 0));
  fgEl("fgEditCases").value = sku.default_pallet_case_qty ?? "";
  fgEl("fgEditComment").value = sku.technologist_comment || "";
  renderFgSkus();
  Promise.all([loadFgBatches(), loadFgRemains()]).catch(showFgError);
}

function toggleFgWarehouse(id) {
  if (fgState.selectedWarehouses.has(id)) {
    fgState.selectedWarehouses.delete(id);
  } else {
    fgState.selectedWarehouses.add(id);
  }
  renderFgWarehouses();
  loadFgRemains().catch(showFgError);
}

async function saveFgSku() {
  if (!fgState.selectedSku) throw new Error("Выберите готовую продукцию");
  if (!fgCan("finished_goods_edit")) throw new Error("Нет права редактирования готовой продукции");
  const body = {
    is_finished_goods: Number(fgEl("fgEditIsFinished").value),
    product_group: fgEl("fgEditGroup").value.trim() || null,
    gtin: fgEl("fgEditGtin").value.trim() || null,
    crpt_required: Number(fgEl("fgEditCrpt").value),
    aggregation_required: Number(fgEl("fgEditAggregation").value),
    sscc_required: Number(fgEl("fgEditSscc").value),
    pallet_label_required: Number(fgEl("fgEditLabel").value),
    quality_hold_required: Number(fgEl("fgEditQualityHold").value),
    default_pallet_case_qty: fgEl("fgEditCases").value ? Number(fgEl("fgEditCases").value) : null,
    technologist_comment: fgEl("fgEditComment").value.trim() || null,
    active: 1,
    updated_by: fgUser(),
  };
  const response = await fetch(`${fgApiBase()}/api/finished-goods/skus/${encodeURIComponent(fgState.selectedSku.articul)}`, {
    method: "PATCH",
    headers: fgHeaders({ "Content-Type": "application/json" }),
    body: JSON.stringify(body),
  });
  const result = await response.json();
  if (!response.ok) throw new Error(result.detail || `Save SKU HTTP ${response.status}`);
  await loadFgSkus();
  const updated = fgState.skus.find((sku) => sku.articul === fgState.selectedSku.articul);
  if (updated) selectFgSku(updated);
}

function initFinishedGoods() {
  if (!fgEl("fgRefresh")) return;
  if (window.wmsAdminAuth && !window.wmsAdminAuth.hasPermission("finished_goods_view")) return;
  fgEl("fgRefresh").addEventListener("click", () => refreshFgPage().catch(showFgError));
  fgEl("fgLoadSkus").addEventListener("click", () => loadFgSkus().catch(showFgError));
  fgEl("fgLoadBatches").addEventListener("click", () => loadFgBatches().catch(showFgError));
  fgEl("fgLoadRemains").addEventListener("click", () => loadFgRemains().catch(showFgError));
  fgEl("fgSaveSku").addEventListener("click", () => saveFgSku().catch(showFgError));
  fgEl("fgSearchTop").addEventListener("input", () => loadFgSkus().catch(showFgError));
  for (const id of ["fgOnlyWithStock", "fgSkuLimit"]) {
    fgEl(id).addEventListener("change", () => loadFgSkus().catch(showFgError));
  }
  for (const id of ["fgBatchQuality", "fgBatchLimit"]) {
    fgEl(id).addEventListener("change", () => loadFgBatches().catch(showFgError));
  }
  for (const id of ["fgRemainQuality", "fgRemainAvailable", "fgRemainLimit"]) {
    fgEl(id).addEventListener("change", () => loadFgRemains().catch(showFgError));
  }
  refreshFgPage().catch(showFgError);
}

function showFgError(error) {
  const message = `Ошибка: ${error.message}`;
  fgEl("fgSkuStatus").textContent = message;
  fgEl("fgWarehouseStatus").textContent = message;
  fgEl("fgBatchStatus").textContent = message;
  fgEl("fgRemainStatus").textContent = message;
}

function escapeFg(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;");
}

function formatFgNumber(value) {
  if (value === null || value === undefined || value === "") return "";
  const number = Number(value);
  if (!Number.isFinite(number)) return escapeFg(value);
  return new Intl.NumberFormat("ru-RU", { maximumFractionDigits: 3 }).format(number);
}

function formatFgDate(value) {
  if (!value) return "";
  return String(value).slice(0, 10);
}

if (window.wmsAdminAuth && window.wmsAdminAuth.state.user) {
  initFinishedGoods();
} else {
  window.addEventListener("wms-admin-auth-ready", initFinishedGoods, { once: true });
}
