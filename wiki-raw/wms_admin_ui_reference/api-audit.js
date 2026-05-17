const state = {
  calls: [],
  selectedId: null,
};

const el = (id) => document.getElementById(id);

function apiBase() {
  return el("apiAuditBase").value.replace(/\/$/, "");
}

function requestHeaders(extra = {}) {
  if (!window.wmsAdminAuth) return { ...extra };
  return window.wmsAdminAuth.headers(extra);
}

function canReplay() {
  return window.wmsAdminAuth && window.wmsAdminAuth.hasPermission("api_audit_replay");
}

function filters() {
  const params = new URLSearchParams();
  const method = el("apiAuditMethod").value;
  const path = el("apiAuditPath").value.trim();
  const fromId = el("apiAuditFromId").value;
  const toId = el("apiAuditToId").value;
  const fromAt = el("apiAuditFromAt").value;
  const toAt = el("apiAuditToAt").value;
  const limit = el("apiAuditLimit").value || "50";
  if (method) params.set("method", method);
  if (path) params.set("path_like", path);
  if (fromId) params.set("from_call_id", fromId);
  if (toId) params.set("to_call_id", toId);
  if (fromAt) params.set("from_at", fromAt);
  if (toAt) params.set("to_at", toAt);
  params.set("limit", limit);
  return params;
}

async function loadCalls() {
  el("apiAuditStatus").textContent = "Загрузка...";
  const response = await fetch(`${apiBase()}/api/admin/api-calls?${filters().toString()}`, {
    headers: requestHeaders(),
  });
  if (!response.ok) throw new Error(`HTTP ${response.status}`);
  state.calls = await response.json();
  renderRows();
  el("apiAuditStatus").textContent = `Вызовов: ${state.calls.length}`;
}

function renderRows() {
  const tbody = el("apiAuditRows");
  tbody.innerHTML = "";
  for (const call of state.calls) {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td>${call.api_call_id ?? ""}</td>
      <td>${formatDate(call.started_at)}</td>
      <td>${call.method ?? ""}</td>
      <td title="${escapeHtml(call.path ?? "")}">${escapeHtml(call.path ?? "")}</td>
      <td>${call.response_status ?? ""}</td>
      <td>${call.status ?? ""}</td>
      <td>${call.duration_ms ?? ""}</td>
      <td>${call.replay_count ?? 0}</td>
    `;
    tr.addEventListener("click", () => loadDetails(call.api_call_id));
    tbody.appendChild(tr);
  }
}

async function loadDetails(id) {
  state.selectedId = id;
  el("apiAuditDetails").textContent = "Загрузка...";
  const response = await fetch(`${apiBase()}/api/admin/api-calls/${id}`, {
    headers: requestHeaders(),
  });
  if (!response.ok) throw new Error(`HTTP ${response.status}`);
  const detail = await response.json();
  el("apiAuditDetails").textContent = JSON.stringify(detail, null, 2);
}

function replayPayload(dryRun) {
  const payload = {
    dry_run: dryRun,
    max_calls: Number(el("apiAuditLimit").value || 50),
    continue_on_error: true,
  };
  const method = el("apiAuditMethod").value;
  const path = el("apiAuditPath").value.trim();
  const fromId = el("apiAuditFromId").value;
  const toId = el("apiAuditToId").value;
  const fromAt = el("apiAuditFromAt").value;
  const toAt = el("apiAuditToAt").value;
  if (method) payload.method = method;
  if (path) payload.path_like = path;
  if (fromId) payload.from_call_id = Number(fromId);
  if (toId) payload.to_call_id = Number(toId);
  if (fromAt) payload.from_at = fromAt;
  if (toAt) payload.to_at = toAt;
  if (!fromId && !toId && !fromAt && !toAt && state.selectedId) payload.call_ids = [state.selectedId];
  return payload;
}

async function replay(dryRun) {
  if (!dryRun && !canReplay()) {
    throw new Error("Нет права api_audit_replay");
  }
  el("apiAuditReplayStatus").textContent = dryRun ? "Dry run..." : "Повтор...";
  const response = await fetch(`${apiBase()}/api/admin/api-calls/replay`, {
    method: "POST",
    headers: requestHeaders({ "Content-Type": "application/json" }),
    body: JSON.stringify(replayPayload(dryRun)),
  });
  const result = await response.json();
  el("apiAuditReplayStatus").textContent = dryRun
    ? `Dry run: ${result.selected_count ?? 0}`
    : `Повторено: ${result.executed_count ?? 0}`;
  el("apiAuditDetails").textContent = JSON.stringify(result, null, 2);
  if (!dryRun) await loadCalls();
}

function formatDate(value) {
  if (!value) return "";
  return String(value).replace("T", " ").slice(0, 19);
}

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;");
}

function initApiAudit() {
  if (!el("apiAuditRefresh")) return;
  if (window.wmsAdminAuth && !window.wmsAdminAuth.hasPermission("api_audit_view")) return;

  const replayButton = el("apiAuditReplay");
  if (replayButton && !canReplay()) {
    replayButton.disabled = true;
    replayButton.title = "Нет права api_audit_replay";
  }

  el("apiAuditRefresh").addEventListener("click", () => loadCalls().catch(showError));
  el("apiAuditDryRun").addEventListener("click", () => replay(true).catch(showError));
  el("apiAuditReplay").addEventListener("click", () => {
    const ok = window.confirm("Повторить выбранный диапазон API вызовов?");
    if (ok) replay(false).catch(showError);
  });

  for (const id of ["apiAuditMethod", "apiAuditPath", "apiAuditFromId", "apiAuditToId", "apiAuditFromAt", "apiAuditToAt", "apiAuditLimit"]) {
    el(id).addEventListener("change", () => loadCalls().catch(showError));
  }

  loadCalls().catch(showError);
}

function showError(error) {
  el("apiAuditStatus").textContent = `Ошибка: ${error.message}`;
}

if (window.wmsAdminAuth && window.wmsAdminAuth.state.user) {
  initApiAudit();
} else {
  window.addEventListener("wms-admin-auth-ready", initApiAudit, { once: true });
}
