(() => {
  const el = id => document.getElementById(id), auth = () => window.wmsAdminAuth;
  const base = () => auth().state.apiBase.replace(/\/$/, "");
  const actorScope = () => JSON.stringify([base(), auth().state.user?.username]);
  const scope = () => JSON.stringify([actorScope(), [...(auth().state.user?.permissions || [])].sort()]);
  const storageKey = () => "wms.aggregate-invalidation.v1:" + actorScope();
  const allowed = () => (auth().state.user?.permissions || []).some(p => p === "*" || p === "trace_manifest_import");
  let epoch = 0, identity = "", busy = false, pending = null;
  function message(value) { el("agMessage").textContent = value; }
  function restore() {
    pending = null;
    try { pending = JSON.parse(localStorage.getItem(storageKey()) || "null"); }
    catch (_) { message("Не удалось прочитать сохранённую операцию. Проверьте доступ к хранилищу браузера."); }
    el("agRetry").hidden = !pending;
    el("agPending").textContent = pending ? JSON.stringify(pending.body, null, 2) : "";
  }
  function reset() {
    ++epoch; busy = false; el("agRows").replaceChildren();
    el("agRead").disabled = false; el("agRetry").disabled = false; restore();
  }
  function cell(row, value) { const td = document.createElement("td"); td.textContent = value ?? ""; row.appendChild(td); }
  async function invalidate(item) {
    if (busy || !allowed()) return;
    if (pending) { message("Сначала повторите сохранённую операцию, результат которой неизвестен."); return; }
    const reference = el("agReference").value.trim();
    if (!reference) { message("Укажите основание вскрытия или изменения состава."); return; }
    const body = {operation_id: "AGG.UI:" + crypto.randomUUID(), warehouse_id: item.warehouse_id,
      origin_pallet_identifier: item.origin_pallet_identifier, system_code: item.system_code,
      profile_code: item.profile_code, code_hash: item.code_hash,
      reason_code: el("agReason").value, document_reference: reference};
    pending = {body};
    try { localStorage.setItem(storageKey(), JSON.stringify(pending)); }
    catch (_) { pending = null; message("Операция не отправлена: не удалось сохранить её идентификатор."); return; }
    restore(); await send();
  }
  async function send() {
    if (busy || !pending || !allowed()) return;
    const saved = pending, owner = scope(), serial = ++epoch, key = storageKey();
    busy = true; el("agRetry").disabled = true;
    try {
      const response = await fetch(base() + "/api/inventory/trace-manifests/aggregations/invalidate",
        {method: "POST", headers: {...auth().headers(), "Content-Type": "application/json"},
          body: JSON.stringify(saved.body)});
      const result = await response.json();
      if (owner !== scope() || serial !== epoch) return;
      if (response.ok || result.detail?.outcome_confirmed || response.status === 422) {
        localStorage.removeItem(key); pending = null; restore();
      }
      if (!response.ok) throw Error(result.detail?.message || result.detail?.code || "Результат не подтверждён. Повторите сохранённую операцию.");
      message("Агрегация отменена; заблокировано кодов: " + result.blocked_aggregate_count + ". Журнал: " + result.journal_id);
      el("agRows").replaceChildren();
    } catch (error) {
      if (owner === scope() && serial === epoch) message(error.message);
    } finally {
      if (owner === scope() && serial === epoch) { busy = false; el("agRetry").disabled = false; }
    }
  }
  async function read() {
    if (busy) return;
    const origin = el("agOrigin").value.trim(), ware = Number(el("agWare").value);
    if (!origin || !Number.isSafeInteger(ware) || ware <= 0) { message("Укажите склад и исходный идентификатор паллеты."); return; }
    const owner = scope(), serial = ++epoch;
    busy = true; el("agRead").disabled = true; el("agRows").replaceChildren();
    try {
      const response = await fetch(base() + "/api/inventory/trace-manifests/warehouses/" + ware
        + "/pallets/" + encodeURIComponent(origin) + "/aggregations", {headers: auth().headers()});
      const rows = await response.json();
      if (owner !== scope() || serial !== epoch) return;
      if (!response.ok) throw Error(rows.detail?.message || "Агрегации не получены.");
      for (const item of rows) {
        const row = document.createElement("tr");
        cell(row, item.system_code + " / " + item.profile_code); cell(row, item.level);
        cell(row, item.code_hash);
        cell(row, item.local_state === "INVALIDATED" ? "Отменена" : "Исходный состав");
        cell(row, item.invalidation_operation_id || "");
        const td = document.createElement("td");
        if (allowed() && item.local_state !== "INVALIDATED") {
          const button = document.createElement("button"); button.textContent = "Отменить агрегацию";
          button.addEventListener("click", () => invalidate(item)); td.appendChild(button);
        }
        row.appendChild(td); el("agRows").appendChild(row);
      }
      message("Агрегаций: " + rows.length + ". Допуск сканирования проверяется при выполнении команды.");
    } catch (error) {
      if (owner === scope() && serial === epoch) message(error.message);
    } finally {
      if (owner === scope() && serial === epoch) { busy = false; el("agRead").disabled = false; }
    }
  }
  el("agRead").addEventListener("click", read);
  el("agRetry").addEventListener("click", send);
  for (const id of ["agOrigin", "agWare"]) el(id).addEventListener("input", () => {
    if (!busy) { ++epoch; el("agRows").replaceChildren(); }
  });
  window.addEventListener("wms-admin-auth-ready", () => {
    const current = scope();
    if (identity !== current) { identity = current; reset(); el("agOrigin").value = ""; el("agWare").value = ""; }
  });
})();
