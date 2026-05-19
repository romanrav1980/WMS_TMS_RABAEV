const waveReplenishmentState = {
  waves: [],
  tasks: [],
  stagingTasks: [],
  pickFaces: [],
  articuls: [],
  selectedWave: null,
  selectedPickFace: null,
  selectedArticul: null,
};

const waveRepEl = (id) => document.getElementById(id);

function waveRepApiBase() {
  return (window.wmsAdminAuth?.state?.apiBase || "http://127.0.0.1:8088").replace(/\/$/, "");
}

function waveRepHeaders(extra = {}) {
  if (!window.wmsAdminAuth) return { ...extra };
  return window.wmsAdminAuth.headers(extra);
}

function waveRepUser() {
  return window.wmsAdminAuth?.state?.user?.username || "admin";
}

function waveRepCan(permission) {
  return window.wmsAdminAuth && window.wmsAdminAuth.hasPermission(permission);
}

async function waveRepFetch(path, options = {}) {
  const response = await fetch(`${waveRepApiBase()}${path}`, {
    ...options,
    headers: waveRepHeaders(options.headers || {}),
  });
  const text = await response.text();
  const body = text ? JSON.parse(text) : {};
  if (!response.ok) {
    const detail = body.detail?.message || body.detail || body.message || `HTTP ${response.status}`;
    throw new Error(typeof detail === "string" ? detail : JSON.stringify(detail));
  }
  return body;
}

function waveRepWaveParams() {
  const params = new URLSearchParams();
  const status = waveRepEl("waveReplenishmentWaveStatus").value;
  const wareId = waveRepEl("waveReplenishmentWareId").value;
  if (status) params.set("status", status);
  if (wareId) params.set("ware_id", wareId);
  params.set("limit", waveRepEl("waveReplenishmentLimit").value || "100");
  return params;
}

async function loadWaveReplenishmentWaves() {
  waveRepEl("waveReplenishmentStatusText").textContent = "Загрузка...";
  waveReplenishmentState.waves = await waveRepFetch(`/api/picking/waves?${waveRepWaveParams().toString()}`);
  const query = waveRepEl("waveReplenishmentSearch").value.trim().toLowerCase();
  const waves = query
    ? waveReplenishmentState.waves.filter((wave) => [wave.pick_wave_id, wave.wave_code, wave.wave_name, wave.status].some((value) => String(value || "").toLowerCase().includes(query)))
    : waveReplenishmentState.waves;
  renderWaveRows(waves);
  waveRepEl("waveReplenishmentStatusText").textContent = `Волн: ${waves.length}`;
  const requestedWaveId = Number(new URLSearchParams(window.location.search).get("wave_id") || 0);
  if (requestedWaveId && waveReplenishmentState.selectedWave?.pick_wave_id !== requestedWaveId) {
    const requestedWave = waveReplenishmentState.waves.find((wave) => Number(wave.pick_wave_id) === requestedWaveId);
    if (requestedWave) await selectWave(requestedWaveId);
  }
}

function renderWaveRows(waves) {
  waveRepEl("waveReplenishmentWaveRows").innerHTML = waves.map((wave) => {
    const selected = waveReplenishmentState.selectedWave?.pick_wave_id === wave.pick_wave_id ? " class=\"selected\"" : "";
    return `<tr${selected} data-wave-id="${escapeWaveRepAttr(wave.pick_wave_id)}">`
      + `<td>${escapeWaveRepHtml(wave.pick_wave_id)}</td>`
      + `<td><b>${escapeWaveRepHtml(wave.wave_code || "-")}</b><small>${escapeWaveRepHtml(wave.wave_name || "")}</small></td>`
      + `<td><span class="task-badge ${waveStatusClass(wave.status)}">${escapeWaveRepHtml(wave.status)}</span></td>`
      + `<td>${escapeWaveRepHtml(wave.ware_name || wave.ware_id || "-")}</td>`
      + `<td>${escapeWaveRepHtml(wave.order_count || 0)}</td>`
      + `<td>${escapeWaveRepHtml(wave.task_count || 0)}</td>`
      + "</tr>";
  }).join("") || "<tr><td colspan=\"6\">Нет волн</td></tr>";
  document.querySelectorAll("#waveReplenishmentWaveRows tr[data-wave-id]").forEach((row) => {
    row.addEventListener("click", () => selectWave(Number(row.dataset.waveId)));
  });
}

async function selectWave(waveId) {
  waveReplenishmentState.selectedWave = waveReplenishmentState.waves.find((wave) => Number(wave.pick_wave_id) === waveId) || null;
  waveRepEl("waveReplenishmentSelectionText").textContent = waveReplenishmentState.selectedWave ? `Волна #${waveId}` : "Волна не выбрана";
  await loadWaveReplenishmentTasks();
  await loadWaveStagingTasks();
  renderWaveRows(waveReplenishmentState.waves);
}

async function loadWaveReplenishmentTasks() {
  const wave = waveReplenishmentState.selectedWave;
  if (!wave) return;
  waveRepEl("waveReplenishmentDetailStatus").textContent = "Загрузка пополнений...";
  waveReplenishmentState.tasks = await waveRepFetch(`/api/picking/waves/${wave.pick_wave_id}/replenishment-tasks?limit=500`);
  renderReplenishmentTasks();
}

function renderReplenishmentTasks() {
  const tasks = waveReplenishmentState.tasks;
  const filtered = filterReplenishmentTasks(tasks);
  const waitingStatuses = new Set(["QUEUED", "WAIT_FREE_CELL", "WAIT_MINIMAX"]);
  waveRepEl("waveReplenishmentKpiQueued").textContent = tasks.filter((task) => task.status === "QUEUED").length;
  waveRepEl("waveReplenishmentKpiWait").textContent = tasks.filter((task) => waitingStatuses.has(task.status)).length;
  waveRepEl("waveReplenishmentKpiDriver").textContent = tasks.filter((task) => task.warehouse_task_id && task.warehouse_task_status !== "DONE").length;
  waveRepEl("waveReplenishmentKpiDone").textContent = tasks.filter((task) => task.status === "DONE").length;
  waveRepEl("waveReplenishmentDetailStatus").textContent = `Строк пополнения: ${filtered.length} / ${tasks.length}`;
  waveRepEl("waveReplenishmentTaskRows").innerHTML = filtered.map((task) => {
    const state = replenishmentQueueState(task);
    const sourceReservation = task.source_reservation_id
      ? `#${task.source_reservation_id}${task.source_available_qty ? ` / ${formatWaveRepQty(task.source_available_qty)}` : ""}`
      : "-";
    const whtStatus = task.warehouse_task_id
      ? `${task.warehouse_task_id} / ${task.warehouse_task_status || "PLANNED"}`
      : "не выпущено";
    const reason = task.wait_reason || replenishmentReasonFallback(task);
    return "<tr>"
      + `<td>${escapeWaveRepHtml(task.pick_wave_replenish_task_id)}</td>`
      + `<td><span class="task-badge ${waveStatusClass(task.status)}">${escapeWaveRepHtml(task.status)}</span><small>${escapeWaveRepHtml(state)}</small></td>`
      + `<td><b>${escapeWaveRepHtml(task.articul)}</b><small>${escapeWaveRepHtml(task.replenishment_method || "-")} / ${escapeWaveRepHtml(task.replenishment_qty_mode || "-")}</small></td>`
      + `<td><b>${escapeWaveRepHtml(task.pallet_uid || "-")}</b><small>${escapeWaveRepHtml(task.source_cell_code || "-")}</small></td>`
      + `<td>${escapeWaveRepHtml(task.target_cell_code || "-")}</td>`
      + `<td>${escapeWaveRepHtml(formatWaveRepQty(task.qty))}</td>`
      + `<td>${escapeWaveRepHtml(sourceReservation)}</td>`
      + `<td><span class="task-badge ${waveStatusClass(task.warehouse_task_status || task.status)}">${escapeWaveRepHtml(whtStatus)}</span></td>`
      + `<td><small>${escapeWaveRepHtml(reason)}</small></td>`
      + "</tr>";
  }).join("") || "<tr><td colspan=\"9\">Нет строк пополнения</td></tr>";
}

function filterReplenishmentTasks(tasks) {
  const value = waveRepEl("waveReplenishmentTaskFilter")?.value || "";
  if (!value) return tasks;
  const waitingStatuses = new Set(["QUEUED", "WAIT_FREE_CELL", "WAIT_MINIMAX"]);
  if (value === "WAITING") return tasks.filter((task) => waitingStatuses.has(task.status));
  if (value === "DRIVER") return tasks.filter((task) => task.warehouse_task_id && task.warehouse_task_status !== "DONE");
  return tasks.filter((task) => task.status === value);
}

function replenishmentQueueState(task) {
  if (task.warehouse_task_id && task.warehouse_task_status !== "DONE") return "у водителя";
  if (task.status === "DONE") return "закрыто";
  if (task.status === "QUEUED") return "fixed-очередь";
  if (task.status === "WAIT_FREE_CELL") return "ждет dynamic";
  if (task.status === "WAIT_MINIMAX") return "ждет Minimax";
  if (task.status === "RELEASED") return "выпуск";
  if (task.status === "FAILED") return "ошибка";
  return "домен";
}

function replenishmentReasonFallback(task) {
  if (task.status === "QUEUED") return "Ждет закрытия предыдущей задачи по fixed pick-face или свободную dynamic ячейку.";
  if (task.status === "WAIT_FREE_CELL") return "Ждет свободную неприкрепленную ячейку отбора.";
  if (task.status === "WAIT_MINIMAX") return "Ждет снижения остатка до Minimax-порога.";
  if (!task.warehouse_task_id && task.source_reservation_id) return "Источник зарезервирован, водительская задача еще не выпущена.";
  return "";
}

async function loadWaveStagingTasks() {
  const wave = waveReplenishmentState.selectedWave;
  if (!wave) return;
  const rows = await waveRepFetch(`/api/picking/waves/${wave.pick_wave_id}/tasks?limit=500`);
  waveReplenishmentState.stagingTasks = rows.filter((row) => row.task_type === "FULL_PALLET");
  renderStagingTasks();
}

function renderStagingTasks() {
  const rows = waveReplenishmentState.stagingTasks;
  waveRepEl("waveStagingTaskRows").innerHTML = rows.map((task) => {
    const warehouseStatus = task.warehouse_task_status || (task.warehouse_task_id ? "PLANNED" : "Не выпущено");
    return "<tr>"
      + `<td>${escapeWaveRepHtml(task.pick_wave_task_id)}</td>`
      + `<td><span class="task-badge ${waveStatusClass(task.status)}">${escapeWaveRepHtml(task.status)}</span></td>`
      + `<td>${escapeWaveRepHtml(task.articul)}</td>`
      + `<td><b>${escapeWaveRepHtml(task.pallet_uid || "-")}</b><small>${escapeWaveRepHtml(formatWaveRepQty(task.qty))}</small></td>`
      + `<td>${escapeWaveRepHtml(task.source_cell_code || "-")}</td>`
      + `<td>${escapeWaveRepHtml(task.target_cell_code || "-")}</td>`
      + `<td><span class="task-badge ${waveStatusClass(warehouseStatus)}">${escapeWaveRepHtml(warehouseStatus)}</span><small>${escapeWaveRepHtml(task.warehouse_task_id || "")}</small></td>`
      + `<td>${escapeWaveRepHtml(task.warehouse_assigned_to || "-")}</td>`
      + "</tr>";
  }).join("") || "<tr><td colspan=\"8\">Нет full-pallet строк для грузовой зоны</td></tr>";
}

async function runMinimaxCheck() {
  const wave = waveReplenishmentState.selectedWave;
  if (!wave) throw new Error("Выберите волну");
  if (!waveRepCan("pick_wave_launch")) throw new Error("Нет права pick_wave_launch");
  waveRepEl("waveReplenishmentDetailStatus").textContent = "Проверка Minimax...";
  const result = await waveRepFetch(`/api/picking/waves/${wave.pick_wave_id}/replenishment/minimax-check`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ updated_by: waveRepUser() }),
  });
  await loadWaveReplenishmentTasks();
  waveRepEl("waveReplenishmentDetailStatus").textContent = `Minimax проверен, выпущено: ${result.released_count || 0}`;
}

async function runStagingRelease() {
  const wave = waveReplenishmentState.selectedWave;
  if (!wave) throw new Error("Выберите волну");
  if (!waveRepCan("pick_wave_launch")) throw new Error("Нет права pick_wave_launch");
  const toCell = waveRepEl("waveStagingToCell").value.trim();
  if (!toCell) throw new Error("Укажите грузовую зону");
  waveRepEl("waveReplenishmentDetailStatus").textContent = "Выпуск задач в грузовую зону...";
  const result = await waveRepFetch(`/api/picking/waves/${wave.pick_wave_id}/staging/release`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ to_cell: toCell, updated_by: waveRepUser() }),
  });
  await loadWaveStagingTasks();
  waveRepEl("waveReplenishmentDetailStatus").textContent = `В грузовую зону выпущено: ${result.released_count || 0}`;
}

async function loadPickFaces() {
  const params = new URLSearchParams();
  const wareId = waveRepEl("waveReplenishmentPickWareId").value;
  const articul = waveRepEl("waveReplenishmentPickArticul").value.trim();
  if (wareId) params.set("ware_id", wareId);
  if (articul) params.set("articul", articul);
  params.set("active_only", "1");
  waveRepEl("waveReplenishmentPickStatus").textContent = "Загрузка...";
  waveReplenishmentState.pickFaces = await waveRepFetch(`/api/picking/pick-faces?${params.toString()}`);
  renderPickFaces();
}

function renderPickFaces() {
  waveRepEl("waveReplenishmentPickStatus").textContent = `Pick-face: ${waveReplenishmentState.pickFaces.length}`;
  waveRepEl("waveReplenishmentPickFaceRows").innerHTML = waveReplenishmentState.pickFaces.map((face) => {
    const selected = waveReplenishmentState.selectedPickFace?.pick_face_id === face.pick_face_id ? " class=\"selected\"" : "";
    return `<tr${selected} data-pick-face-id="${escapeWaveRepAttr(face.pick_face_id)}">`
      + `<td>${escapeWaveRepHtml(face.pick_face_id)}</td>`
      + `<td><b>${escapeWaveRepHtml(face.cell_code)}</b><small>${escapeWaveRepHtml(face.pick_face_code || "")}</small></td>`
      + `<td>${escapeWaveRepHtml(face.ware_name || face.ware_id || "-")}</td>`
      + `<td>${escapeWaveRepHtml(face.articul_count || 0)}</td>`
      + "</tr>";
  }).join("") || "<tr><td colspan=\"4\">Нет pick-face</td></tr>";
  document.querySelectorAll("#waveReplenishmentPickFaceRows tr[data-pick-face-id]").forEach((row) => {
    row.addEventListener("click", () => selectPickFace(Number(row.dataset.pickFaceId)));
  });
}

async function selectPickFace(pickFaceId) {
  waveReplenishmentState.selectedPickFace = waveReplenishmentState.pickFaces.find((face) => Number(face.pick_face_id) === pickFaceId) || null;
  waveReplenishmentState.selectedArticul = null;
  await loadPickFaceArticuls();
  renderPickFaces();
}

async function loadPickFaceArticuls() {
  const face = waveReplenishmentState.selectedPickFace;
  if (!face) return;
  waveReplenishmentState.articuls = await waveRepFetch(`/api/picking/pick-faces/${face.pick_face_id}/articuls`);
  renderPickFaceArticuls();
}

function renderPickFaceArticuls() {
  waveRepEl("waveReplenishmentPickArticulRows").innerHTML = waveReplenishmentState.articuls.map((row) => {
    const selected = waveReplenishmentState.selectedArticul?.pick_face_articul_id === row.pick_face_articul_id ? " class=\"selected\"" : "";
    return `<tr${selected} data-pick-articul-id="${escapeWaveRepAttr(row.pick_face_articul_id)}">`
      + `<td>${escapeWaveRepHtml(row.pick_face_articul_id)}</td>`
      + `<td>${escapeWaveRepHtml(row.articul)}</td>`
      + `<td>${escapeWaveRepHtml(row.replenishment_method || "IMMEDIATE")}</td>`
      + `<td>${escapeWaveRepHtml(row.replenishment_qty_mode || "FILL_TO_VOLUME")}</td>`
      + `<td>${escapeWaveRepHtml(row.min_trigger_box_qty || row.min_trigger_layer_qty || "-")}</td>`
      + `<td>${escapeWaveRepHtml(row.boxes_per_pallet || "-")}</td>`
      + "</tr>";
  }).join("") || "<tr><td colspan=\"6\">Нет артикулов</td></tr>";
  document.querySelectorAll("#waveReplenishmentPickArticulRows tr[data-pick-articul-id]").forEach((row) => {
    row.addEventListener("click", () => selectPickArticul(Number(row.dataset.pickArticulId)));
  });
}

function selectPickArticul(pickFaceArticulId) {
  waveReplenishmentState.selectedArticul = waveReplenishmentState.articuls.find((row) => Number(row.pick_face_articul_id) === pickFaceArticulId) || null;
  renderPickFaceArticuls();
  fillRuleForm();
}

function fillRuleForm() {
  const row = waveReplenishmentState.selectedArticul;
  waveRepEl("waveReplenishmentRuleStatus").textContent = row ? `Правило #${row.pick_face_articul_id}` : "Выберите строку артикула";
  waveRepEl("waveRuleArticul").value = row?.articul || waveRepEl("waveReplenishmentPickArticul").value.trim();
  waveRepEl("waveRuleMethod").value = row?.replenishment_method || "IMMEDIATE";
  waveRepEl("waveRuleQtyMode").value = row?.replenishment_qty_mode || "FILL_TO_VOLUME";
  waveRepEl("waveRuleTriggerBoxes").value = row?.min_trigger_box_qty ?? "";
  waveRepEl("waveRuleTriggerLayers").value = row?.min_trigger_layer_qty ?? "";
  waveRepEl("waveRuleBoxesLayer").value = row?.boxes_per_layer ?? "";
  waveRepEl("waveRuleBoxesPallet").value = row?.boxes_per_pallet ?? "";
  waveRepEl("waveRuleBoxVolume").value = row?.box_volume_m3 ?? "";
  waveRepEl("waveRulePartial").value = String(row?.allow_partial_pallet ?? 1);
}

async function saveRule() {
  const face = waveReplenishmentState.selectedPickFace;
  if (!face) throw new Error("Выберите pick-face");
  if (!waveRepCan("pick_topology_edit")) throw new Error("Нет права pick_topology_edit");
  const current = waveReplenishmentState.selectedArticul;
  const payload = {
    pick_face_articul_id: current?.pick_face_articul_id || null,
    articul: waveRepEl("waveRuleArticul").value.trim(),
    priority: current?.priority || 100,
    min_qty: current?.min_qty ?? null,
    max_qty: current?.max_qty ?? null,
    case_pick_enabled: current?.case_pick_enabled ?? 1,
    replenishment_method: waveRepEl("waveRuleMethod").value,
    replenishment_qty_mode: waveRepEl("waveRuleQtyMode").value,
    min_trigger_box_qty: numberOrNull(waveRepEl("waveRuleTriggerBoxes").value),
    min_trigger_layer_qty: numberOrNull(waveRepEl("waveRuleTriggerLayers").value),
    boxes_per_layer: numberOrNull(waveRepEl("waveRuleBoxesLayer").value),
    boxes_per_pallet: numberOrNull(waveRepEl("waveRuleBoxesPallet").value),
    box_volume_m3: numberOrNull(waveRepEl("waveRuleBoxVolume").value),
    allow_partial_pallet: Number(waveRepEl("waveRulePartial").value),
    active: current?.active ?? 1,
    updated_by: waveRepUser(),
  };
  if (!payload.articul) throw new Error("Укажите артикул");
  await waveRepFetch(`/api/picking/pick-faces/${face.pick_face_id}/articuls`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  await loadPickFaceArticuls();
  waveRepEl("waveReplenishmentRuleStatus").textContent = "Сохранено";
}

function numberOrNull(value) {
  return value === "" || value === null || value === undefined ? null : Number(value);
}

function formatWaveRepQty(value) {
  const number = Number(value || 0);
  return Number.isInteger(number) ? String(number) : number.toFixed(3);
}

function waveStatusClass(status) {
  if (status === "DONE") return "done";
  if (status === "CANCELLED") return "cancelled";
  if (status === "FAILED" || status === "ERROR") return "error";
  if (status === "QUEUED" || status === "WAIT_FREE_CELL" || status === "WAIT_MINIMAX") return "progress";
  if (status === "RELEASED" || status === "PLANNED" || status === "ASSIGNED" || status === "IN_PROGRESS") return "planned";
  return "planned";
}

function escapeWaveRepHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;");
}

function escapeWaveRepAttr(value) {
  return escapeWaveRepHtml(value).replaceAll('"', "&quot;");
}

function showWaveRepError(error) {
  waveRepEl("waveReplenishmentStatusText").textContent = error.message;
  waveRepEl("waveReplenishmentDetailStatus").textContent = error.message;
  waveRepEl("waveReplenishmentPickStatus").textContent = error.message;
}

function initWaveReplenishmentPage() {
  waveRepEl("waveReplenishmentLoad").addEventListener("click", () => loadWaveReplenishmentWaves().catch(showWaveRepError));
  waveRepEl("waveReplenishmentRefresh").addEventListener("click", () => loadWaveReplenishmentWaves().catch(showWaveRepError));
  waveRepEl("waveReplenishmentSearch").addEventListener("input", () => loadWaveReplenishmentWaves().catch(showWaveRepError));
  waveRepEl("waveReplenishmentTaskFilter").addEventListener("change", renderReplenishmentTasks);
  waveRepEl("waveReplenishmentMinimaxCheck").addEventListener("click", () => runMinimaxCheck().catch(showWaveRepError));
  waveRepEl("waveStagingRelease").addEventListener("click", () => runStagingRelease().catch(showWaveRepError));
  waveRepEl("waveReplenishmentPickLoad").addEventListener("click", () => loadPickFaces().catch(showWaveRepError));
  waveRepEl("waveRuleSave").addEventListener("click", () => saveRule().catch(showWaveRepError));
  loadWaveReplenishmentWaves().catch(showWaveRepError);
}

window.addEventListener("wms-admin-auth-ready", initWaveReplenishmentPage, { once: true });
