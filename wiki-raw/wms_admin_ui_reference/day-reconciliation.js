// Обзор сверки дня (NI07.2). Только чтение: GET /api/finance/day-reconciliation/warehouses/{ware_id}.
// Поля drWare/drDay/drZone читают и слушают соседние блоки страницы (фиксация, журнал, грузовая зона) —
// их ID и событие input сохраняются. Отчёт не закрывает день и не меняет запас.
(() => {
  const el = id => document.getElementById(id);
  const auth = () => window.wmsAdminAuth;
  const base = () => auth().state.apiBase.replace(/\/$/, "");
  const cat = () => window.dayReconCatalog;
  const PANELS = ["drFacts", "drBacklog", "drStock", "drErp", "drRegulatory", "drTaskTimes", "drSummary", "drContext", "drLimits"];
  let identity = "";
  let serial = 0;
  let controller = null;
  let loaded = null;
  let deepApplied = false;

  const scope = () => base() + ":" + (auth().state.user?.username || "");
  const wareKey = () => "day-recon-ware:" + scope();

  function node(tag, cls, text) {
    const n = document.createElement(tag);
    if (cls) n.className = cls;
    if (text !== undefined) n.textContent = text;
    return n;
  }

  function setMessage(text, tone = "info") {
    const m = el("drMessage");
    m.textContent = text;
    m.dataset.tone = tone;
  }

  function clear(reason) {
    for (const id of PANELS) el(id)?.replaceChildren();
    loaded = null;
    el("drFilter").value = "";
    el("drFilter").disabled = true;
    el("drFilterNote").textContent = "";
    el("drResult").hidden = true;
    if (reason) setMessage(reason, "info");
  }

  // ── Форматирование ──────────────────────────────────────────────────

  function localTime(iso, zone) {
    try {
      return new Intl.DateTimeFormat("ru-RU", { timeZone: zone, dateStyle: "short", timeStyle: "medium" }).format(new Date(iso));
    } catch {
      return iso;
    }
  }

  const processTitle = key => (cat().processes.find(([k]) => k === key) || [key, key])[1];

  // Переход в реестр переносит склад/дату/ID, если экран их читает; иначе подпись сообщает, какой контекст не перенесён.
  function linkNode(link) {
    if (!link) return node("span", "dr-nolink", "Отдельного экрана нет");
    const target = window.dayReconLinks ? window.dayReconLinks.build(link, loaded) : { href: link.href, carried: [], lost: [] };
    const a = node("a", "dr-link", link.label + (link.kind === "registry" ? " · реестр" : ""));
    a.href = target.href;
    if (link.kind !== "registry") return a;
    a.title = "Ответ сверки агрегатный: откроется реестр, а не конкретный документ." + (target.carried.length ? " Передаётся: " + target.carried.join(", ") + "." : "");
    if (!target.lost.length) return a;
    const wrap = node("span", "dr-link-wrap");
    wrap.append(a, node("small", "dr-link-hint", "Ссылка не передаёт " + target.lost.join(" и ") + ". Проверьте область открытого реестра."));
    return wrap;
  }

  // ── Блоки ───────────────────────────────────────────────────────────

  function renderContext(d) {
    const box = el("drContext");
    const items = [
      ["Склад", String(d.warehouse_id)],
      ["Операционный день", d.business_date],
      ["Часовой пояс", d.timezone_region],
      ["Границы дня", localTime(d.from_utc, d.timezone_region) + " — " + localTime(d.to_utc, d.timezone_region)],
      ["Данные прочитаны", localTime(d.read_at_utc, d.timezone_region)],
      ["Снимок", d.consistent_snapshot ? "согласованный (одна транзакция чтения)" : "без гарантии согласованности"]
    ];
    box.replaceChildren(...items.map(([k, v]) => {
      const item = node("div", "dr-context-item");
      item.append(node("span", "", k), node("strong", "", v));
      return item;
    }));
  }

  function renderSummary(d) {
    const openCount = d.open_items.reduce((n, r) => n + r.count, 0);
    const factsTotal = Object.values(d.daily_facts).reduce((n, v) => n + v, 0);
    const erpCount = d.erp_unacknowledged.reduce((n, r) => n + r.count, 0);
    const cards = [
      ["Открытых пунктов", String(openCount), openCount ? "warn" : "ok", "Текущее состояние, включая прошлые дни"],
      ["Фактов за день", String(factsTotal), "info", "События с подтверждённым временем в выбранных сутках"],
      ["ERP без подтверждения", String(erpCount), erpCount ? "warn" : "neutral", "Отправлено ≠ подтверждено"],
      ["Сообщений маркировки", String(d.regulatory.message_count), "neutral", "Госответ этим отчётом не сверяется"]
    ];
    el("drSummary").replaceChildren(...cards.map(([label, value, tone, hint]) => {
      const c = node("div", "dr-card dr-tone-" + tone);
      c.append(node("span", "", label), node("strong", "", value), node("small", "", hint));
      return c;
    }));
  }

  function groupByProcess(entries) {
    const groups = new Map();
    for (const e of entries) {
      if (!groups.has(e.process)) groups.set(e.process, []);
      groups.get(e.process).push(e);
    }
    return cat().processes.filter(([k]) => groups.has(k)).map(([k, title]) => [title, groups.get(k)])
      .concat([...groups.keys()].filter(k => !cat().processes.some(([p]) => p === k)).map(k => [processTitle(k), groups.get(k)]));
  }

  function renderFacts(d) {
    const entries = Object.entries(d.daily_facts).map(([key, value]) => {
      const info = cat().facts[key] || { title: key, process: "warehouse", meaning: "Показатель без описания в интерфейсе" };
      return { key, value, ...info };
    });
    const box = el("drFacts");
    box.replaceChildren(...groupByProcess(entries).map(([title, rows]) => {
      const group = node("div", "dr-group");
      group.append(node("h3", "", title));
      const list = node("ul", "dr-fact-list");
      for (const r of rows) {
        const li = node("li", "dr-item" + (r.value ? "" : " dr-zero"));
        li.dataset.search = (title + " " + r.title + " " + r.meaning).toLowerCase();
        li.append(node("span", "dr-item-title", r.title), node("strong", "dr-count", String(r.value)), node("small", "dr-item-meaning", r.meaning));
        list.append(li);
      }
      group.append(list);
      return group;
    }));
    const t = d.warehouse_task_time_coverage;
    el("drTaskTimes").textContent = "Дневные счётчики заданий используют только подтверждённое время с часовым поясом. Не вошли: начал без часового пояса — "
      + t.legacy_unclassified_start_count + ", завершений без часового пояса — " + t.legacy_unclassified_finish_count + ".";
  }

  function backlogEntries(d) {
    const out = [];
    for (const [key, count] of Object.entries(d.current_backlog)) {
      const info = cat().backlog[key] || { title: key, process: "warehouse", meaning: "Показатель без описания в интерфейсе", action: "Уточнить у владельца процесса", link: null };
      out.push({ key, count, ...info, documents:d.current_backlog_documents?.[key] });
    }
    const known = new Set(Object.keys(d.current_backlog));
    for (const item of d.open_items) {
      if (known.has(item.code)) continue;
      const info = cat().derived[item.code] || { title: item.code, process: "warehouse", meaning: "Открытый пункт без описания в интерфейсе", action: "Уточнить у владельца процесса", link: null };
      out.push({ key: item.code, count: item.count, ...info,documents:item.documents });
    }
    return out;
  }

  function renderBacklog(d) {
    const entries = backlogEntries(d);
    const open = entries.filter(e => e.count > 0);
    const zero = entries.filter(e => e.count === 0);
    const box = el("drBacklog");
    const parts = [];
    if (!open.length) parts.push(node("p", "dr-empty", "Открытых обязательств по показателям сверки нет."));
    for (const [title, rows] of groupByProcess(open)) {
      const group = node("div", "dr-group");
      group.append(node("h3", "", title));
      for (const r of rows) {
        const card = node("article", "dr-obligation dr-item");
        card.dataset.search = (title + " " + r.title + " " + r.meaning + " " + r.action).toLowerCase();
        const head = node("div", "dr-obligation-head");
        head.append(node("span", "dr-item-title", r.title), node("strong", "dr-count dr-count-open", String(r.count)));
        const why = node("p", "dr-item-meaning", r.meaning);
        const next = node("div", "dr-next");
        next.append(node("span", "", "Дальше: " + r.action), linkNode(r.link));
        card.append(head, why, next); window.dayReconDocuments.append(card,r.documents,r.count,d.warehouse_id);
        group.append(card);
      }
      parts.push(group);
    }
    if (zero.length) {
      const details = node("details", "dr-zero-list");
      details.append(node("summary", "", "Без открытых пунктов: " + zero.length + " показателей"));
      const list = node("ul", "dr-fact-list");
      for (const r of zero) {
        const li = node("li", "dr-item dr-zero");
        li.dataset.search = (processTitle(r.process) + " " + r.title + " " + r.meaning).toLowerCase();
        li.append(node("span", "dr-item-title", r.title), node("strong", "dr-count", "0"), node("small", "dr-item-meaning", processTitle(r.process)));
        list.append(li);
      }
      details.append(list);
      parts.push(details);
    }
    box.replaceChildren(...parts);
  }

  function renderStock(d) {
    const rows = d.stock.by_base_uom;
    const box = el("drStock");
    if (!rows.length) {
      box.replaceChildren(node("p", "dr-empty", "Строк запаса по ячейкам склада нет."));
      return;
    }
    const table = node("table", "dr-table");
    const head = node("thead");
    const hr = node("tr");
    for (const h of ["Единица", "Физически", "Жёсткий резерв", "Строк запаса", "Некорректных строк"]) hr.append(node("th", "", h));
    head.append(hr);
    const body = node("tbody");
    for (const r of rows) {
      const tr = node("tr", "dr-item");
      tr.dataset.search = ("остатки " + r.base_uom).toLowerCase();
      for (const v of [r.base_uom, r.physical_quantity, r.hard_quantity, String(r.stock_rows), String(r.invalid_rows)]) tr.append(node("td", "", v));
      if (Number(r.invalid_rows)) tr.classList.add("dr-row-bad");
      body.append(tr);
    }
    table.append(head, body);
    box.replaceChildren(table, node("p", "dr-note", "Количества по разным единицам не суммируются. Конфликтов состава физических единиц: " + d.stock.physical_unit_composition_conflicts + "."));
  }

  function statusPill(map, raw) {
    const s = map[raw] || { label: "Статус " + raw, tone: "unknown" };
    return node("span", "dr-pill dr-pill-" + s.tone, s.label);
  }

  function renderErp(d) {
    const box = el("drErp");
    const rows = d.erp_unacknowledged;
    if (!rows.length) {
      box.replaceChildren(node("p", "dr-empty", "Неподтверждённых ERP-записей, привязанных к складу, не найдено. Записи без привязки к складу в этот отчёт не входят."));
      return;
    }
    const list = node("ul", "dr-ext-list");
    for (const r of rows) {
      const li = node("li", "dr-item");
      li.dataset.search = ("erp " + r.event_type + " " + r.status).toLowerCase();
      li.append(node("span", "dr-item-title", r.event_type), statusPill(cat().erpStatus, r.status), node("strong", "dr-count", String(r.count)));
      list.append(li);
    }
    box.replaceChildren(list, node("p", "dr-note", "Реестра ERP-подтверждений в интерфейсе нет; разбор отказов — через владельца интеграции."));
  }

  function renderRegulatory(d) {
    const box = el("drRegulatory");
    const r = d.regulatory;
    const parts = [];
    if (!r.groups.length) parts.push(node("p", "dr-empty", "Сообщений маркировки с подтверждённой привязкой к складу нет."));
    else {
      const table = node("table", "dr-table");
      const hr = node("tr");
      for (const h of ["Система", "Событие", "Отправка", "Сообщений", "Принятие госсистемой", "Исходные проводки не подтверждены"]) hr.append(node("th", "", h));
      const head = node("thead");
      head.append(hr);
      const body = node("tbody");
      for (const g of r.groups) {
        const tr = node("tr", "dr-item");
        tr.dataset.search = ("маркировка " + g.system_code + " " + g.event_type + " " + g.delivery_status).toLowerCase();
        const sent = node("td");
        sent.append(statusPill(cat().deliveryStatus, g.delivery_status));
        const accepted = node("td");
        accepted.append(node("span", "dr-pill dr-pill-unknown", g.government_acceptance === "NOT_VERIFIED_BY_THIS_REPORT" ? "Не сверялось" : g.government_acceptance));
        tr.append(node("td", "", g.system_code), node("td", "", g.event_type), sent, node("td", "", String(g.message_count)), accepted, node("td", "", String(g.source_operation_unverified_count)));
        body.append(tr);
      }
      table.append(head, body);
      parts.push(table);
    }
    const note = node("p", "dr-note", "Ожидают отправки: " + r.delivery_pending_count + ". Количество сообщений не равно количеству товара. Полнота привязки сообщений к складу: "
      + (r.coverage_complete ? "подтверждена" : "не подтверждена") + ".");
    const link = node("p", "dr-note");
    link.append(linkNode({ href: "external-outbox.html", label: "Журнал внешних сообщений", kind: "registry" }));
    parts.push(note, link);
    box.replaceChildren(...parts);
  }

  function renderLimits(d) {
    const limits = [];
    if (!d.consistent_snapshot) limits.push("Снимок не согласован: показатели могли читаться в разные моменты.");
    if (d.shipping_register?.has_more) limits.push("В отчёт вошла только первая страница реестра грузовой зоны (20 строк).");
    if (d.shipping_register && !d.shipping_register.all_shipping_zone_coverage_verified) limits.push("Классификация грузовой зоны неполная — пустота зоны не доказана.");
    if (!d.full_regulatory_reconciliation_verified) limits.push("Полная сверка с государственными системами не выполнена: принятие сообщений не проверяется.");
    if (!d.regulatory.coverage_complete) limits.push("Привязка всех сообщений маркировки к складу не подтверждена.");
    const t = d.warehouse_task_time_coverage;
    if (t.legacy_unclassified_start_count || t.legacy_unclassified_finish_count) limits.push("Часть заданий без подтверждённого часового пояса не вошла в дневные счётчики.");
    limits.push(d.day_closed ? "День отмечен закрытым." : "День не закрыт: отчёт сверки сам день не закрывает.");
    const ul = node("ul", "dr-limits-list");
    for (const t2 of limits) ul.append(node("li", "", t2));
    el("drLimits").replaceChildren(node("h3", "", "Известная неполнота данных"), ul);
  }

  function render(d) {
    renderContext(d);
    renderSummary(d);
    renderFacts(d);
    renderBacklog(d);
    renderStock(d);
    renderErp(d);
    renderRegulatory(d);
    renderLimits(d);
    el("drResult").hidden = false;
    el("drFilter").disabled = false;
    applyFilter();
  }

  // ── Фильтр по загруженным группам (клиентский, не поиск по базе) ───

  function applyFilter() {
    if (!loaded) return;
    const q = el("drFilter").value.trim().toLowerCase();
    const items = [...el("drResult").querySelectorAll(".dr-item")];
    let shown = 0;
    for (const it of items) {
      const match = !q || (it.dataset.search || "").includes(q);
      it.hidden = !match;
      if (match) shown += 1;
    }
    for (const g of el("drResult").querySelectorAll(".dr-group")) g.hidden = !!q && !g.querySelector(".dr-item:not([hidden])");
    for (const z of el("drResult").querySelectorAll(".dr-zero-list")) {
      z.hidden = !!q && !z.querySelector(".dr-item:not([hidden])");
      if (q && !z.hidden) z.open = true;
    }
    el("drFilterNote").textContent = q ? "Найдено " + shown + " из " + items.length + " строк — только среди загруженных групп этого отчёта, не поиск по базе." : "";
  }

  // ── Загрузка ────────────────────────────────────────────────────────

  async function load() {
    const ware = Number(el("drWare").value);
    const day = el("drDay").value;
    const zone = el("drZone").value.trim();
    if (!Number.isSafeInteger(ware) || ware < 1) { setMessage("Укажите номер склада — целое положительное число.", "error"); el("drWare").focus(); return; }
    if (!day) { setMessage("Укажите дату фактов.", "error"); el("drDay").focus(); return; }
    if (!zone) { setMessage("Укажите часовой пояс, например Asia/Tbilisi.", "error"); el("drZone").focus(); return; }
    controller?.abort();
    controller = new AbortController();
    const seq = ++serial;
    const owner = scope();
    clear();
    el("dayOverview").setAttribute("aria-busy", "true");
    el("drLoad").disabled = true;
    setMessage("Формируем сверку склада " + ware + " за " + day + "…", "info");
    try {
      localStorage.setItem(wareKey(), String(ware));
    } catch {}
    try {
      const q = new URLSearchParams({ business_date: day, timezone_region: zone });
      const r = await fetch(base() + "/api/finance/day-reconciliation/warehouses/" + ware + "?" + q, { headers: auth().headers(), signal: controller.signal });
      let d = null;
      try { d = await r.json(); } catch { d = null; }
      if (owner !== scope() || seq !== serial) return;
      if (!r.ok) {
        const code = d?.detail?.code;
        const text = typeof d?.detail === "string" ? d.detail : d?.detail?.message;
        const hint = r.status === 403 ? " Проверьте права на склад." : r.status === 401 ? " Войдите заново." : code === "RECONCILIATION_TIMEZONE" ? " Используйте IANA-пояс, например Asia/Tbilisi." : "";
        const base = text || "Сверка недоступна (HTTP " + r.status + ")";
        throw Error(base + (/[.!?]$/.test(base) ? "" : ".") + hint);
      }
      loaded = d;
      deepApplied = true;
      window.dayReconLinks?.write(ware, day);
      render(d);
      const open = d.open_items.reduce((n, x) => n + x.count, 0);
      setMessage("Сверка сформирована: открытых пунктов " + open + ". Обязательства и остатки — текущее состояние; факты — за выбранные сутки.", open ? "warn" : "ok");
    } catch (e) {
      if (e.name === "AbortError" || owner !== scope() || seq !== serial) return;
      setMessage(e.message === "Failed to fetch" ? "Сервер WMS недоступен. Проверьте соединение и повторите." : e.message, "error");
    } finally {
      if (seq === serial) {
        el("drLoad").disabled = false;
        el("dayOverview").removeAttribute("aria-busy");
      }
    }
  }

  function invalidate() {
    controller?.abort();
    ++serial;
    el("drLoad").disabled = false;
    el("dayOverview").removeAttribute("aria-busy");
    clear(loaded === null && !el("drMessage").textContent ? "" : "Параметры изменены — сформируйте сверку заново.");
  }

  function identityChanged() {
    const value = scope();
    if (identity === value) return;
    identity = value;
    controller?.abort();
    ++serial;
    clear("");
    let saved = "";
    try { saved = localStorage.getItem(wareKey()) || ""; } catch {}
    // Прямая ссылка ?warehouse_id=&day= применяется один раз и имеет приоритет над сохранённым складом.
    const deep = !deepApplied && window.dayReconLinks ? window.dayReconLinks.read() : { ware: null, day: null };
    if (deep.ware) saved = String(deep.ware);
    if (el("drWare").value !== saved) {
      el("drWare").value = saved;
      // Соседние блоки страницы слушают input на drWare и сбрасывают свои данные.
      el("drWare").dispatchEvent(new Event("input", { bubbles: true }));
    }
    if (deep.day) { el("drDay").value = deep.day; el("drDay").dispatchEvent(new Event("input", { bubbles: true })); }
    // Считается применённой только после успешного чтения: подтверждение восстановленной сессии отменяет начатое чтение.
    if (deep.ware && deep.day && auth().state.user) load();
  }

  el("drLoad").addEventListener("click", load);
  for (const id of ["drWare", "drDay", "drZone"]) {
    el(id).addEventListener("input", invalidate);
    el(id).addEventListener("keydown", e => { if (e.key === "Enter") load(); });
  }
  el("drFilter").addEventListener("input", applyFilter);
  try {
    const parts = new Intl.DateTimeFormat("en-CA", { timeZone: el("drZone").value || "Asia/Tbilisi", year: "numeric", month: "2-digit", day: "2-digit" }).formatToParts(new Date());
    const part = k => parts.find(p => p.type === k).value;
    el("drDay").value = part("year") + "-" + part("month") + "-" + part("day");
  } catch {}
  clear("");
  window.addEventListener("wms-admin-auth-ready", identityChanged);
  identityChanged();
})();
