const bomState = {
  boms: [],
  selectedBom: null,
};

const bomEl = (id) => document.getElementById(id);

function bomApiBase() {
  return (window.wmsAdminAuth?.state?.apiBase || "http://127.0.0.1:8088").replace(/\/$/, "");
}

function bomHeaders(extra = {}) {
  if (!window.wmsAdminAuth) return { ...extra };
  return window.wmsAdminAuth.headers(extra);
}

function bomCan(permission) {
  return window.wmsAdminAuth && window.wmsAdminAuth.hasPermission(permission);
}

function bomCurrentUser() {
  return window.wmsAdminAuth?.state?.user?.username || "admin";
}

function bomFilters() {
  const params = new URLSearchParams();
  const target = bomEl("bomTargetFilter").value.trim() || bomEl("bomSearch").value.trim();
  if (target) params.set("target_articul", target);
  if (bomEl("bomStatusFilter").value) params.set("status", bomEl("bomStatusFilter").value);
  if (bomEl("bomPrimaryFilter").value !== "") params.set("is_primary", bomEl("bomPrimaryFilter").value);
  if (bomEl("bomActiveOnFilter").value) params.set("active_on", bomEl("bomActiveOnFilter").value);
  params.set("limit", bomEl("bomLimit").value || "100");
  return params;
}

async function bomLoadList() {
  bomEl("bomStatusText").textContent = "Загрузка...";
  const response = await fetch(`${bomApiBase()}/api/bom?${bomFilters().toString()}`, {
    headers: bomHeaders(),
  });
  if (!response.ok) throw new Error(`BOM HTTP ${response.status}`);
  bomState.boms = await response.json();
  renderBomRows();
  bomEl("bomStatusText").textContent = `Рецептов: ${bomState.boms.length}`;
}

function renderBomRows() {
  const tbody = bomEl("bomRows");
  tbody.innerHTML = "";
  for (const bom of bomState.boms) {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td>${bom.bom_id ?? ""}</td>
      <td>${escapeBom(bom.bom_code ?? "")}</td>
      <td>${escapeBom(bom.target_articul ?? "")}</td>
      <td>${escapeBom(bom.status ?? "")}</td>
      <td>${bom.is_primary === 1 ? "Да" : "Нет"}</td>
      <td>${bom.version_no ?? ""}</td>
      <td>${bom.base_qty ?? ""} ${escapeBom(bom.base_unit_code ?? "")}</td>
      <td>${bom.line_count ?? 0}</td>
    `;
    tr.addEventListener("click", () => loadBomDetail(bom.bom_id));
    tbody.appendChild(tr);
  }
}

async function loadBomDetail(bomId) {
  bomEl("bomDetailStatus").textContent = "Загрузка...";
  const response = await fetch(`${bomApiBase()}/api/bom/${bomId}`, {
    headers: bomHeaders(),
  });
  if (!response.ok) throw new Error(`BOM detail HTTP ${response.status}`);
  bomState.selectedBom = await response.json();
  bomEl("bomDetailStatus").textContent = `${bomState.selectedBom.bom_code} / ${bomState.selectedBom.status}`;
  bomEl("bomDetails").textContent = JSON.stringify({
    bom_id: bomState.selectedBom.bom_id,
    bom_code: bomState.selectedBom.bom_code,
    bom_name: bomState.selectedBom.bom_name,
    target_articul: bomState.selectedBom.target_articul,
    bom_kind: bomState.selectedBom.bom_kind,
    base_qty: bomState.selectedBom.base_qty,
    base_unit_code: bomState.selectedBom.base_unit_code,
    is_primary: bomState.selectedBom.is_primary,
    valid_from: bomState.selectedBom.valid_from,
    valid_to: bomState.selectedBom.valid_to,
    version_no: bomState.selectedBom.version_no,
    approved_at: bomState.selectedBom.approved_at,
  }, null, 2);
  renderBomLines();
  bomEl("bomCalculation").textContent = "";
}

function renderBomLines() {
  const tbody = bomEl("bomLineRows");
  tbody.innerHTML = "";
  for (const line of bomState.selectedBom?.lines || []) {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td>${line.line_no ?? ""}</td>
      <td>${escapeBom(line.component_type ?? "")}</td>
      <td>${escapeBom(line.component_articul ?? "")}</td>
      <td>${escapeBom(line.component_name ?? "")}</td>
      <td>${line.qty_per_base ?? ""}</td>
      <td>${escapeBom(line.unit_code ?? "")}</td>
      <td>${line.loss_percent ?? 0}%</td>
    `;
    tbody.appendChild(tr);
  }
}

async function createBom() {
  if (!bomCan("bom_edit")) throw new Error("Нет права bom_edit");
  const body = {
    bom_code: bomEl("bomNewCode").value.trim(),
    bom_name: bomEl("bomNewName").value.trim() || null,
    target_articul: bomEl("bomNewTarget").value.trim(),
    base_qty: Number(bomEl("bomNewBaseQty").value),
    base_unit_code: bomEl("bomNewUnit").value.trim() || "KG",
    is_primary: Number(bomEl("bomNewPrimary").value),
    valid_from: bomEl("bomNewValidFrom").value,
    created_by: bomCurrentUser(),
  };
  const response = await fetch(`${bomApiBase()}/api/bom`, {
    method: "POST",
    headers: bomHeaders({ "Content-Type": "application/json" }),
    body: JSON.stringify(body),
  });
  const result = await response.json();
  if (!response.ok) throw new Error(result.detail || `Create BOM HTTP ${response.status}`);
  await bomLoadList();
  await loadBomDetail(result.id);
}

async function addBomLine() {
  if (!bomCan("bom_edit")) throw new Error("Нет права bom_edit");
  if (!bomState.selectedBom) throw new Error("Выберите BOM");
  const body = {
    line_no: bomEl("bomLineNo").value ? Number(bomEl("bomLineNo").value) : null,
    component_type: bomEl("bomLineType").value,
    component_articul: bomEl("bomLineArticul").value.trim() || null,
    component_name: bomEl("bomLineName").value.trim() || null,
    qty_per_base: bomEl("bomLineQty").value ? Number(bomEl("bomLineQty").value) : null,
    unit_code: bomEl("bomLineUnit").value.trim() || null,
    loss_percent: Number(bomEl("bomLineLoss").value || 0),
    created_by: bomCurrentUser(),
  };
  const response = await fetch(`${bomApiBase()}/api/bom/${bomState.selectedBom.bom_id}/lines`, {
    method: "POST",
    headers: bomHeaders({ "Content-Type": "application/json" }),
    body: JSON.stringify(body),
  });
  const result = await response.json();
  if (!response.ok) throw new Error(result.detail || `Add BOM line HTTP ${response.status}`);
  await loadBomDetail(bomState.selectedBom.bom_id);
}

async function bomLifecycle(action) {
  if (!bomState.selectedBom) throw new Error("Выберите BOM");
  const permissionMap = {
    approve: "bom_approve",
    "make-primary": "bom_make_primary",
    block: "bom_block",
    archive: "bom_block",
  };
  const permission = permissionMap[action];
  if (permission && !bomCan(permission)) throw new Error(`Нет права ${permission}`);
  const reason = action === "block" || action === "archive"
    ? window.prompt("Причина", "Ручное действие из админки")
    : "";
  if (reason === null) return;
  const response = await fetch(`${bomApiBase()}/api/bom/${bomState.selectedBom.bom_id}/${action}`, {
    method: "POST",
    headers: bomHeaders({ "Content-Type": "application/json" }),
    body: JSON.stringify({ reason, user_name: bomCurrentUser() }),
  });
  const result = await response.json();
  if (!response.ok) throw new Error(result.detail || `${action} HTTP ${response.status}`);
  await bomLoadList();
  await loadBomDetail(bomState.selectedBom.bom_id);
}

async function calculateBom() {
  if (!bomState.selectedBom) throw new Error("Выберите BOM");
  const response = await fetch(`${bomApiBase()}/api/bom/${bomState.selectedBom.bom_id}/calculate`, {
    method: "POST",
    headers: bomHeaders({ "Content-Type": "application/json" }),
    body: JSON.stringify({ planned_qty: Number(bomEl("bomCalcQty").value), unit_code: bomState.selectedBom.base_unit_code }),
  });
  const result = await response.json();
  if (!response.ok) throw new Error(result.detail || `Calculate HTTP ${response.status}`);
  bomEl("bomCalculation").textContent = JSON.stringify(result, null, 2);
}

function initBom() {
  if (!bomEl("bomRefresh")) return;
  if (window.wmsAdminAuth && !window.wmsAdminAuth.hasPermission("bom_view")) return;

  const today = new Date().toISOString().slice(0, 10);
  bomEl("bomNewValidFrom").value = today;
  bomEl("bomActiveOnFilter").value = today;

  bomEl("bomRefresh").addEventListener("click", () => bomLoadList().catch(showBomError));
  bomEl("bomLoad").addEventListener("click", () => bomLoadList().catch(showBomError));
  bomEl("bomCreate").addEventListener("click", () => createBom().catch(showBomError));
  bomEl("bomAddLine").addEventListener("click", () => addBomLine().catch(showBomError));
  bomEl("bomCalculate").addEventListener("click", () => calculateBom().catch(showBomError));
  bomEl("bomApprove").addEventListener("click", () => bomLifecycle("approve").catch(showBomError));
  bomEl("bomMakePrimary").addEventListener("click", () => bomLifecycle("make-primary").catch(showBomError));
  bomEl("bomBlock").addEventListener("click", () => bomLifecycle("block").catch(showBomError));
  bomEl("bomArchive").addEventListener("click", () => bomLifecycle("archive").catch(showBomError));

  for (const id of ["bomTargetFilter", "bomStatusFilter", "bomPrimaryFilter", "bomActiveOnFilter", "bomLimit"]) {
    bomEl(id).addEventListener("change", () => bomLoadList().catch(showBomError));
  }

  bomLoadList().catch(showBomError);
}

function showBomError(error) {
  bomEl("bomStatusText").textContent = `Ошибка: ${error.message}`;
  bomEl("bomDetailStatus").textContent = `Ошибка: ${error.message}`;
}

function escapeBom(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;");
}

if (window.wmsAdminAuth && window.wmsAdminAuth.state.user) {
  initBom();
} else {
  window.addEventListener("wms-admin-auth-ready", initBom, { once: true });
}
