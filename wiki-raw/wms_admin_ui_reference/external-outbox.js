const externalState = {
  events: [],
  adapterRequests: [],
  selectedEventId: null,
};

const outboxEl = (id) => document.getElementById(id);

function externalApiBase() {
  return outboxEl("externalBase").value.replace(/\/$/, "");
}

function externalHeaders(extra = {}) {
  if (!window.wmsAdminAuth) return { ...extra };
  return window.wmsAdminAuth.headers(extra);
}

function canRetryExternal() {
  return window.wmsAdminAuth && window.wmsAdminAuth.hasPermission("external_outbox_retry");
}

function outboxFilters() {
  const params = new URLSearchParams();
  const fields = [
    ["target_system", "externalSystem"],
    ["status", "externalStatus"],
    ["event_type", "externalEventType"],
    ["aggregate_type", "externalAggregateType"],
    ["aggregate_id", "externalAggregateId"],
    ["limit", "externalLimit"],
  ];
  for (const [param, id] of fields) {
    const value = outboxEl(id).value.trim();
    if (value) params.set(param, value);
  }
  if (!params.has("limit")) params.set("limit", "50");
  return params;
}

async function loadOutbox() {
  outboxEl("externalStatusText").textContent = "Загрузка...";
  const response = await fetch(`${externalApiBase()}/api/admin/event-outbox?${outboxFilters().toString()}`, {
    headers: externalHeaders(),
  });
  if (!response.ok) throw new Error(`Outbox HTTP ${response.status}`);
  externalState.events = await response.json();
  renderOutboxRows();
  outboxEl("externalStatusText").textContent = `Событий: ${externalState.events.length}`;
  await loadAdapters();
}

function renderOutboxRows() {
  const tbody = outboxEl("externalRows");
  tbody.innerHTML = "";
  for (const event of externalState.events) {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td>${event.event_outbox_id ?? ""}</td>
      <td>${formatExternalDate(event.created_at)}</td>
      <td>${escapeExternal(event.target_system ?? "")}</td>
      <td>${escapeExternal(event.event_type ?? "")}</td>
      <td>${escapeExternal(`${event.aggregate_type ?? ""}:${event.aggregate_id ?? ""}`)}</td>
      <td>${escapeExternal(event.status ?? "")}</td>
      <td>${event.try_count ?? 0}/${event.max_try_count ?? ""}</td>
      <td title="${escapeExternal(event.last_error ?? "")}">${escapeExternal(shorten(event.last_error ?? ""))}</td>
    `;
    tr.addEventListener("click", () => loadOutboxDetail(event.event_outbox_id));
    tbody.appendChild(tr);
  }
}

async function loadOutboxDetail(id) {
  externalState.selectedEventId = id;
  outboxEl("externalDetails").textContent = "Загрузка...";
  const response = await fetch(`${externalApiBase()}/api/admin/event-outbox/${id}`, {
    headers: externalHeaders(),
  });
  if (!response.ok) throw new Error(`Outbox detail HTTP ${response.status}`);
  const detail = await response.json();
  outboxEl("externalDetails").textContent = JSON.stringify(detail, null, 2);
  await loadAdapters(id);
}

async function loadAdapters(eventOutboxId = null) {
  outboxEl("adapterStatusText").textContent = "Загрузка...";
  const params = new URLSearchParams();
  if (eventOutboxId) params.set("event_outbox_id", eventOutboxId);
  params.set("limit", outboxEl("externalLimit").value || "50");
  const response = await fetch(`${externalApiBase()}/api/admin/adapter-requests?${params.toString()}`, {
    headers: externalHeaders(),
  });
  if (!response.ok) throw new Error(`Adapter HTTP ${response.status}`);
  externalState.adapterRequests = await response.json();
  renderAdapterRows();
  outboxEl("adapterStatusText").textContent = `Запросов: ${externalState.adapterRequests.length}`;
}

function renderAdapterRows() {
  const tbody = outboxEl("adapterRows");
  tbody.innerHTML = "";
  for (const row of externalState.adapterRequests) {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td>${row.adapter_request_id ?? ""}</td>
      <td>${row.event_outbox_id ?? ""}</td>
      <td>${escapeExternal(row.system_code ?? "")}</td>
      <td>${escapeExternal(row.request_kind ?? "")}</td>
      <td>${escapeExternal(row.business_key ?? "")}</td>
      <td>${row.http_status ?? ""}</td>
      <td>${escapeExternal(row.status ?? "")}</td>
      <td>${escapeExternal(row.external_status ?? "")}</td>
    `;
    tr.addEventListener("click", () => loadAdapterDetail(row.adapter_request_id));
    tbody.appendChild(tr);
  }
}

async function loadAdapterDetail(id) {
  outboxEl("adapterDetails").textContent = "Загрузка...";
  const response = await fetch(`${externalApiBase()}/api/admin/adapter-requests/${id}`, {
    headers: externalHeaders(),
  });
  if (!response.ok) throw new Error(`Adapter detail HTTP ${response.status}`);
  const detail = await response.json();
  outboxEl("adapterDetails").textContent = JSON.stringify(detail, null, 2);
}

async function retrySelected(dryRun) {
  if (!externalState.selectedEventId) {
    throw new Error("Выберите outbox-событие.");
  }
  if (!dryRun && !canRetryExternal()) {
    throw new Error("Нет права external_outbox_retry");
  }
  const reason = dryRun ? "UI dry run" : window.prompt("Причина повтора", "Ручной повтор из админки");
  if (!dryRun && reason === null) return;
  outboxEl("externalRetryStatus").textContent = dryRun ? "Dry run..." : "Повтор...";
  const response = await fetch(`${externalApiBase()}/api/admin/event-outbox/${externalState.selectedEventId}/retry`, {
    method: "POST",
    headers: externalHeaders({ "Content-Type": "application/json" }),
    body: JSON.stringify({ dry_run: dryRun, reason }),
  });
  const result = await response.json();
  if (!response.ok) throw new Error(result.detail || `Retry HTTP ${response.status}`);
  outboxEl("externalRetryStatus").textContent = dryRun ? "Dry run готов" : "Поставлено в очередь";
  outboxEl("externalDetails").textContent = JSON.stringify(result, null, 2);
  if (!dryRun) await loadOutbox();
}

function formatExternalDate(value) {
  if (!value) return "";
  return String(value).replace("T", " ").slice(0, 19);
}

function shorten(value) {
  const text = String(value || "");
  return text.length > 80 ? `${text.slice(0, 77)}...` : text;
}

function escapeExternal(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;");
}

function initExternalOutbox() {
  if (!outboxEl("externalRefresh")) return;
  if (window.wmsAdminAuth && !window.wmsAdminAuth.hasPermission("external_outbox_view")) return;

  const retryButton = outboxEl("externalRetry");
  if (retryButton && !canRetryExternal()) {
    retryButton.disabled = true;
    retryButton.title = "Нет права external_outbox_retry";
  }

  outboxEl("externalRefresh").addEventListener("click", () => loadOutbox().catch(showExternalError));
  outboxEl("adapterRefresh").addEventListener("click", () => loadAdapters(externalState.selectedEventId).catch(showExternalError));
  outboxEl("externalDryRun").addEventListener("click", () => retrySelected(true).catch(showExternalError));
  outboxEl("externalRetry").addEventListener("click", () => retrySelected(false).catch(showExternalError));

  for (const id of ["externalSystem", "externalStatus", "externalEventType", "externalAggregateType", "externalAggregateId", "externalLimit"]) {
    outboxEl(id).addEventListener("change", () => loadOutbox().catch(showExternalError));
  }

  loadOutbox().catch(showExternalError);
}

function showExternalError(error) {
  outboxEl("externalStatusText").textContent = `Ошибка: ${error.message}`;
}

if (window.wmsAdminAuth && window.wmsAdminAuth.state.user) {
  initExternalOutbox();
} else {
  window.addEventListener("wms-admin-auth-ready", initExternalOutbox, { once: true });
}
