(() => {
  const el = id => document.getElementById(id), auth = () => window.wmsAdminAuth;
  const base = () => auth().state.apiBase.replace(/\/$/, "");
  const owner = () => base() + "|" + (auth().state.user?.username || auth().state.user?.id || "");
  let historySequence = 0;
  let sequence = 0, currentOwner = "", config = null, windows = [], replacement = null;
  const pendingKey = () => "wmsWorkloadPending:" + owner();
  const text = (parent, value) => { const p = document.createElement("p"); p.textContent = value; parent.appendChild(p); };
  const message = value => { el("rwMessage").textContent = value; };
  const intent=window.wmsResourcePending.create(pendingKey,'workload','rwRetry',async()=>{reset();await refresh();message('Исходник архивирован. Сверьте текущее состояние перед новой командой.');});
  function pending() { if(!auth().state.user)return null; const r=intent.read(); return r.damaged?{damaged:true}:r.value; }
  function reset() { clearReplacement(); ++historySequence; ++sequence; el("rwResult").replaceChildren(); config = null; windows = []; ["rwResult", "rwWindows", "rwNormRows", "rwAttendance", "rwPerson", "rwHistory"].forEach(id => el(id).replaceChildren()); el("rwRetry").hidden = !pending(); }
  function ware() { const value = Number(el("rwWare").value); if (!Number.isSafeInteger(value) || value < 1) throw Error("Укажите склад."); return value; }
  function at(id) { const value = el(id).value; if (!value) throw Error("Заполните даты и время."); return value + (value.length === 16 ? ":00" : "") + el("rwOffset").value; }
  function scope() { return owner() + "|" + el("rwWare").value + "|" + el("rwSite").value; }
  async function request(path, method = "GET", body) {
    const response = await fetch(base() + path, {method, headers: {...auth().headers(), "Content-Type": "application/json"}, ...(body === undefined ? {} : {body: JSON.stringify(body)})});
    const result = await response.json();
    if (!response.ok) { const error = Error(result.detail?.message || result.detail?.code || JSON.stringify(result.detail)); error.status = response.status; error.code=result.detail?.code; throw error; }
    return result;
  }
  function clearReplacement() {
    replacement = null; el("rwReplace").disabled = true;
    el("rwReplaceLabel").textContent = "План для изменения не выбран.";
  }
  function renderConfiguration(result) {
    clearReplacement(); config = result; el("rwNormRows").replaceChildren(); el("rwAttendance").replaceChildren();
    result.norms.forEach(row => text(el("rwNormRows"), row.site_code + " · " + row.article + " · " + row.base_per_hour + " " + row.base_uom + "/ч · версия " + row.version_no + (row.active ? "" : " · отключена")));
    result.planned_attendance.forEach(row => {
      const block = document.createElement("div"); text(block, row.person_id + " · " + row.site_code + " · " + row.start_at + " — " + row.finish_at);
      if (row.replaced_plan_operation_id) text(block, "Сохранён вместо предыдущего выхода; прежняя запись остаётся в истории.");

      if (auth().hasPermission("resource_shift_edit") && Date.parse(row.finish_at) > Date.now()) {
        const button = document.createElement("button"); button.textContent = "Отменить плановый выход";
        button.addEventListener("click", () => mutate("/api/resources/workload/attendance/cancel", {warehouse_id: ware(), plan_operation_id: row.plan_operation_id, reason: "Отмена плана выхода ответственным за смену"}));
        block.appendChild(button);
        const change = document.createElement("button"); change.textContent = "Выбрать для изменения";
        change.addEventListener("click", () => {
          if (!config || config.warehouse_id !== ware()) {message("Загрузите текущие планы выбранного склада."); return;}
          replacement = {source: row.plan_operation_id, warehouse: row.ware_id, owner: owner()};
          el("rwPerson").value = String(row.resource_id);
          el("rwReplaceLabel").textContent = "Изменяется выход " + row.person_id + " · " + row.site_code + " · " + row.start_at + " — " + row.finish_at;
          el("rwReplace").disabled = false;
          message("Введите будущий интервал, подсклад и основание. Прежний план заменится только вместе с новым.");
        });

      }
      if (Date.parse(row.finish_at) <= Date.now()) text(block, "Прошедший плановый интервал; фактическая явка учитывается отдельно.");
      const history = document.createElement("button"); history.textContent = "Показать историю";
      history.addEventListener("click", () => showHistory(row.plan_operation_id));
      block.appendChild(history);
      el("rwAttendance").appendChild(block);
    });
  }
  async function showHistory(plan, append = false, continuation = null) {
    const serial = ++historySequence, selected = scope();
    if (!append) el("rwHistory").replaceChildren();
    if (continuation) continuation.disabled = true;
    try {
      const result = await request("/api/resources/workload/warehouses/" + ware() + "/attendance/" + encodeURIComponent(plan) + "/history?limit=20");
      if (serial !== historySequence || selected !== scope()) return;
      if (continuation) continuation.remove();
      result.rows.forEach(row => {
        const block = document.createElement("div");
        text(block, row.person_id + " · " + row.site_code + " · " + row.start_at + " — " + row.finish_at);
        text(block, "Утверждён " + row.planned_by + " · " + row.recorded_at + " · основание: " + row.reason);
        if (row.cancel_operation_id) text(block, "Прежний план отменён " + row.cancelled_by + " · " + row.cancel_recorded_at + " · " + row.cancel_reason);
        el("rwHistory").appendChild(block);
      });
      if (result.has_more) {
        const more = document.createElement("button"); more.textContent = "Предыдущие изменения";
        more.addEventListener("click", () => showHistory(result.next_plan_operation_id, true, more));
        el("rwHistory").appendChild(more);
      }
      message("История плановых изменений прочитана; фактическая явка не изменена.");
    } catch (error) {
      if (serial === historySequence && selected === scope()) {message(error.message); if (continuation) continuation.disabled = false;}
    }
  }
  async function refresh() {
    const serial = ++sequence, selected = scope();
    try {
      const query = new URLSearchParams();
      if (el("rwSite").value) query.set("site_code", el("rwSite").value);
      if (el("rwViewStart").value || el("rwViewFinish").value) {
        query.set("start_at", at("rwViewStart")); query.set("finish_at", at("rwViewFinish"));
      }
      const result = await request("/api/resources/workload/warehouses/" + ware() + "?" + query);
      if (serial !== sequence || selected !== scope()) return;
      renderConfiguration(result); message("Настройки прочитаны: " + (result.selection?.site_code || "все подсклады") + (result.selection?.start_at ? " · выходы, пересекающие выбранный период." : " · текущие и будущие выходы."));
      el("rwPerson").replaceChildren();
      result.eligible_case_resources.forEach(row => { const option = document.createElement("option"); option.value = row.resource_id; option.textContent = row.resource_name + " · " + row.person_id; el("rwPerson").appendChild(option); });
    } catch (error) { if (serial === sequence) message(error.message); }
  }
  async function pendingLock(action) {
    const identity = owner();
    const perform = () => { if (identity !== owner()) throw Error("Пользователь или подключение изменились; повторите выбор."); return action(); };
    try {
      if (navigator.locks) return await navigator.locks.request("wmsWorkloadMutation:" + identity, perform);
      return await perform();
    } catch (error) { if (identity === owner()) message(error.message); }
  }
  async function mutate(path, fields) { return pendingLock(() => mutateUnlocked(path, fields)); }
  async function mutateUnlocked(path, fields) {
    if (pending()) { message("Сначала повторите сохранённое действие."); el("rwRetry").hidden = false; return; }
    const saved = {path, body: {...fields, operation_id: "WORKLOAD.UI:" + crypto.randomUUID()}};
    intent.save(saved); el("rwRetry").hidden = false;
    await retryUnlocked();
  }
  async function retry() { return pendingLock(retryUnlocked); }
  async function retryUnlocked() {
    const record=intent.read(),saved=record.value;
    if(record.damaged)throw Error('Запрос повреждён. Сначала сохраните его в архив и перечитайте настройки.');
    if(!saved)return;
    const identity=owner(); el("rwRetry").disabled=true;
    try {
      const result=await request(saved.path,"POST",saved.body);
      if(identity!==owner())return;
      if(!intent.confirms(saved,result))throw Error('Ответ не подтверждает исходную операцию. Повторите сохранённый запрос.');
      intent.settle(record);el("rwRetry").hidden=true;await refresh();message('Действие подтверждено: '+result.operation_id);
    } catch(error) {
      if(identity!==owner())return;
      if(intent.rejected(error))intent.settle(record);
      message(error.message+(intent.read().raw!==null?' Повторите исходное действие.':' Исправьте данные после перечитывания настроек.'));
      el("rwRetry").hidden=!pending();
    } finally {if(identity===owner())el("rwRetry").disabled=false;}
  }
  function localSecond(iso, finish = false) {
    const match = el("rwOffset").value.match(/^([+-])(\d{2}):(\d{2})$/);
    if (!match) throw Error("Выберите часовой пояс ввода.");
    const minutes = (Number(match[2]) * 60 + Number(match[3])) * (match[1] === "+" ? 1 : -1);
    const instant = Date.parse(iso);
    if (!Number.isFinite(instant)) throw Error("Некорректное время рекомендации.");
    const rounded = (finish ? Math.ceil(instant / 1000) : Math.floor(instant / 1000)) * 1000;
    return new Date(rounded + minutes * 60000).toISOString().slice(0, 19);
  }
  function renderRecommendations(result, serial, selected) {
    const proposal = result.recommendations;
    if (!proposal) return;
    text(el("rwResult"), "Рекомендации по плановому ресурсу: " + proposal.status + ". Доступность конкретного сотрудника ещё не подтверждена.");
    (proposal.capacity_actions || []).forEach(row => {
      const block = document.createElement("div");
      text(block, row.from_utc + " — " + row.to_utc + ": добавить " + row.additional_planned_person_hours +
        " плановых человеко-часов; при полном покрытии интервала — ещё " + row.additional_full_interval_people + " сотрудников.");
      if (auth().hasPermission("resource_shift_edit") && Date.parse(row.to_utc) > Date.now()) {
        const button = document.createElement("button"); button.textContent = "Подставить интервал в план выхода";
        button.addEventListener("click", () => {
          if (serial !== sequence || selected !== scope()) {message("Пересчитайте текущий вариант."); return;}
          clearReplacement(); el("rwStart").value = localSecond(row.from_utc);
          el("rwFinish").value = localSecond(row.to_utc, true);
          el("rwAttendReason").value = "Покрытие рассчитанного дефицита плановой CASE-комплектации";
          message("Интервал подставлен. Выберите квалифицированного сотрудника и отдельно сохраните план; явка не создана.");
        });
        block.appendChild(button);
      }
      el("rwResult").appendChild(block);
    });
    (proposal.wave_duration_scenarios || []).forEach(row => {
      if (!row.one_person_to_utc) {text(el("rwResult"), "Волна " + row.wave_id + ": требуется актуальная норма и единое окно."); return;}
      text(el("rwResult"), "Волна " + row.wave_id + ": с одним сотрудником по норме нужно " + row.known_remaining_person_hours +
        " ч; окончание сценария " + row.one_person_to_utc + ". Сотрудник, подача и стык с рейсом не проверены.");
      const button = document.createElement("button"); button.textContent = "Подставить окно одного сотрудника в предварительный расчёт";
      button.addEventListener("click", () => {
        if (serial !== sequence || selected !== scope()) {message("Пересчитайте текущий вариант."); return;}
        el("rwWave").value = String(row.wave_id); el("rwWaveStart").value = localSecond(row.current_from_utc);
        el("rwWaveFinish").value = localSecond(row.one_person_to_utc, true);
        message("Сценарий подставлен. Добавьте окно и пересчитайте нагрузку; план волны не утверждён.");
      });
      el("rwResult").appendChild(button);
    });
    text(el("rwResult"), "Рекомендация не назначает людей и не переносит утверждённую волну. Подача, перерывы, оборудование и срок рейса проверяются отдельно.");
  }
  async function preview() {
    const serial = ++sequence, selected = scope();
    try {
      const result = await request("/api/resources/workload/warehouses/" + ware() + "/preview", "POST", {site_code: el("rwSite").value, start_at: at("rwViewStart"), finish_at: at("rwViewFinish"), interval_minutes: Number(el("rwInterval").value), wave_windows: windows});
      if (serial !== sequence || selected !== scope()) return;
      el("rwResult").replaceChildren();
      text(el("rwResult"), "Текущих активных сессий: " + result.current_presence_count + ". Это не фонд будущего времени.");
      if (result.status === "NO_WORK") text(el("rwResult"), "Нет текущей CASE-работы в действующих волнах.");
      window.workloadOverview.render(el("rwResult"),result);
      result.work_outside_view.forEach(row => text(el("rwResult"), "За пределами окна: волна " + row.pick_wave_id + " · " + row.article + " · около " + row.estimated_quantity_outside + " " + row.base_uom));
      result.unscheduled_work.forEach(row => text(el("rwResult"), "Нет окна: волна " + row.pick_wave_id + " · " + row.article + " · осталось " + row.remaining_quantity + " " + (row.base_uom || "BASE не определена")));
      result.work.filter(row => row.base_per_hour === null).forEach(row => text(el("rwResult"), "Норма не задана: " + row.article + " " + (row.base_uom || "")));
      renderRecommendations(result,serial,selected);
      message("Предварительный расчёт выполнен; планы и задания не изменены.");
    } catch (error) { if (serial === sequence) message(error.message); }
  }
  function addWindow() {
    try {
      const wave = Number(el("rwWave").value);
      if (!Number.isSafeInteger(wave) || wave < 1) throw Error("Укажите волну.");
      windows = windows.filter(row => row.wave_id !== wave);
      windows.push({wave_id: wave, start_at: at("rwWaveStart"), finish_at: at("rwWaveFinish")});
      el("rwWindows").replaceChildren(); windows.forEach(row => text(el("rwWindows"), "Волна " + row.wave_id + " · " + row.start_at + " — " + row.finish_at)); ++sequence; el("rwResult").replaceChildren();
    } catch (error) { message(error.message); }
  }
  el("rwRefresh").addEventListener("click", refresh); el("rwPreview").addEventListener("click", preview); el("rwRetry").addEventListener("click", retry); el("rwAddWindow").addEventListener("click", addWindow);
  el("rwClearWindows").addEventListener("click", () => { windows = []; ++sequence; el("rwResult").replaceChildren(); el("rwWindows").replaceChildren(); });
  el("rwNorm").addEventListener("click", () => {
    try {
      if (!config || config.warehouse_id !== ware()) throw Error("Сначала загрузите актуальные настройки.");
      const current = config.norms.find(row => row.site_code === el("rwSite").value && row.article === el("rwArticle").value && row.base_uom === el("rwBase").value);
      mutate("/api/resources/workload/norms", {warehouse_id: ware(), site_code: el("rwSite").value, article: el("rwArticle").value, base_uom: el("rwBase").value, base_per_hour: el("rwRate").value, expected_version: current?.version_no || 0, active: true, reason: el("rwNormReason").value});
    } catch (error) { message(error.message); }
  });
  el("rwAttend").addEventListener("click", () => { try { mutate("/api/resources/workload/attendance", {warehouse_id: ware(), site_code: el("rwSite").value, resource_id: Number(el("rwPerson").value), start_at: at("rwStart"), finish_at: at("rwFinish"), reason: el("rwAttendReason").value}); } catch (error) { message(error.message); } });
  el("rwReplaceClear").addEventListener("click", clearReplacement);
  el("rwReplace").addEventListener("click", () => {
    try {
      if (!replacement || replacement.owner !== owner() || replacement.warehouse !== ware()) throw Error("Заново выберите действующий план этого склада.");
      mutate("/api/resources/workload/attendance/replace", {warehouse_id: ware(), plan_operation_id: replacement.source,
        site_code: el("rwSite").value, resource_id: Number(el("rwPerson").value),
        start_at: at("rwStart"), finish_at: at("rwFinish"), reason: el("rwAttendReason").value});
    } catch (error) {message(error.message);}
  });
  ["rwWare", "rwSite"].forEach(id => el(id).addEventListener("input", reset));
  ["rwViewStart", "rwViewFinish", "rwInterval", "rwOffset"].forEach(id => el(id).addEventListener("input", () => { ++sequence; el("rwResult").replaceChildren(); }));
  el("rwOffset").addEventListener("change", reset);
  window.addEventListener("wms-admin-auth-ready", () => {
    if (currentOwner !== owner()) { currentOwner = owner(); reset(); }
    document.querySelectorAll("[data-workload-edit]").forEach(node => { node.hidden = !auth().hasPermission("resource_shift_edit"); });
  });
})();
