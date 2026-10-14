const waveReplenishmentState = {
  waves: [],
  tasks: [],
  stagingTasks: [],
  pickFaces: [],
  articuls: [],
  articulRules: [],
  selectedWave: null,
  listEpoch: 0,
  selectionEpoch: 0,
  initialWaveId: null,
  selectedPickFace: null,
  selectedArticul: null,
  selectedArticulRule: null,
};

const waveRepEl = (id) => document.getElementById(id);
const waveRepIdentity=()=>JSON.stringify([waveRepApiBase(),window.wmsAdminAuth?.state?.user?.username]);

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
  waveRepEl("waveReplenishmentStatusText").textContent="Загрузка...";
  const epoch=++waveReplenishmentState.listEpoch,identity=waveRepIdentity(),params=waveRepWaveParams().toString();
  const rows=await waveRepFetch('/api/picking/waves?'+params);
  if(epoch!==waveReplenishmentState.listEpoch||identity!==waveRepIdentity()||params!==waveRepWaveParams().toString())return;
  waveReplenishmentState.waves=rows;
  const query=waveRepEl("waveReplenishmentSearch").value.trim().toLowerCase();
  const waves=query?rows.filter(wave=>[wave.pick_wave_id,wave.wave_code,wave.wave_name,wave.status]
    .some(value=>String(value||'').toLowerCase().includes(query))):rows;
  renderWaveRows(waves);waveRepEl("waveReplenishmentStatusText").textContent='Волн: '+waves.length;
  if(waveReplenishmentState.initialWaveId){
    const id=waveReplenishmentState.initialWaveId;waveReplenishmentState.initialWaveId=null;
    await selectWave(id);
  }
}

function renderWaveRows(waves) {
  const active=waveReplenishmentState.selectedWave;
  const pinned=active&&!waves.some(wave=>Number(wave.pick_wave_id)===Number(active.pick_wave_id));
  if(pinned){waves=[active,...waves];waveRepEl("waveReplenishmentSelectionText").textContent="Волна #"+active.pick_wave_id+" · "+(active.wave_code||"")+" · закреплена вне текущей выборки";}

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
  if(!Number.isSafeInteger(waveId)||waveId<1)return;
  for(const holder of [window.wmsWaveExecutionIntent,window.wmsWavePickIntent]){
    const saved=holder?.read().value;
    if(saved&&saved.wave!==waveId){waveRepEl('waveReplenishmentStatusText').textContent='Сначала повторите сохранённое решение волны '+saved.wave;return;}
  }
  window.dispatchEvent(new CustomEvent('wms-wave-selection-loading',{detail:{wave_id:waveId}}));
  const epoch=++waveReplenishmentState.selectionEpoch,identity=waveRepIdentity();
  waveReplenishmentState.selectedWave=null;waveReplenishmentState.tasks=[];waveReplenishmentState.stagingTasks=[];
  renderReplenishmentTasks();renderStagingTasks();
  waveRepEl("waveReplenishmentSelectionText").textContent='Читаю волну #'+waveId;
  try{
    const wave=waveReplenishmentState.waves.find(item=>Number(item.pick_wave_id)===waveId)||
      await waveRepFetch('/api/picking/waves/'+waveId+'/header');
    if(epoch!==waveReplenishmentState.selectionEpoch||identity!==waveRepIdentity())return;
    if(Number(wave?.pick_wave_id)!==waveId)throw new Error('Ответ не соответствует выбранной волне.');
    waveReplenishmentState.selectedWave=wave;
    waveRepEl("waveReplenishmentSelectionText").textContent='Волна #'+waveId+' · '+(wave.wave_code||'');
    window.dispatchEvent(new CustomEvent('wms-wave-selected',{detail:{wave_id:waveId}}));
    const results=await Promise.allSettled([loadWaveReplenishmentTasks(),loadWaveStagingTasks()]);
    if(epoch!==waveReplenishmentState.selectionEpoch||identity!==waveRepIdentity())return;
    const failed=results.find(result=>result.status==='rejected');if(failed)throw failed.reason;
    renderWaveRows(waveReplenishmentState.waves);
  }catch(error){if(epoch===waveReplenishmentState.selectionEpoch&&identity===waveRepIdentity())showWaveRepError(error);}
}

async function loadWaveReplenishmentTasks() {
  const wave=waveReplenishmentState.selectedWave;if(!wave)return;
  const epoch=waveReplenishmentState.selectionEpoch,identity=waveRepIdentity();
  waveRepEl("waveReplenishmentDetailStatus").textContent="Загрузка пополнений...";
  const rows=await waveRepFetch('/api/picking/waves/'+wave.pick_wave_id+'/replenishment-tasks?limit=500');
  if(epoch!==waveReplenishmentState.selectionEpoch||identity!==waveRepIdentity()||
    waveReplenishmentState.selectedWave?.pick_wave_id!==wave.pick_wave_id)return;
  waveReplenishmentState.tasks=rows;renderReplenishmentTasks();
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
      + `<td><b>${escapeWaveRepHtml(task.pallet_uid || "-")}</b><small>${escapeWaveRepHtml(task.source_cell_code || "-")}</small><button type="button" data-source-task="${escapeWaveRepHtml(task.pick_wave_replenish_task_id)}">Источники</button></td>`
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
  const wave=waveReplenishmentState.selectedWave;if(!wave)return;
  const epoch=waveReplenishmentState.selectionEpoch,identity=waveRepIdentity();
  const rows=await waveRepFetch('/api/picking/waves/'+wave.pick_wave_id+'/tasks?limit=500');
  if(epoch!==waveReplenishmentState.selectionEpoch||identity!==waveRepIdentity()||
    waveReplenishmentState.selectedWave?.pick_wave_id!==wave.pick_wave_id)return;
  waveReplenishmentState.stagingTasks=rows.filter(row=>row.task_type==='FULL_PALLET');renderStagingTasks();
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
      + `<td><span class="task-badge ${waveStatusClass(warehouseStatus)}">${escapeWaveRepHtml(warehouseStatus)}</span>${Number.isSafeInteger(task.warehouse_task_id)&&task.warehouse_task_id>0 ? `<a class="wave-execution-action" href="warehouse-tasks.html?task_id=${task.warehouse_task_id}#warehouseTaskDetail">Выполнить задание #${task.warehouse_task_id}</a>` : ""}</td>`
      + `<td>${escapeWaveRepHtml(task.warehouse_assigned_to || "-")}</td>`
      + "</tr>";
  }).join("") || "<tr><td colspan=\"8\">Нет заданий целых паллет для грузовой зоны</td></tr>";
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
  window.dispatchEvent(new CustomEvent("wms-wave-selected",{detail:{wave_id:wave.pick_wave_id}}));
  await loadWaveReplenishmentTasks();
  waveRepEl("waveReplenishmentDetailStatus").textContent = `Minimax проверен, выпущено: ${result.released_count || 0}`;
}

async function runStagingRelease() {
  const wave=waveReplenishmentState.selectedWave,button=waveRepEl("waveStagingRelease");
  if(!wave||button.disabled)throw new Error("Выберите волну и дождитесь завершения запроса");
  if(!waveRepCan("pick_wave_launch"))throw new Error("Нет права pick_wave_launch");
  const toCell=waveRepEl("waveStagingToCell").value.trim();
  if(!toCell)throw new Error("Укажите грузовую зону");
  const identity=waveRepIdentity(),epoch=waveReplenishmentState.selectionEpoch;
  const current=()=>identity===waveRepIdentity()&&epoch===waveReplenishmentState.selectionEpoch&&waveReplenishmentState.selectedWave?.pick_wave_id===wave.pick_wave_id;
  button.disabled=true;
  waveRepEl("waveReplenishmentDetailStatus").textContent="Выпуск задач в грузовую зону…";
  try{
    const result=await waveRepFetch('/api/picking/waves/'+wave.pick_wave_id+'/staging/release',{
      method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({to_cell:toCell})});
    if(!current())return;
    if(result.pick_wave_id!==wave.pick_wave_id||result.status!=="RELEASED")throw new Error("Ответ не подтверждает выбранную волну");
    await loadWaveStagingTasks();
    if(current())waveRepEl("waveReplenishmentDetailStatus").textContent="В грузовую зону выпущено: "+(result.released_count||0)+". Откройте задания ниже; повтор с тем же адресом не создаёт дубли.";
  }catch(error){
    if(current())waveRepEl("waveReplenishmentDetailStatus").textContent=error.message+". Перечитайте задания перед повтором; сохраняйте прежний адрес назначения.";
  }finally{button.disabled=!waveRepCan("pick_wave_launch");}
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
      + `<td>${escapeWaveRepHtml(row.use_articul_replenish_rule ? "ARTICUL" : (row.replenishment_release_policy || "LAYER_TRIGGER"))}</td>`
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
  waveRepEl("waveRuleInherit").value = String(row?.use_articul_replenish_rule ?? 1);
  waveRepEl("waveRulePolicy").value = row?.replenishment_release_policy || "LAYER_TRIGGER";
  waveRepEl("waveRuleMethod").value = row?.replenishment_method || "IMMEDIATE";
  waveRepEl("waveRuleQtyMode").value = row?.replenishment_qty_mode || "FILL_TO_VOLUME";
  waveRepEl("waveRuleTriggerBoxes").value = row?.min_trigger_box_qty ?? "";
  waveRepEl("waveRuleTriggerLayers").value = row?.min_trigger_layer_qty ?? "";
  waveRepEl("waveRuleSafetyLayers").value = row?.safety_layer_qty ?? "";
  waveRepEl("waveRuleBoxesLayer").value = row?.boxes_per_layer ?? "";
  waveRepEl("waveRuleBoxesPallet").value = row?.boxes_per_pallet ?? "";
  waveRepEl("waveRuleBoxVolume").value = row?.box_volume_m3 ?? "";
  waveRepEl("waveRulePredictiveBuffer").value = row?.predictive_buffer_min ?? "";
  waveRepEl("waveRulePickRateSource").value = row?.pick_rate_source || "MIXED";
  waveRepEl("waveRuleRecheck").value = String(row?.recheck_on_pick_event ?? 1);
  waveRepEl("waveRulePartial").value = String(row?.allow_partial_pallet ?? 1);
}

async function loadArticulRules() {
  const params = new URLSearchParams();
  const articul = waveRepEl("waveArticulRuleFilter").value.trim();
  if (articul) params.set("articul", articul);
  waveReplenishmentState.articulRules = await waveRepFetch(`/api/picking/articul-replenishment-rules?${params.toString()}`);
  renderArticulRules();
  waveRepEl("waveArticulRuleStatus").textContent = `Правил: ${waveReplenishmentState.articulRules.length}`;
}

function renderArticulRules() {
  waveRepEl("waveArticulRuleRows").innerHTML = waveReplenishmentState.articulRules.map((row) => {
    const selected = waveReplenishmentState.selectedArticulRule?.articul_replenish_rule_id === row.articul_replenish_rule_id ? " class=\"selected\"" : "";
    return `<tr${selected} data-articul-rule-id="${escapeWaveRepAttr(row.articul_replenish_rule_id)}">`
      + `<td>${escapeWaveRepHtml(row.articul_replenish_rule_id)}</td>`
      + `<td>${escapeWaveRepHtml(row.articul)}</td>`
      + `<td>${escapeWaveRepHtml(row.replenishment_release_policy || "LAYER_TRIGGER")}</td>`
      + `<td>${escapeWaveRepHtml(row.replenishment_method || "MINIMAX")}</td>`
      + `<td>${escapeWaveRepHtml(row.min_trigger_box_qty || row.min_trigger_layer_qty || "-")}</td>`
      + `<td>${escapeWaveRepHtml(row.pick_rate_source || "MIXED")}</td>`
      + "</tr>";
  }).join("") || "<tr><td colspan=\"6\">Нет правил артикула</td></tr>";
  document.querySelectorAll("#waveArticulRuleRows tr[data-articul-rule-id]").forEach((row) => {
    row.addEventListener("click", () => selectArticulRule(Number(row.dataset.articulRuleId)));
  });
}

function selectArticulRule(ruleId) {
  waveReplenishmentState.selectedArticulRule = waveReplenishmentState.articulRules.find((row) => Number(row.articul_replenish_rule_id) === ruleId) || null;
  renderArticulRules();
  fillArticulRuleForm();
}

function fillArticulRuleForm() {
  const row = waveReplenishmentState.selectedArticulRule;
  waveRepEl("waveArticulRuleArticul").value = row?.articul || waveRepEl("waveArticulRuleFilter").value.trim() || waveRepEl("waveReplenishmentPickArticul").value.trim();
  waveRepEl("waveArticulRulePolicy").value = row?.replenishment_release_policy || "LAYER_TRIGGER";
  waveRepEl("waveArticulRuleMethod").value = row?.replenishment_method || "MINIMAX";
  waveRepEl("waveArticulRuleQtyMode").value = row?.replenishment_qty_mode || "FILL_TO_VOLUME";
  waveRepEl("waveArticulRuleTriggerBoxes").value = row?.min_trigger_box_qty ?? "";
  waveRepEl("waveArticulRuleTriggerLayers").value = row?.min_trigger_layer_qty ?? 1;
  waveRepEl("waveArticulRuleSafetyLayers").value = row?.safety_layer_qty ?? "";
  waveRepEl("waveArticulRuleBoxesLayer").value = row?.boxes_per_layer ?? "";
  waveRepEl("waveArticulRuleBoxesPallet").value = row?.boxes_per_pallet ?? "";
  waveRepEl("waveArticulRuleBoxVolume").value = row?.box_volume_m3 ?? "";
  waveRepEl("waveArticulRulePredictiveBuffer").value = row?.predictive_buffer_min ?? "";
  waveRepEl("waveArticulRulePickRateSource").value = row?.pick_rate_source || "MIXED";
  waveRepEl("waveArticulRuleRecheck").value = String(row?.recheck_on_pick_event ?? 1);
  waveRepEl("waveArticulRulePartial").value = String(row?.allow_partial_pallet ?? 1);
}

async function saveArticulRule() {
  if (!waveRepCan("pick_topology_edit")) throw new Error("Нет права pick_topology_edit");
  const current = waveReplenishmentState.selectedArticulRule;
  const payload = {
    articul_replenish_rule_id: current?.articul_replenish_rule_id || null,
    articul: waveRepEl("waveArticulRuleArticul").value.trim(),
    replenishment_method: waveRepEl("waveArticulRuleMethod").value,
    replenishment_release_policy: waveRepEl("waveArticulRulePolicy").value,
    replenishment_qty_mode: waveRepEl("waveArticulRuleQtyMode").value,
    min_trigger_box_qty: numberOrNull(waveRepEl("waveArticulRuleTriggerBoxes").value),
    min_trigger_layer_qty: numberOrNull(waveRepEl("waveArticulRuleTriggerLayers").value),
    safety_layer_qty: numberOrNull(waveRepEl("waveArticulRuleSafetyLayers").value),
    boxes_per_layer: numberOrNull(waveRepEl("waveArticulRuleBoxesLayer").value),
    boxes_per_pallet: numberOrNull(waveRepEl("waveArticulRuleBoxesPallet").value),
    box_volume_m3: numberOrNull(waveRepEl("waveArticulRuleBoxVolume").value),
    predictive_buffer_min: numberOrNull(waveRepEl("waveArticulRulePredictiveBuffer").value),
    pick_rate_source: waveRepEl("waveArticulRulePickRateSource").value,
    recheck_on_pick_event: Number(waveRepEl("waveArticulRuleRecheck").value),
    allow_partial_pallet: Number(waveRepEl("waveArticulRulePartial").value),
    active: current?.active ?? 1,
    updated_by: waveRepUser(),
  };
  if (!payload.articul) throw new Error("Укажите артикул");
  await waveRepFetch("/api/picking/articul-replenishment-rules", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  waveRepEl("waveArticulRuleFilter").value = payload.articul;
  await loadArticulRules();
  waveRepEl("waveArticulRuleStatus").textContent = "Сохранено";
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
    use_articul_replenish_rule: Number(waveRepEl("waveRuleInherit").value),
    replenishment_method: waveRepEl("waveRuleMethod").value,
    replenishment_release_policy: waveRepEl("waveRulePolicy").value,
    replenishment_qty_mode: waveRepEl("waveRuleQtyMode").value,
    min_trigger_box_qty: numberOrNull(waveRepEl("waveRuleTriggerBoxes").value),
    min_trigger_layer_qty: numberOrNull(waveRepEl("waveRuleTriggerLayers").value),
    safety_layer_qty: numberOrNull(waveRepEl("waveRuleSafetyLayers").value),
    boxes_per_layer: numberOrNull(waveRepEl("waveRuleBoxesLayer").value),
    boxes_per_pallet: numberOrNull(waveRepEl("waveRuleBoxesPallet").value),
    box_volume_m3: numberOrNull(waveRepEl("waveRuleBoxVolume").value),
    predictive_buffer_min: numberOrNull(waveRepEl("waveRulePredictiveBuffer").value),
    pick_rate_source: waveRepEl("waveRulePickRateSource").value,
    recheck_on_pick_event: Number(waveRepEl("waveRuleRecheck").value),
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
  waveRepEl("waveArticulRuleStatus").textContent = error.message;
}

function initWaveReplenishmentPage() {
  const linkedWare=Number(new URLSearchParams(location.search).get("ware_id"));
  if(Number.isSafeInteger(linkedWare)&&linkedWare>0)waveRepEl("waveReplenishmentWareId").value=String(linkedWare);
  waveReplenishmentState.initialWaveId=Number(new URLSearchParams(location.search).get('wave_id'))||null;
  waveRepEl("waveReplenishmentLoad").addEventListener("click", () => loadWaveReplenishmentWaves().catch(showWaveRepError));
  waveRepEl("waveReplenishmentRefresh").addEventListener("click", () => loadWaveReplenishmentWaves().catch(showWaveRepError));
  waveRepEl("waveReplenishmentSearch").addEventListener("input", () => loadWaveReplenishmentWaves().catch(showWaveRepError));
  waveRepEl("waveReplenishmentTaskFilter").addEventListener("change", renderReplenishmentTasks);
  waveRepEl("waveReplenishmentMinimaxCheck").addEventListener("click", () => runMinimaxCheck().catch(showWaveRepError));
  waveRepEl("waveStagingRelease").addEventListener("click", () => runStagingRelease().catch(showWaveRepError));
  waveRepEl("waveReplenishmentPickLoad").addEventListener("click", () => loadPickFaces().catch(showWaveRepError));
  waveRepEl("waveArticulRuleLoad").addEventListener("click", () => loadArticulRules().catch(showWaveRepError));
  waveRepEl("waveArticulRuleSave").addEventListener("click", () => saveArticulRule().catch(showWaveRepError));
  waveRepEl("waveRuleSave").addEventListener("click", () => saveRule().catch(showWaveRepError));
  loadWaveReplenishmentWaves().catch(showWaveRepError);
  loadArticulRules().catch(showWaveRepError);
}

let waveQueueInitialized=false;
window.addEventListener('wms-admin-auth-ready',()=>{
  if(!waveQueueInitialized){waveQueueInitialized=true;initWaveReplenishmentPage();return;}
  waveReplenishmentState.listEpoch++;waveReplenishmentState.selectionEpoch++;
  waveReplenishmentState.waves=[];waveReplenishmentState.selectedWave=null;
  waveReplenishmentState.tasks=[];waveReplenishmentState.stagingTasks=[];
  renderWaveRows([]);renderReplenishmentTasks();renderStagingTasks();
  waveRepEl('waveReplenishmentSelectionText').textContent='Выберите волну в текущем контексте';
  loadWaveReplenishmentWaves().catch(showWaveRepError);
});

window.addEventListener('wms-wave-requested',event=>{const wave=Number(event.detail?.wave_id);if(Number.isSafeInteger(wave)&&wave>0)void selectWave(wave);else window.dispatchEvent(new CustomEvent('wms-wave-selection-loading',{detail:{wave_id:null}}));});
