const rtTsd = {
  tasks: [],
  index: 0,
  session: null,
};

const rtTsdLabels = {
  RAW_TO_PRODUCTION: "Сырье в производство",
  FG_TO_STORAGE: "Готовая продукция",
  REPLENISHMENT: "Пополнение",
  PICKING_MOVE: "Комплектация",
  OTHER: "Задание",
};

const rtTsdDemoTasks = [
  {
    task_id: 501,
    status: "PLANNED",
    task_type: "REPLENISHMENT",
    task_source: "WAVE",
    source_doc_type: "PICK_WAVE",
    source_doc_id: 1901,
    uid_pallet: "SRC-A-01",
    from_cell: "A-01-04",
    to_cell: "PICK-A-01",
    qty: 100,
    unit_code: "BOX",
    qty_mode: "BOX",
  },
  {
    task_id: 502,
    status: "ASSIGNED",
    task_type: "PICKING_MOVE",
    task_source: "WAVE",
    source_doc_type: "PICK_WAVE",
    source_doc_id: 1901,
    uid_pallet: "RACK-B-01-PAL",
    from_cell: "RACK-B-01",
    to_cell: "LOAD-01",
    qty: 1,
    unit_code: "PAL",
    qty_mode: "PALLET",
    assigned_to: "demo",
  },
  {
    task_id: 503,
    status: "IN_PROGRESS",
    task_type: "REPLENISHMENT",
    task_source: "WAVE",
    source_doc_type: "PICK_WAVE",
    source_doc_id: 1901,
    uid_pallet: "SRC-A-02",
    from_cell: "A-01-05",
    to_cell: "PICK-A-01",
    qty: 50,
    unit_code: "BOX",
    qty_mode: "BOX",
    assigned_to: "demo",
  },
];

function rtTsdDemoMode() {
  return new URLSearchParams(window.location.search).get("demo") === "1";
}

function rtTsdEl(id) {
  return document.getElementById(id);
}

function rtTsdApiBase() {
  return (window.wmsAdminAuth?.state?.apiBase || "http://127.0.0.1:8088").replace(/\/$/, "");
}

function rtTsdHeaders(extra = {}) {
  return window.wmsAdminAuth ? window.wmsAdminAuth.headers(extra) : { ...extra };
}

function rtTsdUser() {
  return window.wmsAdminAuth?.state?.user?.username || "admin";
}

function rtTsdDriver() {
  return rtTsd.session?.operator_user_id || rtTsdEl("rtTsdDriver").value.trim() || rtTsdUser();
}

function rtTsdSessionKey() {
  return "wms.reachtruck.tsd.session";
}

function rtTsdLoadStoredSession() {
  try {
    const text = sessionStorage.getItem(rtTsdSessionKey());
    rtTsd.session = text ? JSON.parse(text) : null;
  } catch {
    rtTsd.session = null;
  }
}

function rtTsdStoreSession(session) {
  rtTsd.session = session;
  if (session) {
    sessionStorage.setItem(rtTsdSessionKey(), JSON.stringify(session));
  } else {
    sessionStorage.removeItem(rtTsdSessionKey());
  }
  rtTsdRenderSession();
}

async function rtTsdFetch(path, options = {}) {
  const response = await fetch(`${rtTsdApiBase()}${path}`, {
    ...options,
    headers: rtTsdHeaders(options.headers || {}),
  });
  const text = await response.text();
  const body = text ? JSON.parse(text) : {};
  if (!response.ok) {
    const detail = body.detail?.message || body.detail || body.message || `HTTP ${response.status}`;
    throw new Error(typeof detail === "string" ? detail : JSON.stringify(detail));
  }
  return body;
}

async function rtTsdLoad() {
  if (rtTsdDemoMode()) {
    const requestedStatus = new URLSearchParams(window.location.search).get("task_status");
    rtTsd.tasks = rtTsdDemoTasks.map((task) => ({ ...task }));
    rtTsd.index = Math.max(0, rtTsd.tasks.findIndex((task) => task.status === requestedStatus));
    rtTsdRender();
    return;
  }
  if (!rtTsd.session?.session_id) {
    rtTsd.tasks = [];
    rtTsdRender();
    rtTsdSetState("Откройте смену");
    return;
  }
  rtTsdSetState("Загрузка...");
  const statuses = ["IN_PROGRESS", "ASSIGNED", "PLANNED"];
  const result = await Promise.all(statuses.map((status) => {
    const params = new URLSearchParams({ status, limit: "100" });
    return rtTsdFetch(`/api/warehouse-tasks?${params.toString()}`);
  }));
  rtTsd.tasks = rtTsdFilter(rtTsdDedupe(result.flat()));
  rtTsd.index = Math.min(rtTsd.index, Math.max(rtTsd.tasks.length - 1, 0));
  rtTsdRender();
}

function rtTsdFilter(tasks) {
  const scope = rtTsdEl("rtTsdScope").value;
  const driver = rtTsdDriver().toLowerCase();
  const params = new URLSearchParams(window.location.search);
  const requestedTaskType = params.get("task_type");
  const requestedTaskSource = params.get("task_source");
  const requestedSourceDocId = params.get("source_doc_id");
  return tasks
    .filter((task) => !requestedTaskType || task.task_type === requestedTaskType)
    .filter((task) => !requestedTaskSource || task.task_source === requestedTaskSource)
    .filter((task) => !requestedSourceDocId || String(task.source_doc_id || "") === requestedSourceDocId)
    .filter((task) => {
      const assignee = String(task.assigned_to || "").toLowerCase();
      if (scope === "free") return !assignee;
      if (scope === "mine") return !assignee || assignee === driver;
      return true;
    })
    .sort(rtTsdCompare);
}

function rtTsdDedupe(tasks) {
  const map = new Map();
  tasks.forEach((task) => map.set(Number(task.task_id), task));
  return [...map.values()];
}

function rtTsdCompare(a, b) {
  const weight = { IN_PROGRESS: 0, ASSIGNED: 1, PLANNED: 2 };
  const aw = weight[a.status] ?? 9;
  const bw = weight[b.status] ?? 9;
  if (aw !== bw) return aw - bw;
  return Number(a.task_id || 0) - Number(b.task_id || 0);
}

function rtTsdCurrent() {
  return rtTsd.tasks[rtTsd.index] || null;
}

function rtTsdRender() {
  const task = rtTsdCurrent();
  rtTsdEl("rtTsdCounter").textContent = rtTsd.tasks.length ? `${rtTsd.index + 1} / ${rtTsd.tasks.length}` : "0 / 0";
  rtTsdEl("rtTsdTaskId").textContent = task ? `#${task.task_id}` : "-";
  rtTsdEl("rtTsdStatus").textContent = task?.status || "-";
  rtTsdEl("rtTsdStatus").className = `task-badge ${rtTsdStatusClass(task?.status)}`;
  rtTsdEl("rtTsdOperation").textContent = task ? rtTsdOperation(task) : "Нет задания";
  rtTsdEl("rtTsdFrom").textContent = task?.from_cell || "-";
  rtTsdEl("rtTsdTo").textContent = task?.to_cell || "-";
  rtTsdEl("rtTsdPallet").textContent = task ? (task.uid_pallet || task.sscc || "-") : "-";
  rtTsdEl("rtTsdMode").textContent = task ? rtTsdModeText(task) : "-";
  rtTsdEl("rtTsdQty").textContent = task ? rtTsdQty(task.qty, task.unit_code) : "-";
  rtTsdEl("rtTsdDoc").textContent = task ? rtTsdDoc(task) : "-";
  rtTsdEl("rtTsdScanPallet").value = task ? (task.uid_pallet || task.sscc || "") : "";
  rtTsdEl("rtTsdScanFrom").value = task?.from_cell || "";
  rtTsdEl("rtTsdScanTo").value = task?.to_cell || "";
  rtTsdEl("rtTsdFactQty").value = "";
  rtTsdEl("rtTsdFactQty").placeholder = task ? `пусто = ${rtTsdQty(task.qty, task.unit_code)}` : "пусто = план";
  rtTsdEl("rtTsdFactQty").disabled = task?.qty_mode === "PALLET";
  rtTsdEl("rtTsdCompleteBoxes").disabled = task?.qty_mode === "PALLET";
  rtTsdSetState(task ? `${task.status}: ${task.assigned_to || "свободно"}` : "Нет активных заданий");
}

async function rtTsdAction(action, options = {}) {
  const task = rtTsdCurrent();
  if (!task) throw new Error("Нет выбранного задания");
  if (!window.wmsAdminAuth?.hasPermission("warehouse_task_execute")) {
    throw new Error("Нет права warehouse_task_execute");
  }
  const payload = {
    assigned_to: rtTsdDriver(),
    updated_by: rtTsdDriver(),
    resource_id: rtTsd.session?.resource_id || null,
    resource_session_id: rtTsd.session?.session_id || null,
    equipment_id: rtTsd.session?.equipment_id || null,
  };
  if (action === "complete") {
    const factQty = rtTsdEl("rtTsdFactQty").value;
    if (options.mode === "boxes" && factQty) payload.fact_qty = Number(factQty);
    payload.scanned_pallet = rtTsdEl("rtTsdScanPallet").value.trim() || null;
    payload.scanned_from_cell = rtTsdEl("rtTsdScanFrom").value.trim() || null;
    payload.scanned_to_cell = rtTsdEl("rtTsdScanTo").value.trim() || null;
  }
  if (action === "cancel") {
    payload.reason = "Отмена с ТСД ричтрака";
  }
  rtTsdSetState("Отправка...");
  await rtTsdFetch(`/api/warehouse-tasks/${task.task_id}/${action}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  await rtTsdLoad();
}

function rtTsdMove(delta) {
  if (!rtTsd.tasks.length) return;
  rtTsd.index = (rtTsd.index + delta + rtTsd.tasks.length) % rtTsd.tasks.length;
  rtTsdRender();
}

function rtTsdOperation(task) {
  if (task.task_type === "REPLENISHMENT" && task.task_source === "WAVE") return "Пополнение волны";
  if (task.task_type === "RAW_TO_PRODUCTION") return "В производство";
  if (task.task_type === "FG_TO_STORAGE") return "Разместить выпуск";
  return rtTsdLabels[task.task_type] || task.task_type || "Задание";
}

function rtTsdDoc(task) {
  const parts = [];
  if (task.source_doc_type) parts.push(task.source_doc_type);
  if (task.source_doc_id) parts.push(`#${task.source_doc_id}`);
  if (task.production_order_id) parts.push(`PO ${task.production_order_id}`);
  return parts.join(" ") || "-";
}

function rtTsdQty(qty, unitCode) {
  const value = Number(qty || 0);
  return `${Number.isInteger(value) ? value : value.toFixed(3)} ${unitCode || ""}`.trim();
}

function rtTsdModeText(task) {
  return task.qty_mode === "PALLET" ? "Паллет целиком" : "Коробки";
}

function rtTsdStatusClass(status) {
  if (status === "IN_PROGRESS") return "progress";
  if (status === "ASSIGNED") return "assigned";
  if (status === "ERROR") return "error";
  return "planned";
}

function rtTsdSetState(text) {
  rtTsdEl("rtTsdState").textContent = text;
}

async function rtTsdShiftLogin() {
  const driver = rtTsdEl("rtTsdDriver").value.trim();
  const password = rtTsdEl("rtTsdPassword").value;
  const equipment = rtTsdEl("rtTsdEquipment").value.trim();
  if (!driver) throw new Error("Укажите водителя или отсканируйте ШК");
  rtTsdSetState("Открытие смены...");
  const session = await rtTsdFetch("/api/resources/sessions/tsd-login", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      driver_code: driver,
      barcode: driver,
      password: password || null,
      equipment_code: equipment || null,
      terminal_id: "TSD-REACHTRUCK",
    }),
  });
  rtTsdStoreSession(session);
  rtTsdEl("rtTsdPassword").value = "";
  await rtTsdLoad();
}

async function rtTsdShiftLogout() {
  if (rtTsd.session?.session_id && !rtTsdDemoMode()) {
    await rtTsdFetch(`/api/resources/sessions/${rtTsd.session.session_id}/logout`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ updated_by: rtTsdDriver() }),
    });
  }
  rtTsdStoreSession(null);
  rtTsd.tasks = [];
  rtTsdRender();
  rtTsdSetState("Смена закрыта");
}

function rtTsdRenderSession() {
  const sessionEl = rtTsdEl("rtTsdSession");
  if (!sessionEl) return;
  if (!rtTsd.session?.session_id) {
    sessionEl.textContent = "Смена не открыта";
    return;
  }
  sessionEl.textContent = `${rtTsd.session.operator_user_id || "-"} / ${rtTsd.session.equipment_code || rtTsd.session.resource_code || "-"} / #${rtTsd.session.session_id}`;
}

function rtTsdShowError(error) {
  rtTsdSetState(error.message);
}

function rtTsdInit() {
  rtTsdLoadStoredSession();
  rtTsdEl("rtTsdDriver").value = rtTsdUser();
  if (rtTsd.session?.operator_user_id) rtTsdEl("rtTsdDriver").value = rtTsd.session.operator_user_id;
  if (rtTsd.session?.equipment_code) rtTsdEl("rtTsdEquipment").value = rtTsd.session.equipment_code;
  rtTsdEl("rtTsdRefresh").addEventListener("click", () => rtTsdLoad().catch(rtTsdShowError));
  rtTsdEl("rtTsdShiftLogin").addEventListener("click", () => rtTsdShiftLogin().catch(rtTsdShowError));
  rtTsdEl("rtTsdShiftLogout").addEventListener("click", () => rtTsdShiftLogout().catch(rtTsdShowError));
  rtTsdEl("rtTsdScope").addEventListener("change", () => rtTsdLoad().catch(rtTsdShowError));
  rtTsdEl("rtTsdDriver").addEventListener("change", () => rtTsdLoad().catch(rtTsdShowError));
  rtTsdEl("rtTsdPrev").addEventListener("click", () => rtTsdMove(-1));
  rtTsdEl("rtTsdNext").addEventListener("click", () => rtTsdMove(1));
  rtTsdEl("rtTsdAssign").addEventListener("click", () => rtTsdAction("assign").catch(rtTsdShowError));
  rtTsdEl("rtTsdStart").addEventListener("click", () => rtTsdAction("start").catch(rtTsdShowError));
  rtTsdEl("rtTsdCompletePallet").addEventListener("click", () => rtTsdAction("complete", { mode: "pallet" }).catch(rtTsdShowError));
  rtTsdEl("rtTsdCompleteBoxes").addEventListener("click", () => rtTsdAction("complete", { mode: "boxes" }).catch(rtTsdShowError));
  rtTsdEl("rtTsdCancel").addEventListener("click", () => rtTsdAction("cancel").catch(rtTsdShowError));
  rtTsdRenderSession();
  rtTsdLoad().catch(rtTsdShowError);
}

window.addEventListener("wms-admin-auth-ready", rtTsdInit);
if (window.wmsAdminAuth?.state?.user) {
  rtTsdInit();
}
