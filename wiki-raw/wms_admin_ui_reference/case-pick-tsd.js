const cpTsd = {
  tasks: [],
  task: null,
  lineIndex: 0,
  session: null,
};

function cpTsdEl(id) {
  return document.getElementById(id);
}

function cpTsdApiBase() {
  return (window.wmsAdminAuth?.state?.apiBase || "http://127.0.0.1:8088").replace(/\/$/, "");
}

function cpTsdHeaders(extra = {}) {
  return window.wmsAdminAuth ? window.wmsAdminAuth.headers(extra) : { ...extra };
}

function cpTsdUser() {
  return window.wmsAdminAuth?.state?.user?.username || "admin";
}

function cpTsdPicker() {
  return cpTsd.session?.operator_user_id || cpTsdEl("cpTsdPicker").value.trim() || cpTsdUser();
}

function cpTsdSessionKey() {
  return "wms.casepick.tsd.session";
}

function cpTsdQuery() {
  return new URLSearchParams(window.location.search);
}

function cpTsdLoadStoredSession() {
  try {
    const text = sessionStorage.getItem(cpTsdSessionKey());
    cpTsd.session = text ? JSON.parse(text) : null;
  } catch {
    cpTsd.session = null;
  }
  if (cpTsdQuery().get("evidence") === "1" && !cpTsd.session?.session_id) {
    cpTsd.session = {
      session_id: "evidence",
      resource_id: "",
      operator_user_id: "evidence-picker",
      resource_code: "EVIDENCE-PICKER",
    };
  }
}

function cpTsdStoreSession(session) {
  cpTsd.session = session;
  if (session) sessionStorage.setItem(cpTsdSessionKey(), JSON.stringify(session));
  else sessionStorage.removeItem(cpTsdSessionKey());
  cpTsdRenderSession();
}

async function cpTsdFetch(path, options = {}) {
  const response = await fetch(`${cpTsdApiBase()}${path}`, {
    ...options,
    headers: cpTsdHeaders(options.headers || {}),
  });
  const text = await response.text();
  const body = text ? JSON.parse(text) : {};
  if (!response.ok) {
    const detail = body.detail?.message || body.detail || body.message || `HTTP ${response.status}`;
    throw new Error(typeof detail === "string" ? detail : JSON.stringify(detail));
  }
  return body;
}

async function cpTsdLoad() {
  if (!cpTsd.session?.session_id) {
    cpTsd.tasks = [];
    cpTsd.task = null;
    cpTsdRender();
    cpTsdSetState("Откройте смену");
    return;
  }
  cpTsdSetState("Загрузка...");
  const params = new URLSearchParams({
    scope: cpTsdEl("cpTsdScope").value,
    limit: "100",
  });
  if (cpTsd.session.resource_id) {
    params.set("resource_id", cpTsd.session.resource_id);
  }
  cpTsd.tasks = await cpTsdFetch(`/api/case-pick/tasks?${params.toString()}`);
  const selected = cpTsd.tasks[0];
  cpTsd.task = selected ? await cpTsdFetch(`/api/case-pick/tasks/${selected.case_pick_task_id}`) : null;
  cpTsd.lineIndex = 0;
  cpTsdRender();
}

function cpTsdCurrentLine() {
  const lines = cpTsd.task?.lines || [];
  return lines[cpTsd.lineIndex] || null;
}

function cpTsdRender() {
  const task = cpTsd.task;
  const line = cpTsdCurrentLine();
  const lines = task?.lines || [];
  cpTsdEl("cpTsdCounter").textContent = lines.length ? `${cpTsd.lineIndex + 1} / ${lines.length}` : "0 / 0";
  cpTsdEl("cpTsdTaskId").textContent = task ? `#${task.case_pick_task_id}` : "-";
  cpTsdEl("cpTsdStatus").textContent = task?.status || "-";
  cpTsdEl("cpTsdStatus").className = `task-badge ${cpTsdStatusClass(task?.status)}`;
  cpTsdEl("cpTsdOperation").textContent = task ? "Собрать клиентский поддон" : "Нет поддона";
  cpTsdEl("cpTsdCell").textContent = line?.cell_code || "-";
  cpTsdEl("cpTsdSscc").textContent = task?.sscc || "-";
  cpTsdEl("cpTsdCustomer").textContent = task?.customer_name || "-";
  cpTsdEl("cpTsdOrder").textContent = task?.order_no || "-";
  cpTsdEl("cpTsdArticul").textContent = line ? `${line.articul}${line.product_name ? ` ${line.product_name}` : ""}` : "-";
  cpTsdEl("cpTsdQty").textContent = line ? `${cpTsdNum(line.picked_qty)} / ${cpTsdNum(line.planned_qty)}` : "-";
  cpTsdEl("cpTsdScanCell").value = line?.cell_code || "";
  cpTsdEl("cpTsdScanProduct").value = line?.articul || "";
  cpTsdEl("cpTsdScanBox").value = "";
  cpTsdEl("cpTsdFactQty").value = "";
  cpTsdEl("cpTsdFactQty").placeholder = line ? cpTsdNum(line.planned_qty) : "план";
  cpTsdSetState(task ? `${task.status}: ${task.assigned_to || "свободно"}` : "Нет заданий");
}

function cpTsdNum(value) {
  const num = Number(value || 0);
  return Number.isInteger(num) ? String(num) : num.toFixed(3);
}

function cpTsdStatusClass(status) {
  if (status === "PICKED" || status === "READY_TO_SHIP") return "done";
  if (status === "IN_PROGRESS" || status === "PARTIAL") return "progress";
  if (status === "FAILED" || status === "SYNC_CONFLICT") return "failed";
  return "planned";
}

async function cpTsdTaskAction(action) {
  const task = cpTsd.task;
  if (!task) throw new Error("Нет выбранного поддона");
  const payload = {
    resource_id: cpTsd.session?.resource_id || null,
    resource_session_id: cpTsd.session?.session_id || null,
    equipment_id: cpTsd.session?.equipment_id || null,
    actor: cpTsdPicker(),
  };
  cpTsdSetState("Отправка...");
  await cpTsdFetch(`/api/case-pick/tasks/${task.case_pick_task_id}/${action}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  cpTsd.task = await cpTsdFetch(`/api/case-pick/tasks/${task.case_pick_task_id}`);
  cpTsdRender();
}

async function cpTsdConfirmLine() {
  const task = cpTsd.task;
  const line = cpTsdCurrentLine();
  if (!task || !line) throw new Error("Нет строки отбора");
  const fact = cpTsdEl("cpTsdFactQty").value;
  const payload = {
    fact_qty: fact ? Number(fact) : null,
    scan_cell: cpTsdEl("cpTsdScanCell").value.trim() || null,
    scan_product: cpTsdEl("cpTsdScanProduct").value.trim() || null,
    scan_box: cpTsdEl("cpTsdScanBox").value.trim() || null,
    scan_container: task.sscc,
    offline_event_id: `online-${Date.now()}-${line.case_pick_line_id}`,
    resource_id: cpTsd.session?.resource_id || null,
    resource_session_id: cpTsd.session?.session_id || null,
    equipment_id: cpTsd.session?.equipment_id || null,
    actor: cpTsdPicker(),
  };
  cpTsdSetState("Подтверждение...");
  await cpTsdFetch(`/api/case-pick/tasks/${task.case_pick_task_id}/lines/${line.case_pick_line_id}/confirm`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  cpTsd.task = await cpTsdFetch(`/api/case-pick/tasks/${task.case_pick_task_id}`);
  cpTsdMove(1);
}

async function cpTsdShortLine() {
  const task = cpTsd.task;
  const line = cpTsdCurrentLine();
  if (!task || !line) throw new Error("Нет строки отбора");
  const picked = Number(cpTsdEl("cpTsdFactQty").value || 0);
  const payload = {
    picked_qty: picked,
    reason_text: "Нет товара в ячейке",
    offline_event_id: `online-short-${Date.now()}-${line.case_pick_line_id}`,
    resource_id: cpTsd.session?.resource_id || null,
    resource_session_id: cpTsd.session?.session_id || null,
    equipment_id: cpTsd.session?.equipment_id || null,
    actor: cpTsdPicker(),
  };
  cpTsdSetState("Вычерк...");
  await cpTsdFetch(`/api/case-pick/tasks/${task.case_pick_task_id}/lines/${line.case_pick_line_id}/short`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  cpTsd.task = await cpTsdFetch(`/api/case-pick/tasks/${task.case_pick_task_id}`);
  cpTsdMove(1);
}

function cpTsdMove(delta) {
  const lines = cpTsd.task?.lines || [];
  if (!lines.length) {
    cpTsdRender();
    return;
  }
  cpTsd.lineIndex = (cpTsd.lineIndex + delta + lines.length) % lines.length;
  cpTsdRender();
}

function cpTsdSetState(text) {
  cpTsdEl("cpTsdState").textContent = text;
}

function cpTsdRenderSession() {
  cpTsdEl("cpTsdSession").textContent = cpTsd.session
    ? `${cpTsd.session.operator_user_id || cpTsd.session.resource_code || "ресурс"}`
    : "Смена не открыта";
}

async function cpTsdShiftLogin() {
  const payload = {
    driver_code: cpTsdEl("cpTsdPicker").value.trim() || cpTsdUser(),
    password: cpTsdEl("cpTsdPassword").value || null,
    barcode: cpTsdEl("cpTsdPicker").value.trim() || null,
    equipment_code: cpTsdEl("cpTsdEquipment").value.trim() || null,
  };
  cpTsdSetState("Вход в смену...");
  const session = await cpTsdFetch("/api/resources/sessions/tsd-login", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  cpTsdStoreSession(session);
  await cpTsdLoad();
}

async function cpTsdShiftLogout() {
  if (!cpTsd.session?.session_id) {
    cpTsdStoreSession(null);
    await cpTsdLoad();
    return;
  }
  await cpTsdFetch(`/api/resources/sessions/${cpTsd.session.session_id}/logout`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ updated_by: cpTsdUser() }),
  });
  cpTsdStoreSession(null);
  await cpTsdLoad();
}

function cpTsdBind() {
  cpTsdEl("cpTsdRefresh").addEventListener("click", () => cpTsdSafe(cpTsdLoad));
  cpTsdEl("cpTsdScope").addEventListener("change", () => cpTsdSafe(cpTsdLoad));
  cpTsdEl("cpTsdShiftLogin").addEventListener("click", () => cpTsdSafe(cpTsdShiftLogin));
  cpTsdEl("cpTsdShiftLogout").addEventListener("click", () => cpTsdSafe(cpTsdShiftLogout));
  cpTsdEl("cpTsdPrev").addEventListener("click", () => cpTsdMove(-1));
  cpTsdEl("cpTsdNext").addEventListener("click", () => cpTsdMove(1));
  cpTsdEl("cpTsdClaim").addEventListener("click", () => cpTsdSafe(() => cpTsdTaskAction("claim")));
  cpTsdEl("cpTsdStart").addEventListener("click", () => cpTsdSafe(() => cpTsdTaskAction("start")));
  cpTsdEl("cpTsdConfirm").addEventListener("click", () => cpTsdSafe(cpTsdConfirmLine));
  cpTsdEl("cpTsdShort").addEventListener("click", () => cpTsdSafe(cpTsdShortLine));
  cpTsdEl("cpTsdClose").addEventListener("click", () => cpTsdSafe(() => cpTsdTaskAction("close-pallet")));
}

async function cpTsdSafe(fn) {
  try {
    await fn();
  } catch (error) {
    cpTsdSetState(error.message || String(error));
  }
}

window.addEventListener("DOMContentLoaded", () => {
  cpTsdLoadStoredSession();
  const scope = cpTsdQuery().get("scope");
  if (scope && cpTsdEl("cpTsdScope").querySelector(`option[value="${scope}"]`)) {
    cpTsdEl("cpTsdScope").value = scope;
  }
  cpTsdRenderSession();
  cpTsdBind();
  cpTsdSafe(cpTsdLoad);
});
