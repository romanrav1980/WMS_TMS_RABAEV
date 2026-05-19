const STAGES = [
  {
    key: "T0",
    label: "T0\nДо запуска",
    badge: "T0 BASELINE",
    status: "BLOCKED",
    note: "Фиксируем исходные свободные и физические остатки. Резервов и активных задач еще нет.",
    progress: 1,
    blockers: [1, 1, 1, 0],
    work: [0, 0, 0, 0],
    done: [0, 0, 0, 0],
    tsd: [
      ["-", "ТСД не используется", "ожидает"],
      ["-", "Водитель не получил задач", "ожидает"],
    ],
    stocks: [
      ["Пополнение", "SKU-A / SRC-A-01", 100, 100, "Исходный source pallet доступен"],
      ["Пополнение", "SKU-A / PICK-A-01", 2, 2, "В pick face не хватает для волны"],
      ["Стеллаж", "SKU-B / RACK-B-01", 1, 1, "Полный паллет на стеллаже"],
      ["Стеллаж", "SKU-B / LOAD-01", 0, 0, "Грузовая зона пустая"],
      ["Коробки", "SKU-C / PICK-C-01", 40, 40, "Коробочный остаток доступен"],
    ],
  },
  {
    key: "T1",
    label: "T1\nLaunch",
    badge: "T1 RESERVE",
    status: "BLOCKED",
    note: "После запуска волны свободные остатки уменьшаются hard reservations. Физические остатки еще не меняются.",
    progress: 2,
    blockers: [1, 1, 1, 0],
    work: [0, 0, 0, 0],
    done: [0, 0, 0, 0],
    tsd: [
      ["API", "POST /api/picking/waves/{id}/launch", "done"],
      ["Сайт", "Readiness показывает блокеры", "BLOCKED"],
    ],
    stocks: [
      ["Пополнение", "SKU-A / SRC-A-01", 100, 0, "Source pallet зарезервирован, физика не двинулась"],
      ["Пополнение", "SKU-A / PICK-A-01", 2, 2, "Pick face еще не пополнен"],
      ["Стеллаж", "SKU-B / RACK-B-01", 1, 0, "Паллет зарезервирован под прямой отбор"],
      ["Стеллаж", "SKU-B / LOAD-01", 0, 0, "Паллет еще не в грузовой зоне"],
      ["Коробки", "SKU-C / PICK-C-01", 40, 28, "12 коробок зарезервировано под CASE_PICK"],
    ],
  },
  {
    key: "T2",
    label: "T2\nРичтрак старт",
    badge: "T2 IN PROGRESS",
    status: "BLOCKED",
    note: "Водитель взял задачу пополнения. Старт задачи не двигает физический остаток.",
    progress: 3,
    blockers: [1, 1, 1, 0],
    work: [1, 0, 0, 0],
    done: [0, 0, 0, 0],
    tsd: [
      ["Assign", "REPLENISHMENT назначено водителю", "done"],
      ["Start", "Водитель начал выполнение", "in progress"],
      ["Scan", "Паллет и ячейки ожидают сканирования", "ожидает"],
    ],
    stocks: [
      ["Пополнение", "SKU-A / SRC-A-01", 100, 0, "Физика не меняется до complete"],
      ["Пополнение", "SKU-A / PICK-A-01", 2, 2, "Целевая ячейка еще не получила товар"],
      ["Стеллаж", "SKU-B / RACK-B-01", 1, 0, "Паллет все еще физически на стеллаже"],
      ["Стеллаж", "SKU-B / LOAD-01", 0, 0, "Грузовая зона пустая"],
      ["Коробки", "SKU-C / PICK-C-01", 40, 28, "CASE_PICK еще открыт"],
    ],
  },
  {
    key: "T3",
    label: "T3\nПополнение",
    badge: "T3 REPL DONE",
    status: "BLOCKED",
    note: "После complete и domain sync физический остаток source уменьшается, pick face увеличивается.",
    progress: 3,
    blockers: [0, 1, 1, 0],
    work: [0, 0, 0, 0],
    done: [1, 0, 0, 0],
    tsd: [
      ["Scan", "Паллет SRC-A-01 подтвержден", "done"],
      ["Scan", "FROM SRC-A-01 -> TO PICK-A-01", "done"],
      ["Complete", "REPLENISHMENT закрыто", "done"],
    ],
    stocks: [
      ["Пополнение", "SKU-A / SRC-A-01", 0, 0, "Паллет физически ушел из хранения"],
      ["Пополнение", "SKU-A / PICK-A-01", 102, 102, "Pick face физически пополнен"],
      ["Стеллаж", "SKU-B / RACK-B-01", 1, 0, "Прямой паллет еще ожидает"],
      ["Стеллаж", "SKU-B / LOAD-01", 0, 0, "Грузовая зона без SKU-B"],
      ["Коробки", "SKU-C / PICK-C-01", 40, 28, "CASE_PICK еще открыт"],
    ],
  },
  {
    key: "T4",
    label: "T4\nСтеллаж",
    badge: "T4 RACK DONE",
    status: "BLOCKED",
    note: "Прямой полный паллет подан со стеллажа в грузовую зону. Физика меняется только после complete.",
    progress: 4,
    blockers: [0, 0, 1, 0],
    work: [0, 0, 0, 0],
    done: [1, 0, 1, 0],
    tsd: [
      ["Assign", "PICKING_MOVE назначено", "done"],
      ["Scan", "RACK-B-01 -> LOAD-01", "done"],
      ["Complete", "Паллет подан в грузовую зону", "done"],
    ],
    stocks: [
      ["Пополнение", "SKU-A / SRC-A-01", 0, 0, "Пополнение закрыто"],
      ["Пополнение", "SKU-A / PICK-A-01", 102, 102, "Pick face доступен"],
      ["Стеллаж", "SKU-B / RACK-B-01", 0, 0, "Паллет физически ушел со стеллажа"],
      ["Стеллаж", "SKU-B / LOAD-01", 1, 1, "Паллет физически в грузовой зоне"],
      ["Коробки", "SKU-C / PICK-C-01", 40, 28, "CASE_PICK еще открыт"],
    ],
  },
  {
    key: "T5",
    label: "T5\nКоробки",
    badge: "T5 CASE DONE",
    status: "BLOCKED",
    note: "Комплектовщик закрыл коробочный отбор. Физический остаток pick face уменьшился на факт.",
    progress: 5,
    blockers: [0, 0, 0, 0],
    work: [0, 0, 0, 0],
    done: [1, 1, 1, 1],
    tsd: [
      ["CASE_PICK", "Ячейка PICK-C-01 подтверждена", "done"],
      ["Fact", "12 коробок отобрано", "done"],
      ["Minimax", "Порог проверен", "done"],
    ],
    stocks: [
      ["Пополнение", "SKU-A / SRC-A-01", 0, 0, "Пополнение закрыто"],
      ["Пополнение", "SKU-A / PICK-A-01", 102, 102, "SKU-A готов к коробочному отбору"],
      ["Стеллаж", "SKU-B / RACK-B-01", 0, 0, "Прямой поток закрыт"],
      ["Стеллаж", "SKU-B / LOAD-01", 1, 1, "Паллет ожидает отгрузки"],
      ["Коробки", "SKU-C / PICK-C-01", 28, 28, "12 коробок физически отобрано"],
    ],
  },
  {
    key: "T6",
    label: "T6\nREADY",
    badge: "T6 READY",
    status: "READY",
    note: "Все физические и доменные шаги закрыты. Readiness больше не содержит блокеров.",
    progress: 6,
    blockers: [0, 0, 0, 0],
    work: [0, 0, 0, 0],
    done: [1, 1, 1, 1],
    tsd: [
      ["Сайт", "GET /readiness", "READY"],
      ["Отчет", "Скриншоты T0..T6 собраны", "done"],
      ["Видео", "Действия ТСД приложены", "done"],
    ],
    stocks: [
      ["Пополнение", "SKU-A / SRC-A-01", 0, 0, "Source pallet не доступен повторно"],
      ["Пополнение", "SKU-A / PICK-A-01", 102, 102, "Физика и free совпадают"],
      ["Стеллаж", "SKU-B / RACK-B-01", 0, 0, "Стеллаж пуст по этой паллете"],
      ["Стеллаж", "SKU-B / LOAD-01", 1, 1, "Грузовая зона содержит паллет"],
      ["Коробки", "SKU-C / PICK-C-01", 28, 28, "Факт коробок отражен физически"],
    ],
  },
];

const PROGRESS = ["Создана", "Рассчитана", "Пополнение", "Комплектация", "Контроль", "Готово"];

function renderStageControls() {
  const root = document.getElementById("stageControls");
  root.innerHTML = STAGES.map((stage, index) => (
    `<button class="stage-button" type="button" data-stage-index="${index}">${escapeHtml(stage.label).replace("\n", "<br />")}</button>`
  )).join("");
  root.querySelectorAll("button").forEach((button) => {
    button.addEventListener("click", () => renderStage(Number(button.dataset.stageIndex || 0)));
  });
}

function renderStage(index) {
  const stage = STAGES[index] || STAGES[0];
  document.querySelectorAll(".stage-button").forEach((button) => {
    button.classList.toggle("active", Number(button.dataset.stageIndex || 0) === index);
  });
  setText("stageStatusBadge", stage.badge);
  setText("stageNote", stage.note);
  setText("stockSnapshot", stage.key);
  setText("monitorStage", stage.key);
  setText("progressUpdated", `снимок ${stage.key}`);
  setText("passportReady", stage.status === "READY" ? "Готова" : "Ожидает");
  setText("tsdBadge", stage.tsd.some((row) => row[2] === "in progress") ? "в работе" : "зафиксировано");

  const readinessBadge = document.getElementById("readinessBadge");
  readinessBadge.textContent = stage.status;
  readinessBadge.className = `badge ${stage.status === "READY" ? "good" : "bad"}`;
  const statusBadge = document.getElementById("stageStatusBadge");
  statusBadge.className = `badge ${stage.status === "READY" ? "good" : "warn"}`;

  setText("openRepl", stage.blockers[0]);
  setText("openRack", stage.blockers[1]);
  setText("openCase", stage.blockers[2]);
  setText("openSync", stage.blockers[3]);
  setText("kpiBlockers", stage.blockers.reduce((sum, value) => sum + value, 0));
  setText("kpiBlockersSub", stage.status === "READY" ? "Readiness READY" : "Readiness BLOCKED");

  setText("monReplWork", stage.work[0]);
  setText("monPickWork", stage.work[1]);
  setText("monRackWork", stage.work[2]);
  setText("monCaseWork", stage.work[3]);
  setText("monReplDone", stage.done[0]);
  setText("monPickDone", stage.done[1]);
  setText("monRackDone", stage.done[2]);
  setText("monCaseDone", stage.done[3]);

  renderProgress(stage.progress);
  renderStocks(stage.stocks, index);
  renderTsd(stage.tsd);
  renderEvidence(index);
}

function renderProgress(activeStep) {
  document.getElementById("progressLine").innerHTML = PROGRESS.map((label, idx) => {
    const stepNo = idx + 1;
    const cls = stepNo < activeStep ? "done" : stepNo === activeStep ? "active" : "";
    return `<div class="progress-step ${cls}"><i>${stepNo < activeStep ? "✓" : stepNo}</i><span>${escapeHtml(label)}</span></div>`;
  }).join("");
}

function renderStocks(rows, stageIndex) {
  const previousRows = stageIndex > 0 ? STAGES[stageIndex - 1].stocks : rows;
  document.getElementById("stockRows").innerHTML = rows.map((row, idx) => {
    const prev = previousRows[idx] || row;
    const physicalClass = deltaClass(row[2] - prev[2]);
    const freeClass = deltaClass(row[3] - prev[3]);
    return `<tr>
      <td>${escapeHtml(row[0])}</td>
      <td>${escapeHtml(row[1])}</td>
      <td>${row[2]} <small class="${physicalClass}">${deltaText(row[2] - prev[2])}</small></td>
      <td>${row[3]} <small class="${freeClass}">${deltaText(row[3] - prev[3])}</small></td>
      <td><small>${escapeHtml(row[4])}</small></td>
    </tr>`;
  }).join("");
}

function renderTsd(rows) {
  document.getElementById("tsdList").innerHTML = rows.map((row) => {
    const badgeClass = row[2] === "done" || row[2] === "READY" ? "good" : row[2] === "in progress" ? "warn" : "";
    return `<div class="tsd-item">
      <i>${escapeHtml(row[0]).slice(0, 1)}</i>
      <div><b>${escapeHtml(row[0])}</b><span>${escapeHtml(row[1])}</span></div>
      <em class="badge ${badgeClass}">${escapeHtml(row[2])}</em>
    </div>`;
  }).join("");
}

function renderEvidence(activeIndex) {
  document.getElementById("evidenceRows").innerHTML = STAGES.map((stage, idx) => {
    const done = idx <= activeIndex;
    return `<tr>
      <td><b>${escapeHtml(stage.key)}</b></td>
      <td><span class="badge ${done ? "good" : ""}">${done ? "скриншот" : "ожидает"}</span></td>
      <td><span class="badge ${done ? "good" : ""}">${done ? "ТСД" : "ожидает"}</span></td>
    </tr>`;
  }).join("");
}

function deltaClass(value) {
  if (value > 0) return "delta-up";
  if (value < 0) return "delta-down";
  return "delta-flat";
}

function deltaText(value) {
  if (value > 0) return `+${value}`;
  if (value < 0) return String(value);
  return "без изменений";
}

function setText(id, value) {
  const node = document.getElementById(id);
  if (node) node.textContent = String(value);
}

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;");
}

renderStageControls();
const requestedStage = new URLSearchParams(window.location.search).get("stage");
const requestedIndex = Math.max(0, STAGES.findIndex((stage) => stage.key === requestedStage));
renderStage(requestedIndex);
