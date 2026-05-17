const state = {
  calls: [],
  slowSql: [],
  selectedId: null,
};

const el = (id) => document.getElementById(id);

function apiBase() {
  return (window.wmsAdminAuth?.state?.apiBase || "http://127.0.0.1:8088").replace(/\/$/, "");
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

function slowSqlFilters() {
  const params = new URLSearchParams();
  const path = el("slowSqlPath")?.value.trim();
  const minMs = el("slowSqlMinMs")?.value;
  const hash = el("slowSqlHash")?.value.trim();
  const limit = el("slowSqlLimit")?.value || "50";
  if (path) params.set("path_like", path);
  if (minMs !== "") params.set("min_elapsed_ms", minMs);
  if (hash) params.set("sql_hash", hash);
  params.set("limit", limit);
  return params;
}

async function loadSlowSql() {
  if (!el("slowSqlRows")) return;
  el("slowSqlStatus").textContent = "Загрузка...";
  const response = await fetch(`${apiBase()}/api/admin/slow-sql?${slowSqlFilters().toString()}`, {
    headers: requestHeaders(),
  });
  if (response.status === 403) throw new Error("Нет права просмотра Slow SQL");
  if (!response.ok) throw new Error(`HTTP ${response.status}`);
  state.slowSql = await response.json();
  renderSlowSqlRows("log");
  el("slowSqlStatus").textContent = `Записей: ${state.slowSql.length}`;
}

async function loadSlowSqlTop() {
  if (!el("slowSqlRows")) return;
  el("slowSqlStatus").textContent = "Расчет топа...";
  const limit = el("slowSqlLimit").value || "50";
  const response = await fetch(`${apiBase()}/api/admin/slow-sql/top?limit=${encodeURIComponent(limit)}`, {
    headers: requestHeaders(),
  });
  if (response.status === 403) throw new Error("Нет права просмотра Slow SQL");
  if (!response.ok) throw new Error(`HTTP ${response.status}`);
  state.slowSql = await response.json();
  renderSlowSqlRows("top");
  el("slowSqlStatus").textContent = `Групп запросов: ${state.slowSql.length}`;
}

async function loadOracleTopSql() {
  if (!el("slowSqlRows")) return;
  el("slowSqlStatus").textContent = "Чтение Oracle V$SQL...";
  const limit = el("slowSqlLimit").value || "50";
  const response = await fetch(`${apiBase()}/api/admin/slow-sql/oracle-top?limit=${encodeURIComponent(limit)}`, {
    headers: requestHeaders(),
  });
  if (response.status === 403) throw new Error("Нет права просмотра Slow SQL");
  if (!response.ok) throw new Error(`HTTP ${response.status}`);
  const result = await response.json();
  state.slowSql = result.rows || [];
  renderSlowSqlRows("oracle");
  el("slowSqlStatus").textContent = result.available
    ? `Oracle SQL: ${state.slowSql.length}`
    : `Oracle V$SQL недоступен: ${result.error || "нет прав"}`;
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

function renderSlowSqlRows(mode) {
  const tbody = el("slowSqlRows");
  tbody.innerHTML = "";
  for (const row of state.slowSql) {
    const tr = document.createElement("tr");
    if (mode === "top") {
      tr.innerHTML = `
        <td>${escapeHtml(row.sql_text_hash || "")}</td>
        <td>${formatDate(row.last_seen_at)}</td>
        <td title="${escapeHtml(row.api_path_sample || "")}">${escapeHtml(row.api_path_sample || "")}</td>
        <td>${escapeHtml(row.operation_kind_sample || "")}</td>
        <td>${row.max_elapsed_ms ?? ""}</td>
        <td>${row.exec_count ?? ""}</td>
        <td>${row.avg_elapsed_ms ?? ""}</td>
      `;
      tr.addEventListener("click", () => {
        el("slowSqlDetails").textContent = JSON.stringify(row, null, 2);
      });
    } else if (mode === "oracle") {
      tr.innerHTML = `
        <td>${escapeHtml(row.sql_id || "")}</td>
        <td>${escapeHtml(row.module || "")}</td>
        <td title="${escapeHtml(row.action || "")}">${escapeHtml(row.action || "")}</td>
        <td>${row.executions ?? ""}</td>
        <td>${row.elapsed_ms_avg ?? row.elapsed_ms_total ?? ""}</td>
        <td>${row.buffer_gets ?? ""}</td>
        <td>${row.disk_reads ?? ""}</td>
      `;
      tr.addEventListener("click", () => {
        el("slowSqlDetails").textContent = JSON.stringify(row, null, 2);
      });
    } else {
      tr.innerHTML = `
        <td>${row.log_id ?? ""}</td>
        <td>${formatDate(row.created_at)}</td>
        <td title="${escapeHtml(row.api_path || "")}">${escapeHtml(row.api_path || "")}</td>
        <td>${escapeHtml(row.operation_kind || "")}</td>
        <td>${row.elapsed_ms ?? ""}</td>
        <td>${row.row_count ?? ""}</td>
        <td>${row.error_text ? "Да" : ""}</td>
      `;
      tr.addEventListener("click", () => loadSlowSqlDetails(row.log_id));
    }
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

async function loadSlowSqlDetails(id) {
  if (!id) return;
  el("slowSqlDetails").textContent = "Загрузка...";
  const response = await fetch(`${apiBase()}/api/admin/slow-sql/${id}`, {
    headers: requestHeaders(),
  });
  if (!response.ok) throw new Error(`HTTP ${response.status}`);
  const detail = await response.json();
  el("slowSqlDetails").textContent = JSON.stringify(detail, null, 2);
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
  initSlowSql();
}

function initSlowSql() {
  if (!el("slowSqlRefresh")) return;
  if (window.wmsAdminAuth && !window.wmsAdminAuth.hasPermission("slow_sql_view")) {
    el("slowSql").hidden = true;
    return;
  }
  el("slowSqlRefresh").addEventListener("click", () => loadSlowSql().catch(showSlowSqlError));
  el("slowSqlTop").addEventListener("click", () => loadSlowSqlTop().catch(showSlowSqlError));
  el("slowSqlOracleTop").addEventListener("click", () => loadOracleTopSql().catch(showSlowSqlError));
  for (const id of ["slowSqlPath", "slowSqlMinMs", "slowSqlHash", "slowSqlLimit"]) {
    el(id).addEventListener("change", () => loadSlowSql().catch(showSlowSqlError));
  }
  loadSlowSql().catch(showSlowSqlError);
}

function showError(error) {
  el("apiAuditStatus").textContent = `Ошибка: ${error.message}`;
}

function showSlowSqlError(error) {
  if (el("slowSqlStatus")) {
    el("slowSqlStatus").textContent = `Ошибка: ${error.message}`;
  }
}

if (window.wmsAdminAuth && window.wmsAdminAuth.state.user) {
  initApiAudit();
} else {
  window.addEventListener("wms-admin-auth-ready", initApiAudit, { once: true });
}
