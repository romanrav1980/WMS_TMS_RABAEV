const warehouseSyncState = {
  allRows: [],
  rows: [],
  selected: null,
  preset: "attention",
  task: null,
};

const syncEl = (id) => document.getElementById(id);

const SYNC_SOURCE_LABELS = {
  WAVE: "Волна",
  MES_RAW_SUPPLY: "Сырье в производство",
  MES_COMPLETION: "Выпуск ГП",
  PICKING: "Комплектация",
};

const SYNC_SCENARIOS = {
  "MES_RAW_SUPPLY:RAW_TO_PRODUCTION:PRODUCTION_ORDER": {
    title: "Сырье в производство",
    checks: [
      "Проверить связанную RRL_MES_RAW_TRANSFER_TASK по SOURCE_TASK_ID.",
      "Если есть residual warehouse task, MES-задача должна оставаться IN_PROGRESS.",
      "Сравнить FACT_QTY и плановое TASK_QTY до retry.",
      "Проверить hard reservation: после финального закрытия она должна стать CONSUMED.",
    ],
    retry: "Retry безопасен после исправления данных сырьевой задачи; handler не должен создавать дубль при SYNCED.",
  },
  "MES_COMPLETION:FG_TO_STORAGE:PRODUCTION_ORDER": {
    title: "Размещение готовой продукции",
    checks: [
      "Проверить RRL_MES_MOVEMENT по SOURCE_MOVEMENT_ID.",
      "Movement должен быть FG_PALLET_RELEASE и паллет/SSCC должен совпадать с warehouse task.",
      "Если STATUS уже APPLIED_TO_WMS, TARGET_LOCATION обязан совпадать с TO_CELL.",
      "Если movement применен в другую ячейку, сначала оформить ручную коррекцию, затем retry.",
    ],
    retry: "Retry опасен при расхождении ячеек после APPLIED_TO_WMS: без коррекции он должен оставаться ERROR.",
  },
  "WAVE:REPLENISHMENT:PICK_WAVE": {
    title: "Пополнение ячейки отбора под волну",
    checks: [
      "Проверить RRL_PICK_WAVE_REPLENISH_TASK по SOURCE_TASK_ID.",
      "Если есть residual warehouse task, replenishment task не должен считаться полностью закрытым.",
      "Проверить статус волны и готовность pick face.",
      "Убедиться, что нет дублей warehouse task по той же строке пополнения.",
    ],
    retry: "Retry безопасен после восстановления строки пополнения волны или закрытия residual task.",
  },
};

function syncApiBase() {
  return (window.wmsAdminAuth?.state?.apiBase || "http://127.0.0.1:8088").replace(/\/$/, "");
}

function syncHeaders(extra = {}) {
  if (!window.wmsAdminAuth) return { ...extra };
  return window.wmsAdminAuth.headers(extra);
}

function syncCan(permission) {
  return window.wmsAdminAuth && window.wmsAdminAuth.hasPermission(permission);
}

function syncUser() {
  return window.wmsAdminAuth?.state?.user?.username || "admin";
}

async function syncFetch(path, options = {}) {
  const response = await fetch(`${syncApiBase()}${path}`, {
    ...options,
    headers: syncHeaders(options.headers || {}),
  });
  const text = await response.text();
  const body = text ? JSON.parse(text) : {};
  if (!response.ok) {
    const detail = body.detail?.message || body.detail || body.message || `HTTP ${response.status}`;
    throw new Error(typeof detail === "string" ? detail : JSON.stringify(detail));
  }
  return body;
}

function syncParams() {
  const params = new URLSearchParams();
  const status = syncEl("warehouseSyncStatus").value;
  const source = syncEl("warehouseSyncSource").value;
  const docType = syncEl("warehouseSyncDocType").value;
  const docId = syncEl("warehouseSyncDocId").value;
  if (status) params.set("status", status);
  if (source) params.set("task_source", source);
  if (docType) params.set("source_doc_type", docType);
  if (docId) params.set("source_doc_id", docId);
  params.set("limit", syncEl("warehouseSyncLimit").value || "150");
  return params;
}

async function loadWarehouseSync() {
  syncEl("warehouseSyncStatusText").textContent = "Загрузка...";
  warehouseSyncState.allRows = await syncFetch(`/api/warehouse-tasks/domain-sync?${syncParams().toString()}`);
  warehouseSyncState.rows = applyWarehouseSyncSearch(warehouseSyncState.allRows);
  if (warehouseSyncState.selected && !warehouseSyncState.rows.some((row) => row.sync_id === warehouseSyncState.selected.sync_id)) {
    warehouseSyncState.selected = null;
    warehouseSyncState.task = null;
  }
  renderWarehouseSyncRows();
  renderWarehouseSyncSummary();
  renderWarehouseSyncDetail();
}

function applyWarehouseSyncSearch(rows) {
  const query = syncEl("warehouseSyncSearch").value.trim().toLowerCase();
  if (!query) return rows;
  return rows.filter((row) => [
    row.sync_id,
    row.task_id,
    row.task_source,
    row.task_type,
    row.source_doc_type,
    row.source_doc_id,
    row.source_task_id,
    row.source_movement_id,
    row.sync_key,
    row.sync_status,
    row.last_error,
    row.updated_by,
  ].some((value) => String(value || "").toLowerCase().includes(query)));
}

function setWarehouseSyncPreset(preset) {
  warehouseSyncState.preset = preset;
  document.querySelectorAll("[data-sync-preset]").forEach((button) => {
    button.classList.toggle("active", button.dataset.syncPreset === preset);
  });
  if (preset === "errors") {
    syncEl("warehouseSyncStatus").value = "ERROR";
  } else if (preset === "pending") {
    syncEl("warehouseSyncStatus").value = "PENDING";
  } else if (preset === "synced") {
    syncEl("warehouseSyncStatus").value = "SYNCED";
  } else if (preset === "attention") {
    syncEl("warehouseSyncStatus").value = "";
  } else if (preset === "raw") {
    syncEl("warehouseSyncStatus").value = "";
    syncEl("warehouseSyncSource").value = "MES_RAW_SUPPLY";
    syncEl("warehouseSyncDocType").value = "PRODUCTION_ORDER";
  } else if (preset === "fg") {
    syncEl("warehouseSyncStatus").value = "";
    syncEl("warehouseSyncSource").value = "MES_COMPLETION";
    syncEl("warehouseSyncDocType").value = "PRODUCTION_ORDER";
  } else if (preset === "wave") {
    syncEl("warehouseSyncStatus").value = "";
    syncEl("warehouseSyncSource").value = "WAVE";
    syncEl("warehouseSyncDocType").value = "PICK_WAVE";
  } else {
    syncEl("warehouseSyncStatus").value = "";
    syncEl("warehouseSyncSource").value = "";
    syncEl("warehouseSyncDocType").value = "";
    syncEl("warehouseSyncDocId").value = "";
  }
  loadWarehouseSync().catch(showWarehouseSyncError);
}

function visibleSyncRows() {
  if (warehouseSyncState.preset !== "attention") return warehouseSyncState.rows;
  return warehouseSyncState.rows.filter((row) => ["ERROR", "RETRY_PENDING", "PENDING", "IN_PROGRESS"].includes(row.sync_status));
}

function renderWarehouseSyncRows() {
  const rows = visibleSyncRows();
  const html = rows.map((row) => {
    const selected = warehouseSyncState.selected?.sync_id === row.sync_id ? " class=\"selected\"" : "";
    return `<tr${selected} data-sync-id="${escapeSyncAttr(row.sync_id)}">`
      + `<td><b>#${escapeSyncHtml(row.sync_id)}</b><small>${escapeSyncHtml(row.sync_key || "-")}</small></td>`
      + `<td>#${escapeSyncHtml(row.task_id)}</td>`
      + `<td>${escapeSyncHtml(SYNC_SOURCE_LABELS[row.task_source] || row.task_source || "-")}<small>${escapeSyncHtml(row.task_type || "-")}</small></td>`
      + `<td>${escapeSyncHtml(sourceText(row))}</td>`
      + `<td><span class="task-badge ${syncStatusClass(row.sync_status)}">${escapeSyncHtml(row.sync_status)}</span></td>`
      + `<td>${escapeSyncHtml(row.sync_attempt ?? 0)}</td>`
      + `<td>${escapeSyncHtml(formatSyncTime(row.updated_at || row.created_at))}</td>`
      + `<td>${escapeSyncHtml(shortError(row.last_error))}</td>`
      + "</tr>";
  }).join("");
  syncEl("warehouseSyncRows").innerHTML = html || "<tr><td colspan=\"8\">Нет строк синхронизации</td></tr>";
  document.querySelectorAll("#warehouseSyncRows tr[data-sync-id]").forEach((row) => {
    row.addEventListener("click", () => selectWarehouseSync(Number(row.dataset.syncId)));
  });
}

function renderWarehouseSyncSummary() {
  const rows = warehouseSyncState.allRows;
  const errorCount = rows.filter((row) => row.sync_status === "ERROR").length;
  const retryCount = rows.filter((row) => row.sync_status === "RETRY_PENDING").length;
  const pendingCount = rows.filter((row) => ["PENDING", "IN_PROGRESS"].includes(row.sync_status)).length;
  const syncedCount = rows.filter((row) => row.sync_status === "SYNCED").length;
  syncEl("warehouseSyncKpiError").textContent = errorCount;
  syncEl("warehouseSyncKpiRetry").textContent = retryCount;
  syncEl("warehouseSyncKpiPending").textContent = pendingCount;
  syncEl("warehouseSyncKpiSynced").textContent = syncedCount;
  syncEl("warehouseSyncErrorBadge").textContent = errorCount;
  syncEl("warehouseSyncStatusText").textContent = `Строк: ${warehouseSyncState.rows.length}, требуют внимания: ${visibleSyncRows().length}`;
}

async function selectWarehouseSync(syncId) {
  warehouseSyncState.selected = warehouseSyncState.allRows.find((row) => Number(row.sync_id) === syncId) || null;
  warehouseSyncState.task = null;
  renderWarehouseSyncRows();
  renderWarehouseSyncDetail();
  if (warehouseSyncState.selected?.task_id) {
    try {
      warehouseSyncState.task = await syncFetch(`/api/warehouse-tasks/${warehouseSyncState.selected.task_id}`);
    } catch (error) {
      warehouseSyncState.task = { last_error: error.message };
    }
    renderWarehouseSyncDetail();
  }
}

function renderWarehouseSyncDetail() {
  const row = warehouseSyncState.selected;
  const task = warehouseSyncState.task;
  syncEl("warehouseSyncSelectionText").textContent = row ? `Выбран sync #${row.sync_id}` : "Sync не выбран";
  syncEl("warehouseSyncDetailStatus").textContent = row ? `${row.sync_status} / ${row.task_source || "-"}` : "Выберите строку sync";
  syncEl("warehouseSyncDetailId").textContent = row ? `#${row.sync_id}, попытка ${row.sync_attempt ?? 0}` : "-";
  syncEl("warehouseSyncDetailTask").textContent = row ? `#${row.task_id} ${row.task_type || ""}`.trim() : "-";
  syncEl("warehouseSyncDetailRoute").textContent = task ? `${task.from_cell || "-"} -> ${task.to_cell || "-"}` : "-";
  syncEl("warehouseSyncDetailDocument").textContent = row ? sourceText(row) : "-";
  syncEl("warehouseSyncDetailKey").textContent = row?.sync_key || "-";
  syncEl("warehouseSyncDetailTime").textContent = row ? `создано ${formatSyncTime(row.created_at)}, обновлено ${formatSyncTime(row.updated_at)}` : "-";
  syncEl("warehouseSyncDetailUser").textContent = row?.updated_by || task?.assigned_to || "-";
  syncEl("warehouseSyncDetailError").textContent = row?.last_error || task?.last_error || "-";
  renderScenarioGuidance(row, task);
}

async function retryWarehouseSync() {
  const row = warehouseSyncState.selected;
  if (!row) throw new Error("Выберите строку sync");
  if (!syncCan("warehouse_task_execute")) throw new Error("Нет права warehouse_task_execute");
  await syncFetch(`/api/warehouse-tasks/${row.task_id}/sync/retry`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ updated_by: syncUser() }),
  });
  await loadWarehouseSync();
  const updated = warehouseSyncState.allRows.find((item) => item.task_id === row.task_id);
  warehouseSyncState.selected = updated || null;
  renderWarehouseSyncDetail();
}

function openSelectedWarehouseTask() {
  const row = warehouseSyncState.selected;
  if (!row) {
    showWarehouseSyncError(new Error("Выберите строку sync"));
    return;
  }
  const url = `warehouse-tasks.html?task_id=${encodeURIComponent(row.task_id)}`;
  window.location.href = url;
}

function sourceText(row) {
  const parts = [];
  if (row.source_doc_type) parts.push(row.source_doc_type);
  if (row.source_doc_id) parts.push(`#${row.source_doc_id}`);
  if (row.source_task_id) parts.push(`task ${row.source_task_id}`);
  if (row.source_movement_id) parts.push(`move ${row.source_movement_id}`);
  return parts.join(" ") || "-";
}

function scenarioKey(row) {
  if (!row) return "";
  return `${row.task_source || ""}:${row.task_type || ""}:${row.source_doc_type || ""}`;
}

function renderScenarioGuidance(row, task) {
  const scenario = SYNC_SCENARIOS[scenarioKey(row)];
  const title = syncEl("warehouseSyncScenarioTitle");
  const list = syncEl("warehouseSyncScenarioChecks");
  const risk = syncEl("warehouseSyncRetryRisk");
  const retryButton = syncEl("warehouseSyncRetry");
  if (!row || !scenario) {
    title.textContent = row ? "Нет сценарной подсказки" : "Сценарий не выбран";
    list.innerHTML = "";
    risk.textContent = row ? "Для этого типа sync пока нет отдельной инструкции." : "Выберите строку sync для оценки retry.";
    risk.className = "warehouse-sync-risk";
    retryButton.classList.remove("danger");
    retryButton.title = "";
    return;
  }
  title.textContent = scenario.title;
  list.innerHTML = scenario.checks.map((item) => `<li>${escapeSyncHtml(item)}</li>`).join("");
  const dangerous = isDangerousRetry(row, task);
  risk.textContent = dangerous ? `${scenario.retry} Требуется ручная проверка перед retry.` : scenario.retry;
  risk.className = `warehouse-sync-risk${dangerous ? " danger" : ""}`;
  retryButton.classList.toggle("danger", dangerous);
  retryButton.title = dangerous ? "Проверьте расхождение перед повтором" : "";
}

function isDangerousRetry(row, task) {
  if (!row || row.task_source !== "MES_COMPLETION" || row.task_type !== "FG_TO_STORAGE") return false;
  const errorText = String(row.last_error || task?.last_error || "").toLowerCase();
  return errorText.includes("already applied") || errorText.includes("target location") || errorText.includes("ячей");
}

function syncStatusClass(status) {
  if (status === "SYNCED") return "done";
  if (status === "ERROR") return "error";
  if (status === "IN_PROGRESS") return "progress";
  if (status === "RETRY_PENDING") return "assigned";
  return "planned";
}

function formatSyncTime(value) {
  if (!value) return "-";
  return String(value).replace("T", " ").slice(0, 19);
}

function shortError(value) {
  if (!value) return "-";
  const text = String(value);
  return text.length > 120 ? `${text.slice(0, 117)}...` : text;
}

function showWarehouseSyncError(error) {
  syncEl("warehouseSyncStatusText").textContent = error.message;
}

function escapeSyncHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;");
}

function escapeSyncAttr(value) {
  return escapeSyncHtml(value);
}

function initWarehouseSync() {
  syncEl("warehouseSyncRefresh").addEventListener("click", () => loadWarehouseSync().catch(showWarehouseSyncError));
  syncEl("warehouseSyncLoad").addEventListener("click", () => loadWarehouseSync().catch(showWarehouseSyncError));
  syncEl("warehouseSyncSearch").addEventListener("input", () => {
    warehouseSyncState.rows = applyWarehouseSyncSearch(warehouseSyncState.allRows);
    renderWarehouseSyncRows();
    renderWarehouseSyncSummary();
  });
  document.querySelectorAll("[data-sync-preset]").forEach((button) => {
    button.addEventListener("click", () => setWarehouseSyncPreset(button.dataset.syncPreset));
  });
  syncEl("warehouseSyncRetry").addEventListener("click", () => retryWarehouseSync().catch(showWarehouseSyncError));
  syncEl("warehouseSyncOpenTask").addEventListener("click", openSelectedWarehouseTask);
  loadWarehouseSync().catch(showWarehouseSyncError);
}

window.addEventListener("wms-admin-auth-ready", initWarehouseSync);
