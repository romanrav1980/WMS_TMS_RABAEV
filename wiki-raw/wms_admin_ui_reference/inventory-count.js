(() => {
  "use strict";
  const el = id => document.getElementById(id);
  if (window.matchMedia("(max-width:760px)").matches) el("countNav").open = false;
  let lots = [], busy = false, loadedRevision = null, loadedCell = null, loadedArticle = null, loadVersion = 0;
  const message = text => { el("countMessage").textContent = text; };
  const context = () => {
    const auth = window.wmsAdminAuth;
    return { base: (auth.state.apiBase || "http://127.0.0.1:8088").replace(/\/$/, ""),
      actor: auth.state.user?.username || "" };
  };
  const intentKey = () => { const c = context(); return JSON.stringify(["retailcase.inventoryIntent", c.base, c.actor]); };
  const readIntent = () => JSON.parse(localStorage.getItem(intentKey()) || "null");
  function pending() { el("countRetry").hidden = !readIntent(); }
  async function api(path, body) {
    const response = await fetch(context().base + path, { method: body ? "POST" : "GET",
      headers: window.wmsAdminAuth.headers(body ? { "Content-Type": "application/json" } : {}),
      body: body ? JSON.stringify(body) : undefined });
    const data = await response.json();
    if (!response.ok) { const e = new Error(typeof data.detail === "string" ? data.detail : JSON.stringify(data.detail || data));
      e.detail = data.detail; e.status = response.status; throw e; }
    return data;
  }
  async function load() {
    if (busy) return;
    const version = ++loadVersion, auth = context();
    lots = []; loadedRevision = loadedCell = loadedArticle = null;
    el("countRows").replaceChildren();
    message("Загружаем партии…");
    try {
      const revision = el("countRevision").value.trim(), cell = el("countCell").value.trim();
      if (!/^[1-9][0-9]*$/.test(revision) || !cell) throw new Error("Укажите документ и ячейку.");
      const article = el("countArticle").value.trim();
      const task = el("countInventoryTask").value.trim();
      if (task && !/^[1-9][0-9]*$/.test(task)) throw new Error("Укажите корректный номер задания.");
      const data = await api("/api/inventory/stock-posting/inventory/" + revision + "/lots?cell=" + encodeURIComponent(cell) + (article ? "&article=" + encodeURIComponent(article) : "") + (task ? "&inventory_task_id=" + encodeURIComponent(task) : ""));
      if (version !== loadVersion) return;
      if (auth.actor !== context().actor || auth.base !== context().base
        || revision !== el("countRevision").value.trim() || cell !== el("countCell").value.trim()
        || article !== el("countArticle").value.trim() || task !== el("countInventoryTask").value.trim()) {
        message("Сеанс или параметры пересчёта изменились. Загрузите партии заново."); return;
      }
      lots = article ? data.lots.filter(lot => lot.article === article) : data.lots;
      loadedRevision = revision; loadedCell = cell; loadedArticle = article;
      const rows = lots.map((lot, index) => {
        const tr = document.createElement("tr");
        for (const value of [lot.uid, lot.article, lot.expiry_date, lot.physical_qty, lot.hard_qty, lot.unit]) {
          const td = document.createElement("td"); td.textContent = String(value ?? ""); tr.append(td);
        }
        const quantity = document.createElement("input"); quantity.className = "count-qty"; quantity.inputMode = "decimal";
        quantity.value = String(lot.physical_qty); quantity.dataset.count = String(index);
        quantity.title = "Фактически измеренное количество этой паллеты в указанной единице";
        const qtyCell = document.createElement("td"); qtyCell.append(quantity); tr.append(qtyCell);
        const profiles = document.createElement("select"); profiles.dataset.profile = String(index);
        profiles.title = "Выберите систему маркировки из карточки товара для сканирования найденных единиц";
        for (const profile of lot.marking_profiles || []) {
          const option = document.createElement("option"); option.value = JSON.stringify(profile);
          option.textContent = profile.system_code + " / " + profile.profile_code; profiles.append(option);
        }
        const codes = document.createElement("textarea"); codes.dataset.units = String(index);
        codes.disabled = profiles.options.length === 0;
        codes.title = "Коды всех фактически найденных единиц, по одному в строке";
        const unitsCell = document.createElement("td"); unitsCell.append(profiles, codes);
        if ((lot.lost_codes || []).length) {
          const lost = document.createElement("p"); lost.className = "count-lost"; lost.dataset.lost = String(index);
          lost.title = "Эти единицы списаны прежним пересчётом как не найденные. Если код нашёлся на этой паллете, отсканируйте его вместе с остальными найденными и увеличьте количество: единица вернётся в остаток с прежним собственником и сроком.";
          lost.textContent = "Не найдены ранее (" + lot.lost_codes.length + "): " + lot.lost_codes.join(", ");
          unitsCell.append(lost);
        }
        tr.append(unitsCell);
        return tr;
      });
      el("countRows").replaceChildren(...rows); message(rows.length ? "Партии загружены. Введите фактическое количество." : "В ячейке нет зарегистрированных партий.");
      pending(); el("countCell").focus();
    } catch (error) {
      if (version === loadVersion) message(error.status === 403 ? "Нет доступа к пересчёту или собственнику товара. Проверьте назначение задания и права." : error.message);
    }
  }
  async function submit(retry) {
    if (busy) return;
    busy = true; el("countPost").disabled = el("countRetry").disabled = true;
    let key;
    let attempted = false, priorUnknown = false;
    try {
      key = intentKey();
      let body = readIntent();
      if (!retry && body) throw new Error("Сначала повторите сохранённую команду: " + body.operation_id);
      if (!body) {
        if (retry) throw new Error("Сохранённой команды нет.");
        if (loadedRevision !== el("countRevision").value.trim() || loadedCell !== el("countCell").value.trim() || loadedArticle !== el("countArticle").value.trim()) throw new Error("Загрузите выбранный документ и ячейку повторно перед проводкой.");
        const reason = el("countReason").value.trim(); if (!reason) throw new Error("Укажите причину пересчёта.");
        const taskId = el("countInventoryTask").value.trim();
        if (taskId && (!/^[1-9][0-9]*$/.test(taskId) || !loadedArticle)) throw new Error("Укажите корректное задание и его артикул.");
        const counts = [];
        for (const [index, lot] of lots.entries()) {
          const quantity = document.querySelector('[data-count="' + index + '"]').value.trim();
          if (!/^[0-9]{1,18}(\.[0-9]{1,9})?$/.test(quantity)) throw new Error("Количество должно быть неотрицательным числом с точкой.");
          if (quantity !== String(lot.physical_qty) || taskId) {
            const rawCodes = document.querySelector('[data-units="' + index + '"]').value.split(/\r?\n/).filter(code => code.length > 0);
            const profile = document.querySelector('[data-profile="' + index + '"]').value;
            const scans = rawCodes.map(code => ({ ...JSON.parse(profile), code }));
            counts.push({ uid: lot.uid, article: lot.article, cell: lot.cell, unit: lot.unit, quantity,
              expected_stock_version: lot.stock_version, scans });
          }
        }
        if (!counts.length && !taskId) throw new Error("Нет изменённых строк.");
        body = { operation_id: "INVENTORY.UI:" + crypto.randomUUID(),
          revision_id: Number(el("countRevision").value), reason, counts, ...(taskId ? {inventory_task_id: Number(taskId)} : {}) };
        localStorage.setItem(key, JSON.stringify(body)); pending();
      }
      priorUnknown = !!localStorage.getItem(key + ":delivery");
      localStorage.setItem(key + ":delivery", "unknown"); attempted = true;
      const result = await api("/api/inventory/stock-posting/inventory/counts", body);
      localStorage.removeItem(key + ":delivery");
      localStorage.removeItem(key); pending();
      lots = []; loadedRevision = loadedCell = null; el("countRows").replaceChildren(); el("countCell").focus();
      const outcome = (result.counts || []).map(fact => fact.lost_units ? fact.uid + ": не найдено " + fact.lost_units + " ед., коды записаны как недостача"
        : fact.found_units ? fact.uid + ": найдено " + fact.found_units + " ед., возвращены в остаток" : null).filter(Boolean);
      message("Пересчёт подтверждён сервером. Операция: " + result.operation_id + (outcome.length ? "\n" + outcome.join("\n") : ""));
    } catch (error) {
      if (attempted && !priorUnknown && error.detail?.outcome_confirmed === true) {
        localStorage.removeItem(key + ":delivery");
        localStorage.removeItem(key); pending();
      }
      message(error.message + (readIntent() ? " Команда сохранена для повтора." : ""));
    } finally {
      busy = false; el("countPost").disabled = el("countRetry").disabled = false;
    }
  }
  el("countLoad").addEventListener("click", load);
  el("countCell").addEventListener("keydown", event => { if (event.key === "Enter") { event.preventDefault(); load(); } });
  el("countPost").addEventListener("click", () => submit(false));
  el("countRetry").addEventListener("click", () => submit(true));
  el("countCreate").addEventListener("click", async () => {
    if (busy) return;
    busy = true; el("countCreate").disabled = true;
    try {
      const warehouse = el("countWarehouse").value.trim();
      if (!/^[1-9][0-9]*$/.test(warehouse)) throw new Error("Укажите склад.");
      const result = await api("/api/inventory/stock-posting/inventory/revisions", { warehouse_id: Number(warehouse) });
      el("countRevision").value = result.revision_id; message("Документ открыт: " + result.revision_id); el("countCell").focus();
    } catch (error) { message(error.message); }
    finally { busy = false; el("countCreate").disabled = false; }
  });
  el("countHelp").addEventListener("click", () => el("countHelpDialog").showModal());
  el("countHelpClose").addEventListener("click", () => el("countHelpDialog").close());
  window.addEventListener("storage", pending);
  const source = new URLSearchParams(location.search);
  if (/^[1-9][0-9]*$/.test(source.get("revision_id") || "")) el("countRevision").value = source.get("revision_id");
  if (/^[1-9][0-9]*$/.test(source.get("inventory_task_id") || "")) el("countInventoryTask").value = source.get("inventory_task_id");
  if (source.get("article")) el("countArticle").value = source.get("article");
  if (source.get("cell")) el("countCell").value = source.get("cell");
  function onAuthenticated() { pending(); if(el("countRevision").value && el("countCell").value)load(); }
  window.addEventListener("wms-admin-auth-ready", onAuthenticated);
  if(window.wmsAdminAuth.state.user)onAuthenticated();
  pending();
})();
