const mesState = {
  orders: [],
  selectedOrder: null,
  selectedBomLine: null,
  genealogy: null,
  traceEdges: [],
  outboxEvents: [],
  finishedGoods: [],
};

const mesEl = (id) => document.getElementById(id);

function mesApiBase() {
  return (window.wmsAdminAuth?.state?.apiBase || "http://127.0.0.1:8088").replace(/\/$/, "");
}

function mesHeaders(extra = {}) {
  if (!window.wmsAdminAuth) return { ...extra };
  return window.wmsAdminAuth.headers(extra);
}

function mesCan(permission) {
  return window.wmsAdminAuth && window.wmsAdminAuth.hasPermission(permission);
}

function mesCurrentUser() {
  return window.wmsAdminAuth?.state?.user?.username || "admin";
}

function mesFilters() {
  const params = new URLSearchParams();
  const target = mesEl("mesTargetFilter").value.trim() || mesEl("mesSearch").value.trim();
  if (target) params.set("target_articul", target);
  if (mesEl("mesStatusFilter").value) params.set("status", mesEl("mesStatusFilter").value);
  params.set("limit", mesEl("mesLimit").value || "100");
  return params;
}

async function mesLoadOrders() {
  mesEl("mesStatusText").textContent = "Загрузка...";
  const response = await fetch(`${mesApiBase()}/api/mes/production-orders?${mesFilters().toString()}`, {
    headers: mesHeaders(),
  });
  if (!response.ok) throw new Error(`MES HTTP ${response.status}`);
  mesState.orders = await response.json();
  renderMesOrders();
  mesEl("mesStatusText").textContent = `Заказов: ${mesState.orders.length}`;
}

function renderMesOrders() {
  const tbody = mesEl("mesOrderRows");
  tbody.innerHTML = "";
  for (const order of mesState.orders) {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td>${order.production_order_id ?? ""}</td>
      <td>${escapeMes(order.order_no ?? "")}</td>
      <td>${escapeMes(order.target_articul ?? "")}</td>
      <td>${escapeMes(order.status ?? "")}</td>
      <td>${order.planned_qty ?? ""} ${escapeMes(order.unit_code ?? "")}</td>
      <td>${order.fact_qty ?? ""}</td>
      <td>${order.prod_batch_id ?? ""}</td>
    `;
    tr.addEventListener("click", () => loadMesOrder(order.production_order_id));
    tbody.appendChild(tr);
  }
}

async function loadMesOrder(orderId) {
  mesEl("mesDetailStatus").textContent = "Загрузка...";
  const response = await fetch(`${mesApiBase()}/api/mes/production-orders/${orderId}`, {
    headers: mesHeaders(),
  });
  const result = await response.json();
  if (!response.ok) throw new Error(result.detail || `MES detail HTTP ${response.status}`);
  mesState.selectedOrder = result;
  mesEl("mesDetailStatus").textContent = `${result.order_no} / ${result.status}`;
  mesEl("mesDetails").textContent = JSON.stringify({
    production_order_id: result.production_order_id,
    order_no: result.order_no,
    bom_id: result.bom_id,
    target_articul: result.target_articul,
    planned_qty: result.planned_qty,
    fact_qty: result.fact_qty,
    unit_code: result.unit_code,
    status: result.status,
    prod_batch_id: result.prod_batch_id,
  }, null, 2);
  renderMesMovements(result.movements || []);
  renderMesBomLines(result.bom_lines || []);
  mesEl("mesGenealogy").textContent = "";
  renderMesGenealogy({ raw_usage: [], pallets: [] });
  renderMesFinishedGoods([], []);
  renderMesTraceEdges([]);
  renderMesOutbox([]);
  updateMesKpis(result, null);
  await loadMesOperatorData(result).catch(showMesError);
}

function renderMesBomLines(lines) {
  const tbody = mesEl("mesBomLineRows");
  tbody.innerHTML = "";
  for (const line of lines) {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td>${line.line_no ?? ""}</td>
      <td>${escapeMes(line.component_type ?? "")}</td>
      <td>${escapeMes(line.component_articul ?? "")}</td>
      <td>${escapeMes(line.component_name ?? "")}</td>
      <td>${line.planned_qty ?? ""} ${escapeMes(line.unit_code ?? "")}</td>
      <td>${line.loss_percent ?? 0}%</td>
      <td>
        <button type="button" data-action="pick" data-line-id="${line.order_line_id ?? ""}">Подбор</button>
        <button type="button" data-action="issue" data-line-id="${line.order_line_id ?? ""}">Выдать</button>
      </td>
    `;
    tr.querySelector("button[data-action='pick']").addEventListener("click", () => pickRawForLine(line, true).catch(showMesError));
    tr.querySelector("button[data-action='issue']").addEventListener("click", () => issueRawLine(line).catch(showMesError));
    tbody.appendChild(tr);
  }
}

function fillRawFromBomLine(line) {
  mesState.selectedBomLine = line;
  const suffix = new Date().toISOString().replace(/[-:TZ.]/g, "").slice(0, 14);
  mesEl("mesRawPallet").value = `RAW-${line.component_articul || "PAL"}-${suffix}`.slice(0, 100);
  mesEl("mesRawArticul").value = line.component_articul || "";
  mesEl("mesRawQty").value = line.planned_qty || "";
  mesEl("mesRawFrom").value = "RM-A01-01";
  mesEl("mesRawTo").value = "MES_PROD";
}

async function pickRawForLine(line, fillForm = true) {
  if (!line?.component_articul) throw new Error("В строке BOM нет артикула сырья");
  const params = new URLSearchParams({
    articul: line.component_articul,
    only_available: "1",
    limit: "20",
  });
  const remains = await fetchMesJson(`/api/raw-material/remains?${params.toString()}`);
  if (!remains.length) {
    throw new Error(`Нет свободного остатка сырья ${line.component_articul}`);
  }
  const plannedQty = Number(line.planned_qty || 0);
  const picked = remains.find((row) => Number(row.available_qty || row.qty || 0) >= plannedQty) || remains[0];
  const issueQty = Math.min(plannedQty || Number(picked.available_qty || picked.qty || 0), Number(picked.available_qty || picked.qty || 0));
  const result = {
    uid_pallet: picked.uid_pallet,
    raw_articul: picked.articul || line.component_articul,
    quantity: issueQty,
    unit_code: picked.unit_type || line.unit_code || "KG",
    source_location: picked.cell,
    production_location: "MES_PROD",
  };
  if (fillForm) {
    mesState.selectedBomLine = line;
    mesEl("mesRawPallet").value = result.uid_pallet || "";
    mesEl("mesRawArticul").value = result.raw_articul || "";
    mesEl("mesRawQty").value = result.quantity || "";
    mesEl("mesRawFrom").value = result.source_location || "";
    mesEl("mesRawTo").value = result.production_location;
    mesEl("mesStatusText").textContent = `Подобрано сырьё: ${result.raw_articul} / ${result.uid_pallet}`;
  }
  return result;
}

function mesRawLineTypes() {
  return new Set(["RAW", "SEMIFINISHED", "PACKAGING", "ADDITIVE"]);
}

async function issueRawLine(line) {
  if (!mesState.selectedOrder) throw new Error("Выберите заказ");
  if (!mesCan("mes_production_edit")) throw new Error("Нет права mes_production_edit");
  if (!mesRawLineTypes().has(String(line.component_type || "").toUpperCase())) return null;
  const picked = await pickRawForLine(line, false);
  const response = await fetch(`${mesApiBase()}/api/mes/production-orders/${mesState.selectedOrder.production_order_id}/issue-raw`, {
    method: "POST",
    headers: mesHeaders({ "Content-Type": "application/json" }),
    body: JSON.stringify({
      uid_pallet: picked.uid_pallet || null,
      raw_articul: picked.raw_articul || null,
      quantity: picked.quantity,
      unit_code: line.unit_code || picked.unit_code || mesState.selectedOrder.unit_code || "KG",
      source_location: picked.source_location || null,
      production_location: picked.production_location || "MES_PROD",
      created_by: mesCurrentUser(),
    }),
  });
  const result = await response.json();
  if (!response.ok) throw new Error(result.detail || `Issue BOM line HTTP ${response.status}`);
  return result;
}

async function issueAllRawFromBom() {
  if (!mesState.selectedOrder) throw new Error("Выберите заказ");
  const lines = (mesState.selectedOrder.bom_lines || []).filter((line) => mesRawLineTypes().has(String(line.component_type || "").toUpperCase()));
  if (!lines.length) throw new Error("В заказе нет строк BOM для выдачи сырья");
  mesEl("mesStatusText").textContent = "Выдача сырья по BOM...";
  let issued = 0;
  for (const line of lines) {
    const existingQty = (mesState.selectedOrder.movements || [])
      .filter((movement) => movement.movement_type === "RAW_ISSUE_TO_PRODUCTION" && movement.raw_articul === line.component_articul && movement.status !== "CANCELLED")
      .reduce((sum, movement) => sum + Number(movement.quantity || 0), 0);
    if (existingQty >= Number(line.planned_qty || 0)) continue;
    await issueRawLine(line);
    issued += 1;
  }
  await loadMesOrder(mesState.selectedOrder.production_order_id);
  mesEl("mesStatusText").textContent = `Выдано строк BOM: ${issued}`;
}

function renderMesMovements(movements) {
  const tbody = mesEl("mesMovementRows");
  tbody.innerHTML = "";
  for (const movement of movements) {
    const canRetry = movement.status === "ERROR" && mesCan("mes_wms_bridge_apply");
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td>${movement.movement_id ?? ""}</td>
      <td>${escapeMes(movement.movement_type ?? "")}</td>
      <td>${escapeMes(mesMovementStatusLabel(movement.status))}</td>
      <td>${escapeMes(movement.uid_pallet ?? "")}</td>
      <td>${escapeMes(movement.source_location ?? "")}</td>
      <td>${escapeMes(movement.target_location ?? "")}</td>
      <td>${movement.quantity ?? ""} ${escapeMes(movement.unit_code ?? "")}</td>
      <td>${escapeMes(movement.last_error ?? "")}</td>
      <td>${canRetry ? `<button type="button" data-movement-id="${movement.movement_id}">Retry</button>` : ""}</td>
    `;
    const retryButton = tr.querySelector("button[data-movement-id]");
    if (retryButton) {
      retryButton.addEventListener("click", () => retryMesMovement(movement.movement_id).catch(showMesError));
    }
    tbody.appendChild(tr);
  }
}

function updateMesKpis(order, genealogy) {
  if (!mesEl("mesKpiStatus")) return;
  const movements = order?.movements || [];
  const wmsTotal = movements.filter((m) => ["RAW_ISSUE_TO_PRODUCTION", "RAW_CONSUMPTION", "FG_PALLET_RELEASE"].includes(m.movement_type)).length;
  const wmsApplied = movements.filter((m) => m.status === "APPLIED_TO_WMS").length;
  const wmsErrors = movements.filter((m) => m.status === "ERROR").length;
  mesEl("mesKpiStatus").textContent = order?.status || "-";
  mesEl("mesKpiPlan").textContent = `${order?.planned_qty ?? "-"} ${order?.unit_code || ""}`.trim();
  mesEl("mesKpiFact").textContent = `${order?.fact_qty ?? "-"} ${order?.unit_code || ""}`.trim();
  mesEl("mesKpiWms").textContent = wmsErrors ? `Ошибок: ${wmsErrors}` : `${wmsApplied}/${wmsTotal || 0}`;
  if (genealogy?.pallets?.length) {
    mesEl("mesKpiFact").textContent = `${order?.fact_qty ?? "-"} / паллет: ${genealogy.pallets.length}`;
  }
}

async function loadMesOperatorData(order) {
  const genealogy = await fetchMesJson(`/api/mes/production-orders/${order.production_order_id}/genealogy`);
  mesState.genealogy = genealogy;
  const view = mesGenealogyView(genealogy);
  mesEl("mesGenealogy").textContent = JSON.stringify(view, null, 2);
  renderMesGenealogy(view);
  updateMesKpis(order, view);

  const prodBatchId = view.order?.prod_batch_id;
  const [batches, remains, orderTrace, outbox] = await Promise.all([
    prodBatchId ? fetchMesJson(`/api/finished-goods/batches?prod_batch_id=${encodeURIComponent(prodBatchId)}&limit=20`) : [],
    prodBatchId ? fetchMesJson(`/api/finished-goods/remains?prod_batch_id=${encodeURIComponent(prodBatchId)}&limit=50`) : [],
    fetchMesJson(`/api/trace/entities/PRODUCTION_ORDER/${encodeURIComponent(order.production_order_id)}/forward?limit=100`),
    fetchMesJson(`/api/admin/event-outbox?aggregate_type=PRODUCTION_ORDER&aggregate_id=${encodeURIComponent(order.production_order_id)}&limit=20`),
  ]);
  renderMesFinishedGoods(batches, remains);
  renderMesOutbox(outbox);

  const extraTrace = [];
  if (prodBatchId) {
    extraTrace.push(...await fetchMesJson(`/api/trace/entities/FINISHED_GOODS_LOT/${encodeURIComponent(prodBatchId)}/forward?limit=100`));
  }
  for (const pallet of view.pallets || []) {
    if (pallet.uid_pallet) {
      extraTrace.push(...await fetchMesJson(`/api/trace/entities/PALLET/${encodeURIComponent(pallet.uid_pallet)}/forward?limit=20`));
    }
  }
  renderMesTraceEdges([...orderTrace, ...extraTrace]);
}

async function fetchMesJson(path) {
  const response = await fetch(`${mesApiBase()}${path}`, { headers: mesHeaders() });
  const result = await response.json();
  if (!response.ok) throw new Error(result.detail || `MES HTTP ${response.status}`);
  return result;
}

function mesGenealogyView(result) {
  return {
    order: {
      production_order_id: result.order?.production_order_id,
      order_no: result.order?.order_no,
      status: result.order?.status,
      prod_batch_id: result.order?.prod_batch_id,
      target_articul: result.order?.target_articul,
    },
    batch_readiness: result.batch_readiness || {},
    raw_usage: result.raw_usage || [],
    pallets: result.pallets || [],
  };
}

function renderMesFinishedGoods(batches, remains) {
  const tbody = mesEl("mesFinishedGoodsRows");
  if (!tbody) return;
  tbody.innerHTML = "";
  const batch = batches?.[0] || {};
  const totalRemain = (remains || []).reduce((sum, row) => sum + Number(row.qty || 0), 0);
  const tr = document.createElement("tr");
  tr.innerHTML = `
    <td>${escapeMes(batch.prod_batch_no ?? "")}</td>
    <td>${escapeMes(batch.articul ?? "")}</td>
    <td>${escapeMes(batch.quality_status ?? "")}</td>
    <td>${escapeMes(batch.shipment_release_status ?? "")}</td>
    <td>${batch.pallet_count ?? remains?.length ?? ""}</td>
    <td>${totalRemain || ""}</td>
  `;
  tbody.appendChild(tr);
  for (const remain of remains || []) {
    const row = document.createElement("tr");
    row.innerHTML = `
      <td>${escapeMes(remain.prod_batch_no ?? "")}</td>
      <td>${escapeMes(remain.articul ?? "")}</td>
      <td>${escapeMes(remain.quality_status ?? "")}</td>
      <td>${escapeMes(remain.ware_name ?? "")}</td>
      <td>${escapeMes(remain.uid_pallet ?? "")}</td>
      <td>${remain.qty ?? ""}</td>
    `;
    tbody.appendChild(row);
  }
}

function renderMesTraceEdges(edges) {
  const tbody = mesEl("mesTraceRows");
  if (!tbody) return;
  tbody.innerHTML = "";
  for (const edge of edges || []) {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td>${escapeMes(edge.from_entity_type ?? "")}:${escapeMes(edge.from_entity_id ?? "")}</td>
      <td>${escapeMes(edge.to_entity_type ?? "")}:${escapeMes(edge.to_entity_id ?? "")}</td>
      <td>${escapeMes(edge.edge_type ?? "")}</td>
      <td>${edge.quantity ?? ""} ${escapeMes(edge.unit_code ?? "")}</td>
      <td>${escapeMes(edge.event_type ?? "")}</td>
    `;
    tbody.appendChild(tr);
  }
}

function renderMesOutbox(events) {
  const tbody = mesEl("mesOutboxRows");
  if (!tbody) return;
  tbody.innerHTML = "";
  for (const event of events || []) {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td>${event.event_outbox_id ?? ""}</td>
      <td>${escapeMes(event.event_type ?? "")}</td>
      <td>${escapeMes(event.target_system ?? "")}</td>
      <td>${escapeMes(event.status ?? "")}</td>
      <td>${event.try_count ?? 0}/${event.max_try_count ?? ""}</td>
      <td>${escapeMes(event.last_error ?? "")}</td>
    `;
    tbody.appendChild(tr);
  }
}

function mesMovementStatusLabel(status) {
  return {
    MES_POSTED: "Ожидает WMS",
    PENDING_WMS_APPLY: "В применении",
    APPLIED_TO_WMS: "Применено в WMS",
    ERROR: "Ошибка",
    CANCELLED: "Отменено",
  }[status] || status || "";
}

function mesStamp() {
  return new Date().toISOString().replace(/[-:TZ.]/g, "").slice(0, 14);
}

function mesNumeric18() {
  return String(Date.now()).padStart(18, "0").slice(-18);
}

function autoMesOrderNo() {
  const suffix = mesStamp();
  mesEl("mesNewOrderNo").value = `MO-${suffix}`;
  if (!mesEl("mesNewLine").value.trim()) mesEl("mesNewLine").value = "LINE-1";
  mesEl("mesStatusText").textContent = `Новый номер заказа: ${mesEl("mesNewOrderNo").value}`;
}

async function findMesBom() {
  const target = mesEl("mesNewTarget").value.trim();
  if (!target) throw new Error("Укажите артикул готовой продукции");
  const params = new URLSearchParams({
    target_articul: target,
    planned_date: new Date().toISOString().slice(0, 10),
  });
  if (mesEl("mesNewLine").value.trim()) params.set("production_line", mesEl("mesNewLine").value.trim());
  const response = await fetch(`${mesApiBase()}/api/bom/default?${params.toString()}`, {
    headers: mesHeaders(),
  });
  const result = await response.json();
  if (!response.ok) throw new Error(result.detail || `Find BOM HTTP ${response.status}`);
  mesEl("mesNewBomId").value = result.bom_id;
  mesEl("mesNewUnit").value = result.base_unit_code || "KG";
  mesEl("mesStatusText").textContent = `BOM подобран: ${result.bom_code} / ID ${result.bom_id}`;
  return result;
}

async function createMesOrder() {
  if (!mesCan("mes_production_edit")) throw new Error("Нет права mes_production_edit");
  if (!mesEl("mesNewOrderNo").value.trim()) {
    autoMesOrderNo();
  }
  if (!mesEl("mesNewBomId").value) {
    await findMesBom();
  }
  const body = {
    order_no: mesEl("mesNewOrderNo").value.trim(),
    bom_id: mesEl("mesNewBomId").value ? Number(mesEl("mesNewBomId").value) : null,
    target_articul: mesEl("mesNewTarget").value.trim(),
    planned_qty: Number(mesEl("mesNewQty").value),
    unit_code: mesEl("mesNewUnit").value.trim() || "KG",
    production_line: mesEl("mesNewLine").value.trim() || null,
    created_by: mesCurrentUser(),
  };
  const response = await fetch(`${mesApiBase()}/api/mes/production-orders`, {
    method: "POST",
    headers: mesHeaders({ "Content-Type": "application/json" }),
    body: JSON.stringify(body),
  });
  const result = await response.json();
  if (!response.ok) throw new Error(result.detail || `Create MES order HTTP ${response.status}`);
  await mesLoadOrders();
  await loadMesOrder(result.id);
}

async function issueMesRaw() {
  if (!mesState.selectedOrder) throw new Error("Выберите заказ");
  if (!mesCan("mes_production_edit")) throw new Error("Нет права mes_production_edit");
  const body = {
    uid_pallet: mesEl("mesRawPallet").value.trim() || null,
    raw_articul: mesEl("mesRawArticul").value.trim() || null,
    quantity: Number(mesEl("mesRawQty").value),
    unit_code: mesState.selectedOrder.unit_code || "KG",
    source_location: mesEl("mesRawFrom").value.trim() || null,
    production_location: mesEl("mesRawTo").value.trim() || "MES_PROD",
    created_by: mesCurrentUser(),
  };
  const response = await fetch(`${mesApiBase()}/api/mes/production-orders/${mesState.selectedOrder.production_order_id}/issue-raw`, {
    method: "POST",
    headers: mesHeaders({ "Content-Type": "application/json" }),
    body: JSON.stringify(body),
  });
  const result = await response.json();
  if (!response.ok) throw new Error(result.detail || `Issue raw HTTP ${response.status}`);
  await loadMesOrder(mesState.selectedOrder.production_order_id);
}

async function completeMesOrder() {
  if (!mesState.selectedOrder) throw new Error("Выберите заказ");
  if (!mesCan("mes_production_complete")) throw new Error("Нет права mes_production_complete");
  const qty = Number(mesEl("mesFactQty").value);
  const body = {
    prod_batch_no: mesEl("mesLotNo").value.trim() || null,
    fact_qty: qty,
    unit_code: mesState.selectedOrder.unit_code || "KG",
    pallets: [{
      uid_pallet: mesEl("mesFgPallet").value.trim(),
      pallet_no: 1,
      quantity: qty,
      sscc: mesEl("mesFgSscc").value.trim() || null,
    }],
    idempotency_key: `${mesState.selectedOrder.order_no}:complete`,
    created_by: mesCurrentUser(),
  };
  const response = await fetch(`${mesApiBase()}/api/mes/production-orders/${mesState.selectedOrder.production_order_id}/complete`, {
    method: "POST",
    headers: mesHeaders({ "Content-Type": "application/json" }),
    body: JSON.stringify(body),
  });
  const result = await response.json();
  if (!response.ok) throw new Error(result.detail || `Complete HTTP ${response.status}`);
  await loadMesOrder(mesState.selectedOrder.production_order_id);
}

async function applyMesWms() {
  if (!mesState.selectedOrder) throw new Error("Выберите заказ");
  if (!mesCan("mes_wms_bridge_apply")) throw new Error("Нет права mes_wms_bridge_apply");
  const response = await fetch(`${mesApiBase()}/api/mes/production-orders/${mesState.selectedOrder.production_order_id}/apply-wms`, {
    method: "POST",
    headers: mesHeaders({ "Content-Type": "application/json" }),
    body: JSON.stringify({ applied_by: mesCurrentUser() }),
  });
  const result = await response.json();
  if (!response.ok) throw new Error(result.detail || `Apply WMS HTTP ${response.status}`);
  await loadMesOrder(mesState.selectedOrder.production_order_id);
}

function prefillMesCompletion() {
  if (!mesState.selectedOrder) throw new Error("Выберите заказ");
  const order = mesState.selectedOrder;
  const orderNo = order.order_no || `MO-${mesStamp()}`;
  mesEl("mesLotNo").value = `${orderNo}-LOT`;
  mesEl("mesFactQty").value = order.planned_qty || "";
  mesEl("mesFgPallet").value = `${orderNo}-FG-01`.slice(0, 100);
  mesEl("mesFgSscc").value = mesNumeric18();
  mesEl("mesStatusText").textContent = "Выпуск заполнен из заказа";
}

async function runMesFullCycle() {
  if (!mesState.selectedOrder) throw new Error("Выберите заказ");
  if (!mesCan("mes_production_edit")) throw new Error("Нет права mes_production_edit");
  if (!mesCan("mes_production_complete")) throw new Error("Нет права mes_production_complete");
  mesEl("mesStatusText").textContent = "Полный цикл: выдача сырья...";
  await issueAllRawFromBom();
  mesEl("mesStatusText").textContent = "Полный цикл: выпуск партии...";
  prefillMesCompletion();
  await completeMesOrder();
  mesEl("mesStatusText").textContent = "Полный цикл: применение в WMS...";
  await applyMesWms();
  await loadMesOperatorData(mesState.selectedOrder);
  mesEl("mesStatusText").textContent = "Полный цикл выполнен";
}

async function retryMesMovement(movementId) {
  const response = await fetch(`${mesApiBase()}/api/mes/movements/${movementId}/retry`, {
    method: "POST",
    headers: mesHeaders({ "Content-Type": "application/json" }),
    body: JSON.stringify({ updated_by: mesCurrentUser() }),
  });
  const result = await response.json();
  if (!response.ok) throw new Error(result.detail || `Retry movement HTTP ${response.status}`);
  if (mesState.selectedOrder) {
    await loadMesOrder(mesState.selectedOrder.production_order_id);
  }
}

async function loadMesGenealogy() {
  if (!mesState.selectedOrder) throw new Error("Выберите заказ");
  await loadMesOperatorData(mesState.selectedOrder);
}

function renderMesGenealogy(genealogy) {
  const rawRows = mesEl("mesGenealogyRawRows");
  rawRows.innerHTML = "";
  for (const usage of genealogy.raw_usage || []) {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td>${escapeMes(usage.raw_articul ?? "")}</td>
      <td>${usage.quantity_planned ?? ""}</td>
      <td>${usage.quantity_fact ?? ""}</td>
      <td>${escapeMes(usage.unit_code ?? "")}</td>
      <td>${escapeMes(usage.used_at ?? "")}</td>
      <td>${escapeMes(usage.used_by ?? "")}</td>
    `;
    rawRows.appendChild(tr);
  }
  const palletRows = mesEl("mesGenealogyPalletRows");
  palletRows.innerHTML = "";
  for (const pallet of genealogy.pallets || []) {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td>${escapeMes(pallet.uid_pallet ?? "")}</td>
      <td>${escapeMes(pallet.sscc ?? "")}</td>
      <td>${pallet.quantity ?? ""}</td>
      <td>${pallet.pack_count ?? ""}</td>
      <td>${escapeMes(pallet.aggregation_status ?? "")}</td>
      <td>${escapeMes(pallet.created_by ?? "")}</td>
    `;
    palletRows.appendChild(tr);
  }
}

function fillMesDemoFields() {
  const suffix = new Date().toISOString().replace(/[-:TZ.]/g, "").slice(0, 14);
  mesEl("mesNewOrderNo").value = `MES-DEMO-${suffix}`;
  mesEl("mesNewTarget").value = "FG-DEMO-PETFOOD";
  mesEl("mesNewQty").value = "100";
  mesEl("mesNewUnit").value = "KG";
  mesEl("mesNewLine").value = "LINE-1";
  mesEl("mesRawPallet").value = `RAW-DEMO-${suffix}`;
  mesEl("mesRawArticul").value = "RM-MEAT-BEEF-FROZ-01";
  mesEl("mesRawQty").value = "50";
  mesEl("mesRawFrom").value = "RM-A01-01";
  mesEl("mesRawTo").value = "MES_PROD";
  mesEl("mesLotNo").value = `LOT-DEMO-${suffix}`;
  mesEl("mesFactQty").value = "100";
  mesEl("mesFgPallet").value = `FG-DEMO-${suffix}`;
  mesEl("mesFgSscc").value = `0000000000${suffix}`.slice(-18);
}

function initMes() {
  if (!mesEl("mesRefresh")) return;
  if (window.wmsAdminAuth && !window.wmsAdminAuth.hasPermission("mes_production_view")) return;
  mesEl("mesRefresh").addEventListener("click", () => mesLoadOrders().catch(showMesError));
  mesEl("mesLoad").addEventListener("click", () => mesLoadOrders().catch(showMesError));
  mesEl("mesAutoOrderNo").addEventListener("click", () => autoMesOrderNo());
  mesEl("mesFindBom").addEventListener("click", () => findMesBom().catch(showMesError));
  mesEl("mesCreateOrder").addEventListener("click", () => createMesOrder().catch(showMesError));
  mesEl("mesFillDemo").addEventListener("click", () => fillMesDemoFields());
  mesEl("mesPickRaw").addEventListener("click", () => {
    const line = mesState.selectedBomLine || mesState.selectedOrder?.bom_lines?.[0];
    if (!line) return showMesError(new Error("Выберите строку BOM"));
    pickRawForLine(line, true).catch(showMesError);
  });
  mesEl("mesIssueRaw").addEventListener("click", () => issueMesRaw().catch(showMesError));
  mesEl("mesIssueAllRaw").addEventListener("click", () => issueAllRawFromBom().catch(showMesError));
  mesEl("mesPrefillCompletion").addEventListener("click", () => {
    try { prefillMesCompletion(); } catch (error) { showMesError(error); }
  });
  mesEl("mesCompleteOrder").addEventListener("click", () => completeMesOrder().catch(showMesError));
  mesEl("mesApplyWms").addEventListener("click", () => applyMesWms().catch(showMesError));
  mesEl("mesRunFullCycle").addEventListener("click", () => runMesFullCycle().catch(showMesError));
  mesEl("mesLoadGenealogy").addEventListener("click", () => loadMesGenealogy().catch(showMesError));
  for (const id of ["mesStatusFilter", "mesTargetFilter", "mesLimit"]) {
    mesEl(id).addEventListener("change", () => mesLoadOrders().catch(showMesError));
  }
  mesLoadOrders().catch(showMesError);
}

function showMesError(error) {
  mesEl("mesStatusText").textContent = `Ошибка: ${error.message}`;
  mesEl("mesDetailStatus").textContent = `Ошибка: ${error.message}`;
}

function escapeMes(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;");
}

if (window.wmsAdminAuth && window.wmsAdminAuth.state.user) {
  initMes();
} else {
  window.addEventListener("wms-admin-auth-ready", initMes, { once: true });
}
