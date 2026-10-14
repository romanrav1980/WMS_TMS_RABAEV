(() => {
  const el = id => document.getElementById(id), auth = () => window.wmsAdminAuth;
  const scope = () => JSON.stringify([auth().state.apiBase, auth().state.user?.username,
    ...["sdWare", "sdArticle", "sdFrom", "sdTo", "sdForecast", "sdUnit", "sdPalletWeight", "sdCosts", "sdCandidateRoute"].map(id => el(id).value)]);
  let sequence = 0, identity = "", lastPreview = null, busy = false;
  const pendingKey = () => "nicora.slotting.draft:" + auth().state.apiBase + ":" + auth().state.user?.username;
  const actorScope = () => auth().state.apiBase + "|" + auth().state.user?.username;
  const text = (value) => {const p = document.createElement("p"); p.textContent = value; el("sdResult").appendChild(p);};
  async function read() {
    const serial = ++sequence, selected = scope(); el("sdResult").replaceChildren();
    lastPreview = null; el("sdSaveDraft").disabled = true;
    try {
      const ware = Number(el("sdWare").value), article = el("sdArticle").value.trim();
      if (!Number.isSafeInteger(ware) || ware <= 0 || !article) throw Error("Укажите склад и артикул.");
      const body = {period_from: el("sdFrom").value, period_to_exclusive: el("sdTo").value};
      if (el("sdForecast").value.trim()) {
        body.declared_period_forecast = el("sdForecast").value.trim();
        body.forecast_base_uom = el("sdUnit").value.trim();
      }
      if (el("sdCandidateRoute").value.trim()) {
        const route = Number(el("sdCandidateRoute").value);
        if (!Number.isSafeInteger(route) || route <= 0) throw Error("Укажите целочисленный идентификатор маршрута.");
        body.candidate_pick_route_id = route;
      }
      if (el("sdPalletWeight").value.trim()) body.declared_pallet_gross_weight_kg = el("sdPalletWeight").value.trim();
      const costLines = el("sdCosts").value.trim().split(/\r?\n/).filter(line => line.trim());
      body.recommendation_costs = costLines.map(line => {
        const parts = line.split(";").map(part => part.trim());
        if (parts.length !== 4 || !/^\d+$/.test(parts[0]) || !Number.isSafeInteger(Number(parts[0]))) throw Error("Норматив: ID; секунды отбора на единицу; секунды пополнения; основание.");
        return {pick_face_id: Number(parts[0]), pick_seconds_per_base: parts[1],
          replenish_seconds_per_pallet: parts[2], basis: parts[3]};
      });
      const base = auth().state.apiBase.replace(/\/$/, "");
      const response = await fetch(base + "/api/inventory/slotting/warehouses/" + ware + "/articles/" + encodeURIComponent(article) + "/scenario",
        {method: "POST", headers: {...auth().headers(), "Content-Type": "application/json"}, body: JSON.stringify(body)});
      const result = await response.json();
      if (!response.ok) throw Error(result.detail?.message || result.detail?.code || JSON.stringify(result.detail));
      if (serial !== sequence || selected !== scope()) return;
      lastPreview = {scope: selected, body, result, ware, article};
      el("sdSaveDraft").disabled = result.range_recommendation?.status !== "NOMINAL_RECOMMENDATION";
      const q = result.scenario, unit = result.base_uom;
      text("Известная незавершённая потребность: " + q.firm_unpicked_quantity + " " + unit);
      text("Заказы заменили в прогнозе: " + q.forecast_consumed_by_orders + " " + unit);
      text("Итого в сценарии: " + q.scenario_required_quantity + " " + unit);
      text("Пригодный старый запас для периода: " + q.old_stock_credit + " " + unit + " · назначенные подачи: " + q.scheduled_inbound_credit);
      text("Дополнительная номинальная подача: " + (q.nominal_additional_quantity ?? "норма паллетной кратности не задана") + " " + unit);
      text("Это расчёт объёма. Геометрия, маршруты, партии и утверждение диапазона ещё нужны; размещение не изменено.");
      if (result.undated_unpicked_quantity !== "0") text("Без даты: ещё " + result.undated_unpicked_quantity + " " + unit + ". Укажите плановый период этих заказов.");
      result.sources.undated_orders.forEach(row => text("Заказ " + row.order_id + " · строка " + row.line_id + " · без даты · " + row.unpicked_quantity + " " + unit));
      result.sources.old_stock.forEach(row => text(row.cell + " · идентификатор паллеты " + row.pallet_identifier + " · учтено " + row.credit + " " + unit + (row.eligibility_reason ? " · причина " + row.eligibility_reason : "")));
      result.sources.scheduled_inbound.forEach(row => text("Подача " + row.task_id + " · " + row.source_cell + " → " + row.target_cell + " · учтено " + row.credit + " " + unit + (row.exclusion_reason ? " · " + row.exclusion_reason : "")));
      const layout = result.existing_range;
      if (layout) {
        text("Действующий диапазон: " + layout.distinct_cell_count + " ячеек · известная свободная объёмная ёмкость: " + layout.known_remaining_volume_base_quantity + " " + unit);
        text("Вне известной ёмкости: " + (layout.additional_quantity_outside_known_volume ?? "расчёт неполон") + " · проверка массы, геометрии и маршрута ещё обязательна.");
        layout.cells.forEach(row => text(row.cell + " · режим: " + (row.range_mode || "LEGACY_ACTIVE") + " · новое пополнение: " + (row.new_replenishment_allowed === false ? "запрещено" : "по обычным правилам") + " · объёмный бюджет: " + (row.remaining_volume_base_quantity ?? "не подтверждён") + " " + unit +
          (row.capacity_refusal ? " · " + row.capacity_refusal : "") + " · " +
          (row.withdrawal_blockers.length ? "нельзя вывести: " + row.withdrawal_blockers.join(", ") : "нет текущих блокировок вывода; утверждение ещё требуется")));
      }
      const recommendation = result.range_recommendation;
      if (recommendation) {
        text("Кандидаты: " + (recommendation.candidate_pick_route_id ? "маршрут " + recommendation.candidate_pick_route_id : "склад") + "; прежний диапазон и спрос — весь артикул склада.");
        text("Рекомендация диапазона: " + recommendation.status + " · дополнительных целых паллет: " + (recommendation.required_additional_whole_pallets ?? "не определено"));
        text("Рекомендуемое число ячеек с сохранением старого диапазона: " + (recommendation.recommended_total_face_count ?? "нет полного расчёта"));
        if (recommendation.estimated_total_additional_seconds !== null && recommendation.estimated_total_additional_seconds !== undefined)
          text("Дополнительные затраты по заявленным нормативам: " + recommendation.estimated_total_additional_seconds + " секунд.");
        (recommendation.selected_faces || []).forEach(row => text("Предложено: " + row.cell + " · ячейка " + row.pick_face_id +
          " · целая паллета " + row.nominal_pallet_base_quantity + " " + unit + " · отбор " + row.estimated_pick_seconds +
          " сек · пополнение " + row.estimated_replenish_seconds + " сек"));
        (recommendation.candidates || []).forEach(row => text("Кандидат " + row.pick_face_id + " · " + row.cell + " · " +
          (row.refusal_reasons.length ? row.refusal_reasons.join(", ") : "номинально целая паллета помещается; нужна проверка геометрии и утверждение")));
        if ((recommendation.faces_without_declared_cost || []).length)
          text("Нужны нормативы для допустимых ячеек: " + recommendation.faces_without_declared_cost.join(", "));
        text("Слотирование и текущие задания сохранены. Рекомендация пока не утверждена.");
      }
      el("sdMessage").textContent = result.status === "PERIOD_ASSIGNMENT_REQUIRED" ? "Есть заказы без подтверждённого периода." : "Сценарий рассчитан.";
    } catch (error) { if (serial === sequence) el("sdMessage").textContent = error.message; }
  }
  const draftPath = (ware, article) => "/api/inventory/slotting/warehouses/" + ware + "/articles/" + encodeURIComponent(article) + "/recommendations";
  async function sendDraft(record) {
    const owner = actorScope(), key = pendingKey();
    if (record.actorScope !== owner) throw Error("Команда принадлежит другому пользователю или серверу.");
    const response = await fetch(auth().state.apiBase.replace(/\/$/, "") + record.path,
      {method: "POST", headers: {...auth().headers(), "Content-Type": "application/json"}, body: JSON.stringify(record.body)});
    const result = await response.json();
    if (!response.ok) throw Error(result.detail?.message || result.detail?.code || JSON.stringify(result.detail));
    const saved = JSON.parse(localStorage.getItem(key) || "null");
    if (saved?.body.operation_id === record.body.operation_id) localStorage.removeItem(key);
    if (owner !== actorScope()) return;
    if (result.proposal_id) el("sdProposal").value = result.proposal_id;
    el("sdDraftMessage").textContent = result.status === "DRAFT" ? "Сохранение записано. Откройте предложение для актуального состояния; диапазон не применён." :
      result.status === "APPROVED" ? "Диапазон утверждён; прежние задания сохранены, старые назначения вымываются." :
      result.status === "DRAIN_CLOSED" ? "Пустое назначение выведено из диапазона; история сохранена." : "Отмена записана; история сохранена.";
    el("sdDraftResult").textContent = JSON.stringify(result, null, 2);
  }
  async function mutation(kind) {
    if (busy) return;
    busy = true;
    try {
      const execute = async () => {
        let record = JSON.parse(localStorage.getItem(pendingKey()) || "null");
        if (kind !== "retry") {
          if (record) throw Error("Сначала повторите неподтверждённую исходную команду.");
          const reason = el("sdDraftReason").value.trim();
          if (reason.length < 8) throw Error("Укажите основание, не менее 8 символов.");
          if (kind === "save") {
            if (!lastPreview || lastPreview.scope !== scope() || lastPreview.result.range_recommendation?.status !== "NOMINAL_RECOMMENDATION")
              throw Error("Сначала рассчитайте полный текущий вариант.");
            record = {actorScope: actorScope(), path: draftPath(lastPreview.ware, lastPreview.article),
              body: {...lastPreview.body, operation_id: "RANGE.DRAFT:" + crypto.randomUUID(),
                expected_source_signature: lastPreview.result.source_signature, reason}};
          } else {
            const ware = Number(el("sdWare").value), article = el("sdArticle").value.trim(), proposal = el("sdProposal").value.trim();
            if (!Number.isSafeInteger(ware) || ware <= 0 || !article || (kind !== "close" && !proposal)) throw Error("Укажите склад, артикул и идентификатор предложения.");
            let path, body;
            if (kind === "close") {
              const mapping = Number(el("sdDrainMapping").value);
              if (!Number.isSafeInteger(mapping) || mapping <= 0) throw Error("Укажите идентификатор вымываемого назначения.");
              path = draftPath(ware, article) + "/actions/close-drain";
              body = {operation_id: "RANGE.CLOSE:" + crypto.randomUUID(), pick_face_articul_id: mapping, reason};
            } else if (kind === "approve") {
              if (!el("sdGeometryChecked").checked || !el("sdCompatibilityChecked").checked) throw Error("Перед утверждением нужна фактическая проверка геометрии и совместимости.");
              path = draftPath(ware, article) + "/" + encodeURIComponent(proposal) + "/approve";
              body = {operation_id: "RANGE.APPROVE:" + crypto.randomUUID(), geometry_checked: true, product_compatibility_checked: true, reason};
            } else {
              path = draftPath(ware, article) + "/" + encodeURIComponent(proposal) + "/cancel";
              body = {operation_id: "RANGE.CANCEL:" + crypto.randomUUID(), reason};
            }
            record = {actorScope: actorScope(), path, body};
          }
          localStorage.setItem(pendingKey(), JSON.stringify(record));
        }
        if (!record) throw Error("Неподтверждённой команды нет.");
        const source = record.path.match(/\/warehouses\/(\d+)\/articles\/([^/]+)/);
        el("sdDraftMessage").textContent = "Исходная команда " + record.body.operation_id + (source ? " · склад " + source[1] +
          " · артикул " + decodeURIComponent(source[2]) : "") + ". При сбое повторите её без изменений.";
        await sendDraft(record);
      };
      if (navigator.locks) await navigator.locks.request(pendingKey(), execute);
      else await execute();
    } catch (error) {el("sdDraftMessage").textContent = error.message;}
    finally {busy = false;}
  }
  async function readDraft() {
    const selected = scope(), owner = actorScope();
    el("sdDraftResult").textContent = "";
    try {
      const ware = Number(el("sdWare").value), article = el("sdArticle").value.trim(), proposal = el("sdProposal").value.trim();
      if (!Number.isSafeInteger(ware) || ware <= 0 || !article || !proposal) throw Error("Укажите склад, артикул и предложение.");
      const response = await fetch(auth().state.apiBase.replace(/\/$/, "") + draftPath(ware, article) + "/" + encodeURIComponent(proposal),
        {headers: auth().headers()});
      const result = await response.json();
      if (!response.ok) throw Error(result.detail?.message || JSON.stringify(result.detail));
      if (selected !== scope() || owner !== actorScope()) return;
      el("sdDraftResult").textContent = JSON.stringify(result, null, 2);
      el("sdDraftMessage").textContent = "Состояние: " + result.status + " · автор: " + result.created_by + ". Это история предложения.";
    } catch (error) {if (selected === scope() && owner === actorScope()) el("sdDraftMessage").textContent = error.message;}
  }
  el("sdSaveDraft").addEventListener("click", () => mutation("save"));
  el("sdRetryDraft").addEventListener("click", () => mutation("retry"));
  el("sdCancelDraft").addEventListener("click", () => mutation("cancel"));
  el("sdReadDraft").addEventListener("click", readDraft);
  el("sdApproveDraft").addEventListener("click", () => mutation("approve"));
  el("sdCloseDrain").addEventListener("click", () => mutation("close"));
  el("sdClearDraftPending").addEventListener("click", () => {
    if (busy) return;
    try {
      const record = JSON.parse(localStorage.getItem(pendingKey()) || "null");
      if (!record) throw Error("Локального повтора нет.");
      localStorage.setItem(pendingKey() + ":last-cleared", JSON.stringify(record));
      localStorage.removeItem(pendingKey());
      el("sdDraftMessage").textContent = "Локальный повтор " + record.body.operation_id + " очищен. Запись Oracle сохранена; прежний запрос оставлен в локальной истории.";
    } catch (error) {el("sdDraftMessage").textContent = error.message;}
  });
  el("sdRead").addEventListener("click", read);
  ["sdWare", "sdArticle", "sdFrom", "sdTo", "sdForecast", "sdUnit", "sdPalletWeight", "sdCosts", "sdCandidateRoute"].forEach(id => el(id).addEventListener("input", () => {++sequence; lastPreview = null; el("sdGeometryChecked").checked = false; el("sdCompatibilityChecked").checked = false; el("sdSaveDraft").disabled = true; el("sdResult").replaceChildren();}));
  ["sdWare", "sdArticle"].forEach(id => el(id).addEventListener("input", () => {
    el("sdDraftResult").textContent = ""; el("sdDraftMessage").textContent = "";
    el("sdProposal").value = ""; el("sdDrainMapping").value = "";
  }));
  window.addEventListener("wms-admin-auth-ready", () => {
    const current = auth().state.apiBase + "|" + (auth().state.user?.username || "");
    if (identity !== current) {identity = current; el("sdDraftResult").textContent = ""; el("sdDraftMessage").textContent = ""; ++sequence; lastPreview = null; el("sdGeometryChecked").checked = false; el("sdCompatibilityChecked").checked = false; el("sdSaveDraft").disabled = true; el("sdResult").replaceChildren();}
  });
})();
