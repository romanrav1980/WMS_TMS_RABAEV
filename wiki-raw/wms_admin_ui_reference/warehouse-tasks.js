const warehouseTaskState = {
  allTasks: [],
  tasks: [],
  selectedTask: null,
  preset: "all",
  initialTaskId: null,
  readEpoch: 0,
  confirmedBound: false,
};

const warehouseTaskEl = (id) => document.getElementById(id);

const TASK_TYPE_LABELS = {
  RAW_TO_PRODUCTION: "Сырье в производство",
  FG_TO_STORAGE: "Готовая продукция",
  PUTAWAY: "Размещение",
  REPLENISHMENT: "Пополнение",
  PICKING_MOVE: "Комплектация",
  OTHER: "Другое",
};

const TASK_SOURCE_LABELS = {
  MES_RAW_SUPPLY: "Снабжение производства",
  MES_COMPLETION: "Выпуск",
  SAP_RECEIPT: "Приёмка SAP",
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
    const detail = body.detail?.reason === 'TASK_EXPECTED_SIGNATURE_CHANGED'
      ? 'Бланк устарел. Сверьте выполненную работу с текущим заданием и проверьте исходный бланк перед новым подтверждением.'
      : body.detail?.message || body.detail || body.message || `HTTP ${response.status}`;
    const error = new Error(typeof detail === "string" ? detail : JSON.stringify(detail));
    error.status = response.status;
    error.code = body.detail?.code;
    error.oracleCode = body.detail?.oracle_code;
    error.outcomeConfirmed = body.detail?.outcome_confirmed;
    error.operationId = body.detail?.operation_id;
    throw error;
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
  if(warehouseTaskState.preset==="shipping-zone")params.set("queue_group","SHIPPING");
  if(warehouseTaskState.preset==="waiting")params.set("queue_group","DEFER_WAITING");
  const docType=warehouseTaskEl("warehouseTaskDocType").value;
  if(docType)params.set("source_doc_type",docType);
  if (assignee) params.set("assigned_to", assignee);
  params.set("limit", warehouseTaskEl("warehouseTaskLimit").value || "150");
  return params;
}

async function loadWarehouseTasks() {
  warehouseTaskEl("warehouseTaskStatusText").textContent = "Загрузка...";
  const token=++warehouseTaskState.readEpoch;
  const identity=JSON.stringify([warehouseTaskApiBase(),window.wmsAdminAuth?.state?.user?.username]);
  const query=warehouseTaskParams().toString();
  const directPaperTask = window.warehouseTaskPaper?.directTaskId();
  const tasks = directPaperTask ? [await warehouseTaskFetch(`/api/warehouse-tasks/${directPaperTask}`)] :
    await warehouseTaskFetch(`/api/warehouse-tasks?${query}`);
  if(token!==warehouseTaskState.readEpoch||query!==warehouseTaskParams().toString()||
    identity!==JSON.stringify([warehouseTaskApiBase(),window.wmsAdminAuth?.state?.user?.username]))return;
  warehouseTaskState.allTasks=tasks;
  warehouseTaskState.tasks = applySearch(warehouseTaskState.allTasks);
  if (warehouseTaskState.selectedTask) {
    warehouseTaskState.selectedTask = warehouseTaskState.tasks.find(
      task => Number(task.task_id) === Number(warehouseTaskState.selectedTask.task_id)
    ) || null;
  }
  let openLinkedDetail=false;
  if(warehouseTaskState.initialTaskId){
    const id=warehouseTaskState.initialTaskId;
    const linked=warehouseTaskState.tasks.find(task=>Number(task.task_id)===id)||await warehouseTaskFetch(`/api/warehouse-tasks/${id}`);
    if(token!==warehouseTaskState.readEpoch||identity!==JSON.stringify([warehouseTaskApiBase(),window.wmsAdminAuth?.state?.user?.username]))return;
    warehouseTaskState.initialTaskId=null;warehouseTaskState.selectedTask=linked;
    openLinkedDetail=window.location.hash==='#warehouseTaskDetail';
  }
  renderWarehouseTasks();
  renderWarehouseTaskSummary();
  renderWarehouseTaskDetail();
  if(openLinkedDetail)warehouseTaskEl('warehouseTaskDetail')?.scrollIntoView?.({block:'start',behavior:'auto'});
}

function applySearch(tasks) {
  const query = warehouseTaskEl("warehouseTaskSearch").value.trim().toLowerCase();
  if (!query) return tasks;
  return tasks.filter((task) => [
    task.task_id,
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

function setWarehouseTaskPreset(preset, reload = true) {
  warehouseTaskState.preset = preset;
  document.querySelectorAll("[data-task-preset]").forEach((button) => {
    button.classList.toggle("active", button.dataset.taskPreset === preset);
  });
  warehouseTaskEl("warehouseTaskDocType").value = "";
  if (preset === "waiting") {
    warehouseTaskEl("warehouseTaskType").value = "PUTAWAY";
    warehouseTaskEl("warehouseTaskSource").value = "MANUAL";
    warehouseTaskEl("warehouseTaskDocType").value = "";
  } else if (preset === "wave-pickface") {
    warehouseTaskEl("warehouseTaskType").value = "REPLENISHMENT";
    warehouseTaskEl("warehouseTaskSource").value = "WAVE";
  } else if (preset === "shipping-zone") {
    warehouseTaskEl("warehouseTaskType").value = "";
    warehouseTaskEl("warehouseTaskSource").value = "";
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
  if(reload)loadWarehouseTasks().catch(showWarehouseTaskError);
}

function renderWarehouseTasks() {
  const rows = warehouseTaskState.tasks.map((task) => {
    const selected = warehouseTaskState.selectedTask?.task_id === task.task_id ? " class=\"selected\"" : "";
    return `<tr${selected} data-task-id="${escapeWarehouseTaskAttr(task.task_id)}">`
      + `<td>${escapeWarehouseTaskHtml(task.task_id)}</td>`
      + `<td><b>${escapeWarehouseTaskHtml(classifyTask(task))}</b><small>${escapeWarehouseTaskHtml(task.task_type)}</small></td>`
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
    row.tabIndex=0;row.title="Открыть карточку задания";
    row.addEventListener("click", () => selectWarehouseTask(Number(row.dataset.taskId)));
    row.addEventListener("keydown",event=>{if(event.key==="Enter"||event.key===" "){event.preventDefault();selectWarehouseTask(Number(row.dataset.taskId));}});
  });
}

function renderWarehouseTaskSummary() {
  const tasks = warehouseTaskState.tasks;
  const activeCount = tasks.filter((task) => ["PLANNED", "ASSIGNED", "IN_PROGRESS", "ERROR"].includes(task.status)).length;
  warehouseTaskEl("warehouseTaskStatusText").textContent = `В выборке: ${tasks.length}, активных: ${activeCount}${warehouseTaskState.allTasks.length>=Number(warehouseTaskEl("warehouseTaskLimit").value||150)?"; достигнут лимит выдачи":""}`;
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
  const terminal=!task||["DONE","CANCELLED"].includes(task.status);
  window.warehouseTaskActions.render(task);
  warehouseTaskEl("warehouseTaskSelectionText").textContent = task ? `Выбрано задание ${task.task_id}` : "Задание не выбрано";
  warehouseTaskEl("warehouseTaskDetailStatus").textContent = task ? `${task.status} / ${classifyTask(task)}` : "Выберите задание";
  warehouseTaskEl("warehouseTaskDetailOperation").textContent = task ? `${classifyTask(task)} (${task.task_type})` : "-";
  warehouseTaskEl("warehouseTaskDetailDocument").textContent = task ? sourceDocText(task) : "-";
  warehouseTaskEl("warehouseTaskDetailPallet").textContent = task ? (task.uid_pallet || task.sscc || "-") : "-";
  warehouseTaskEl("warehouseTaskDetailRoute").textContent = task ? `${task.from_cell || "-"} -> ${task.to_cell || "-"}${task.to_slot_code ? " / слот "+task.to_slot_code : ""}` : "-";
  warehouseTaskEl("warehouseTaskDetailMode").textContent = task ? qtyModeText(task) : "-";
  warehouseTaskEl("warehouseTaskDetailQty").textContent = task ? formatTaskQty(task) : "-";
  const caseNote=warehouseTaskEl("warehouseTaskCaseNote");
  if(caseNote){
    const hu=task?.unit_code==="HU";
    caseNote.hidden=!(hu||task?.source_doc_type==="ST_DEFER_CASE");
    caseNote.textContent=hu
      ?"Перемещается одно грузовое место HU со всеми вложениями. Количество мест не равно количеству товара. Ссылка «Текущий состав HU» показывает состав сейчас; после распаковки он может отличаться от состава при выполнении задания."
      :"Перемещается одно готовое грузовое место CASE целиком. Товарные количества и резервы каждой партии сохраняются; «1 CASE» означает число мест, а не одну единицу товара.";
  }
  const huLink=warehouseTaskEl("warehouseTaskHuLink");
  if(huLink){
    const identifier=task?.uid_pallet||task?.sscc;
    huLink.hidden=!(task?.unit_code==="HU"&&identifier&&warehouseTaskCan("warehouse_task_view"));
    if(!huLink.hidden)huLink.href="warehouse-hus.html?identifier="+encodeURIComponent(identifier)+"#huComposition";
    else huLink.removeAttribute("href");
  }
  const waveLink=warehouseTaskEl('warehouseTaskWaveLink');
  if(waveLink){
    const wave=Number(task?.source_doc_id);
    waveLink.hidden=!(task?.task_source==='WAVE' && Number.isSafeInteger(wave)&&wave>0 && warehouseTaskCan('pick_wave_view'));
    if(!waveLink.hidden)waveLink.href='wave-replenishment.html?wave_id='+wave+'#waveExecution';
    else waveLink.removeAttribute?.('href');
  }
  warehouseTaskEl("warehouseTaskDetailParent").textContent = task?.parent_task_id ? `#${task.parent_task_id}` : "-";
  warehouseTaskEl("warehouseTaskDetailError").textContent = task ? (task.last_error || "-") : "-";
  warehouseTaskEl("warehouseTaskEditAssignee").value = task?.assigned_to || warehouseTaskUser();
  warehouseTaskEl("warehouseTaskScanPallet").value = "";
  warehouseTaskEl("warehouseTaskScanFrom").value = "";
  warehouseTaskEl("warehouseTaskScanTo").value = "";
  warehouseTaskEl("warehouseTaskScanSlot").value = "";
  warehouseTaskEl("warehouseTaskFactQty").value = task?.qty_exact ?? task?.qty ?? "";
  warehouseTaskEl("warehouseTaskFactQty").disabled = !task || task.qty_mode === "PALLET" || terminal;
  warehouseTaskEl("warehouseTaskProgress").textContent = "-";
  window.dispatchEvent(new CustomEvent("warehouse-task-selected",{detail:task?{task_id:task.task_id,status:task.status,task_type:task.task_type,task_source:task.task_source}:null}));
  if (task) showWarehouseTaskProgress(task.task_id).catch(error => {
    if (warehouseTaskState.selectedTask?.task_id === task.task_id)
      warehouseTaskEl("warehouseTaskProgress").textContent = error.message;
  });
}

async function changeWarehouseTask(action) {
  const task = warehouseTaskState.selectedTask;
  if (!task) throw new Error("Выберите задание");
  const permission=action==="cancel"?"warehouse_task_edit":"warehouse_task_execute"; if (!warehouseTaskCan(permission)) throw new Error("Нет права "+permission);
  const payload = {
    assigned_to: warehouseTaskEl("warehouseTaskEditAssignee").value.trim() || warehouseTaskUser(),
    updated_by: warehouseTaskUser(),
  };
  if (action === "complete") {
    const factQty = warehouseTaskEl("warehouseTaskFactQty").value;
    if (factQty) payload.fact_qty = factQty;
    payload.scanned_pallet = warehouseTaskEl("warehouseTaskScanPallet").value.trim() || null;
    payload.scanned_from_cell = warehouseTaskEl("warehouseTaskScanFrom").value.trim() || null;
    payload.scanned_to_cell = warehouseTaskEl("warehouseTaskScanTo").value.trim() || null;
    const slotCode=warehouseTaskEl("warehouseTaskScanSlot").value.trim();
    if(slotCode)payload.scanned_to_slot_code=slotCode;
  }
  if (action !== 'complete') window.warehouseTaskPaper?.guard(task, action, payload);
  if (action === "cancel") {
    payload.reason = warehouseTaskEl("warehouseTaskCancelReason").value.trim() || "Отмена из админки складских заданий";
  }
  if (action === "complete") {
    window.warehouseTaskPaper?.guard(task, action, payload);
    const scanDraft=window.warehouseTaskScans?.draftId(task.task_id);
    if(scanDraft) payload.scan_draft_id=scanDraft;
    await window.warehouseTaskRecovery.complete(task.task_id, payload);
    return;
  } else {
    await window.warehouseTaskActions.send(task, action, payload);
  }
}

function classifyTask(task) {
  if(task.wait_plan_operation_id&&task.unit_code==="HU")return "Целое HU в ожидание рейса";
  if (task.task_type === "PUTAWAY" && ["ST_DEFER","ST_DEFER_CASE"].includes(task.source_doc_type)) return task.source_doc_type==="ST_DEFER_CASE" ? "CASE в ожидание рейса" : "Перемещение в ожидание рейса";
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
  if(task.wait_plan_operation_id)parts.push("Ожидание СТ "+task.wait_st_number+" · рейс решения "+task.wait_target_tt_id);
  if (task.source_doc_type) parts.push(task.source_doc_type === "ST_DEFER_CASE" ? "Перенос СТ · CASE" : task.source_doc_type === "ST_DEFER" ? "Перенос СТ" : task.source_doc_type);
  if (task.source_doc_id) parts.push(`#${task.source_doc_id}`);
  if (task.production_order_id) parts.push(`PO ${task.production_order_id}`);
  return parts.join(" ") || "-";
}

function formatQty(qty, unitCode) {
  return `${String(qty ?? "0")} ${unitCode || ""}`.trim();
}

function formatTaskQty(task) {
  const planned = formatQty(task.qty_exact ?? task.qty, task.unit_code);
  if (task.fact_qty === null || task.fact_qty === undefined || task.fact_qty === "") return planned;
  return `${planned} / факт ${formatQty(task.fact_qty_exact ?? task.fact_qty, task.unit_code)}`;
}

function qtyModeText(task) {
  if(task.unit_code==="HU")return "HU · одно место";
  if(task.source_doc_type==="ST_DEFER_CASE" && task.unit_code==="CASE")return "CASE · одно место";
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

async function showWarehouseTaskProgress(taskId) {
  const epoch=warehouseTaskState.readEpoch;
  const identity=JSON.stringify([warehouseTaskApiBase(),window.wmsAdminAuth?.state?.user?.username]);
  const progress = await warehouseTaskFetch(`/api/warehouse-tasks/${taskId}/progress`);
  if (epoch!==warehouseTaskState.readEpoch ||
    identity!==JSON.stringify([warehouseTaskApiBase(),window.wmsAdminAuth?.state?.user?.username]) ||
    Number(warehouseTaskState.selectedTask?.task_id) !== Number(taskId)) return;
  warehouseTaskEl("warehouseTaskProgress").textContent =
    `Подтверждено ${progress.confirmed_quantity}, осталось ${progress.remaining_quantity} ${progress.unit_code || ""}` +
    (progress.next_task_id ? `; следующее задание #${progress.next_task_id}` : `; ${progress.status}`);
  window.warehouseTaskFamily.render(progress,taskId);
}

function initWarehouseTasks() {
  warehouseTaskState.readEpoch++;
  warehouseTaskState.allTasks=[];warehouseTaskState.tasks=[];warehouseTaskState.selectedTask=null;
  renderWarehouseTasks();renderWarehouseTaskSummary();renderWarehouseTaskDetail();
  window.warehouseTaskRecovery.init(warehouseTaskFetch);
  if(!warehouseTaskState.confirmedBound){
  warehouseTaskState.confirmedBound=true;
  window.addEventListener("warehouse-task-confirmed", async event => {
    const result = event.detail.result;
    const message = result.residual_task_id
      ? `Принят факт ${result.quantity}; осталось ${result.remaining_quantity}; следующее задание #${result.residual_task_id}`
      : `Задание #${event.detail.task_id}: факт подтверждён`;
    warehouseTaskEl("warehouseTaskSelectionText").textContent = message;
    try {
      warehouseTaskState.initialTaskId=result.residual_task_id||event.detail.task_id;
      await loadWarehouseTasks();
    } catch (error) { showWarehouseTaskError(error); }
    warehouseTaskEl("warehouseTaskSelectionText").textContent = message;
  });
  }
  loadWarehouseTasks().catch(showWarehouseTaskError);
}

function bindWarehouseTaskControls() {
  const params = new URLSearchParams(window.location.search);
  warehouseTaskState.initialTaskId = Number(params.get("task_id") || 0) || null;
  const preset=params.get("preset");
  if(["all","waiting","wave-pickface","shipping-zone","finished-goods","production-wave"].includes(preset)){
    setWarehouseTaskPreset(preset,false);
  }
  warehouseTaskEl("warehouseTaskRefresh").addEventListener("click", () => loadWarehouseTasks().catch(showWarehouseTaskError));
  warehouseTaskEl("warehouseTaskLoad").addEventListener("click", () => loadWarehouseTasks().catch(showWarehouseTaskError));
  warehouseTaskEl("warehouseTaskSearch").addEventListener("input", () => {
    warehouseTaskState.tasks = applySearch(warehouseTaskState.allTasks);
    renderWarehouseTasks();
    renderWarehouseTaskSummary();
  });
  document.querySelectorAll("[data-task-preset]").forEach((button) => {
    button.addEventListener("click", event => {
      event.preventDefault();
      const url=new URL(window.location.href);
      url.searchParams.set("preset",button.dataset.taskPreset);
      url.searchParams.delete("task_id");
      window.history.replaceState(null,"",url);
      setWarehouseTaskPreset(button.dataset.taskPreset);
    });
  });
  warehouseTaskEl("warehouseTaskAssign").addEventListener("click", () => changeWarehouseTask("assign").catch(showWarehouseTaskError));
  warehouseTaskEl("warehouseTaskStart").addEventListener("click", () => changeWarehouseTask("start").catch(showWarehouseTaskError));
  warehouseTaskEl("warehouseTaskComplete").addEventListener("click", () => changeWarehouseTask("complete").catch(showWarehouseTaskError));
  warehouseTaskEl("warehouseTaskCancel").addEventListener("click", () => changeWarehouseTask("cancel").catch(showWarehouseTaskError));
}
bindWarehouseTaskControls();
window.addEventListener("wms-admin-auth-ready", initWarehouseTasks);
