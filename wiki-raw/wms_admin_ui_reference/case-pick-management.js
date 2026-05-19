const caseState = {
  tasks: [],
  shorts: [],
  selectedId: null,
  demo: false,
};

const demoTasks = [
  { case_pick_task_id: 1, assigned_to: "Иванов И.И.", equipment_code: "T-01", trolley_capacity: "3 паллета", wave_code: "R-15", route: "Маршрут A", sscc: "SSCC-000125", pallet_count_text: "2 из 2", total_lines: 60, picked_lines: 54, planned_qty: 60, picked_qty: 54, status: "IN_PROGRESS", problem: "", last_action: "2 мин назад\nСканирован ящик", efficiency: 115, zone_code: "A", customer_name: "ООО Мегаполис" },
  { case_pick_task_id: 2, assigned_to: "Петров П.П.", equipment_code: "T-02", trolley_capacity: "2 паллета", wave_code: "R-18", route: "Маршрут B", sscc: "SSCC-000128", pallet_count_text: "1 из 1", total_lines: 60, picked_lines: 42, planned_qty: 60, picked_qty: 42, status: "IN_PROGRESS", problem: "", last_action: "3 мин назад\nСканирован товар", efficiency: 110, zone_code: "B", customer_name: "АО Восток" },
  { case_pick_task_id: 3, assigned_to: "Сидоров С.С.", equipment_code: "T-03", trolley_capacity: "3 паллета", wave_code: "R-15", route: "Маршрут A", sscc: "SSCC-000131", pallet_count_text: "3 из 3", total_lines: 60, picked_lines: 33, planned_qty: 60, picked_qty: 33, status: "PARTIAL", problem: "Нехватка товара\nЯчейка A1-02-01", last_action: "8 мин назад\nОжидает пополнения", efficiency: 88, zone_code: "A", customer_name: "ООО Трейд-Сервис" },
  { case_pick_task_id: 4, assigned_to: "Кузнецов К.К.", equipment_code: "T-04", trolley_capacity: "1 паллета", wave_code: "R-21", route: "Маршрут C", sscc: "SSCC-000133", pallet_count_text: "1 из 1", total_lines: 60, picked_lines: 24, planned_qty: 60, picked_qty: 24, status: "IN_PROGRESS", problem: "Переезд\nB1-04-05 -> C1-02-01", last_action: "1 мин назад\nНаправляется в C1", efficiency: 92, zone_code: "C", customer_name: "ИП Петров" },
  { case_pick_task_id: 5, assigned_to: "Морозов М.С.", equipment_code: "T-05", trolley_capacity: "2 паллета", wave_code: "R-18", route: "Маршрут B", sscc: "SSCC-000134", pallet_count_text: "2 из 2", total_lines: 60, picked_lines: 18, planned_qty: 60, picked_qty: 18, status: "IN_PROGRESS", problem: "", last_action: "5 мин назад\nСканирован товар", efficiency: 65, zone_code: "B", customer_name: "ООО Продукты+" },
  { case_pick_task_id: 6, assigned_to: "Нюшков Н.А.", equipment_code: "T-06", trolley_capacity: "1 паллета", wave_code: "R-22", route: "Маршрут D", sscc: "SSCC-000136", pallet_count_text: "1 из 1", total_lines: 60, picked_lines: 15, planned_qty: 60, picked_qty: 15, status: "IN_PROGRESS", problem: "", last_action: "7 мин назад\nСканирован ящик", efficiency: 58, zone_code: "D", customer_name: "ООО Ритейл" },
  { case_pick_task_id: 7, assigned_to: "Волков В.В.", equipment_code: "T-07", trolley_capacity: "3 паллета", wave_code: "R-21", route: "Маршрут C", sscc: "SSCC-000137", pallet_count_text: "3 из 3", total_lines: 60, picked_lines: 6, planned_qty: 60, picked_qty: 6, status: "FAILED", problem: "Не начал работу\nЗадание получено", last_action: "10 мин назад\nСканирован товар", efficiency: 25, zone_code: "C", customer_name: "ООО Склад" },
  { case_pick_task_id: 8, assigned_to: "Тарасов Т.А.", equipment_code: "T-08", trolley_capacity: "1 паллета", wave_code: "R-15", route: "Маршрут A", sscc: "SSCC-000128", pallet_count_text: "1 из 1", total_lines: 60, picked_lines: 0, planned_qty: 60, picked_qty: 0, status: "NEW", problem: "", last_action: "25 мин назад\nЗадание получено", efficiency: 0, zone_code: "A", customer_name: "ООО Омега" },
  { case_pick_task_id: 9, assigned_to: "Афанасьев А.А.", equipment_code: "T-09", trolley_capacity: "2 паллета", wave_code: "R-22", route: "Маршрут D", sscc: "SSCC-000138", pallet_count_text: "2 из 2", total_lines: 40, picked_lines: 0, planned_qty: 40, picked_qty: 0, status: "NEW", problem: "", last_action: "15 мин назад\nНет активности", efficiency: 0, zone_code: "D", customer_name: "ООО Сфера" },
  { case_pick_task_id: 10, assigned_to: "Гордеев Г.Г.", equipment_code: "T-10", trolley_capacity: "1 паллета", wave_code: "R-19", route: "Маршрут E", sscc: "SSCC-000140", pallet_count_text: "1 из 1", total_lines: 50, picked_lines: 0, planned_qty: 50, picked_qty: 0, status: "OFFLINE", problem: "Оффлайн\nНет активности 50 мин", last_action: "35 мин назад\nНет задач", efficiency: 0, zone_code: "E", customer_name: "ООО Фуд" },
  { case_pick_task_id: 11, assigned_to: "Дмитриев Д.Д.", equipment_code: "T-11", trolley_capacity: "2 паллета", wave_code: "R-19", route: "Маршрут E", sscc: "SSCC-000139", pallet_count_text: "2 из 2", total_lines: 50, picked_lines: 0, planned_qty: 50, picked_qty: 0, status: "WAITING", problem: "", last_action: "12 мин назад\nНет задания", efficiency: 0, zone_code: "E", customer_name: "ООО Линия" },
];

const demoShorts = [
  { case_pick_short_id: 1, case_pick_task_id: 3, sscc: "SSCC-000131", articul: "128456", cell_code: "A1-02-01", short_qty: 3, status: "PENDING_APPROVAL", created_by: "Сидоров С.С.", reason_text: "Нехватка товара" },
  { case_pick_short_id: 2, case_pick_task_id: 7, sscc: "SSCC-000137", articul: "200143", cell_code: "C2-03-01", short_qty: 1, status: "PENDING_APPROVAL", created_by: "Волков В.В.", reason_text: "Не начал работу" },
];

function caseApiBase() {
  return (window.wmsAdminAuth?.state?.apiBase || "http://127.0.0.1:8088").replace(/\/$/, "");
}

function caseHeaders(extra = {}) {
  return window.wmsAdminAuth ? window.wmsAdminAuth.headers(extra) : { ...extra };
}

async function caseFetch(path, options = {}) {
  const response = await fetch(`${caseApiBase()}${path}`, { ...options, headers: caseHeaders(options.headers || {}) });
  const text = await response.text();
  const body = text ? JSON.parse(text) : {};
  if (!response.ok) {
    const detail = body.detail?.message || body.detail || body.message || `HTTP ${response.status}`;
    throw new Error(typeof detail === "string" ? detail : JSON.stringify(detail));
  }
  return body;
}

async function loadCaseData() {
  try {
    const [tasks, shorts] = await Promise.all([
      caseFetch("/api/case-pick/tasks?scope=all&limit=200"),
      caseFetch("/api/case-pick/shorts?limit=100"),
    ]);
    caseState.demo = tasks.length === 0;
    caseState.tasks = tasks.length ? tasks.map(normalizeApiTask) : demoTasks;
    caseState.shorts = tasks.length ? shorts : demoShorts;
  } catch (error) {
    caseState.demo = true;
    caseState.tasks = demoTasks;
    caseState.shorts = demoShorts;
  }
  caseState.selectedId = caseState.selectedId || caseState.tasks[0]?.case_pick_task_id || null;
  renderAll();
}

function normalizeApiTask(task) {
  const planned = Number(task.planned_qty || task.total_lines || 0);
  const picked = Number(task.picked_qty || task.picked_lines || 0);
  const trolleyCapacity = task.equipment_capacity_class
    || task.trolley_capacity
    || (task.trolley_pallet_capacity ? `${task.trolley_pallet_capacity} паллета` : null)
    || "1 паллета";
  const routePallets = Number(task.route_pallet_count || 0);
  const routeDone = Number(task.route_done_pallet_count || 0);
  return {
    ...task,
    assigned_to: task.assigned_to || task.resource_name || task.resource_code || "-",
    equipment_code: task.equipment_code || task.equipment_id || "-",
    trolley_capacity: trolleyCapacity,
    wave_code: task.wave_code || `W-${task.pick_wave_id}`,
    route: task.route || task.route_name || task.route_code || "Маршрут",
    pallet_count_text: routePallets ? `${routeDone} из ${routePallets}` : "1 из 1",
    total_lines: Number(task.total_lines || planned || 0),
    picked_lines: Number(task.picked_lines || picked || 0),
    planned_qty: planned,
    picked_qty: picked,
    efficiency: planned ? Math.round((picked / planned) * 100) : 0,
    problem: task.problem || "",
    last_action: task.last_action || (task.closed_at ? "Поддон закрыт" : task.started_at ? "Идет сбор" : "Задание получено"),
  };
}

function filteredTasks() {
  const query = getValue("caseSearch").toLowerCase();
  const zone = getValue("caseZoneFilter");
  const status = getValue("caseStatusFilter");
  const wave = getValue("caseWaveFilter");
  const trolley = getValue("caseTrolleyFilter");
  return caseState.tasks.filter((task) => {
    const haystack = `${task.assigned_to || ""} ${task.sscc || ""} ${task.wave_code || ""} ${task.customer_name || ""}`.toLowerCase();
    return (!query || haystack.includes(query))
      && (!zone || String(task.zone_code || "").includes(zone))
      && (!status || task.status === status)
      && (!wave || task.wave_code === wave)
      && (!trolley || task.trolley_capacity === trolley);
  });
}

function renderAll() {
  renderWaveFilter();
  renderKpis();
  renderRows();
  renderDetail();
  renderRouteSummary();
  renderAnalytics();
}

function renderWaveFilter() {
  const select = document.getElementById("caseWaveFilter");
  const current = select.value;
  const waves = [...new Set(caseState.tasks.map((task) => task.wave_code).filter(Boolean))];
  select.innerHTML = '<option value="">Все рейсы</option>' + waves.map((wave) => `<option>${escapeHtml(wave)}</option>`).join("");
  select.value = waves.includes(current) ? current : "";
}

function renderKpis() {
  const tasks = caseState.tasks;
  const activePickers = new Set(tasks.filter((task) => isWorking(task.status)).map((task) => task.assigned_to)).size;
  const waves = new Set(tasks.map((task) => task.wave_code)).size;
  const picked = sum(tasks, "picked_qty");
  const planned = sum(tasks, "planned_qty") || 1;
  const problems = tasks.filter((task) => task.problem || ["FAILED", "SYNC_CONFLICT", "OFFLINE"].includes(task.status)).length + caseState.shorts.filter((s) => s.status === "PENDING_APPROVAL").length;
  const notStarted = tasks.filter((task) => ["NEW", "WAITING"].includes(task.status)).length;
  const kpis = [
    ["Комплектовщиков", activePickers, `активных из ${new Set(tasks.map((task) => task.assigned_to)).size}`, "blue", "К"],
    ["Рейсов сегодня", waves, "активных", "violet", "Р"],
    ["Собрано сегодня", Math.round(picked), `${Math.round((picked / planned) * 100)}% плана`, "green", "С"],
    ["Производительность", `${Math.round(avg(tasks, "efficiency"))}%`, "к плану", "green", "%"],
    ["Проблемы сейчас", problems, "требуют внимания", "orange", "!"],
    ["Не начали", notStarted, "комплектовщик", "red", "Н"],
  ];
  document.getElementById("caseKpis").innerHTML = kpis.map(([label, value, note, color, icon]) => `
    <article class="case-kpi">
      <i class="${color}">${icon}</i>
      <div><b>${escapeHtml(label)}</b><strong>${escapeHtml(value)}</strong><span>${escapeHtml(note)}</span></div>
      ${label === "Собрано сегодня" || label === "Производительность" ? '<svg viewBox="0 0 80 24"><path d="M2 22 L12 20 L22 14 L32 18 L42 9 L52 13 L62 6 L78 2"/></svg>' : ""}
    </article>
  `).join("");
}

function renderRows() {
  const rows = filteredTasks();
  document.getElementById("caseRows").innerHTML = rows.map((task, index) => {
    const progress = pct(task);
    const progressClass = progress < 20 ? "red" : progress < 60 ? "orange" : progress < 80 ? "blue" : "";
    return `
      <tr data-case-id="${task.case_pick_task_id}">
        <td class="${index < 2 ? "case-strong" : ""}">${index + 1}</td>
        <td><span class="case-picker"><i class="case-avatar">${initials(task.assigned_to)}</i><span><b>${escapeHtml(task.assigned_to || "-")}</b><small>${task.status === "NEW" ? "Ожидает" : "Опытный"}</small></span></span></td>
        <td><b>${escapeHtml(task.equipment_code || "-")}</b><small>${escapeHtml(task.trolley_capacity || "1 паллета")}</small></td>
        <td><b>${escapeHtml(task.wave_code || "-")}</b><small>${escapeHtml(task.route || "")}</small></td>
        <td><b>${escapeHtml(task.sscc || "-")}</b><small>Поддон</small></td>
        <td><span class="${progress < 60 ? "case-problem" : "case-strong"}">${escapeHtml(task.pallet_count_text || "1 из 1")}</span></td>
        <td><span class="case-progress"><span><b>${Math.round(task.picked_qty || task.picked_lines || 0)} / ${Math.round(task.planned_qty || task.total_lines || 0)}</b><i class="case-bar ${progressClass}"><i style="width:${progress}%"></i></i></span><em>${progress}%</em></span></td>
        <td><b class="${task.efficiency < 80 ? "case-problem" : "case-strong"}">${Math.round(task.efficiency || progress)}%</b><small>${task.efficiency >= 100 ? "+ к плану" : "- к плану"}</small></td>
        <td>${statusBadge(task.status)}<small>${statusText(task.status)}</small></td>
        <td>${task.problem ? `<span class="case-problem">${escapeHtml(formatProblem(task.problem)).replaceAll("\n", "<br>")}</span>` : '<span class="case-muted">-</span>'}</td>
        <td>${escapeHtml(formatLastAction(task.last_action) || "-").replaceAll("\n", "<br>")}</td>
      </tr>
    `;
  }).join("");
  document.querySelectorAll("#caseRows tr").forEach((row) => {
    row.addEventListener("click", () => {
      caseState.selectedId = Number(row.dataset.caseId);
      renderDetail();
    });
  });
}

function renderDetail() {
  const task = caseState.tasks.find((item) => item.case_pick_task_id === caseState.selectedId) || caseState.tasks[0];
  if (!task) {
    document.getElementById("caseDetail").innerHTML = "<p class=\"case-muted\">Нет данных</p>";
    return;
  }
  caseState.selectedId = task.case_pick_task_id;
  const related = caseState.tasks.filter((item) => item.wave_code === task.wave_code);
  const problem = caseState.shorts.find((item) => item.case_pick_task_id === task.case_pick_task_id) || (task.problem ? { reason_text: task.problem, sscc: task.sscc, created_by: task.assigned_to } : null);
  document.getElementById("caseDetail").innerHTML = `
    <div class="case-detail-title">
      <div><b>Детали рейса: ${escapeHtml(task.wave_code || "-")} (${escapeHtml(task.route || "Маршрут")})</b><span class="case-muted">${caseState.demo ? "Демо-режим" : "Данные API"}</span></div>
      <button type="button" aria-label="Закрыть">x</button>
    </div>
    <div class="case-detail-progress">
      <span>${Math.round(task.picked_qty || task.picked_lines || 0)} / ${Math.round(task.planned_qty || task.total_lines || 0)} позиций</span>
      <strong>${pct(task)}%</strong>
      <i class="case-bar"><i style="width:${pct(task)}%"></i></i>
    </div>
    <div class="case-muted">Поддонов в рейсе: ${related.length}</div>
    <div class="case-detail-list">
      ${related.slice(0, 5).map((item) => `
        <div class="case-detail-row">
          <b>${escapeHtml(item.sscc || "-")}</b>
          <span>${escapeHtml(item.assigned_to || "-")}</span>
          ${statusBadge(item.status)}
        </div>
      `).join("")}
    </div>
    ${problem ? `
      <div class="case-alert">
        <b>Критически для закрытия рейса</b>
        <span>${escapeHtml(problem.sscc || task.sscc || "-")}</span>
        <span>${escapeHtml(formatProblem(problem.reason_text || "Проблема комплектации")).replaceAll("\n", " ")}</span>
        <span>Комплектовщик: ${escapeHtml(problem.created_by || task.assigned_to || "-")}</span>
      </div>
    ` : ""}
    <div class="case-actions">
      <button id="caseTransfer" type="button">Передать</button>
      <button id="caseOpenTsd" type="button">Открыть ТСД</button>
      <button id="caseApproveShort" type="button">Подтвердить вычерк</button>
      <button id="caseRejectShort" class="danger" type="button">Отклонить</button>
    </div>
  `;
  document.getElementById("caseTransfer")?.addEventListener("click", () => caseSafe(() => transferSelected(task)));
  document.getElementById("caseOpenTsd")?.addEventListener("click", () => window.location.href = "case-pick-tsd.html");
  document.getElementById("caseApproveShort")?.addEventListener("click", () => caseSafe(() => approveSelectedShort(task)));
  document.getElementById("caseRejectShort")?.addEventListener("click", () => caseSafe(() => rejectSelectedShort(task)));
}

function renderRouteSummary() {
  const routes = groupBy(caseState.tasks, "wave_code");
  document.getElementById("caseRoutes").innerHTML = Object.entries(routes).map(([wave, rows]) => {
    const progress = routeProgress(rows);
    const doneCount = rows.filter((row) => pct(row) >= 100).length;
    const activeCount = rows.filter((row) => isWorking(row.status)).length;
    const blocking = routeBlocker(rows);
    const cls = blocking ? "case-blocked" : progress < 60 ? "case-warn" : "";
    const remaining = Math.max(0, 100 - progress);
    return `
      <article class="case-route-card ${cls}">
        <div class="case-route-head">
          <div><b>${escapeHtml(wave)} / ${escapeHtml(rows[0].route || "Маршрут")}</b><span class="case-muted">${rows.length} подд., ${uniquePickers(rows)} компл.</span></div>
          <strong>${progress}%</strong>
        </div>
        ${miniBar(progress)}
        <div class="case-route-meta">
          <span>Завершено: <b>${doneCount} из ${rows.length}</b></span>
          <span>В работе: <b>${activeCount}</b></span>
          <span>Осталось: <b>${remaining}%</b></span>
          <span>Позиций: <b>${Math.round(sum(rows, "picked_qty"))}/${Math.round(sum(rows, "planned_qty"))}</b></span>
        </div>
        <div class="case-route-pallets">
          ${rows.slice(0, 4).map((row) => `
            <div class="case-route-pallet">
              <span title="${escapeHtml(row.sscc || "-")}">${escapeHtml(row.sscc || "-")} · ${escapeHtml(row.assigned_to || "-")}</span>
              <b>${pct(row)}%</b>
            </div>
          `).join("")}
        </div>
        ${blocking ? `
          <div class="case-route-blocker">
            <span>Держит закрытие: ${escapeHtml(blocking.sscc || "-")}</span>
            <span>${escapeHtml(blocking.assigned_to || "-")} · ${pct(blocking)}%</span>
            <span>${escapeHtml(formatProblem(blocking.problem || formatLastAction(blocking.last_action) || "Ожидает действия")).replaceAll("\n", " ")}</span>
          </div>
        ` : `
          <div class="case-route-blocker ok">
            <span>Критичных блокеров нет</span>
            <span>Ответственные: ${escapeHtml(rows.map((row) => row.assigned_to).slice(0, 3).join(", "))}</span>
          </div>
        `}
      </article>
    `;
  }).join("");
}

function renderAnalytics() {
  const tasks = caseState.tasks;
  const done = tasks.filter((t) => pct(t) >= 100).length;
  const work = tasks.filter((t) => isWorking(t.status)).length;
  const wait = tasks.length - done - work;
  setText("caseDoneCount", `${done} (${Math.round(done / Math.max(tasks.length, 1) * 100)}%)`);
  setText("caseWorkCount", `${work} (${Math.round(work / Math.max(tasks.length, 1) * 100)}%)`);
  setText("caseWaitCount", `${wait} (${Math.round(wait / Math.max(tasks.length, 1) * 100)}%)`);
  document.getElementById("caseDelayed").innerHTML = [...tasks].sort((a, b) => pct(a) - pct(b)).slice(0, 4).map((t, i) => `<tr><td>${i + 1}. <b>${escapeHtml(t.wave_code)}</b><span class="case-muted">${escapeHtml(t.route || "")}</span></td><td>${pct(t)}%</td></tr>`).join("");
  const bands = [["80-100%", tasks.filter((t) => pct(t) >= 80).length, 90], ["50-79%", tasks.filter((t) => pct(t) >= 50 && pct(t) < 80).length, 65], ["20-49%", tasks.filter((t) => pct(t) >= 20 && pct(t) < 50).length, 35], ["0-19%", tasks.filter((t) => pct(t) < 20).length, 12]];
  document.getElementById("caseProgressBands").innerHTML = bands.map(([label, count, width]) => `<tr><td>${label}</td><td>${miniBar(width)}</td><td>${count}</td></tr>`).join("");
  const waves = Object.entries(groupBy(tasks, "wave_code")).slice(0, 3);
  document.getElementById("caseWaves").innerHTML = waves.map(([wave, rows]) => `<tr><td><b>${escapeHtml(wave)}</b></td><td>${miniBar(Math.round(sum(rows, "picked_qty") / Math.max(sum(rows, "planned_qty"), 1) * 100))}</td></tr>`).join("");
  const statuses = groupBy(tasks, "status");
  document.getElementById("casePickerStatuses").innerHTML = Object.entries(statuses).map(([status, rows]) => `<tr><td>${statusBadge(status)}</td><td>${rows.length}</td></tr>`).join("");
  const pendingShorts = caseState.shorts.filter((s) => s.status === "PENDING_APPROVAL");
  document.getElementById("caseProblems").innerHTML = [
    ["Нехватка товара", pendingShorts.length || 2],
    ["Не начали работу", tasks.filter((t) => t.status === "NEW").length],
    ["Оффлайн", tasks.filter((t) => t.status === "OFFLINE").length],
    ["Ошибки сканирования", 0],
  ].map(([name, count], i) => `<tr><td>${i + 1}. ${escapeHtml(name)}</td><td>${count}</td></tr>`).join("");
  document.getElementById("caseLastProblems").innerHTML = pendingShorts.slice(0, 4).map((short) => `<tr><td><span class="case-problem">${escapeHtml(short.reason_text || "Вычерк")}</span><span class="case-muted">Ячейка ${escapeHtml(short.cell_code || "-")}, арт. ${escapeHtml(short.articul || "-")}</span></td><td>8 мин назад</td></tr>`).join("") || '<tr><td>Нет открытых проблем</td><td></td></tr>';
}

async function transferSelected(task) {
  if (caseState.demo) {
    alert("Демо-режим: transfer будет доступен на API-данных.");
    return;
  }
  const toResourceId = Number(prompt("ID ресурса нового комплектовщика"));
  if (!toResourceId) return;
  await caseFetch(`/api/case-pick/tasks/${task.case_pick_task_id}/transfer`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ to_resource_id: toResourceId, reason: "Передача из ARM комплектации" }),
  });
  await loadCaseData();
}

async function approveSelectedShort(task) {
  const short = caseState.shorts.find((item) => item.case_pick_task_id === task.case_pick_task_id && item.status === "PENDING_APPROVAL");
  if (!short) {
    alert("Нет вычерка на подтверждение.");
    return;
  }
  if (caseState.demo) {
    short.status = "ACCEPTED";
    renderAll();
    return;
  }
  await caseFetch(`/api/case-pick/shorts/${short.case_pick_short_id}/approve`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ reason_text: "Подтверждено из ARM комплектации" }),
  });
  await loadCaseData();
}

async function rejectSelectedShort(task) {
  const short = caseState.shorts.find((item) => item.case_pick_task_id === task.case_pick_task_id && item.status === "PENDING_APPROVAL");
  if (!short) {
    alert("Нет вычерка на отклонение.");
    return;
  }
  if (caseState.demo) {
    short.status = "REJECTED";
    renderAll();
    return;
  }
  await caseFetch(`/api/case-pick/shorts/${short.case_pick_short_id}/reject`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ reason_text: "Отклонено из ARM комплектации" }),
  });
  await loadCaseData();
}

function pct(task) {
  const planned = Number(task.planned_qty || task.total_lines || 0);
  const picked = Number(task.picked_qty || task.picked_lines || 0);
  return Math.max(0, Math.min(100, planned ? Math.round((picked / planned) * 100) : 0));
}

function routeProgress(rows) {
  return Math.round(sum(rows, "picked_qty") / Math.max(sum(rows, "planned_qty"), 1) * 100);
}

function routeBlocker(rows) {
  const problem = rows.find((row) => row.problem);
  if (problem) return problem;
  return [...rows].filter((row) => pct(row) < 100).sort((a, b) => pct(a) - pct(b))[0] || null;
}

function uniquePickers(rows) {
  return new Set(rows.map((row) => row.assigned_to).filter(Boolean)).size;
}

function statusBadge(status) {
  const map = {
    IN_PROGRESS: ["В работе", "green"],
    PARTIAL: ["Остановлен", "orange"],
    WAIT_CONTROL: ["Контроль", "blue"],
    PICKED: ["Собран", "green"],
    READY_TO_SHIP: ["Готов", "green"],
    NEW: ["Получил задание", "violet"],
    WAITING: ["Ожидает", "gray"],
    FAILED: ["Не начал", "red"],
    OFFLINE: ["Оффлайн", "gray"],
    SYNC_CONFLICT: ["Конфликт", "red"],
  };
  const [label, cls] = map[status] || [status || "-", "gray"];
  return `<span class="case-badge ${cls}">${escapeHtml(label)}</span>`;
}

function statusText(status) {
  if (status === "IN_PROGRESS") return "Идет сбор";
  if (status === "PARTIAL") return "Нехватка товара";
  if (status === "NEW") return "Не начал";
  if (status === "OFFLINE") return "Нет сессии";
  if (status === "WAIT_CONTROL") return "Ожидает контроль";
  return "";
}

function formatProblem(value) {
  const text = String(value || "");
  return text
    .replaceAll("WAIT_REPLENISHMENT", "Ожидает пополнение")
    .replaceAll("SYNC_CONFLICT", "Конфликт синхронизации")
    .replaceAll("CELL ", "Ячейка ");
}

function formatLastAction(value) {
  const text = String(value || "");
  return text
    .replaceAll("PALLET_CLOSED", "Поддон закрыт")
    .replaceAll("PICKING_IN_PROGRESS", "Идет сбор")
    .replaceAll("TASK_ASSIGNED", "Задание назначено")
    .replaceAll("TASK_RECEIVED", "Задание получено");
}

function miniBar(value) {
  const cls = value < 20 ? "red" : value < 60 ? "orange" : "";
  return `<span class="case-progress"><span><i class="case-bar ${cls}"><i style="width:${value}%"></i></i></span><em>${value}%</em></span>`;
}

function initials(name) {
  return String(name || "?").split(/\s+/).filter(Boolean).slice(0, 2).map((part) => part[0]).join("").toUpperCase();
}

function isWorking(status) {
  return ["IN_PROGRESS", "PARTIAL", "WAIT_CONTROL", "PICKED"].includes(status);
}

function groupBy(rows, key) {
  return rows.reduce((acc, row) => {
    const value = row[key] || "-";
    acc[value] = acc[value] || [];
    acc[value].push(row);
    return acc;
  }, {});
}

function sum(rows, key) {
  return rows.reduce((total, row) => total + Number(row[key] || 0), 0);
}

function avg(rows, key) {
  return rows.length ? sum(rows, key) / rows.length : 0;
}

function getValue(id) {
  return document.getElementById(id).value.trim();
}

function setText(id, value) {
  document.getElementById(id).textContent = value;
}

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;");
}

async function caseSafe(fn) {
  try {
    await fn();
  } catch (error) {
    alert(error.message || String(error));
  }
}

["caseSearch", "caseZoneFilter", "caseStatusFilter", "caseWaveFilter", "caseTrolleyFilter"].forEach((id) => {
  document.getElementById(id).addEventListener("input", () => {
    renderRows();
    renderRouteSummary();
  });
});

document.getElementById("caseRefresh").addEventListener("click", () => caseSafe(loadCaseData));
document.getElementById("caseConfigure").addEventListener("click", () => alert("Настройка вида будет сохранена в профиле диспетчера."));

loadCaseData();
