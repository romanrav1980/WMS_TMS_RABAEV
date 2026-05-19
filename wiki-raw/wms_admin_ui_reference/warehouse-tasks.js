const warehouseTaskState = {
  allTasks: [],
  tasks: [],
  selectedTask: null,
  preset: "all",
  initialTaskId: null,
};

const warehouseTaskEl = (id) => document.getElementById(id);

const TASK_TYPE_LABELS = {
  RAW_TO_PRODUCTION: "Сырье в производство",
  FG_TO_STORAGE: "Готовая продукция",
  REPLENISHMENT: "Пополнение",
  PICKING_MOVE: "Комплектация",
  OTHER: "Другое",
};

const TASK_SOURCE_LABELS = {
  MES_RAW_SUPPLY: "Снабжение производства",
  MES_COMPLETION: "Выпуск",
  PICKING: "Комплектация",
  WAVE: "Волна",
  MANUAL: "Ручная",
};

function warehouseTaskApiBase() {
  return (window.wmsAdminAuth?.state?.apiBase || "http://127.0.0.1:8088").replace(/\/$/, "");
}

function warehouseTaskHeaders(extra = {}) {
  if (!window.wmsAdminAuth) return { ...extra };
  return window.wmsAdminAuth.headers(extra);
}

function warehouseTaskCan(permission) {
  return window.wmsAdminAuth && window.wmsAdminAuth.hasPermission(permission);
}

function warehouseTaskUser() {
  return window.wmsAdminAuth?.state?.user?.username || "admin";
}

async function warehouseTaskFetch(path, options = {}) {
  const response = await fetch(`${warehouseTaskApiBase()}${path}`, {
    ...options,
    headers: warehouseTaskHeaders(options.headers || {}),
  });
  const text = await response.text();
  const body = text ? JSON.parse(text) : {};
  if (!response.ok) {
    const detail = body.detail?.message || body.detail || body.message || `HTTP ${response.status}`;
    throw new Error(typeof detail === "string" ? detail : JSON.stringify(detail));
  }
  return body;
}

function warehouseTaskParams() {
  const params = new URLSearchParams();
  const status = warehouseTaskEl("warehouseTaskStatus").value;
  const type = warehouseTaskEl("warehouseTaskType").value;
  const source = warehouseTaskEl("warehouseTaskSource").value;
  const sourceDoc = warehouseTaskEl("warehouseTaskSourceDoc").value;
  const assignee = warehouseTaskEl("warehouseTaskAssignee").value.trim();
  if (status) {
    params.set("status", status);
  }
  if (type) params.set("task_type", type);
  if (source) params.set("task_source", source);
  if (sourceDoc) params.set("source_doc_id", sourceDoc);
  if (assignee) params.set("assigned_to", assignee);
  params.set("limit", warehouseTaskEl("warehouseTaskLimit").value || "150");
  return params;
}

async function loadWarehouseTasks() {
  warehouseTaskEl("warehouseTaskStatusText").textContent = "Загрузка...";
  warehouseTaskState.allTasks = await warehouseTaskFetch(`/api/warehouse-tasks?${warehouseTaskParams().toString()}`);
  warehouseTaskState.tasks = applySearch(warehouseTaskState.allTasks);
  if (warehouseTaskState.initialTaskId && !warehouseTaskState.selectedTask) {
    warehouseTaskState.selectedTask = warehouseTaskState.tasks.find((task) => Number(task.task_id) === warehouseTaskState.initialTaskId) || null;
  }
  if (warehouseTaskState.selectedTask && !warehouseTaskState.tasks.some((task) => task.task_id === warehouseTaskState.selectedTask.task_id)) {
    warehouseTaskState.selectedTask = null;
  }
  renderWarehouseTasks();
  renderWarehouseTaskSummary();
  renderWarehouseTaskDetail();
}

function applySearch(tasks) {
  const query = warehouseTaskEl("warehouseTaskSearch").value.trim().toLowerCase();
  if (!query) return tasks;
  return tasks.filter((task) => [
    task.uid_pallet,
    task.sscc,
    task.from_cell,
    task.to_cell,
    task.assigned_to,
    task.raw_articul,
    task.target_articul,
    task.source_doc_id,
    task.production_order_id,
  ].some((value) => String(value || "").toLowerCase().includes(query)));
}

function setWarehouseTaskPreset(preset) {
  warehouseTaskState.preset = preset;
  document.querySelectorAll("[data-task-preset]").forEach((button) => {
    button.classList.toggle("active", button.dataset.taskPreset === preset);
  });
  if (preset === "wave-pickface") {
    warehouseTaskEl("warehouseTaskType").value = "REPLENISHMENT";
    warehouseTaskEl("warehouseTaskSource").value = "WAVE";
  } else if (preset === "shipping-zone") {
    warehouseTaskEl("warehouseTaskType").value = "REPLENISHMENT";
    warehouseTaskEl("warehouseTaskSource").value = "WAVE";
  } else if (preset === "finished-goods") {
    warehouseTaskEl("warehouseTaskType").value = "FG_TO_STORAGE";
    warehouseTaskEl("warehouseTaskSource").value = "MES_COMPLETION";
  } else if (preset === "production-wave") {
    warehouseTaskEl("warehouseTaskType").value = "RAW_TO_PRODUCTION";
    warehouseTaskEl("warehouseTaskSource").value = "MES_RAW_SUPPLY";
  } else {
    warehouseTaskEl("warehouseTaskType").value = "";
    warehouseTaskEl("warehouseTaskSource").value = "";
  }
  loadWarehouseTasks().catch(showWarehouseTaskError);
}

function renderWarehouseTasks() {
  const rows = warehouseTaskState.tasks.map((task) => {
    const selected = warehouseTaskState.selectedTask?.task_id === task.task_id ? " class=\"selected\"" : "";
    return `<tr${selected} data-task-id="${escapeWarehouseTaskAttr(task.task_id)}">`
      + `<td>${escapeWarehouseTaskHtml(task.task_id)}</td>`
      + `<td><b>${escapeWarehouseTaskHtml(TASK_TYPE_LABELS[task.task_type] || task.task_type)}</b><small>${escapeWarehouseTaskHtml(classifyTask(task))}</small></td>`
      + `<td>${escapeWarehouseTaskHtml(TASK_SOURCE_LABELS[task.task_source] || task.task_source)}<small>${escapeWarehouseTaskHtml(sourceDocText(task))}</small></td>`
      + `<td>${escapeWarehouseTaskHtml(qtyModeText(task))}</td>`
      + `<td>${escapeWarehouseTaskHtml(task.uid_pallet || task.sscc || "-")}</td>`
      + `<td>${escapeWarehouseTaskHtml(task.from_cell || "-")}</td>`
      + `<td>${escapeWarehouseTaskHtml(task.to_cell || "-")}</td>`
      + `<td>${escapeWarehouseTaskHtml(formatTaskQty(task))}</td>`
      + `<td><span class="task-badge ${statusClass(task.status)}">${escapeWarehouseTaskHtml(task.status)}</span></td>`
      + `<td>${escapeWarehouseTaskHtml(task.assigned_to || "-")}</td>`
      + "</tr>";
  }).join("");
  warehouseTaskEl("warehouseTaskRows").innerHTML = rows || "<tr><td colspan=\"10\">Нет заданий</td></tr>";
  document.querySelectorAll("#warehouseTaskRows tr[data-task-id]").forEach((row) => {
    row.addEventListener("click", () => selectWarehouseTask(Number(row.dataset.taskId)));
  });
}

function renderWarehouseTaskSummary() {
  const tasks = warehouseTaskState.tasks;
  const activeCount = tasks.filter((task) => ["PLANNED", "ASSIGNED", "IN_PROGRESS", "ERROR"].includes(task.status)).length;
  warehouseTaskEl("warehouseTaskStatusText").textContent = `Заданий: ${tasks.length}, активных: ${activeCount}`;
  warehouseTaskEl("warehouseTaskKpiPickFace").textContent = tasks.filter((task) => task.task_type === "REPLENISHMENT" && task.task_source === "WAVE").length;
  warehouseTaskEl("warehouseTaskKpiShipping").textContent = tasks.filter((task) => task.task_type === "PICKING_MOVE" || (task.task_type === "REPLENISHMENT" && task.source_doc_type === "SHIPMENT")).length;
  warehouseTaskEl("warehouseTaskKpiProduction").textContent = tasks.filter((task) => task.task_type === "RAW_TO_PRODUCTION" || task.source_doc_type === "PRODUCTION_WAVE").length;
  warehouseTaskEl("warehouseTaskKpiFinished").textContent = tasks.filter((task) => task.task_type === "FG_TO_STORAGE").length;
}

function selectWarehouseTask(taskId) {
  warehouseTaskState.selectedTask = warehouseTaskState.tasks.find((task) => Number(task.task_id) === taskId) || null;
  renderWarehouseTasks();
  renderWarehouseTaskDetail();
}

function renderWarehouseTaskDetail() {
  const task = warehouseTaskState.selectedTask;
  warehouseTaskEl("warehouseTaskSelectionText").textContent = task ? `Выбрано задание ${task.task_id}` : "Задание не выбрано";
  warehouseTaskEl("warehouseTaskDetailStatus").textContent = task ? `${task.status} / ${TASK_TYPE_LABELS[task.task_type] || task.task_type}` : "Выберите задание";
  warehouseTaskEl("warehouseTaskDetailOperation").textContent = task ? `${classifyTask(task)} (${task.task_type})` : "-";
  warehouseTaskEl("warehouseTaskDetailDocument").textContent = task ? sourceDocText(task) : "-";
  warehouseTaskEl("warehouseTaskDetailPallet").textContent = task ? (task.uid_pallet || task.sscc || "-") : "-";
  warehouseTaskEl("warehouseTaskDetailRoute").textContent = task ? `${task.from_cell || "-"} -> ${task.to_cell || "-"}` : "-";
  warehouseTaskEl("warehouseTaskDetailMode").textContent = task ? qtyModeText(task) : "-";
  warehouseTaskEl("warehouseTaskDetailQty").textContent = task ? formatTaskQty(task) : "-";
  warehouseTaskEl("warehouseTaskDetailParent").textContent = task?.parent_task_id ? `#${task.parent_task_id}` : "-";
  warehouseTaskEl("warehouseTaskDetailError").textContent = task ? (task.last_error || "-") : "-";
  warehouseTaskEl("warehouseTaskEditAssignee").value = task?.assigned_to || warehouseTaskUser();
  warehouseTaskEl("warehouseTaskScanPallet").value = task ? (task.uid_pallet || task.sscc || "") : "";
  warehouseTaskEl("warehouseTaskScanFrom").value = task?.from_cell || "";
  warehouseTaskEl("warehouseTaskScanTo").value = task?.to_cell || "";
  warehouseTaskEl("warehouseTaskFactQty").value = task?.qty ?? "";
}

async function changeWarehouseTask(action) {
  const task = warehouseTaskState.selectedTask;
  if (!task) throw new Error("Выберите задание");
  if (!warehouseTaskCan("warehouse_task_execute")) throw new Error("Нет права warehouse_task_execute");
  const payload = {
    assigned_to: warehouseTaskEl("warehouseTaskEditAssignee").value.trim() || warehouseTaskUser(),
    updated_by: warehouseTaskUser(),
  };
  if (action === "complete") {
    const factQty = warehouseTaskEl("warehouseTaskFactQty").value;
    if (factQty) payload.fact_qty = Number(factQty);
    payload.scanned_pallet = warehouseTaskEl("warehouseTaskScanPallet").value.trim() || null;
    payload.scanned_from_cell = warehouseTaskEl("warehouseTaskScanFrom").value.trim() || null;
    payload.scanned_to_cell = warehouseTaskEl("warehouseTaskScanTo").value.trim() || null;
  }
  if (action === "cancel") {
    payload.reason = warehouseTaskEl("warehouseTaskCancelReason").value.trim() || "Отмена из админки складских заданий";
  }
  await warehouseTaskFetch(`/api/warehouse-tasks/${task.task_id}/${action}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  await loadWarehouseTasks();
  const updated = warehouseTaskState.tasks.find((item) => item.task_id === task.task_id);
  warehouseTaskState.selectedTask = updated || null;
  renderWarehouseTaskDetail();
}

function classifyTask(task) {
  if (task.task_type === "REPLENISHMENT" && task.task_source === "WAVE") {
    return "Пополнение под волну";
  }
  if (task.task_type === "REPLENISHMENT" && task.source_doc_type === "SHIPMENT") {
    return "Спуск на грузовую зону";
  }
  if (task.task_type === "RAW_TO_PRODUCTION" || task.source_doc_type === "PRODUCTION_WAVE") {
    return "Пополнение производства";
  }
  if (task.task_type === "FG_TO_STORAGE") {
    return "Размещение выпуска";
  }
  return TASK_TYPE_LABELS[task.task_type] || task.task_type || "Задание";
}

function sourceDocText(task) {
  const parts = [];
  if (task.source_doc_type) parts.push(task.source_doc_type);
  if (task.source_doc_id) parts.push(`#${task.source_doc_id}`);
  if (task.production_order_id) parts.push(`PO ${task.production_order_id}`);
  return parts.join(" ") || "-";
}

function formatQty(qty, unitCode) {
  const value = Number(qty || 0);
  return `${Number.isInteger(value) ? value : value.toFixed(3)} ${unitCode || ""}`.trim();
}

function formatTaskQty(task) {
  const planned = formatQty(task.qty, task.unit_code);
  if (task.fact_qty === null || task.fact_qty === undefined || task.fact_qty === "") return planned;
  return `${planned} / факт ${formatQty(task.fact_qty, task.unit_code)}`;
}

function qtyModeText(task) {
  return (task.qty_mode || "BOX") === "PALLET" ? "Паллет" : "Коробки";
}

function statusClass(status) {
  if (status === "DONE") return "done";
  if (status === "CANCELLED") return "cancelled";
  if (status === "ERROR") return "error";
  if (status === "IN_PROGRESS") return "progress";
  if (status === "ASSIGNED") return "assigned";
  return "planned";
}

function showWarehouseTaskError(error) {
  warehouseTaskEl("warehouseTaskStatusText").textContent = error.message;
}

function escapeWarehouseTaskHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;");
}

function escapeWarehouseTaskAttr(value) {
  return escapeWarehouseTaskHtml(value);
}

function initWarehouseTasks() {
  const params = new URLSearchParams(window.location.search);
  warehouseTaskState.initialTaskId = Number(params.get("task_id") || 0) || null;
  warehouseTaskEl("warehouseTaskRefresh").addEventListener("click", () => loadWarehouseTasks().catch(showWarehouseTaskError));
  warehouseTaskEl("warehouseTaskLoad").addEventListener("click", () => loadWarehouseTasks().catch(showWarehouseTaskError));
  warehouseTaskEl("warehouseTaskSearch").addEventListener("input", () => {
    warehouseTaskState.tasks = applySearch(warehouseTaskState.allTasks);
    renderWarehouseTasks();
    renderWarehouseTaskSummary();
  });
  document.querySelectorAll("[data-task-preset]").forEach((button) => {
    button.addEventListener("click", () => setWarehouseTaskPreset(button.dataset.taskPreset));
  });
  warehouseTaskEl("warehouseTaskAssign").addEventListener("click", () => changeWarehouseTask("assign").catch(showWarehouseTaskError));
  warehouseTaskEl("warehouseTaskStart").addEventListener("click", () => changeWarehouseTask("start").catch(showWarehouseTaskError));
  warehouseTaskEl("warehouseTaskComplete").addEventListener("click", () => changeWarehouseTask("complete").catch(showWarehouseTaskError));
  warehouseTaskEl("warehouseTaskCancel").addEventListener("click", () => changeWarehouseTask("cancel").catch(showWarehouseTaskError));
  loadWarehouseTasks().catch(showWarehouseTaskError);
}

window.addEventListener("wms-admin-auth-ready", initWarehouseTasks);
