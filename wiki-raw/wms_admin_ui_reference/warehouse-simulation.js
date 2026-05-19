(() => {
  const SHIFT_MINUTES = 720;
  const SHIFT_START_HOUR = 8;
  const COLORS = {
    green: "#19a765",
    blue: "#2563d8",
    amber: "#f59e0b",
    red: "#ee3e37",
    gray: "#94a3b8",
    dark: "#101f35",
    rack: "#2f4159",
    rackSide: "#1d2b3d",
    pallet: "#d6a35e",
    floor: "#dce5ef",
  };

  const rootCauseByType = {
    PICK_FACE_QUEUE: "Несколько комплектовщиков пришли к одному pick-face одновременно",
    AISLE_CONGESTION: "Перегруз 10-метрового сегмента аллеи",
    REACHTRUCK_BLOCK: "Ричтрак выполняет опускание паллеты в зоне отбора",
    DYNAMIC_CELL_SHORTAGE: "Нет свободной динамической ячейки под пополнение SKU",
    MINIMAX_WAIT: "Пополнение ожидает снижения остатка до Minimax-порога",
    REACH_RESOURCE_SHORTAGE: "Очередь пополнений выше пропускной способности RTP",
    PICKER_RESOURCE_SHORTAGE: "Активных клиентских паллет больше доступной емкости комплектовщиков",
    DOCK_QUEUE: "Ворота и скорость отгрузки ограничивают выпуск клиентов",
    SHIPMENT_RATE_LIMIT: "Ограничение 15 паллет в час задерживает рейс",
  };

  const state = {
    layout: buildDemoLayout(),
    events: buildDemoEvents(),
    metrics: [],
    collisionsCsv: [],
    report: buildDemoReport(),
    currentMinute: getInitialMinute(),
    playing: true,
    speed: 5,
    selectedWaveId: "",
    selectedZone: "",
    selectedCollisionType: "",
    layers: {
      pickers: true,
      reachtrucks: true,
      replenishment: true,
      picking: true,
      monoPallets: true,
      shipping: true,
      collisions: true,
      heatmap: true,
      routes: true,
    },
    taskTab: "overdue",
    hitRegions: [],
    timer: null,
  };

  const els = {};
  let ctx;
  let canvas;

  document.addEventListener("DOMContentLoaded", () => {
    cacheElements();
    ctx = els.warehouseCanvas.getContext("2d");
    canvas = els.warehouseCanvas;
    bindEvents();
    initializeFromUrl().finally(() => {
      normalizeData();
      fillFilters();
      render();
      startPlayback();
    });
  });

  function cacheElements() {
    [
      "warehouseCanvas", "sceneOverlays", "detailCard", "currentClock", "timeScrubber", "timeBadge",
      "playPause", "speedSelect", "waveFilter", "zoneFilter", "collisionTypeFilter", "rtpTaskList",
      "collisionFeed", "rtpDriverCard", "routeWidget", "timelineMarkers", "notificationCount",
      "kpiProductivity", "kpiProductivitySub", "kpiUnits", "kpiPickers", "kpiSla", "kpiSlaSub",
      "kpiOverdue", "kpiCollisions", "kpiCollisionsSub", "kpiSpeed", "overdueTabCount",
      "allTaskCount", "sceneRunId", "sceneSubtitle", "sidebarRunId", "evidenceStatus",
      "layoutFile", "eventsFile", "metricsFile", "collisionsFile", "reportFile", "loadDemo",
      "tabOverdue", "tabAllTasks", "stepBack", "stepForward", "liveButton", "calendarButton",
    ].forEach((id) => {
      els[id] = document.getElementById(id);
    });
  }

  function bindEvents() {
    els.playPause.addEventListener("click", () => {
      state.playing = !state.playing;
      if (state.playing) startPlayback();
      else stopPlayback();
      renderPlaybackButton();
    });
    els.speedSelect.addEventListener("change", () => {
      state.speed = Number(els.speedSelect.value);
      if (state.playing) {
        stopPlayback();
        startPlayback();
      }
    });
    els.timeScrubber.addEventListener("input", () => {
      state.currentMinute = Number(els.timeScrubber.value);
      render();
    });
    els.waveFilter.addEventListener("change", () => {
      state.selectedWaveId = els.waveFilter.value;
      render();
    });
    els.zoneFilter.addEventListener("change", () => {
      state.selectedZone = els.zoneFilter.value;
      render();
    });
    els.collisionTypeFilter.addEventListener("change", () => {
      state.selectedCollisionType = els.collisionTypeFilter.value;
      render();
    });
    document.querySelectorAll("[data-layer]").forEach((node) => {
      node.addEventListener("change", () => {
        state.layers[node.dataset.layer] = node.checked;
        render();
      });
    });
    els.tabOverdue.addEventListener("click", () => {
      state.taskTab = "overdue";
      els.tabOverdue.classList.add("active");
      els.tabAllTasks.classList.remove("active");
      renderPanels();
    });
    els.tabAllTasks.addEventListener("click", () => {
      state.taskTab = "all";
      els.tabAllTasks.classList.add("active");
      els.tabOverdue.classList.remove("active");
      renderPanels();
    });
    els.stepBack.addEventListener("click", () => {
      state.currentMinute = Math.max(0, state.currentMinute - 5);
      render();
    });
    els.stepForward.addEventListener("click", () => {
      state.currentMinute = Math.min(SHIFT_MINUTES, state.currentMinute + 5);
      render();
    });
    els.liveButton.addEventListener("click", () => {
      state.currentMinute = Math.min(SHIFT_MINUTES, latestEventMinute());
      render();
    });
    els.loadDemo.addEventListener("click", () => {
      stopPlayback();
      state.layout = buildDemoLayout();
      state.events = buildDemoEvents();
      state.metrics = buildDemoMetrics();
      state.collisionsCsv = [];
      state.report = buildDemoReport();
      state.currentMinute = 102;
      state.playing = true;
      normalizeData();
      fillFilters();
      render();
      startPlayback();
    });
    els.warehouseCanvas.addEventListener("click", handleCanvasClick);
    bindFileInput(els.layoutFile, "json", (payload) => { state.layout = payload; normalizeData(); fillFilters(); render(); });
    bindFileInput(els.eventsFile, "jsonl", (payload) => { state.events = payload; normalizeData(); fillFilters(); render(); });
    bindFileInput(els.metricsFile, "csv", (payload) => { state.metrics = payload; render(); });
    bindFileInput(els.collisionsFile, "csv", (payload) => { state.collisionsCsv = payload; render(); });
    bindFileInput(els.reportFile, "json", (payload) => { state.report = payload; render(); });
    window.addEventListener("resize", renderScene);
  }

  async function initializeFromUrl() {
    state.metrics = buildDemoMetrics();
    const params = new URLSearchParams(window.location.search);
    const runId = params.get("runId") || hashParam("runId");
    const evidenceDir = params.get("evidenceDir") || hashParam("evidenceDir") || window.WAREHOUSE_SIMULATION_EVIDENCE_DIR
      || (runId ? `../../runtime/test-evidence/warehouse-minute-simulation/${runId}` : "");
    const initialMinute = params.get("minute") || hashParam("minute");
    if (initialMinute) state.currentMinute = clamp(Number(initialMinute), 0, SHIFT_MINUTES);
    if (!evidenceDir) {
      setEvidenceStatus("demo fallback");
      return;
    }
    setEvidenceStatus(`loading ${evidenceDir}`);
    const loaded = await loadEvidenceDirectory(evidenceDir);
    if (loaded) {
      setEvidenceStatus(evidenceDir);
    } else {
      setEvidenceStatus("demo fallback: evidence unavailable");
    }
  }

  async function loadEvidenceDirectory(dir) {
    try {
      const [layout, eventsText, metricsText, collisionText, report] = await Promise.all([
        fetchJson(`${dir}/layout.json`),
        fetchText(`${dir}/events.jsonl`),
        fetchTextOptional(`${dir}/metrics-by-minute.csv`),
        fetchTextOptional(`${dir}/collision-report.csv`),
        fetchJsonOptional(`${dir}/report.json`),
      ]);
      state.layout = layout;
      state.events = parseJsonl(eventsText);
      if (metricsText) state.metrics = parseCsv(metricsText);
      if (collisionText) state.collisionsCsv = parseCsv(collisionText);
      if (report) state.report = report;
      return true;
    } catch (exc) {
      console.warn("Unable to load warehouse simulation evidence", exc);
      return false;
    }
  }

  function normalizeData() {
    state.events = (state.events || []).map((event, index) => ({
      ...event,
      id: event.id || `event-${index}`,
      minute: Number(event.minute || 0),
      event_type: event.event_type || event.type || "UNKNOWN",
      clock: event.clock || event.ts || clock(Number(event.minute || 0)),
    })).sort((a, b) => a.minute - b.minute);
    state.layout.cells = state.layout.cells || [];
    state.layout.gates = state.layout.gates || [];
    enrichLayout();
  }

  function enrichLayout() {
    if (state.layout.cells.length) return;
    state.layout = buildDemoLayout();
  }

  function startPlayback() {
    stopPlayback();
    state.playing = true;
    renderPlaybackButton();
    state.timer = setInterval(() => {
      state.currentMinute = state.currentMinute >= SHIFT_MINUTES ? 0 : state.currentMinute + 1;
      render();
    }, Math.max(20, 900 / state.speed));
  }

  function stopPlayback() {
    if (state.timer) clearInterval(state.timer);
    state.timer = null;
    state.playing = false;
    renderPlaybackButton();
  }

  function render() {
    els.currentClock.textContent = clock(state.currentMinute);
    els.timeScrubber.value = state.currentMinute;
    els.timeBadge.textContent = clock(state.currentMinute);
    els.timeBadge.style.left = `${(state.currentMinute / SHIFT_MINUTES) * 100}%`;
    renderRunLabels();
    renderKpis();
    renderScene();
    renderPanels();
    renderTimeline();
  }

  function renderRunLabels() {
    const runId = state.report?.run_id || state.layout?.run_id || "demo";
    els.sceneRunId.textContent = runId;
    els.sidebarRunId.textContent = runId;
    els.sceneSubtitle.textContent = `${state.layout.cells.length || 0} ячеек · ${state.layout.gates.length || 0} ворот · ${visibleEvents().length} событий`;
  }

  function renderPlaybackButton() {
    els.playPause.classList.toggle("paused", !state.playing);
  }

  function renderKpis() {
    const metrics = currentMetrics();
    const resources = resourceStateAt(state.currentMinute);
    const collisions = activeCollisions();
    const tasks = replenishmentTasksAt(state.currentMinute);
    const unitsDone = Number(metrics?.done_pick_lines || metrics?.units_processed || countEvents("PICKER_TASK_DONE"));
    const totalUnits = Number(metrics?.total_pick_lines || state.report?.totals?.pick_lines || Math.max(1, unitsDone));
    const expectedProgress = Math.max(1, totalUnits * (state.currentMinute / SHIFT_MINUTES));
    const productivity = Math.round((unitsDone / expectedProgress) * 100);
    const completedRepl = tasks.filter((task) => task.status === "DONE").length;
    const overdue = tasks.filter((task) => task.overdueMinutes > 0 && task.status !== "DONE").length;
    const sla = completedRepl ? Math.max(40, Math.round(((completedRepl - overdue) / completedRepl) * 100)) : 100;
    const activePickers = resources.filter((row) => row.kind === "picker" && row.status !== "ожид.").length;
    const avgSpeed = activePickers ? (resources.filter((row) => row.kind === "picker").reduce((sum, row) => sum + row.speedRatio, 0) / activePickers / 100 * 1.21) : 0;
    els.kpiProductivity.textContent = `${clamp(productivity, 0, 160)}%`;
    els.kpiProductivitySub.textContent = productivity >= 100 ? "+ к плану" : "ниже плана";
    els.kpiUnits.textContent = `${formatNumber(unitsDone)} / ${formatNumber(totalUnits)}`;
    els.kpiPickers.textContent = `${activePickers} / 10`;
    els.kpiSla.textContent = `${sla}%`;
    els.kpiSlaSub.textContent = sla >= 95 ? "цель 95%" : `ниже цели на ${95 - sla}%`;
    els.kpiOverdue.textContent = String(overdue);
    els.kpiCollisions.textContent = String(collisions.length);
    els.kpiCollisionsSub.textContent = collisions.filter((row) => row.severity === "critical").length ? "критические" : "активные";
    els.kpiSpeed.textContent = `${avgSpeed.toFixed(2).replace(".", ",")} м/с`;
    els.notificationCount.textContent = String(collisions.length);
  }

  function renderScene() {
    if (!ctx || !canvas) return;
    resizeCanvas();
    state.hitRegions = [];
    const view = makeView();
    drawSceneBackground();
    drawFloor(view);
    drawGates(view);
    drawRacks(view);
    if (state.layers.heatmap) drawHeatmap(view);
    if (state.layers.routes) drawTrails(view);
    if (state.layers.reachtrucks) drawResources(view, "reachtruck");
    if (state.layers.pickers) drawResources(view, "picker");
    if (state.layers.collisions) drawCollisionHotspots(view);
    renderOverlays(view);
  }

  function resizeCanvas() {
    const rect = canvas.getBoundingClientRect();
    const scale = window.devicePixelRatio || 1;
    canvas.width = Math.max(1, Math.floor(rect.width * scale));
    canvas.height = Math.max(1, Math.floor(rect.height * scale));
    ctx.setTransform(scale, 0, 0, scale, 0, 0);
    canvas.cssWidth = rect.width;
    canvas.cssHeight = rect.height;
  }

  function makeView() {
    const w = canvas.cssWidth || canvas.width;
    const h = canvas.cssHeight || canvas.height;
    return {
      w,
      h,
      originX: w * 0.51,
      originY: 88,
      sx: 8.0,
      sy: 7.25,
      z: 8.5,
    };
  }

  function iso(view, x, y, z = 0) {
    return {
      x: view.originX + (x - y * 1.85) * view.sx,
      y: view.originY + (x * 0.42 + y * 1.03) * view.sy - z * view.z,
    };
  }

  function drawSceneBackground() {
    const w = canvas.cssWidth;
    const h = canvas.cssHeight;
    const gradient = ctx.createLinearGradient(0, 0, w, h);
    gradient.addColorStop(0, "#f8fbff");
    gradient.addColorStop(.55, "#e8eef7");
    gradient.addColorStop(1, "#d6e0eb");
    ctx.fillStyle = gradient;
    ctx.fillRect(0, 0, w, h);
  }

  function drawFloor(view) {
    const corners = [
      iso(view, -8, -7, 0),
      iso(view, 101, -7, 0),
      iso(view, 101, 105, 0),
      iso(view, -8, 105, 0),
    ];
    polygon(corners, "#e8eef5", "#c9d5e2", 1);
    for (let aisle = 1; aisle <= 25; aisle += 1) {
      const y = (aisle - 1) * 4;
      const a = iso(view, -2, y - .95, 0);
      const b = iso(view, 92, y - .95, 0);
      const c = iso(view, 92, y + .95, 0);
      const d = iso(view, -2, y + .95, 0);
      polygon([a, b, c, d], aisle % 2 ? "#f6f9fc" : "#edf3f9", "#cfdae7", .6);
      ctx.fillStyle = COLORS.blue;
      ctx.font = "700 10px Segoe UI";
      const label = iso(view, -7, y, 0);
      ctx.fillText(`A${String(aisle).padStart(2, "0")}`, label.x, label.y);
    }
    const dockA = iso(view, -10, -5, 0);
    const dockB = iso(view, -2, -5, 0);
    const dockC = iso(view, -2, 101, 0);
    const dockD = iso(view, -10, 101, 0);
    polygon([dockA, dockB, dockC, dockD], "#dfe8f2", "#cbd7e5", 1);
  }

  function drawGates(view) {
    (state.layout.gates || []).forEach((gate) => {
      const y = Number(gate.y_m || (Number(gate.aisle || 1) - 1) * 4);
      const p = iso(view, -5.8, y, 0);
      drawBox(view, -5.8, y - .75, 0, 4.2, 1.5, .35, "#eff6ff", "#c7daf5");
      ctx.fillStyle = COLORS.blue;
      ctx.font = "800 9px Segoe UI";
      ctx.fillText(gate.gate_id || `G${String(gate.aisle).padStart(2, "0")}`, p.x - 8, p.y - 7);
      if (Number(gate.aisle || 0) % 5 === 0) {
        drawTruckDock(view, -8.8, y - .65);
      }
    });
  }

  function drawRacks(view) {
    const cells = state.layout.cells.filter((cell) => Number(cell.level) === 1 || String(cell.cell_id || "").endsWith("-L1"));
    const visible = cells.filter((cell) => Number(cell.slot || 0) % 2 === 1);
    visible.forEach((cell) => {
      const slot = Number(cell.slot || parseSlot(cell.cell_id));
      const aisle = Number(cell.aisle || parseAisle(cell.cell_id));
      const x = Number(cell.x_m ?? (slot - 1) * 1.5);
      const y = Number(cell.y_m ?? (aisle - 1) * 4);
      const role = cell.role || "FIXED_PICK_FACE";
      const height = role === "DYNAMIC_PICK_FACE" ? 1.6 : role === "DUPLICATE_A_PICK_FACE" ? 2.15 : 1.9;
      const topColor = role === "DYNAMIC_PICK_FACE" ? "#7dd3fc" : role === "DUPLICATE_A_PICK_FACE" ? "#c4b5fd" : "#d5a35e";
      drawBox(view, x, y - .55, 0, 1.05, 1.1, height, topColor, COLORS.rack);
      if (slot % 10 === 1) {
        const p = iso(view, x, y - .95, height + .3);
        ctx.fillStyle = "#174c9a";
        ctx.font = "800 9px Segoe UI";
        ctx.fillText(`S${String(slot).padStart(3, "0")}`, p.x - 10, p.y);
      }
    });
  }

  function drawBox(view, x, y, z, dx, dy, dz, topColor, sideColor) {
    const p1 = iso(view, x, y, z + dz);
    const p2 = iso(view, x + dx, y, z + dz);
    const p3 = iso(view, x + dx, y + dy, z + dz);
    const p4 = iso(view, x, y + dy, z + dz);
    const b2 = iso(view, x + dx, y, z);
    const b3 = iso(view, x + dx, y + dy, z);
    const b4 = iso(view, x, y + dy, z);
    polygon([p1, p2, p3, p4], topColor, "rgba(31,47,72,.35)", .45);
    polygon([p2, b2, b3, p3], shade(sideColor, .15), "rgba(31,47,72,.25)", .4);
    polygon([p3, b3, b4, p4], sideColor, "rgba(31,47,72,.25)", .4);
  }

  function drawTruckDock(view, x, y) {
    drawBox(view, x, y, 0, 2.7, 1.2, .9, "#ffffff", "#9aa8b9");
    drawBox(view, x + 2.7, y, 0, 1.0, 1.2, .65, "#d1d7e0", "#8593a4");
  }

  function drawHeatmap(view) {
    activeCollisions(90).forEach((collision) => {
      const loc = collisionLocation(collision);
      if (!loc) return;
      const p = iso(view, loc.x, loc.y, 0.2);
      const radius = collision.severity === "critical" ? 44 : 32;
      const gradient = ctx.createRadialGradient(p.x, p.y, 2, p.x, p.y, radius);
      gradient.addColorStop(0, collision.severity === "critical" ? "rgba(238,62,55,.62)" : "rgba(245,158,11,.58)");
      gradient.addColorStop(1, "rgba(245,158,11,0)");
      ctx.fillStyle = gradient;
      ctx.beginPath();
      ctx.arc(p.x, p.y, radius, 0, Math.PI * 2);
      ctx.fill();
    });
  }

  function drawTrails(view) {
    const resources = resourceStateAt(state.currentMinute);
    resources.forEach((resource) => {
      if (state.selectedWaveId && resource.waveId !== state.selectedWaveId) return;
      const trail = resource.trail || [];
      if (trail.length < 2) return;
      ctx.strokeStyle = resource.kind === "reachtruck" ? "rgba(37,99,216,.55)" : "rgba(25,167,101,.48)";
      ctx.lineWidth = resource.kind === "reachtruck" ? 3 : 2;
      ctx.setLineDash(resource.kind === "reachtruck" ? [9, 7] : [5, 5]);
      ctx.beginPath();
      trail.forEach((point, index) => {
        const p = iso(view, point.x, point.y, .25);
        if (index === 0) ctx.moveTo(p.x, p.y);
        else ctx.lineTo(p.x, p.y);
      });
      ctx.stroke();
      ctx.setLineDash([]);
    });
  }

  function drawResources(view, kind) {
    resourceStateAt(state.currentMinute).filter((resource) => resource.kind === kind).forEach((resource) => {
      if (state.selectedWaveId && resource.waveId !== state.selectedWaveId) return;
      const p = iso(view, resource.x, resource.y, kind === "reachtruck" ? .9 : .55);
      const color = statusColor(resource.statusColor);
      if (kind === "reachtruck") {
        drawBox(view, resource.x - .7, resource.y - .35, .05, 1.4, .7, .55, color, "#243042");
        drawHalo(p.x, p.y, color, 18);
      } else {
        drawPerson(p.x, p.y, color);
        drawHalo(p.x, p.y, color, 13);
      }
      state.hitRegions.push({ type: "resource", resource, x: p.x, y: p.y, r: kind === "reachtruck" ? 18 : 14 });
    });
  }

  function drawPerson(x, y, color) {
    ctx.fillStyle = color;
    ctx.beginPath();
    ctx.arc(x, y - 8, 5, 0, Math.PI * 2);
    ctx.fill();
    ctx.fillRect(x - 4, y - 4, 8, 13);
    ctx.fillStyle = "#fff";
    ctx.fillRect(x - 8, y + 4, 16, 4);
  }

  function drawHalo(x, y, color, radius) {
    ctx.strokeStyle = color;
    ctx.lineWidth = 2;
    ctx.globalAlpha = .55;
    ctx.beginPath();
    ctx.arc(x, y, radius, 0, Math.PI * 2);
    ctx.stroke();
    ctx.globalAlpha = 1;
  }

  function drawCollisionHotspots(view) {
    activeCollisions(45).forEach((collision) => {
      const loc = collisionLocation(collision);
      if (!loc) return;
      const p = iso(view, loc.x, loc.y, 1.0);
      const color = collision.severity === "critical" ? COLORS.red : COLORS.amber;
      ctx.fillStyle = color;
      ctx.beginPath();
      ctx.arc(p.x, p.y, 8, 0, Math.PI * 2);
      ctx.fill();
      ctx.fillStyle = "#fff";
      ctx.font = "900 11px Segoe UI";
      ctx.textAlign = "center";
      ctx.fillText("!", p.x, p.y + 4);
      ctx.textAlign = "left";
      state.hitRegions.push({ type: "collision", collision, x: p.x, y: p.y, r: 16 });
    });
  }

  function renderOverlays(view) {
    const resources = resourceStateAt(state.currentMinute)
      .filter((resource) => !state.selectedWaveId || resource.waveId === state.selectedWaveId);
    const resourceBadges = resources.map((resource) => {
      const p = iso(view, resource.x, resource.y, resource.kind === "reachtruck" ? 2.2 : 1.8);
      const label = resource.kind === "reachtruck"
        ? `${resource.id}<span>${resource.status}</span>`
        : `${resource.id} ${resource.speedRatio}%<span>${resource.status}</span>`;
      return `<button class="resource-badge ${resource.statusColor}" style="left:${p.x}px;top:${p.y}px" data-resource-id="${escapeHtml(resource.id)}">${label}</button>`;
    }).join("");
    const callouts = activeCollisions(40).slice(-5).map((collision) => {
      const loc = collisionLocation(collision);
      if (!loc) return "";
      const p = iso(view, loc.x, loc.y, 3.0);
      const cls = collision.severity === "critical" ? "" : "warning";
      return `<button class="callout ${cls}" style="left:${p.x}px;top:${p.y}px" data-collision-id="${escapeHtml(collision.id)}"><b>${escapeHtml(collisionTitle(collision))}</b><span>${escapeHtml(collision.locationLabel)} · задержка ${collision.lostMinutes} мин</span></button>`;
    }).join("");
    els.sceneOverlays.innerHTML = resourceBadges + callouts;
    els.sceneOverlays.querySelectorAll("[data-resource-id]").forEach((node) => {
      node.addEventListener("click", () => showResourceDetail(node.dataset.resourceId));
    });
    els.sceneOverlays.querySelectorAll("[data-collision-id]").forEach((node) => {
      node.addEventListener("click", () => showCollisionDetail(node.dataset.collisionId));
    });
  }

  function renderPanels() {
    const tasks = replenishmentTasksAt(state.currentMinute);
    const overdue = tasks.filter((task) => task.overdueMinutes > 0 && task.status !== "DONE");
    els.overdueTabCount.textContent = String(overdue.length);
    els.allTaskCount.textContent = String(tasks.length);
    const list = state.taskTab === "overdue" ? overdue : tasks;
    els.rtpTaskList.innerHTML = list.slice(0, 12).map(renderRtpTask).join("") || `<div class="rtp-task-card"><b>Нет открытых RTP задач</b><span>На текущей минуте очередь пополнения не блокирует волну.</span></div>`;
    els.rtpTaskList.querySelectorAll("[data-task-id]").forEach((node) => {
      node.addEventListener("click", () => showTaskDetail(node.dataset.taskId));
    });
    renderDriverCard(tasks);
    renderCollisionsPanel();
    renderRouteWidget();
  }

  function renderRtpTask(task) {
    const severity = task.overdueMinutes >= 20 ? "critical" : task.overdueMinutes > 0 ? "warning" : "";
    const delayClass = task.overdueMinutes >= 20 ? "" : "warning";
    const stockPct = clamp(task.stockPercent, 0, 100);
    return `
      <button class="rtp-task-card ${severity}" type="button" data-task-id="${escapeHtml(task.id)}">
        <div class="task-top"><span class="delay-pill ${delayClass}">${task.overdueMinutes || task.ageMinutes} мин</span><b>${escapeHtml(task.targetCell)}</b></div>
        <div class="task-body">
          <div>
            <b>${escapeHtml(task.reason)}</b>
            <span>${escapeHtml(task.sku)} · ${task.stockText}</span>
            <div class="stock-mini"><i style="width:${stockPct}%"></i></div>
            <span>${escapeHtml(task.zone)} · ${escapeHtml(task.status)}</span>
          </div>
          <div class="pallet-icon" aria-hidden="true"></div>
        </div>
      </button>
    `;
  }

  function renderDriverCard(tasks) {
    const active = resourceStateAt(state.currentMinute).filter((row) => row.kind === "reachtruck");
    const busiest = active.sort((a, b) => b.queue - a.queue)[0] || { id: "RT01", driver: "RTD01", utilization: 0, queue: tasks.length };
    els.rtpDriverCard.innerHTML = `
      <b>${escapeHtml(busiest.id)} · ${escapeHtml(busiest.driver || "водитель")}</b>
      <span>Загрузка: ${busiest.utilization || Math.min(100, 40 + tasks.length * 4)}%</span>
      <span>Очередь: ${busiest.queue || tasks.filter((task) => task.status !== "DONE").length} задач</span>
    `;
  }

  function renderCollisionsPanel() {
    const rows = activeCollisions(120)
      .filter((row) => !state.selectedCollisionType || row.type === state.selectedCollisionType)
      .slice(-20)
      .reverse();
    els.collisionFeed.innerHTML = rows.map((collision) => {
      const warning = collision.severity === "critical" ? "critical" : "warning";
      return `
        <button class="collision-card ${warning}" type="button" data-collision-id="${escapeHtml(collision.id)}">
          <span class="collision-icon">${collision.severity === "critical" ? "!" : "△"}</span>
          <span class="collision-meta">
            <span class="collision-top"><b>${escapeHtml(collisionTitle(collision))}</b><span>${escapeHtml(collision.clock)}</span></span>
            <span>${escapeHtml(collision.locationLabel)}</span>
            <span>${escapeHtml(collision.rootCause)}</span>
            <span>Влияет: ${escapeHtml(collision.affectedResources.join(", ") || collision.waveId || "волна")} · потеря ~${collision.productivityLoss}/час</span>
          </span>
        </button>
      `;
    }).join("") || `<div class="collision-card"><span class="collision-icon">✓</span><span class="collision-meta"><b>Нет активных коллизий</b><span>Склад работает без критических блокеров.</span></span></div>`;
    els.collisionFeed.querySelectorAll("[data-collision-id]").forEach((node) => {
      node.addEventListener("click", () => showCollisionDetail(node.dataset.collisionId));
    });
  }

  function renderRouteWidget() {
    const waveId = state.selectedWaveId || inferCurrentWave();
    const progress = routeProgress(waveId);
    els.routeWidget.innerHTML = `
      <h3>Прогресс маршрутов (${escapeHtml(waveId || "все волны")})</h3>
      ${progress.map((route) => `
        <div class="route-row">
          <span>${escapeHtml(route.id)}</span>
          <span class="route-bar"><i class="${route.color}" style="width:${route.percent}%"></i></span>
          <span>${route.blocked ? "Заблокирован" : `${route.percent}%`}</span>
        </div>
      `).join("")}
    `;
  }

  function renderTimeline() {
    const markers = [];
    state.events.forEach((event) => {
      if (event.event_type === "WAVE_LAUNCHED") markers.push({ minute: event.minute, color: "green" });
      if (event.event_type === "COLLISION") markers.push({ minute: event.minute, color: severityForEvent(event) === "critical" ? "red" : "amber" });
      if (event.event_type === "CLIENT_READY") markers.push({ minute: event.minute, color: "blue" });
      if (event.event_type === "PALLET_LOADING_STARTED") markers.push({ minute: event.minute, color: "gray" });
    });
    els.timelineMarkers.innerHTML = markers.slice(0, 260).map((marker) => `<i class="timeline-marker ${marker.color}" style="left:${(marker.minute / SHIFT_MINUTES) * 100}%"></i>`).join("");
  }

  function fillFilters() {
    const waves = Array.from(new Set(state.events.map((event) => event.wave_id).filter(Boolean))).sort();
    els.waveFilter.innerHTML = `<option value="">Все волны</option>${waves.map((wave) => `<option>${escapeHtml(wave)}</option>`).join("")}`;
    const zones = Array.from({ length: 25 }, (_, index) => `A${String(index + 1).padStart(2, "0")}`);
    els.zoneFilter.innerHTML = `<option value="">Все зоны</option>${zones.map((zone) => `<option>${zone}</option>`).join("")}`;
    const types = Object.keys(rootCauseByType);
    els.collisionTypeFilter.innerHTML = `<option value="">Все (${types.length})</option>${types.map((type) => `<option>${type}</option>`).join("")}`;
  }

  function visibleEvents() {
    return state.events.filter((event) => event.minute <= state.currentMinute)
      .filter((event) => !state.selectedWaveId || event.wave_id === state.selectedWaveId);
  }

  function currentMetrics() {
    if (!state.metrics?.length) return null;
    let best = state.metrics[0];
    state.metrics.forEach((row) => {
      if (Number(row.minute) <= state.currentMinute) best = row;
    });
    return best;
  }

  function resourceStateAt(minute) {
    const resources = new Map();
    const events = state.events.filter((event) => event.minute <= minute && event.resource_id);
    events.forEach((event) => {
      const id = event.resource_id;
      const previous = resources.get(id) || makeResource(id);
      const loc = eventToLocation(event) || { x: previous.x, y: previous.y, cell: previous.cell };
      const trail = previous.trail.concat([{ x: loc.x, y: loc.y, minute: event.minute }]).slice(-9);
      const kind = id.startsWith("RT") ? "reachtruck" : "picker";
      const speedRatio = kind === "picker" ? speedRatioForPicker(id, event) : 100;
      const status = statusLabel(kind, event, speedRatio);
      resources.set(id, {
        ...previous,
        id,
        kind,
        x: loc.x,
        y: loc.y,
        cell: loc.cell,
        waveId: event.wave_id || previous.waveId,
        clientId: event.client_id || previous.clientId,
        sku: event.sku_id || previous.sku,
        palletId: event.pallet_id || previous.palletId,
        taskId: event.task_id || previous.taskId,
        status,
        statusColor: statusColorName(status, speedRatio),
        speedRatio,
        queue: replenishmentTasksAt(minute).filter((task) => task.status !== "DONE").length,
        utilization: clamp(Math.round((minute / SHIFT_MINUTES) * 100), 0, 100),
        driver: id.startsWith("RT") ? `RTD${id.slice(2)}` : "",
        trail,
      });
    });
    for (let index = 1; index <= 10; index += 1) {
      const id = `P${String(index).padStart(2, "0")}`;
      if (!resources.has(id)) resources.set(id, makeResource(id));
    }
    for (let index = 1; index <= 5; index += 1) {
      const id = `RT${String(index).padStart(2, "0")}`;
      if (!resources.has(id)) resources.set(id, makeResource(id));
    }
    return Array.from(resources.values());
  }

  function makeResource(id) {
    const isRt = id.startsWith("RT");
    const n = Number(id.replace(/\D/g, "")) || 1;
    return {
      id,
      kind: isRt ? "reachtruck" : "picker",
      x: isRt ? -4 : 2 + n * 2,
      y: isRt ? (n - 1) * 14 + 3 : (n - 1) * 7 + 3,
      status: "ожид.",
      statusColor: "gray",
      speedRatio: 0,
      queue: 0,
      utilization: 0,
      trail: [],
    };
  }

  function replenishmentTasksAt(minute) {
    const tasks = new Map();
    state.events.filter((event) => event.minute <= minute).forEach((event) => {
      if (!["REPLENISHMENT_PLANNED", "REPLENISHMENT_RELEASED", "REACHTRUCK_TASK_STARTED", "REPLENISHMENT_DONE"].includes(event.event_type)) return;
      const id = event.task_id || `${event.wave_id || "WAVE"}-${event.sku_id || "SKU"}-${event.target_cell || event.minute}`;
      const previous = tasks.get(id) || {
        id,
        waveId: event.wave_id,
        sku: event.sku_id || "SKU",
        targetCell: event.target_cell || event.cell || "A01-S001-L1",
        sourceCell: event.source_cell || "",
        createdMinute: event.minute,
        status: "PLANNED",
        reason: "Низкий остаток",
        stockPercent: 30,
        stockText: "12 / 96 шт",
      };
      if (event.event_type === "REPLENISHMENT_RELEASED") previous.status = "RELEASED";
      if (event.event_type === "REACHTRUCK_TASK_STARTED") previous.status = "IN_PROGRESS";
      if (event.event_type === "REPLENISHMENT_DONE") previous.status = "DONE";
      previous.targetCell = event.target_cell || previous.targetCell;
      previous.sourceCell = event.source_cell || previous.sourceCell;
      previous.sku = event.sku_id || previous.sku;
      previous.waveId = event.wave_id || previous.waveId;
      previous.ageMinutes = Math.max(0, minute - previous.createdMinute);
      previous.overdueMinutes = previous.status !== "DONE" ? Math.max(0, previous.ageMinutes - 15) : 0;
      previous.reason = taskReason(previous);
      previous.zone = `Зона ${parseAisle(previous.targetCell) || 1} · Стеллаж ${aisleLabel(previous.targetCell)}`;
      tasks.set(id, previous);
    });
    if (!tasks.size) {
      activeCollisions(180).slice(-8).forEach((collision, index) => {
        tasks.set(`collision-task-${index}`, {
          id: `collision-task-${index}`,
          waveId: collision.waveId,
          sku: collision.sku || `SKU-${String(80000 + index).padStart(5, "0")}`,
          targetCell: collision.locationLabel || "A01-S023-L1",
          sourceCell: "",
          createdMinute: Math.max(0, collision.minute - 20),
          status: collision.severity === "critical" ? "WAITING" : "QUEUED",
          reason: taskReasonFromCollision(collision.type),
          stockPercent: collision.severity === "critical" ? 0 : 18,
          stockText: collision.severity === "critical" ? "0 / 48 шт" : "12 / 96 шт",
          ageMinutes: Math.max(1, minute - collision.minute + 20),
          overdueMinutes: Math.max(0, minute - collision.minute + 5),
          zone: `Зона ${parseAisle(collision.locationLabel) || 1} · Стеллаж ${aisleLabel(collision.locationLabel)}`,
        });
      });
    }
    return Array.from(tasks.values()).sort((a, b) => b.overdueMinutes - a.overdueMinutes || b.ageMinutes - a.ageMinutes);
  }

  function activeCollisions(windowMinutes = 35) {
    const minMinute = Math.max(0, state.currentMinute - windowMinutes);
    return state.events
      .filter((event) => event.event_type === "COLLISION" && event.minute >= minMinute && event.minute <= state.currentMinute)
      .map((event, index) => normalizeCollision(event, index))
      .filter((collision) => !state.selectedWaveId || collision.waveId === state.selectedWaveId);
  }

  function normalizeCollision(event, index) {
    const type = event.collision_type || event.type || "PICK_FACE_QUEUE";
    const severity = severityForType(type, Number(event.lost_minutes || 1));
    const locationLabel = event.cell || event.segment || event.gate_id || event.locationId || event.target_cell || "A01-S023-L1";
    const affected = Array.isArray(event.resources) ? event.resources : [event.resource_id, event.affected_resource].filter(Boolean);
    const lost = Number(event.lost_minutes || event.lostMinutes || 1);
    return {
      id: event.id || `collision-${event.minute}-${index}`,
      minute: event.minute,
      clock: event.clock || clock(event.minute),
      type,
      severity,
      locationLabel,
      affectedResources: affected,
      waveId: event.wave_id || event.waveId || inferWaveByMinute(event.minute),
      clientId: event.client_id || "",
      sku: event.sku_id || event.sku || "",
      rootCause: rootCauseByType[type] || "Операционная задержка склада",
      lostMinutes: lost,
      productivityLoss: Math.round(lost * 18),
      raw: event,
    };
  }

  function routeProgress(waveId) {
    const base = waveId ? Number(waveId.replace(/\D/g, "")) || 1 : Math.max(1, Math.ceil(state.currentMinute / 60));
    const done = countEvents("PICKER_TASK_DONE", waveId);
    const collisions = activeCollisions(80).filter((row) => !waveId || row.waveId === waveId);
    return [1, 2, 3, 4].map((idx) => {
      const percent = clamp(Math.round((done / Math.max(1, base * 180)) * 100) - idx * 9 + 44, 8, 96);
      const blocked = idx === 4 && collisions.some((row) => row.severity === "critical");
      return {
        id: `R-${100 + idx}`,
        percent: blocked ? 18 : percent,
        blocked,
        color: blocked ? "red" : percent > 75 ? "green" : percent > 45 ? "blue" : "amber",
      };
    });
  }

  function handleCanvasClick(event) {
    const rect = canvas.getBoundingClientRect();
    const x = event.clientX - rect.left;
    const y = event.clientY - rect.top;
    const hit = state.hitRegions.find((region) => Math.hypot(region.x - x, region.y - y) <= region.r);
    if (!hit) return;
    if (hit.type === "resource") showResourceObjectDetail(hit.resource);
    if (hit.type === "collision") showCollisionObjectDetail(hit.collision);
  }

  function showResourceDetail(id) {
    const resource = resourceStateAt(state.currentMinute).find((row) => row.id === id);
    if (resource) showResourceObjectDetail(resource);
  }

  function showResourceObjectDetail(resource) {
    const title = resource.kind === "reachtruck" ? `${resource.id} / ${resource.driver}` : resource.id;
    const body = resource.kind === "reachtruck"
      ? [
          `Статус: ${resource.status}`,
          `Текущая задача: ${resource.taskId || "нет"}`,
          `Очередь: ${resource.queue || 0} задач`,
          `Источник/назначение: ${resource.cell || "маршрут"}`,
          `Волна: ${resource.waveId || "нет"}`,
          `Влияет на: ${resource.clientId || "wave route"}`,
        ]
      : [
          `Статус: ${resource.status}`,
          `Скорость: ${resource.speedRatio}% к плану`,
          `Текущая задача: ${resource.taskId || "нет"}`,
          `Волна: ${resource.waveId || "нет"}`,
          `Клиент: ${resource.clientId || "нет"}`,
          `Паллета: ${resource.palletId || "нет"}`,
          `SKU: ${resource.sku || "нет"}`,
        ];
    setDetail(title, body);
  }

  function showCollisionDetail(id) {
    const collision = activeCollisions(180).find((row) => row.id === id);
    if (collision) showCollisionObjectDetail(collision);
  }

  function showCollisionObjectDetail(collision) {
    setDetail(`Коллизия: ${collision.type}`, [
      `Severity: ${collision.severity}`,
      `Адрес: ${collision.locationLabel}`,
      `Время: ${collision.clock}`,
      `Root cause: ${collision.rootCause}`,
      `Affected resources: ${collision.affectedResources.join(", ") || "не указано"}`,
      `Wave/client: ${collision.waveId || "-"} / ${collision.clientId || "-"}`,
      `Lost minutes: ${collision.lostMinutes}`,
      `Productivity loss: ~${collision.productivityLoss}/час`,
    ]);
  }

  function showTaskDetail(id) {
    const task = replenishmentTasksAt(state.currentMinute).find((row) => row.id === id);
    if (!task) return;
    setDetail(`RTP задача ${task.id}`, [
      `Статус: ${task.status}`,
      `Источник: ${task.sourceCell || "ожидает выбора"}`,
      `Назначение: ${task.targetCell}`,
      `SKU: ${task.sku}`,
      `Просрочка: ${task.overdueMinutes} мин`,
      `Причина: ${task.reason}`,
      `Волна: ${task.waveId || "нет"}`,
    ]);
  }

  function setDetail(title, rows) {
    els.detailCard.innerHTML = `<b>${escapeHtml(title)}</b>${rows.map((row) => `<span>${escapeHtml(row)}</span>`).join("")}`;
  }

  function eventToLocation(event) {
    const cellId = event.cell || event.target_cell || event.source_cell || event.locationId;
    const cell = cellId ? cellById(cellId) : null;
    if (cell) return { x: Number(cell.x_m), y: Number(cell.y_m), cell: cell.cell_id };
    if (event.from?.x !== undefined) return { x: Number(event.from.x), y: Number(event.from.y), cell: event.from.locationId || "" };
    if (event.to?.x !== undefined) return { x: Number(event.to.x), y: Number(event.to.y), cell: event.to.locationId || "" };
    if (event.segment) {
      const parsed = /A(\d+)-SEG(\d+)/.exec(event.segment);
      if (parsed) return { x: Number(parsed[2]) * 10 + 5, y: (Number(parsed[1]) - 1) * 4, cell: event.segment };
    }
    return null;
  }

  function collisionLocation(collision) {
    const raw = collision.raw || {};
    const cell = cellById(raw.cell || raw.target_cell || raw.source_cell || collision.locationLabel);
    if (cell) return { x: Number(cell.x_m), y: Number(cell.y_m) };
    if (raw.segment) {
      const parsed = /A(\d+)-SEG(\d+)/.exec(raw.segment);
      if (parsed) return { x: Number(parsed[2]) * 10 + 5, y: (Number(parsed[1]) - 1) * 4 };
    }
    const aisle = parseAisle(collision.locationLabel) || 3;
    return { x: 30 + (collision.minute % 30), y: (aisle - 1) * 4 };
  }

  function cellById(id) {
    return state.layout.cells.find((cell) => cell.cell_id === id || cell.locationId === id);
  }

  function speedRatioForPicker(id, event) {
    const base = { P01: 78, P02: 96, P03: 64, P04: 74, P05: 104, P06: 88, P07: 132, P08: 118, P09: 121, P10: 98 }[id] || 96;
    if (event.event_type === "COLLISION") return Math.max(35, base - 30);
    return clamp(base + ((state.currentMinute + Number(id.replace(/\D/g, ""))) % 17) - 8, 45, 138);
  }

  function statusLabel(kind, event, speedRatio) {
    if (kind === "reachtruck") {
      if (event.event_type === "REACHTRUCK_TASK_STARTED") return "в пути";
      if (event.event_type === "REPLENISHMENT_DONE") return "готов";
      return "queue";
    }
    if (speedRatio < 60) return "стоп";
    if (speedRatio < 82) return "замедлен";
    if (event.event_type === "PICKER_TASK_DONE") return "готов";
    return "отбор";
  }

  function statusColorName(status, speedRatio) {
    if (status === "стоп") return "red";
    if (status === "замедлен") return "amber";
    if (status === "ожид.") return "gray";
    if (speedRatio >= 105) return "green";
    return "blue";
  }

  function statusColor(name) {
    return COLORS[name] || COLORS.blue;
  }

  function taskReason(task) {
    if (task.overdueMinutes > 20) return "Пик-лицо пусто";
    if (task.status === "QUEUED") return "Нет динамической ячейки";
    if (task.status === "PLANNED") return "Minimax wait";
    return "Низкий остаток";
  }

  function taskReasonFromCollision(type) {
    if (type === "PICK_FACE_QUEUE") return "Пик-лицо пусто";
    if (type === "DYNAMIC_CELL_SHORTAGE") return "Нет динамической ячейки";
    if (type === "MINIMAX_WAIT") return "Minimax wait";
    return "Низкий остаток";
  }

  function activeCollisionTypes() {
    return new Set(activeCollisions(120).map((row) => row.type));
  }

  function severityForType(type, lost) {
    if (["PICK_FACE_QUEUE", "REACHTRUCK_BLOCK", "DOCK_QUEUE", "REACH_RESOURCE_SHORTAGE"].includes(type) || lost >= 5) return "critical";
    return "warning";
  }

  function severityForEvent(event) {
    return severityForType(event.collision_type || event.type, Number(event.lost_minutes || 1));
  }

  function collisionTitle(collision) {
    return {
      PICK_FACE_QUEUE: "Пик-лицо пусто",
      AISLE_CONGESTION: "Затор в проходе",
      REACHTRUCK_BLOCK: "Блокировка маршрута",
      DYNAMIC_CELL_SHORTAGE: "Нет dynamic ячейки",
      MINIMAX_WAIT: "Minimax wait",
      REACH_RESOURCE_SHORTAGE: "Очередь RTP",
      PICKER_RESOURCE_SHORTAGE: "Нехватка комплектовщиков",
      DOCK_QUEUE: "Очередь на ворота",
      SHIPMENT_RATE_LIMIT: "Ограничение отгрузки",
    }[collision.type] || collision.type;
  }

  function countEvents(type, waveId = "") {
    return state.events.filter((event) => event.minute <= state.currentMinute && event.event_type === type && (!waveId || event.wave_id === waveId)).length;
  }

  function inferCurrentWave() {
    return inferWaveByMinute(state.currentMinute);
  }

  function inferWaveByMinute(minute) {
    return `WAVE-SIM-${String(Math.min(10, Math.floor(minute / 60) + 1)).padStart(2, "0")}`;
  }

  function latestEventMinute() {
    return Math.max(0, ...state.events.map((event) => Number(event.minute || 0)));
  }

  function clock(minute) {
    const value = SHIFT_START_HOUR * 60 + Number(minute || 0);
    return `${String(Math.floor(value / 60)).padStart(2, "0")}:${String(value % 60).padStart(2, "0")}`;
  }

  function parseAisle(cellId) {
    const match = /A(\d+)/.exec(String(cellId || ""));
    return match ? Number(match[1]) : 0;
  }

  function parseSlot(cellId) {
    const match = /S(\d+)/.exec(String(cellId || ""));
    return match ? Number(match[1]) : 1;
  }

  function aisleLabel(cellId) {
    const aisle = parseAisle(cellId);
    return aisle ? `A${String(aisle).padStart(2, "0")}` : "A01";
  }

  function polygon(points, fill, stroke, lineWidth) {
    ctx.beginPath();
    points.forEach((point, index) => {
      if (index === 0) ctx.moveTo(point.x, point.y);
      else ctx.lineTo(point.x, point.y);
    });
    ctx.closePath();
    ctx.fillStyle = fill;
    ctx.fill();
    if (stroke) {
      ctx.strokeStyle = stroke;
      ctx.lineWidth = lineWidth;
      ctx.stroke();
    }
  }

  function shade(hex, amount) {
    return hex;
  }

  async function fetchJson(url) {
    const response = await fetch(url, { cache: "no-store" });
    if (!response.ok) throw new Error(`${response.status} ${url}`);
    return response.json();
  }

  async function fetchJsonOptional(url) {
    try {
      return await fetchJson(url);
    } catch {
      return null;
    }
  }

  async function fetchText(url) {
    const response = await fetch(url, { cache: "no-store" });
    if (!response.ok) throw new Error(`${response.status} ${url}`);
    return response.text();
  }

  async function fetchTextOptional(url) {
    try {
      return await fetchText(url);
    } catch {
      return "";
    }
  }

  function bindFileInput(input, type, callback) {
    input.addEventListener("change", () => {
      const file = input.files && input.files[0];
      if (!file) return;
      file.text().then((text) => {
        if (type === "json") callback(JSON.parse(text));
        if (type === "jsonl") callback(parseJsonl(text));
        if (type === "csv") callback(parseCsv(text));
        setEvidenceStatus(`loaded ${file.name}`);
      });
    });
  }

  function parseJsonl(text) {
    return text.split(/\r?\n/).map((line) => line.trim()).filter(Boolean).map((line) => JSON.parse(line));
  }

  function parseCsv(text) {
    const rows = text.split(/\r?\n/).filter(Boolean);
    if (!rows.length) return [];
    const headers = splitCsvLine(rows[0]);
    return rows.slice(1).map((row) => {
      const values = splitCsvLine(row);
      return headers.reduce((acc, header, index) => {
        acc[header] = values[index] ?? "";
        return acc;
      }, {});
    });
  }

  function splitCsvLine(line) {
    const result = [];
    let value = "";
    let quoted = false;
    for (let index = 0; index < line.length; index += 1) {
      const char = line[index];
      if (char === '"') quoted = !quoted;
      else if (char === "," && !quoted) {
        result.push(value);
        value = "";
      } else {
        value += char;
      }
    }
    result.push(value);
    return result;
  }

  function setEvidenceStatus(value) {
    els.evidenceStatus.textContent = value;
  }

  function getInitialMinute() {
    const params = new URLSearchParams(window.location.search);
    const initialMinute = params.get("minute") || hashParam("minute");
    return initialMinute ? clamp(Number(initialMinute), 0, SHIFT_MINUTES) : 102;
  }

  function hashParam(name) {
    const hash = window.location.hash.replace(/^#/, "").replaceAll(";", "&");
    if (!hash) return "";
    return new URLSearchParams(hash).get(name) || "";
  }

  function clamp(value, min, max) {
    return Math.max(min, Math.min(max, value));
  }

  function formatNumber(value) {
    return new Intl.NumberFormat("ru-RU").format(Math.round(Number(value || 0)));
  }

  function escapeHtml(value) {
    return String(value ?? "")
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;");
  }

  function buildDemoLayout() {
    const cells = [];
    const gates = [];
    for (let aisle = 1; aisle <= 25; aisle += 1) {
      const y = (aisle - 1) * 4;
      gates.push({ gate_id: `G${String(aisle).padStart(2, "0")}`, aisle, x_m: 0, y_m: y });
      for (let slot = 1; slot <= 60; slot += 1) {
        const role = slot % 13 === 0 ? "DYNAMIC_PICK_FACE" : slot % 17 === 0 ? "DUPLICATE_A_PICK_FACE" : "FIXED_PICK_FACE";
        cells.push({ cell_id: `A${String(aisle).padStart(2, "0")}-S${String(slot).padStart(3, "0")}-L1`, aisle, slot, level: 1, x_m: (slot - 1) * 1.5, y_m: y, role });
      }
    }
    return { run_id: "demo", gates, cells };
  }

  function buildDemoEvents() {
    const events = [];
    for (let wave = 1; wave <= 10; wave += 1) {
      const minute = (wave - 1) * 60;
      events.push({ minute, clock: clock(minute), event_type: "WAVE_LAUNCHED", wave_id: `WAVE-SIM-${String(wave).padStart(2, "0")}`, clients: 5 });
    }
    for (let minute = 6; minute <= SHIFT_MINUTES; minute += 8) {
      const waveId = inferWaveByMinute(minute);
      const aisle = 1 + (minute % 25);
      const slot = 1 + (minute % 60);
      events.push({ minute, clock: clock(minute), event_type: "PICKER_TASK_STARTED", resource_id: `P${String((minute % 10) + 1).padStart(2, "0")}`, wave_id: waveId, client_id: `C${String(Math.min(50, Math.ceil(minute / 12))).padStart(3, "0")}`, pallet_id: `CP-${minute}`, sku_id: `SKU-${String((minute % 1000) + 1).padStart(4, "0")}`, cell: `A${String(aisle).padStart(2, "0")}-S${String(slot).padStart(3, "0")}-L1`, qty_boxes: 4 });
    }
    for (let minute = 8; minute <= SHIFT_MINUTES; minute += 13) {
      const waveId = inferWaveByMinute(minute);
      const target = `A${String(1 + ((minute + 3) % 25)).padStart(2, "0")}-S${String(1 + (minute % 45)).padStart(3, "0")}-L1`;
      const source = `A${String(1 + (minute % 25)).padStart(2, "0")}-S${String(20 + (minute % 30)).padStart(3, "0")}-L1`;
      events.push({ minute, clock: clock(minute), event_type: "REPLENISHMENT_RELEASED", task_id: `RPL-${minute}`, resource_id: `RT${String((minute % 5) + 1).padStart(2, "0")}`, wave_id: waveId, sku_id: `SKU-${String((minute % 1000) + 1).padStart(4, "0")}`, source_cell: source, target_cell: target });
      events.push({ minute: minute + 1, clock: clock(minute + 1), event_type: "REACHTRUCK_TASK_STARTED", task_id: `RPL-${minute}`, resource_id: `RT${String((minute % 5) + 1).padStart(2, "0")}`, wave_id: waveId, source_cell: source, target_cell: target });
      events.push({ minute: minute + 7, clock: clock(minute + 7), event_type: "REPLENISHMENT_DONE", task_id: `RPL-${minute}`, resource_id: `RT${String((minute % 5) + 1).padStart(2, "0")}`, wave_id: waveId, source_cell: source, target_cell: target });
    }
    ["PICK_FACE_QUEUE", "AISLE_CONGESTION", "REACHTRUCK_BLOCK", "DOCK_QUEUE", "REACH_RESOURCE_SHORTAGE"].forEach((type, offset) => {
      for (let minute = 42 + offset * 17; minute <= 690; minute += 91) {
        const aisle = 1 + ((minute + offset) % 25);
        const slot = 1 + (minute % 55);
        events.push({ minute, clock: clock(minute), event_type: "COLLISION", collision_type: type, wave_id: inferWaveByMinute(minute), cell: `A${String(aisle).padStart(2, "0")}-S${String(slot).padStart(3, "0")}-L1`, resources: [`P${String((minute % 10) + 1).padStart(2, "0")}`, `RT${String((minute % 5) + 1).padStart(2, "0")}`], lost_minutes: 4 + (minute % 8) });
      }
    });
    return events.sort((a, b) => a.minute - b.minute);
  }

  function buildDemoMetrics() {
    const rows = [];
    for (let minute = 0; minute <= SHIFT_MINUTES; minute += 1) {
      rows.push({
        minute,
        done_pick_lines: Math.round(minute * 13.1),
        total_pick_lines: 9447,
        picker_busy: Math.min(10, Math.ceil(minute / 18)),
      });
    }
    return rows;
  }

  function buildDemoReport() {
    return {
      run_id: "demo",
      scenario: { clients: 50, waves: 10, sku: 1000, pick_faces: 1500, pickers: 10, reachtrucks: 5 },
      totals: { pick_lines: 9447, replenishment_tasks: 90, shipped_pallets: 202, collisions: 121, lost_minutes: 247 },
    };
  }
})();
