// Прогноз складской нагрузки (NI08.1).
// POST /api/transport/warehouse-forecast/warehouses/{ware_id}/view — расчёт/чтение (transport_dispatch_view).
// POST …/project?limit=100 — обновление проекции истории (transport_dispatch_edit), только по явной кнопке.
// Серверная математика не дублируется: интерфейс показывает её результат и объясняет основания.
(() => {
  const el = id => document.getElementById(id);
  const auth = () => window.wmsAdminAuth;
  const base = () => auth().state.apiBase.replace(/\/$/, "");
  const X = () => window.warehouseForecastExplain;
  const LIMITS = { wfHistory: [1, 90], wfHorizon: [1, 31], wfMinimum: [1, 90] };
  const INPUTS = ["wfWare", "wfHistory", "wfHorizon", "wfMinimum", "wfScope", "wfCurrent"];
  let serial = 0;
  let controller = null;
  let result = null;
  let readAt = null;
  let sort = { key: "article", dir: 1 };
  let identity = "";

  const scope = () => base() + "|" + (auth().state.user?.username || "");
  const owner = () => scope() + "|" + INPUTS.map(id => (el(id).type === "checkbox" ? el(id).checked : el(id).value)).join("|");

  function node(tag, cls, text) {
    const n = document.createElement(tag);
    if (cls) n.className = cls;
    if (text !== undefined) n.textContent = text;
    return n;
  }

  function setMessage(id, text, tone = "info") {
    el(id).textContent = text;
    el(id).dataset.tone = tone;
  }

  // ── Проверка ввода по границам API (ForecastRequest) ───────────────

  function fieldError(id, text) {
    el(id + "Error").textContent = text;
    el(id).setAttribute("aria-invalid", text ? "true" : "false");
    return !text;
  }

  function validate() {
    let ok = true;
    const ware = el("wfWare").value.trim();
    ok = fieldError("wfWare", /^[1-9][0-9]{0,15}$/.test(ware) && Number.isSafeInteger(Number(ware)) ? "" : "Целое положительное число") && ok;
    for (const [id, [lo, hi]] of Object.entries(LIMITS)) {
      const v = el(id).value.trim();
      const n = Number(v);
      ok = fieldError(id, /^[0-9]+$/.test(v) && n >= lo && n <= hi ? "" : `Целое число от ${lo} до ${hi}`) && ok;
    }
    if (ok && Number(el("wfMinimum").value) > Number(el("wfHistory").value) + (el("wfCurrent").checked ? 1 : 0)) {
      fieldError("wfMinimum", "Больше дней в окне — рекомендация гарантированно будет заблокирована");
    }
    return ok;
  }

  function body() {
    return {
      history_days: Number(el("wfHistory").value),
      horizon_days: Number(el("wfHorizon").value),
      minimum_active_days: Number(el("wfMinimum").value),
      include_current_day: el("wfCurrent").checked,
      scope: el("wfScope").value
    };
  }

  // ── Отрисовка ──────────────────────────────────────────────────────

  const utc = iso => {
    try {
      return new Intl.DateTimeFormat("ru-RU", { timeZone: "UTC", dateStyle: "short", timeStyle: "short" }).format(new Date(iso)) + " UTC";
    } catch {
      return iso;
    }
  };

  // Только для отображения: исходная точная строка остаётся в подсказке и в формуле.
  const shortDecimal = (s, digits = 2) => {
    const n = Number(s);
    return Number.isFinite(n) ? n.toLocaleString("ru-RU", { maximumFractionDigits: digits }) : s;
  };

  function renderStatus(r) {
    const info = X().overall[r.status] || { tone: "neutral", title: "Статус " + r.status, text: "Статус не описан в интерфейсе.", next: "Уточните у владельца расчёта." };
    const box = el("wfStatus");
    box.className = "wf-status wf-tone-" + info.tone;
    const extra = r.status === "NEEDS_PROJECTION" ? " Неучтённых выехавших мест: " + (r.gap_count_capped ? "не менее " : "") + r.projection_gaps_at_least + "." : "";
    box.replaceChildren(node("strong", "", info.title), node("p", "", info.text + extra), node("p", "wf-next", "Дальше: " + info.next));
    el("wfProjectPanel").classList.toggle("wf-attention", r.status === "NEEDS_PROJECTION");
  }

  function renderSummary(r) {
    const loads = r.observed_days.reduce((n, d) => n + Number(d.load_count || 0), 0);
    const items = [
      ["Окно истории", utc(r.window_from_utc) + " — " + utc(r.window_to_utc)],
      ["Календарных дней в окне", shortDecimal(r.exposure_calendar_days), "Точное значение: " + r.exposure_calendar_days],
      ["Текущий неполный день", r.includes_partial_current_day ? "включён — значения меняются в течение дня" : "не включён"],
      ["Дней с выездами", r.observed_days.length + " (мест погрузки: " + loads + ")"],
      ["Минимум активных дней", String(r.minimum_active_days)],
      ["Неучтённые выехавшие места", (r.gap_count_capped ? "≥ " : "") + r.projection_gaps_at_least],
      ["Вид работы", (X().scopes[r.quantity_scope] || { title: r.quantity_scope }).title],
      ["Прочитано", readAt ? readAt.toLocaleString("ru-RU") : "—"],
      ["Подпись данных", r.source_data_signature.slice(0, 12) + "…", r.source_data_signature]
    ];
    el("wfSummary").replaceChildren(...items.map(([k, v, title]) => {
      const c = node("div", "wf-sum-item");
      c.append(node("span", "", k), node("strong", "", v));
      if (title) c.title = title;
      return c;
    }));
    el("wfMethod").textContent = (X().method[r.forecast_method] || r.forecast_method) + " Источник: " + r.source + "; запас не изменён: " + (r.stock_changed ? "нет" : "да") + ", план не применён: " + (r.plan_applied ? "нет" : "да") + ".";
  }

  // Мини-график только по реальным числам ответа: мест погрузки в дни с выездами.
  function renderDays(r) {
    const box = el("wfDays");
    if (!r.observed_days.length) {
      box.replaceChildren(node("p", "wf-empty", "В окне нет дней с исполненной и учтённой работой."));
      return;
    }
    const max = Math.max(...r.observed_days.map(d => Number(d.load_count) || 0), 1);
    const list = node("ol", "wf-bars");
    list.setAttribute("aria-label", "Мест погрузки по дням с выездами");
    for (const d of r.observed_days) {
      const li = node("li");
      const bar = node("span", "wf-bar");
      bar.style.setProperty("--h", Math.max(4, (Number(d.load_count) / max) * 100) + "%");
      bar.title = d.day_utc + ": мест погрузки " + d.load_count + ", верхних мест " + d.top_places;
      li.append(node("b", "", String(d.load_count)), bar, node("small", "", d.day_utc.slice(5)));
      list.append(li);
    }
    box.replaceChildren(list, node("p", "wf-note", "Показаны только дни с выездами. Дни без выездов участвуют в среднем как нулевые календарные дни окна."));
  }

  function rateCell(rate) {
    const td = node("td", "num", rate === null ? "—" : shortDecimal(rate, 4));
    if (rate !== null) td.title = "Точное значение: " + rate;
    return td;
  }

  const sortValue = (row, key) => {
    const v = row[key];
    if (["observed_quantity", "daily_rate", "estimated_quantity", "active_days"].includes(key)) return v === null || v === undefined ? -Infinity : Number(v);
    return String(v ?? "");
  };

  function renderRows() {
    if (!result) return;
    const q = el("wfSearch").value.trim().toLowerCase();
    const rows = result.series
      .filter(r => !q || (r.article + " " + r.base_uom).toLowerCase().includes(q))
      .sort((a, b) => {
        const x = sortValue(a, sort.key);
        const y = sortValue(b, sort.key);
        return (x > y ? 1 : x < y ? -1 : 0) * sort.dir;
      });
    const body = el("wfRows");
    if (!result.series.length) {
      const tr = node("tr");
      const td = node("td", "wf-empty", result.status === "NEEDS_PROJECTION"
        ? "Товарные ряды не показываются, пока выехавшие места не перенесены в историю прогноза."
        : "Товарных рядов нет — это не нулевая нагрузка, а отсутствие учтённой работы в окне.");
      td.colSpan = 7;
      tr.append(td);
      body.replaceChildren(tr);
    } else {
      body.replaceChildren(...rows.map(r => {
        const info = X().row[r.status] || { tone: "neutral", label: r.status, text: "Статус не описан в интерфейсе" };
        const tr = node("tr");
        const status = node("td");
        status.append(node("span", "wf-pill wf-tone-" + info.tone, info.label), node("small", "", info.text));
        if (r.status === "READY") status.append(node("small", "wf-formula", r.observed_quantity + " " + r.base_uom + " ÷ " + shortDecimal(result.exposure_calendar_days) + " дн. × " + r.horizon_days + " → вверх до шага 10^-" + r.base_scale + " = " + r.estimated_quantity));
        const est = node("td", "num", r.estimated_quantity === null ? "заблокировано" : r.estimated_quantity + " " + r.base_uom);
        if (r.estimated_quantity === null) est.classList.add("wf-blocked");
        tr.append(node("td", "", r.article), node("td", "", r.base_uom), node("td", "num", r.observed_quantity), node("td", "num", String(r.active_days)), rateCell(r.daily_rate), est, status);
        tr.title = "Мест-листьев: " + r.leaf_count + "; источников: " + r.source_count + "; версия правила единицы: " + (r.policy_version ?? "нет");
        return tr;
      }));
    }
    for (const th of document.querySelectorAll(".wf-table th")) {
      const key = th.querySelector("button")?.dataset.sort;
      th.setAttribute("aria-sort", key === sort.key ? (sort.dir > 0 ? "ascending" : "descending") : "none");
    }
    el("wfSearchNote").textContent = q ? "Показано " + rows.length + " из " + result.series.length + " рядов — поиск только по загруженному результату." : "";
    const units = new Map();
    for (const r of result.series) units.set(r.base_uom, (units.get(r.base_uom) || 0) + 1);
    el("wfUnits").textContent = result.series.length
      ? "Рядов по единицам: " + [...units.entries()].map(([u, n]) => u + " — " + n).join(", ") + ". Количества разных единиц не суммируются."
      : "";
  }

  function render(r) {
    renderStatus(r);
    renderSummary(r);
    renderDays(r);
    renderRows();
    window.warehouseForecastLabour?.render(r);
    el("wfResult").hidden = false;
  }

  function clearResult(text) {
    result = null;
    window.warehouseForecastLabour?.clear();
    el("wfResult").hidden = true;
    el("wfRows").replaceChildren();
    el("wfSearch").value = "";
    if (text !== undefined) setMessage("wfMessage", text, "info");
  }

  // ── Запросы ────────────────────────────────────────────────────────

  async function api(path, init, signal) {
    const r = await fetch(base() + path, { ...init, headers: { ...auth().headers(), "Content-Type": "application/json" }, signal });
    let data = null;
    try { data = await r.json(); } catch { data = null; }
    if (!r.ok) {
      const detail = data?.detail;
      const text = Array.isArray(detail) ? detail.map(d => (d.loc || []).slice(-1)[0] + ": " + d.msg).join("; ") : typeof detail === "string" ? detail : detail?.message;
      const hint = r.status === 403 ? " Проверьте права и склад." : r.status === 401 ? " Войдите заново." : "";
      throw Error((text || "Сервер вернул HTTP " + r.status) + "." + hint);
    }
    return data;
  }

  async function calculate() {
    if (!validate()) {
      setMessage("wfMessage", "Исправьте отмеченные поля.", "error");
      return;
    }
    controller?.abort();
    controller = new AbortController();
    const seq = ++serial;
    const own = owner();
    clearResult();
    el("wfRead").disabled = true;
    el("wfResult").setAttribute("aria-busy", "true");
    setMessage("wfMessage", "Рассчитываем по исполненной истории склада " + el("wfWare").value + "…", "info");
    try {
      const data = await api("/api/transport/warehouse-forecast/warehouses/" + Number(el("wfWare").value) + "/view", { method: "POST", body: JSON.stringify(body()) }, controller.signal);
      if (own !== owner() || seq !== serial) return;
      result = data;
      readAt = new Date();
      render(data);
      setMessage("wfMessage", "Расчёт выполнен: " + (X().overall[data.status]?.title || data.status) + ".", data.status === "ADVISORY" ? "ok" : "warn");
    } catch (e) {
      if (e.name === "AbortError" || own !== owner() || seq !== serial) return;
      setMessage("wfMessage", e.message === "Failed to fetch" ? "Сервер WMS недоступен. Проверьте соединение и повторите." : e.message, "error");
    } finally {
      if (seq === serial) {
        el("wfRead").disabled = false;
        el("wfResult").removeAttribute("aria-busy");
      }
    }
  }

  // Явное обновление проекции: меняет историю прогноза, поэтому подтверждается пользователем.
  async function project() {
    if (!fieldError("wfWare", /^[1-9][0-9]{0,15}$/.test(el("wfWare").value.trim()) ? "" : "Целое положительное число")) return;
    const ware = Number(el("wfWare").value);
    if (!window.confirm("Перенести до 100 выехавших мест склада " + ware + " в историю прогноза? Запас и рейсы не меняются.")) return;
    const own = scope() + "|" + ware;
    el("wfProject").disabled = true;
    el("wfProjectErrors").replaceChildren();
    setMessage("wfProjectMessage", "Обновляем историю склада " + ware + "…", "info");
    try {
      const data = await api("/api/transport/warehouse-forecast/warehouses/" + ware + "/project?limit=100", { method: "POST" });
      if (own !== scope() + "|" + Number(el("wfWare").value)) return;
      clearResult();
      setMessage("wfProjectMessage", "Найдено мест: " + data.sources_seen + "; перенесено: " + data.projected.length + "; ошибок: " + data.errors.length + "; запас изменён: " + (data.stock_changed ? "да" : "нет") + ". Рассчитайте прогноз заново." + (data.sources_seen >= data.maximum_batch ? " Обработана одна партия (" + data.maximum_batch + "), возможно, остались ещё места." : ""), data.errors.length ? "warn" : "ok");
      if (data.errors.length) {
        const ul = node("ul", "wf-errors");
        for (const err of data.errors.slice(0, 20)) ul.append(node("li", "", err.source_load_operation_id + ": " + err.code + " — " + err.message));
        el("wfProjectErrors").replaceChildren(ul);
      }
    } catch (e) {
      setMessage("wfProjectMessage", e.message === "Failed to fetch" ? "Сервер недоступен: результат обновления неизвестен. Рассчитайте прогноз — поле «Неучтённые выехавшие места» покажет фактическое состояние." : e.message, "error");
    } finally {
      el("wfProject").disabled = false;
    }
  }

  // ── События ────────────────────────────────────────────────────────

  function invalidate() {
    const inFlight = el("wfRead").disabled;
    controller?.abort();
    ++serial;
    el("wfRead").disabled = false;
    el("wfResult").removeAttribute("aria-busy");
    if (result || inFlight) clearResult("Параметры изменены — рассчитайте прогноз заново.");
    el("wfScopeHelp").textContent = X().scopes[el("wfScope").value]?.hint || "";
  }

  function identityChanged() {
    const value = scope();
    if (value === identity) return;
    identity = value;
    invalidate();
    clearResult("");
    setMessage("wfProjectMessage", "");
    el("wfProjectPanel").hidden = !auth().hasPermission?.("transport_dispatch_edit");
  }

  el("wfRead").addEventListener("retailcase-invalidate", invalidate);
  el("wfRead").addEventListener("click", calculate);
  el("wfProject").addEventListener("click", project);
  for (const id of INPUTS) {
    el(id).addEventListener(el(id).tagName === "SELECT" || el(id).type === "checkbox" ? "change" : "input", invalidate);
    if (el(id).tagName === "INPUT" && el(id).type !== "checkbox") el(id).addEventListener("keydown", e => { if (e.key === "Enter") calculate(); });
  }
  el("wfSearch").addEventListener("input", renderRows);
  for (const btn of document.querySelectorAll(".wf-table th button")) {
    btn.addEventListener("click", () => {
      const key = btn.dataset.sort;
      sort = { key, dir: sort.key === key ? -sort.dir : 1 };
      renderRows();
    });
  }
  el("wfScopeHelp").textContent = X().scopes[el("wfScope").value]?.hint || "";
  window.addEventListener("wms-admin-auth-ready", identityChanged);
  if (auth().state.user) identityChanged();
})();
