/* Форма передачи CASE (C0121): вместо последовательных prompt — один доступный <dialog>. Поля подписаны,
   числовые ID проверяет сервер (список чужих сессий API не отдаёт). Справка — статический /help/case-handoff.html. */
(() => {
  const HELP = "/help/case-handoff.html";
  const esc = v => escapeHtml(v ?? "—");
  let dlg = null, busy = false, changed = false, ctx = null;

  function shell() {
    if (dlg) return dlg;
    dlg = document.createElement("dialog");
    dlg.id = "caseHandoffDialog"; dlg.className = "ch-dialog"; dlg.setAttribute("aria-labelledby", "chTitle");
    dlg.addEventListener("cancel", event => { if (busy) event.preventDefault(); });
    dlg.addEventListener("close", () => { const done = ctx?.done; ctx = null; done?.(changed); });
    document.body.append(dlg);
    return dlg;
  }

  function head(task) {
    return `<header class="ch-head"><h2 id="chTitle">Передача задания #${esc(task)}</h2>
      <a href="${HELP}" target="_blank" rel="noopener" data-help-id="case.handoff.help" title="Справка: как передать паллету другому комплектовщику. Откроется в новой вкладке">Справка</a>
      <button type="button" class="ch-x" data-act="close" aria-label="Закрыть" title="Закрыть форму. Сохранённый запрос не удаляется" data-help-id="case.handoff.close">×</button></header>`;
  }

  function currentCard(t) {
    return `<dl class="ch-now" aria-label="Текущий исполнитель">
      <div><dt>Сейчас у</dt><dd>${esc(t.assigned_to)}</dd></div><div><dt>Ресурс</dt><dd>${esc(t.assigned_resource_id)}</dd></div>
      <div><dt>Сессия</dt><dd>${esc(t.resource_session_id)}</dd></div><div><dt>Техника</dt><dd>${esc(t.equipment_id)}</dd></div>
      <div><dt>Паллета</dt><dd>${esc(t.sscc)}</dd></div><div><dt>Версия содержимого</dt><dd>${esc(t.content_version)}</dd></div>
      <div><dt>Склад</dt><dd>${esc(t.ware_id)}</dd></div><div><dt>Отобрано строк</dt><dd>${esc(t.picked_lines)} из ${esc(t.total_lines)}</dd></div></dl>`;
  }

  const loaded = t => Number(t.picked_lines || 0) > 0 || Number(t.picked_qty || 0) > 0;

  function formHtml(t) {
    const need = loaded(t);
    return `<form class="ch-form" novalidate>
      <fieldset><legend>Кому передать</legend>
        <label>ID ресурса нового комплектовщика<input name="resource" inputmode="numeric" autocomplete="off" required title="Номер ресурса (человека) из карточки ресурса или Ганта. Сервер проверит, что ресурс активен на этом складе" data-help-id="case.handoff.resource"></label>
        <label>ID активной сессии нового комплектовщика<input name="session" inputmode="numeric" autocomplete="off" required title="Номер открытой сессии комплектовщика на терминале. Список сессий экран не получает — номер проверит сервер" data-help-id="case.handoff.session"></label>
        <label>ID техники (необязательно)<input name="equipment" inputmode="numeric" autocomplete="off" title="Номер тележки или техники, если она передаётся вместе с паллетой" data-help-id="case.handoff.equipment"></label>
      </fieldset>
      <fieldset><legend>Физическая передача</legend>
        <label>Идентификатор паллеты${need ? "" : " (паллета пуста — можно не сканировать)"}<input name="scan" autocomplete="off" ${need ? "required" : ""} title="Отсканируйте или введите идентификатор передаваемой паллеты: внешний, внутренний или SSCC. Сервер сверит его с заданием" data-help-id="case.handoff.scan"></label>
        <label>Причина<input name="reason" required maxlength="1000" value="Подтверждённая передача из ARM комплектации" title="Почему задание передаётся. Попадёт в журнал передачи" data-help-id="case.handoff.reason"></label>
        <label class="ch-check"><input type="checkbox" name="confirm" title="Подтвердите, что паллета физически передана новому комплектовщику" data-help-id="case.handoff.confirm"> Паллета физически передана новому комплектовщику</label>
      </fieldset>
      <p class="ch-note">Передача меняет только исполнителя. Вес и количество не меняются. Права и совпадение исполнителя, сессии и версии проверяет сервер.</p>
      <div class="ch-actions"><button type="submit" data-help-id="case.handoff.submit" title="Сохранить запрос передачи и отправить его на сервер. При потере ответа запрос остаётся для точного повтора">Передать</button>
        <button type="button" data-act="close" data-help-id="case.handoff.cancel" title="Закрыть без передачи">Отмена</button></div>
    </form>`;
  }

  const receiptBtn = `<button type="button" data-act="receipt" data-help-id="case.handoff.receipt" title="Спросить сервер, выполнен ли именно этот запрос (неизменная квитанция по его ключу). Текущий исполнитель карточки доказательством не является">Проверить квитанцию</button>`;
  const copyBtn = `<button type="button" data-act="copy" data-help-id="case.handoff.copy" title="Сохранить копию записи в браузере для разбора. Запрос и блокировка новой передачи остаются, на сервере ничего не меняется">Копия для разбора</button>`;
  const stuckNote = `<p class="ch-note">Серверной отмены передачи нет. Пока исход не подтверждён ответом или квитанцией, новая передача по заданию заблокирована: поздний запрос ещё может выполниться. Если квитанции нет долго — передайте ключ запроса руководителю смены.</p>`;

  function pendingHtml(e) {
    if (e.record.damaged) return `<section class="ch-pending ch-bad" aria-label="Повреждённый запрос"><p><b>Сохранённый запрос передачи повреждён.</b> Повторить его нельзя. Новая передача по этому заданию заблокирована, пока квитанция сервера не подтвердит исход.</p>${stuckNote}
      <div class="ch-actions">${receiptBtn}${copyBtn}</div></section>`;
    const b = e.body;
    return `<section class="ch-pending" aria-label="Сохранённый запрос"><p><b>${e.kind === "legacy" ? "Запрос из прежней версии экрана — исход неизвестен." : "Есть сохранённый запрос передачи."}</b> Повтор отправит то же тело с тем же ключом ${esc(b.offline_event_id)}.</p>
      <dl class="ch-now"><div><dt>Ресурс</dt><dd>${esc(b.to_resource_id)}</dd></div><div><dt>Сессия</dt><dd>${esc(b.to_resource_session_id)}</dd></div>
        <div><dt>Техника</dt><dd>${esc(b.to_equipment_id)}</dd></div><div><dt>Паллета</dt><dd>${esc(b.scan_container)}</dd></div><div><dt>Версия</dt><dd>${esc(b.expected_content_version)}</dd></div></dl>
      <div class="ch-actions"><button type="button" data-act="retry" data-help-id="case.handoff.retry" title="Повторить ровно тот же запрос. Повтор не создаёт вторую передачу">Повторить передачу</button>${receiptBtn}${copyBtn}</div>${stuckNote}</section>`;
  }

  function status(message, tone) {
    const el = dlg.querySelector(".ch-status");
    el.textContent = message || ""; el.className = "ch-status" + (tone ? " " + tone : "");
  }

  function render(current, e) {
    dlg.innerHTML = head(ctx.task) + `<div class="ch-body">${current ? currentCard(current) : ""}
      ${e.kind || e.record.damaged ? pendingHtml(e) : current ? formHtml(current) : ""}</div><p class="ch-status" role="status" aria-live="polite"></p>`;
    dlg.querySelector(".ch-body input:not([type=checkbox]), .ch-body button")?.focus();
  }

  const id = v => { const s = String(v ?? "").trim(); return s === "" ? null : /^[1-9][0-9]{0,15}$/.test(s) && Number.isSafeInteger(+s) ? +s : NaN; };

  function readForm(form) {
    const f = Object.fromEntries(new FormData(form)), out = { resource: id(f.resource), session: id(f.session),
      equipment: id(f.equipment), scan: String(f.scan ?? "").trim(), reason: String(f.reason ?? "").trim() };
    const bad = name => { form.elements[name].setAttribute("aria-invalid", "true"); form.elements[name].focus(); };
    form.querySelectorAll("[aria-invalid]").forEach(x => x.removeAttribute("aria-invalid"));
    if (!(out.resource > 0)) { bad("resource"); return "Укажите ID ресурса целым числом."; }
    if (!(out.session > 0)) { bad("session"); return "Укажите ID активной сессии целым числом."; }
    if (Number.isNaN(out.equipment)) { bad("equipment"); return "ID техники — целое число или пусто."; }
    if (form.elements.scan.required && !out.scan) { bad("scan"); return "Отсканируйте идентификатор паллеты."; }
    if (out.scan.length > 150) { bad("scan"); return "Идентификатор паллеты длиннее 150 символов."; }
    if (out.reason.length < 3) { bad("reason"); return "Укажите причину передачи."; }
    if (!f.confirm) { bad("confirm"); return "Подтвердите физическую передачу паллеты."; }
    return out;
  }

  async function run(action) {
    if (busy) return;
    busy = true; dlg.querySelectorAll("button, input").forEach(x => { x.dataset.wasDisabled = x.disabled; x.disabled = true; });
    try { await action(); }
    catch (error) { status(error.message || String(error), "bad"); }
    finally { busy = false; dlg?.querySelectorAll("button, input").forEach(x => { x.disabled = x.dataset.wasDisabled === "true"; }); }
  }

  async function sendEntry(e) {
    status("Отправка…");
    const r = await window.caseHandoff.deliver(e);
    if (r.outcome === "done") { changed = true; await reload(r.proven ? "Квитанция сервера подтверждает этот запрос: передача выполнена." : "Задание передано."); return; }
    if (r.outcome === "refused") { changed = true; await reload(r.message, "bad"); return; }
    await reload(r.message, "warn");
  }

  async function reload(message, tone) {
    const task = ctx.task;
    let current = null, error = null;
    try { current = await caseFetch("/api/case-pick/tasks/" + task); } catch (e) { error = e; }
    if (!ctx || ctx.task !== task) return;
    ctx.current = current;
    render(current, window.caseHandoff.entry(task));
    if (error) status(([401, 403, 404].includes(error.status) ? "Карточка недоступна: " : "Карточку не удалось перечитать: ") + error.message
      + (message ? ". " + message : ""), "bad");
    else status(message, tone);
    if (!current && !window.caseHandoff.entry(task).kind) dlg.querySelector(".ch-form")?.remove();
  }

  function bind() {
    dlg.addEventListener("click", event => {
      const act = event.target.closest("[data-act]")?.dataset.act;
      if (act === "close" && !busy) dlg.close();
      if (act === "retry") run(() => sendEntry(window.caseHandoff.entry(ctx.task)));
      if (act === "receipt") run(async () => {
        const r = await window.caseHandoff.receipt(window.caseHandoff.entry(ctx.task));
        if (r.state === "confirmed") changed = true;
        await reload(r.message, r.state === "confirmed" ? "" : "warn");
      });
      if (act === "copy") run(async () => { window.caseHandoff.copy(window.caseHandoff.entry(ctx.task)); status("Копия сохранена для разбора. Запрос и блокировка новой передачи остаются."); });
    });
    dlg.addEventListener("submit", event => {
      event.preventDefault();
      if (busy) return;
      const data = readForm(event.target); // до блокировки: заблокированные поля не попадают в FormData
      if (typeof data === "string") { status(data, "bad"); return; }
      run(async () => {
        const current = await caseFetch("/api/case-pick/tasks/" + ctx.task);
        if (current.assignment_version !== ctx.current.assignment_version || current.content_version !== ctx.current.content_version || current.resource_session_id !== ctx.current.resource_session_id
          || current.assigned_to !== ctx.current.assigned_to) { ctx.current = current; await reload("Карточка изменилась, пока форма была открыта. Проверьте исполнителя и повторите.", "warn"); return; }
        await sendEntry(window.caseHandoff.create(ctx.task, current, data));
      });
    });
    dlg.addEventListener("keydown", event => {
      if (event.key === "Enter" && event.target.name === "scan") { event.preventDefault(); event.target.form.elements.reason.focus(); }
    });
  }

  /** Открыть форму для задания. Возвращает Promise<boolean>: было ли изменение (для перечитывания списка). */
  function open(task) {
    if (!dlg) { shell(); bind(); }
    if (dlg.open) return Promise.resolve(false);
    changed = false;
    return new Promise(done => {
      ctx = { task, done, current: null };
      dlg.innerHTML = head(task) + `<p class="ch-status" role="status" aria-live="polite">Чтение карточки…</p>`;
      dlg.showModal();
      run(() => reload(""));
    });
  }

  window.caseHandoffDialog = { open };
})();
